import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text  # Importa direttamente la libreria
from database import get_db
from logger import logger
import schemas

# tutte le richieste che iniziano per brain arrivano qua
router = APIRouter(prefix="/brain")

# use for the glucose advices based on phase without meal and sport
# In brain.py


@router.post("/glucose_advice")
def add_glucose_and_get_advice(data: schemas.GlucoseCreate, db=Depends(get_db)):
    # 1. Recupero profilo utente completo
    user_profile = db.execute(
        text("SELECT * FROM profiles WHERE id = :u_id"),
        {"u_id": data.user_id}
    ).mappings().first()

    if not user_profile:
        raise HTTPException(status_code=404, detail="Profilo utente non trovato")

    # 2. SALVATAGGIO (DB)
    query = text("""
        INSERT INTO glucose (user_id, sugar_value, recorded_at, source_type, phase, insulin_value, insulin_time)
        VALUES (:u_id, :s_val, :r_at, :s_type, :ph, :ins, :ins_time)
    """)
    db.execute(query, {
        "u_id": data.user_id,
        "s_val": data.sugar_value,
        "r_at": data.recorded_at,
        "s_type": data.source_type,
        "ph": data.phase,
        "ins": data.insulin_value,
        "ins_time": data.insulin_time
    })
    db.commit()

    # 3. GENERAZIONE CONSIGLIO INTELLIGENTE
    # Calcoliamo quanta insulina è attiva basandoci sulla durata specifica dell'utente
    current_iob = calculate_iob(
        data.insulin_value, 
        data.insulin_time, 
        user_profile['insulin_duration']
    )

    advice = get_smart_advice(
        data.sugar_value, 
        data.phase, 
        user_profile, 
        current_iob
    )

    return {
        "status": "Success",
        "advice": advice,
        "iob": current_iob # Restituiamo anche l'IOB per la UI se serve
    }

# Funzione di supporto (sempre in brain.py)


def get_glucose_advice_logic(sugar_value):
    if sugar_value < 70:
        return "Glicemia bassa! Mangia 15g di zuccheri rapidi."
    elif sugar_value > 180:
        return "Glicemia alta. Bevi acqua e valuta una correzione."
    else:
        return "Ottimo valore, sei nel target!"
    
def get_user_profile(user_id, db):
    query = text("SELECT * FROM profiles WHERE id = :u_id")
    return db.execute(query, {"u_id": user_id}).mappings().first()


@router.get("/tools/calculate_bolus/{user_id}")
def calculate_bolus(user_id: int, carbs: float, current_glucose: float, db=Depends(get_db)):
    # 1. Recupera i parametri medici dell'utente
    user = db.execute(text("SELECT ic_ratio, isf, target_ideal FROM profiles WHERE id = :u_id"),
                      {"u_id": user_id}).mappings().first()

    if not user:
        raise HTTPException(
            status_code=404, detail="Parametri utente non trovati")

    # 2. Calcolo dose per i carboidrati (Dose Pasto)
    meal_dose = carbs / user['ic_ratio']

    # 3. Calcolo dose di correzione (Dose Correttiva)
    # Se la glicemia è sopra il target, aggiunge insulina. Se è sotto, ne toglie.
    correction_dose = (current_glucose - user['target_ideal']) / user['isf']

    total_dose = meal_dose + correction_dose

    return {
        "total_dose": round(total_dose, 1),
        "breakdown": {
            "meal_component": round(meal_dose, 1),
            "correction_component": round(correction_dose, 1)
        }
    }


def check_active_insulin_dynamic(insulin_value, insulin_time, duration_hours):
    if not insulin_value or insulin_value <= 0:
        return 0.0
    
    diff = datetime.now() - datetime.fromisoformat(str(insulin_time))
    elapsed_hours = diff.total_seconds() / 3600
    
    if elapsed_hours >= duration_hours:
        return 0.0
        
    # Calcolo lineare semplice della rimanente (IOB)
    remaining_perc = 1 - (elapsed_hours / duration_hours)
    return round(insulin_value * remaining_perc, 1)

from datetime import datetime, timedelta

def calculate_iob(insulin_value, insulin_time, duration_hours):
    """Calcola l'Insulina Attiva (IOB) residua."""
    if not insulin_value or insulin_value <= 0 or not insulin_time:
        return 0.0
    
    # Conversione orario
    if isinstance(insulin_time, str):
        # Gestisce i vari formati ISO che possono arrivare da Flutter
        insulin_time = datetime.fromisoformat(insulin_time.replace('Z', '+00:00'))
        
    diff = datetime.now() - insulin_time
    elapsed_hours = diff.total_seconds() / 3600
    
    if elapsed_hours >= duration_hours:
        return 0.0
        
    # Calcolo lineare semplice della rimanente
    remaining_perc = 1 - (elapsed_hours / duration_hours)
    return round(insulin_value * remaining_perc, 1)

def get_smart_advice(sugar, phase, profile, iob):
    """Genera il consiglio basato su Glicemia, Fase e Insulina Attiva."""
    target_ideal = profile['target_ideal']
    isf = profile['isf']
    
    # 1. GESTIONE IPOGLICEMIA (Priorità assoluta)
    if sugar < profile['hypo_threshold']:
        if iob > 0:
            return f"⚠️ IPOGLICEMIA GRAVE! Hai ancora {iob} UI attive. Assumi 15g di zuccheri ora e ripeti tra 15 min. L'insulina ti spingerà ancora più giù."
        return "Glicemia bassa. Applica la regola dei 15: 15g di zucchero e ricontrolla tra 15 minuti."

    # 2. LOGICA PER FASE: NOTTE
    if phase == "notte":
        if sugar > profile['target_max'] and iob > 0:
            return f"Valore alto ({sugar}), ma hai {iob} UI attive. Non correggere ora per evitare ipo notturne. Ricontrolla tra 2 ore."
        if sugar < 100:
            return "Valore al limite basso per la notte. Considera uno spuntino proteico per stabilità."

    # 3. LOGICA PER FASE: DIGIUNO (Mattina)
    if phase == "digiuno":
        if sugar > 150:
            return "Buongiorno. Valore alto al risveglio. Valuta la correzione con la colazione anticipando il bolo di 10 min."

    # 4. CALCOLO CORREZIONE (Fasi Generiche / Check)
    if sugar > profile['target_max']:
        # Quanta insulina servirebbe per tornare al target?
        needed_correction = round((sugar - target_ideal) / isf, 1)
        
        if iob >= needed_correction:
            return f"Glicemia alta ({sugar}), ma l'insulina già in circolo ({iob} UI) è sufficiente. Aspetta che faccia effetto."
        else:
            gap = round(needed_correction - iob, 1)
            return f"Glicemia alta. L'insulina attiva ({iob} UI) non basta. Valuta una correzione extra di {gap} UI."

    return "Sei nel tuo target ideale. Ottimo lavoro!"
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text  # Importa direttamente la libreria
from database import get_db
from logger import logger
import schemas

# tutte le richieste che iniziano per brain arrivano qua
router = APIRouter(prefix="/brain")

#use for the glucose advices based on phase without meal and sport
# In brain.py

@router.post("/glucose_advice")
def add_glucose_and_get_advice(data: schemas.GlucoseCreate, db=Depends(get_db)):
    # 1. SALVATAGGIO (Quello che facevi prima)
    query = text("""
        INSERT INTO glucose (user_id, sugar_value, recorded_at, source_type, phase)
        VALUES (:u_id, :s_val, :r_at, :s_type, :ph)
    """)
    try:
        db.execute(query, {
            "u_id": data.user_id,
            "s_val": data.sugar_value,
            "r_at": data.recorded_at,
            "s_type": data.source_type,
            "ph": data.phase
        })
        db.commit()

        # 2. GENERAZIONE CONSIGLIO (L'intelligenza)
        # Qui metti la logica: se non è sport o cibo, dai un consiglio
        advice = get_glucose_advice_logic(data.sugar_value)

        # 3. RITORNO UNIFICATO
        return {
            "status": "Success",
            "advice": advice  # Flutter aspetta questa stringa!
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Funzione di supporto (sempre in brain.py)
def get_glucose_advice_logic(sugar_value):
    if sugar_value < 70:
        return "Glicemia bassa! Mangia 15g di zuccheri rapidi."
    elif sugar_value > 180:
        return "Glicemia alta. Bevi acqua e valuta una correzione."
    else:
        return "Ottimo valore, sei nel target!"


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

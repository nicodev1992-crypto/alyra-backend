from datetime import datetime, timezone
from datetime import datetime, timedelta, timezone
import datetime
import message_database
import premealadvice
import postmealadvice

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text  # Importa direttamente la libreria
from database import get_db
from logger import logger
import schemas

# tutte le richieste che iniziano per brain arrivano qua
router = APIRouter(prefix="/brain")


@router.post("/glucose_advice")
def add_glucose_and_get_advice(data: schemas.GlucoseData, db=Depends(get_db)):
    # 1. Recupero profilo utente completo
    user_profile = db.execute(
        text("SELECT * FROM profiles WHERE id = :u_id"),
        {"u_id": data.user_id}
    ).mappings().first()

    if not user_profile:
        raise HTTPException(
            status_code=404, detail="Profilo utente non trovato")

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

    advice = getGlucoseAdvice(data, user_id=data.user_id, db=db)

    queryAdvice = text("""
        INSERT INTO messages (created_at,user_id, last_glucose_advice,last_meal_advice)
        VALUES (:time,:u_id, :l_g_advice, :l_m_advice)
    """)
    db.execute(queryAdvice, {
        "created_at": datetime.now(timezone.utc),
        "u_id": data.user_id,
        "l_g_advice": advice,
        "l_m_advice": None
    })
    db.commit()

    return {
        "status": "Success",
        "advice": advice,
        "iob": current_iob  # Restituiamo anche l'IOB per la unità di insulina se serve
    }


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


def calculate_iob(insulin_value, insulin_time, duration_hours):
    """Calcola l'IOB residua gestendo errori di input e fusi orari."""

    # 1. GESTIONE MANCANZA DATI: Se non c'è l'ora o il valore, IOB è 0
    if not insulin_value or insulin_value <= 0 or insulin_time is None:
        return 0.0

    try:
        # 2. CONVERSIONE: Se è una stringa (ISO da Flutter), la trasformiamo in datetime
        if isinstance(insulin_time, str):
            # Gestisce il formato 'Z' di Flutter/Dart trasformandolo in offset +00:00
            insulin_time = datetime.fromisoformat(
                insulin_time.replace('Z', '+00:00'))

        # 3. UNIFORMITÀ FUSO ORARIO: Forza UTC se l'oggetto è "naive"
        if insulin_time.tzinfo is None:
            insulin_time = insulin_time.replace(tzinfo=timezone.utc)

        # 4. CALCOLO DIFFERENZA (Entrambi ora sono aware e UTC)
        now = datetime.now(timezone.utc)
        diff = now - insulin_time
        elapsed_hours = diff.total_seconds() / 3600

        # 5. LOGICA DI DECADIMENTO
        if elapsed_hours >= duration_hours or elapsed_hours < 0:
            return 0.0

        # Calcolo lineare della rimanente
        remaining_perc = 1 - (elapsed_hours / duration_hours)
        return round(insulin_value * remaining_perc, 1)

    except Exception as e:
        # Se qualcosa va storto nella conversione, non crashare l'app
        print(f"Errore nel calcolo IOB: {e}")
        return 0.0


def getGlucoseAdvice(glucoseData, user_id, db):  # salvo consiglio
    user_profile = db.execute(
        text("SELECT * FROM profiles WHERE id = :u_id"),
        {"u_id": user_id}
    ).mappings().first()

    if not user_profile:
        raise HTTPException(
            status_code=404, detail="Profilo utente non trovato")

    fase = getattr(glucoseData, 'phase', 'Check') or 'Check'
    glucose_value = glucoseData.sugar_value

    # Soglie personalizzate (con valori di default medici standard)
    ipo_threshold = user_profile.get('hypo_threshold', 70)
    target_min = user_profile.get('target_min', 80)
    target_max = user_profile.get('target_max', 140)
    measurement_unit = user_profile.get('measurement_unit', "mg/Dl")
    isf = user_profile.get('isf', 0)
    insulin_duration = user_profile.get('insulin_duration', 0)
    measurement_unit = user_profile.get('measurement_unit', "mg/Dl")
    ideal_target = user_profile.get('target_ideal', 110)

    advice = ""

    # CASO 1: IPOGLICEMIA (Servono zuccheri ultra-rapidi, NO grassi o proteine che rallentano l'assorbimento)
    if glucose_value <= ipo_threshold:
        advice = message_database.getAlarmLowGlucoseMessage(fase,
                                                            glucose_value, measurement_unit)

    # CASO 2: TENDENZA AL BASSO (Glicemia calante, serve stabilità)
    elif target_min < glucose_value < ideal_target:
        advice = message_database.getWarningLowGlucoseMessage(
            fase, glucose_value, measurement_unit, insulin_duration)

    elif glucose_value == ideal_target:
        advice = message_database.getPerfectGlucoseMessage(
            fase, measurement_unit, insulin_duration, ideal_target)

    elif ideal_target < glucose_value <= target_max:
        advice = message_database.getWarningHighGlucoseMessage(
            fase, glucose_value, measurement_unit, isf, insulin_duration, ideal_target)

    # CASO 4: IPERGLICEMIA (Glicemia alta, i carboidrati vanno ridotti a zero)
    else:
        advice = message_database.getAlarmHighGlucoseMessage(fase,
                                                             glucose_value, measurement_unit, isf, insulin_duration, ideal_target)

    # Output finale pulito
    return advice + message_database.LEGAL_DISCLAIMER


def getPostMealFoodAdvice(glucose_data, meal_data, user_id: int, db) -> str:
    # 1. Recupero del profilo utente per le soglie mediche personalizzate
    user_profile = db.execute(
        text("SELECT * FROM profiles WHERE id = :u_id"),
        {"u_id": user_id}
    ).mappings().first()

    if not user_profile:
        raise HTTPException(
            status_code=404, detail="Profilo utente non trovato")

    current_glucose = float(glucose_data.sugar_value or 0.0)

    # Soglie personalizzate (o default clinici)
    hypo_threshold = user_profile.get('hypo_threshold', 70)
    target_min = user_profile.get('target_min', 80)
    target_max = user_profile.get('target_max', 140)

    # 2. LOGICA DI CONTROLLO ESCLUSIVA PER IL POST-PASTO

    # --- CASO 1: IPOGLICEMIA IMMEDIATA ---
    if current_glucose <= hypo_threshold:
        return (
            f"🚨 ALLERTA IPOGLICEMIA POST-PASTO ({current_glucose} mg/dL)!\n"
            "La glicemia è scesa sotto la soglia di sicurezza. Questo può capitare per un dosaggio eccessivo di insulina o per un forte anticipo.\n\n"
            "COSA FARE IMMEDIATAMENTE:\n"
            "1. Assumi subito 15g di carboidrati a rapido assorbimento (es. 3 bustine di zucchero sciolte in acqua, 150ml di succo di frutta o mezza lattina di Coca-Cola normale).\n"
            "2. Riposati e ricontrolla il valore tra 15 minuti."
        )

    # --- CASO 2: TENDENZA AL BASSO ---
    elif hypo_threshold < current_glucose < target_min:
        return f"🟡 Glicemia post-prandiale tendente al basso ({current_glucose} mg/dL). Monitora il trend, se scende ancora assumi un piccolo snack."

    # --- CASO 3: IN TARGET ---
    elif target_min <= current_glucose <= target_max:
        return f"🟢 Glicemia Post-Pasto in perfetto target ({current_glucose} mg/dL)! Ottima gestione del pasto precedente."

    # --- CASO 4: IPERGLICEMIA ---
    else:
        return (
            f"🚨 IPERGLICEMIA POST-PASTO ({current_glucose} mg/dL)!\n"
            "La glicemia dopo il pasto è alta. Valuta se è necessaria una dose di correzione (bolo di correzione tramite ISF) e bevi molta acqua per aiutare i reni."
        )


def getPreFoodAdvice(df_glucose, user_id, db, mealData):
    user_profile = db.execute(
        text("SELECT * FROM profiles WHERE id = :u_id"),
        {"u_id": user_id}
    ).mappings().first()

    if not user_profile:
        raise HTTPException(
            status_code=404, detail="Profilo utente non trovato")

    glucose_value = float(df_glucose.sugar_value or 0.0)

    # Soglie personalizzate (con valori di default medici standard)
    ipo_threshold = user_profile.get('hypo_threshold', 70)
    target_min = user_profile.get('target_min', 80)
    target_max = user_profile.get('target_max', 140)
    ideal_target = user_profile.get('target_ideal', 120)
    measurement_unit = user_profile.get('measurement_unit', "mg/Dl")

    # 3. Logica di raccomandazione del CIBO
    advice = ""

    if glucose_value <= ipo_threshold:
        advice = premealadvice.getPreMealTooLowAlarmAdvice(
            glucose_value, measurement_unit, mealData)

    elif target_min < glucose_value < ideal_target:
        advice = premealadvice.getPreMealUnderTargetIdealAdvice(
            glucose_value, user_profile, mealData)

    elif glucose_value == ideal_target:
        advice = premealadvice.getPreMealExactTargetIdealAdvice(
            glucose_value, user_profile, mealData)

    elif ideal_target < glucose_value < target_max:
        advice = premealadvice.getPreMealOverTargetIdealAdvice(
            glucose_value, user_profile, mealData)

    # CASO 4: IPERGLICEMIA (Glicemia alta, i carboidrati vanno ridotti a zero)
    elif glucose_value >= target_max:
        advice = premealadvice.getPreMealGlucoseTooHigh(
            glucose_value, measurement_unit, mealData)

    # Output finale pulito
    return advice

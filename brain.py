from datetime import datetime, timezone
import message_database
import simple_message_database
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

    advice = getGlucoseAdvice(current_iob, data, user_id=data.user_id, db=db)

    queryAdvice = text("""
        INSERT INTO messages (created_at,user_id, last_glucose_advice,last_meal_advice)
        VALUES (:time,:u_id, :l_g_advice, :l_m_advice)
    """)
    db.execute(queryAdvice, {
        "time": datetime.now(timezone.utc),
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


def calculate_iob(insulin_units: float, insulin_time_raw, insulin_duration: float) -> float:
    """
    Calcola l'Insulina Attiva (IOB) con gestione robusta degli errori e fusi orari,
    utilizzando una curva di decadimento parabolica (Modello Walsh) per massima precisione medica.
    """
    # 1. Controlli preventivi di sicurezza (Evita calcoli inutili)
    if not insulin_units or insulin_units <= 0:
        return 0.0
    if not insulin_duration or insulin_duration <= 0:
        return 0.0
    if insulin_time_raw is None:
        return 0.0

    try:
        # 2. Gestione e parsing dell'orario da Flutter (Stringa ISO o Datetime)
        if isinstance(insulin_time_raw, str):
            # Sostituisce la Z con il formato offset compatibile con Python standard
            orario_pulito = insulin_time_raw.replace('Z', '+00:00')
            ora_iniezione = datetime.fromisoformat(orario_pulito)
        else:
            ora_iniezione = insulin_time_raw

        # 3. Allineamento fusi orari (Forza UTC se l'oggetto è naive)
        if ora_iniezione.tzinfo is None:
            ora_iniezione = ora_iniezione.replace(tzinfo=timezone.utc)

        # 4. Calcolo delle ore trascorse
        ora_attuale = datetime.now(timezone.utc)
        differenza_tempo = ora_attuale - ora_iniezione
        ore_trascorse = differenza_tempo.total_seconds() / 3600.0

        # 5. Vincoli temporali biologici
        if ore_trascorse <= 0:
            # Nel futuro? Ritorna l'intera dose
            return round(float(insulin_units), 2)
        if ore_trascorse >= insulin_duration:
            return 0.0

        # 6. DECADIMENTO PARABOLICO PROFESSIONALE (Curva di Walsh)
        # Sostituisce il calcolo lineare elementare con una fisica di assorbimento reale
        t = ore_trascorse
        d = insulin_duration

        if t < (d / 2):
            # Prima metà della durata: l'insulina si attiva e tocca il picco
            percentuale_consumata = 2.0 * (t ** 2) / (d ** 2)
        else:
            # Seconda metà della durata: esaurimento della coda dell'insulina
            percentuale_consumata = 1.0 - (2.0 * ((d - t) ** 2) / (d ** 2))

        percentuale_residua = max(0.0, 1.0 - percentuale_consumata)
        iob = insulin_units * percentuale_residua

        # Ritorna a 2 decimali (Fondamentale per la precisione dell'insulina)
        return round(iob, 2)

    except Exception as e:
        # Fail-safe assoluto: l'app non deve bloccarsi mai
        print(f"Errore critico calcolo IOB: {e}")
        return 0.0


def getGlucoseAdvice(current_iob, glucoseData, user_id, db):  # salvo consiglio
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
    ic_ratio = user_profile.get('ic_ratio', 0)
    insulin_duration = user_profile.get('insulin_duration', 0)
    measurement_unit = user_profile.get('measurement_unit', "mg/Dl")
    ideal_target = user_profile.get('target_ideal', 110)

    advice = ""

    # CASO 1: IPOGLICEMIA (Servono zuccheri ultra-rapidi, NO grassi o proteine che rallentano l'assorbimento)
    if glucose_value <= ipo_threshold:
        advice = simple_message_database.getSevereLowGlucoseMessage(
            fase, glucose_value, current_iob, insulin_duration, ideal_target, None, measurement_unit)
        # advice = message_database.getSevereLowGlucoseMessage(
        #     fase, glucose_value, measurement_unit, current_iob, ic_ratio, insulin_duration)

    # CASO 2: TENDENZA AL BASSO (Glicemia calante, serve stabilità)
    elif target_min < glucose_value < ideal_target:
        advice = simple_message_database.getWarningLowGlucoseMessage(
            fase, glucose_value, current_iob, insulin_duration, None, measurement_unit, ideal_target)

        # advice = message_database.getWarningLowGlucoseMessage(
        #     fase, glucose_value, measurement_unit, current_iob, insulin_duration, ideal_target)

    elif glucose_value == ideal_target:
        advice = simple_message_database.getPerfectGlucoseMessage(
            fase, glucose_value,  current_iob, insulin_duration, None, measurement_unit, ideal_target)

        # advice = message_database.getPerfectGlucoseMessage(
        #     fase, glucose_value, measurement_unit, current_iob, insulin_duration, ideal_target)

    elif ideal_target < glucose_value <= target_max:
        advice = simple_message_database.getWarningHighGlucoseMessage(
            fase, glucose_value, current_iob, insulin_duration, None, measurement_unit, ideal_target)
        # advice = message_database.getWarningHighGlucoseMessage(
        #     fase, glucose_value, measurement_unit, isf, insulin_duration, ideal_target, current_iob)

    # CASO 4: IPERGLICEMIA (Glicemia alta, i carboidrati vanno ridotti a zero)
    else:
        advice = simple_message_database.getAlarmHighGlucoseMessage(
            fase, glucose_value, current_iob, insulin_duration, ideal_target, None, measurement_unit)

        # advice = message_database.getAlarmHighGlucoseMessage(
        #     fase, glucose_value, measurement_unit, isf, current_iob, insulin_duration, ideal_target)

    # Output finale pulito
    return advice + message_database.LEGAL_DISCLAIMER


def getPreMealFoodAdvice(glucose_data, mealData, user_id: int, db) -> str:
    user_profile = db.execute(
        text("SELECT * FROM profiles WHERE id = :u_id"),
        {"u_id": user_id}
    ).mappings().first()

    if not user_profile:
        raise HTTPException(
            status_code=404, detail="Profilo utente non trovato")

    glucose_value = float(glucose_data.sugar_value or 0.0)

    # Soglie personalizzate (con valori di default medici standard)
    ipo_threshold = user_profile.get('hypo_threshold', 70)
    target_min = user_profile.get('target_min', 80)
    target_max = user_profile.get('target_max', 140)
    ideal_target = user_profile.get('target_ideal', 120)
    measurement_unit = user_profile.get('measurement_unit', "mg/Dl")

    current_iob = calculate_iob(
        glucose_data.insulin_value,
        glucose_data.insulin_time,
        user_profile['insulin_duration']
    )

    # 3. Logica di raccomandazione del CIBO
    advice = ""

    if glucose_value <= ipo_threshold:
        advice = premealadvice.getPreMealTooLowAlarmAdvice(
            glucose_value, user_profile, mealData, current_iob)

    elif target_min < glucose_value < ideal_target:
        advice = premealadvice.getPreMealUnderTargetIdealAdvice(
            glucose_value, user_profile, mealData, current_iob)

    elif glucose_value == ideal_target:
        advice = premealadvice.getPreMealExactTargetIdealAdvice(
            glucose_value, user_profile, mealData, current_iob)

    elif ideal_target < glucose_value < target_max:
        advice = premealadvice.getPreMealOverTargetIdealAdvice(
            glucose_value, user_profile, mealData, current_iob)

    # CASO 4: IPERGLICEMIA (Glicemia alta, i carboidrati vanno ridotti a zero)
    elif glucose_value >= target_max:
        advice = premealadvice.getPreMealGlucoseTooHigh(
            glucose_value, user_profile, mealData, current_iob)

    # Output finale pulito
    return advice

def getPostMealFoodAdvice(glucose_data, mealData, user_id: int, db) -> str:
    user_profile = db.execute(
        text("SELECT * FROM profiles WHERE id = :u_id"),
        {"u_id": user_id}
    ).mappings().first()

    if not user_profile:
        raise HTTPException(
            status_code=404, detail="Profilo utente non trovato")

    glucose_value = float(glucose_data.sugar_value or 0.0)

    # Soglie personalizzate (con valori di default medici standard)
    ipo_threshold = user_profile.get('hypo_threshold', 70)
    target_min = user_profile.get('target_min', 80)
    target_max = user_profile.get('target_max', 140)
    ideal_target = user_profile.get('target_ideal', 120)
    measurement_unit = user_profile.get('measurement_unit', "mg/Dl")

    current_iob = calculate_iob(
        glucose_data.insulin_value,
        glucose_data.insulin_time,
        user_profile['insulin_duration']
    )

    # 3. Logica di raccomandazione del CIBO
    advice = ""

    if glucose_value <= ipo_threshold:
        advice = postmealadvice.getPostMealTooLowAlarmAdvice(
            glucose_value, user_profile, mealData, current_iob)

    elif target_min < glucose_value < ideal_target:
        advice = postmealadvice.getPostMealUnderTargetIdealAdvice(
            glucose_value, user_profile, mealData, current_iob)

    elif glucose_value == ideal_target:
        advice = postmealadvice.getPostMealExactTargetIdealAdvice(
            glucose_value, user_profile, mealData, current_iob)

    elif ideal_target < glucose_value < target_max:
        advice = postmealadvice.getPostMealOverTargetIdealAdvice(
            glucose_value, user_profile, mealData, current_iob)

    # CASO 4: IPERGLICEMIA (Glicemia alta, i carboidrati vanno ridotti a zero)
    elif glucose_value >= target_max:
        advice = postmealadvice.getPostMealGlucoseTooHigh(
            glucose_value, user_profile, mealData, current_iob)

    # Output finale pulito
    return advice

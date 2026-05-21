from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text  # Importa direttamente la libreria
from database import get_db
from logger import logger
import schemas
# tutte le richieste che iniziano per post arrivano qua
router = APIRouter(prefix="/post")


# -------------------------------------- USER REGISTER AND LOGIN
@router.post("/register_user")
def insert_new_profile(user: schemas.UserRegister, db=Depends(get_db)):
    logger.info(f"Inserimento profilo completo per: {user.full_name}")

    # Logica hypo_threshold esistente...
    if user.hypo_threshold is not None:
        hyp_thres = user.hypo_threshold
    else:
        hyp_thres = 70 if user.measurement_unit == "mg/dL" else 3.9

    query = text("""
    INSERT INTO profiles (
        full_name, measurement_unit, diabetes_type, diabetes_note, 
        target_min, target_max, target_ideal, ic_ratio, isf, 
        insulin_duration, ketone_threshold, hypo_threshold, 
        email, phone_number, password,
        privacy_accepted, privacy_timestamp  
    )
    VALUES (
        :f_name, :m_unit, :diabete, :diabete_n, 
        :t_min, :t_max, :t_ideal, :ic, :isf, 
        :ins_dur, :ket_t, :hyp_t, :em, :phone, :password,
        :p_acc, :p_ts  
    )
    RETURNING id;
    """)

    try:
        result = db.execute(query, {
            "f_name": user.full_name,
            "m_unit": user.measurement_unit,
            "diabete": user.diabetes_type,
            "diabete_n": user.diabetes_note,
            "t_min": user.target_min,
            "t_max": user.target_max,
            "t_ideal": user.target_ideal,
            "ic": user.ic_ratio,
            "isf": user.isf,
            "ins_dur": user.insulin_duration,
            "ket_t": user.ketone_threshold,
            "hyp_t": hyp_thres,
            "em": user.email,
            "phone": user.phone_number,
            "password": user.password,
            # --- VALORI PRIVACY ---
            "p_acc": user.privacy_accepted,
            "p_ts": user.privacy_timestamp
        })

        new_id = result.fetchone()[0]
        db.commit()

        return {
            "status": "success",
            "user_id": new_id,
            "message": f"Profilo medico di {user.full_name} creato correttamente"
        }
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Errore DB: {e}")
        raise HTTPException(
            status_code=500, detail="Errore nel salvataggio del profilo medico")


@router.post("/login")
def login_user(credentials: dict, db=Depends(get_db)):
    email = credentials.get("email")
    password = credentials.get("password")

    # Cerchiamo l'utente nel database
    # Importante: usa lo stesso nome tabella (profiles) e colonne che hai usato nella registrazione
    query = text(
        "SELECT id, full_name FROM profiles WHERE email = :em AND password = :pw")
    result = db.execute(query, {"em": email, "pw": password}).fetchone()

    if result:
        return {
            "status": "success",
            "user_id": result[0],
            "full_name": result[1]
        }
    else:
        # Se le credenziali sono sbagliate, restituiamo un errore 401
        raise HTTPException(status_code=401, detail="Email o password errati")


# GLUCOSE

@router.post("/glucose")
def add_glucose(data: schemas.GlucoseData, db=Depends(get_db)):
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
        return {"status": "Success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# MEAL

@router.post("/glucose_meal")
def insert_glucose_meal(glucose_data: schemas.GlucoseData, meal_data: schemas.MealData, db=Depends(get_db)):
    try:
        print('Trying')
    except:
        print('Error')


@router.post("/glucose_meal")
def insert_unified_log(
    glucose_data: schemas.GlucoseData,
    meal_data: schemas.MealData,
    meal_phase : str,
    db=Depends(get_db)
):
    try:
        # Usa il campo user_id da uno dei due modelli (es. glucose_data)
        u_id = glucose_data.user_id

        # 1. Controllo se il profilo utente esiste
        user_profile = db.execute(
            text("SELECT id FROM profiles WHERE id = :u_id"),
            {"u_id": u_id}
        ).mappings().first()

        if not user_profile:
            raise HTTPException(
                status_code=404, detail="Profilo utente non trovato")

        
        # 2. SALVATAGGIO GLICEMIA + INSULINA
        # Controlla se l'utente ha inserito una glicemia valida (es. maggiore di 0)
        if glucose_data.sugar_value > 0:
            query_glucose = text("""
                INSERT INTO glucose (user_id, sugar_value, recorded_at, source_type, phase, insulin_value, insulin_time)
                VALUES (:u_id, :s_val, :r_at, :s_type, :ph, :ins, :ins_time)
            """)
            db.execute(query_glucose, {
                "u_id": u_id,
                "s_val": glucose_data.sugar_value,
                "r_at": glucose_data.recorded_at,
                "s_type": glucose_data.source_type,
                "ph": glucose_data.phase,
                # Se non c'è, Pydantic passerà None -> NULL nel DB
                "ins": glucose_data.insulin_value,
                # Se non c'è, Pydantic passerà None -> NULL nel DB
                "ins_time": glucose_data.insulin_time
            })

        if(meal_phase == "Pre"):
            db.commit()
            return {"status": "success",
                "message": "Dati salvati correttamente",
                "advice": "Pre pranzo!!"
                }
            
        # Salva il pasto solo se l'utente sta effettivamente mangiando qualcosa
        if meal_data.carbs_grams > 0:
            query_meal = text("""
                INSERT INTO meals (
                    user_id, name, carbs_grams, sugars_grams, 
                    fats_grams, proteins_grams, fibers_grams, 
                    glycemic_index, notes, consumed_at, meal_grams
                )
                VALUES (
                    :u_id, :name, :carb, :sug, 
                    :fat, :prot, :fib, 
                    :g_idx, :not, :at, :m_grams
                )
            """)
            db.execute(query_meal, {
                "u_id": u_id,
                "name": meal_data.name or "Pasto",
                "m_grams": meal_data.meal_grams,
                "carb": meal_data.carbs_grams,
                "sug": meal_data.sugars_grams,
                "fat": meal_data.fats_grams,
                "prot": meal_data.proteins_grams,
                "fib": meal_data.fibers_grams,
                "g_idx": meal_data.glycemic_index,
                "not": meal_data.notes,
                "at": meal_data.consumed_at
            })

        # Se tutto è andato a buon fine, fa il commit di entrambe le tabelle
        db.commit()
        return {"status": "success",
                "message": "Dati salvati correttamente",
                "advice": "Post pranzo!"
                }

    except HTTPException as http_ex:
        # Se l'errore è il 404 del profilo, non serve fare rollback ma lo rilanciamo
        db.rollback()
        raise http_ex
    except Exception as e:
        # In caso di errore SQL o di connessione, annulla tutto
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# POST DEXCOM
# @router.post("/sync_dexcom/{user_id}")
# def sync_dexcom(user_id: int, db=Depends(get_db)):
#     # Nota: In un futuro dovrai salvare le credenziali Dexcom nel ProfileModel
#     # Per ora puoi testarlo con variabili d'ambiente o parametri
#     dex_data = get_dexcom_value("username_amico", "password_amico")

#     if dex_data:
#         # Controlliamo se il valore esiste già per evitare duplicati
#         query_check = text(
#             "SELECT id FROM glucose WHERE recorded_at = :r_at AND user_id = :u_id")
#         exists = db.execute(
#             query_check, {"r_at": dex_data["time"], "u_id": user_id}).fetchone()

#         if not exists:
#             query_insert = text("""
#                 INSERT INTO glucose (user_id, sugar_value, recorded_at, source_type, phase)
#                 VALUES (:u_id, :s_val, :r_at, 'CGM', 'Auto')
#             """)
#             db.execute(query_insert, {
#                 "u_id": user_id,
#                 "s_val": dex_data["mg_dl"],
#                 "r_at": dex_data["time"]
#             })
#             db.commit()
#             return {"status": "updated", "value": dex_data["mg_dl"]}

#         return {"status": "already_synced", "value": dex_data["mg_dl"]}

#     raise HTTPException(status_code=404, detail="Dati Dexcom non disponibili")

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text  # Importa direttamente la libreria
from logger import logger
from typing import Optional
from database import get_db
import brain

# tutte le richieste che iniziano per get arrivano qua
router = APIRouter(prefix="/get")


@router.get("/wakeup")
def wakeup():
    return {"status": "server is awake"}

# USER


@router.get("/user")  # USATA IN USERSERVICE
def get_dati_by_ID(user_id: int, db=Depends(get_db)):
    logger.info(f"Richiesta nome profilo utente con id {user_id}")

    query = text("""
                 SELECT * FROM profiles p
                 WHERE p.id = :u_id
                 """)
    try:
        result = db.execute(query, {"u_id": user_id})
        rows = [dict(row._mapping) for row in result]

        logger.info(f"✅ Query eseguita, trovati {len(rows)} risultati")
        return rows
    except SQLAlchemyError as e:
        logger.error(f"❌ Errore nella query: {e}")
        return {"error": "Errore database"}


@router.get("/user_exists")  # USATA IN USERSERVICE
def check_user_exists(user_id: int, db=Depends(get_db)):
    logger.info(f"Verifica esistenza utente id {user_id}")

    # Chiediamo solo l'ID, non tutto il profilo (*)
    query = text("SELECT id FROM profiles WHERE id = :u_id")

    try:
        result = db.execute(query, {"u_id": user_id}).fetchone()

        if result:
            logger.info(f"✅ Utente {user_id} trovato.")
            return {"exists": True}
        else:
            logger.warning(f"⚠️ Utente {user_id} non trovato nel database.")
            return {"exists": False}

    except SQLAlchemyError as e:
        logger.error(f"❌ Errore database: {e}")
        return {"exists": False, "error": str(e)}


@router.get("/ricerca/id_utente")  # NON USATA
def get_id_utente_by_name_and_email(full_name: str, email: Optional[str] = None, phone_number: Optional[str] = None,
                                    db=Depends(get_db)
                                    ):
    logger.info(
        f"Ricerca per nome: {full_name}, email fornita: {email is not None}, numero fornito {phone_number is not None}")

    # Query che gestisce l'email opzionale
    query_str = """
        SELECT p.id 
        FROM profiles p 
        WHERE p.full_name = :f_n
    """
    params = {"f_n": full_name}

    # Aggiungi il filtro email solo se il parametro è stato passato
    if email:
        query_str += " AND p.email = :em"
        params["em"] = email

    if phone_number:
        query_str += "AND p.phone_number = :num"
        params["num"] = phone_number

    query = text(query_str)

    try:
        result = db.execute(query, params)
        rows = [row for row in result.mappings()]

        if not rows:
            logger.warning(f"⚠️ Nessun utente trovato per {full_name}")
            # Returning a 404 is cleaner for a "search" endpoint
            raise HTTPException(status_code=404, detail="Utente non trovato")

        return rows
    except SQLAlchemyError as e:
        logger.error(f"❌ Errore: {e}")
        return {"error": "Errore database"}

# GET GLUCOSE
@router.get("/last_glucose")
def get_last_glucose_and_advice(user_id: int, db=Depends(get_db)):
    query = text("""
        SELECT g.sugar_value, g.phase, g.recorded_at
        FROM glucose g
        WHERE g.user_id = :u_id
        ORDER BY g.recorded_at DESC
        LIMIT 1
    """)
    try:
        result = db.execute(query, {"u_id": user_id}).mappings().first()
        if result:
            # 1. Recuperiamo la data dal database
            dt = result.get("recorded_at")
            recorded_at_str = None

            if dt:
                # 2. Se la data non ha un fuso orario, gli diciamo esplicitamente che è UTC
                if dt.tzinfo is None:
                    from datetime import timezone
                    dt = dt.replace(tzinfo=timezone.utc)
                # 3. .isoformat() ora genererà una stringa perfetta che finisce con '+00:00' o 'Z'
                recorded_at_str = dt.isoformat()

            return {
                "sugar_value": result["sugar_value"],
                "phase": result["phase"],
                "recorded_at": recorded_at_str,  # <--- Ora questa stringa è corretta per Flutter
                "food_advice": get_last_glucose_advice(user_id=user_id, db=db)
            }
        return None
    except Exception as e:
        logger.error(f"Errore: {e}")
        return None
    
    
def get_last_glucose_advice(user_id: int, db=Depends(get_db)):
    query = text("""
        SELECT m.last_glucose_advice,
        FROM messages m
        WHERE m.user_id = :u_id
        ORDER BY m.created_at DESC
        LIMIT 1
    """)
    try:
        result = db.execute(query, {"u_id": user_id}).mappings().first()
        if result:
            # 1. Recuperiamo la data dal database
            dt = result.get("created_at")

            if dt:
                # 2. Se la data non ha un fuso orario, gli diciamo esplicitamente che è UTC
                if dt.tzinfo is None:
                    from datetime import timezone
                    dt = dt.replace(tzinfo=timezone.utc)

            return {
                "glucose_advice": result["last_glucose_advice"],
            }
        return None
    except Exception as e:
        logger.error(f"Errore: {e}")
        return None


# MEAL


@router.get("/last_meal")  # USATA IN MEALSERVICE
def get_last_meal(user_id: int, db=Depends(get_db)):
    query = text("""
        SELECT * FROM meals m
        WHERE m.user_id = :u_id
        ORDER BY m.consumed_at DESC
        LIMIT 1
    """)
    try:
        result = db.execute(query, {"u_id": user_id}).mappings().first()
        if result:
            # Trasformiamo l'oggetto Row in un dizionario pulito
            return dict(result)
        return None  # Oppure un errore 404
    except SQLAlchemyError as e:
        return {"error": str(e)}


# @router.get('/search_food')
# def search_food():
#     query = request.args.get('q', '')
#     if len(query) < 2:
#         return jsonify([])  # Non cercare per una sola lettera

#     # Cerchi i cibi che iniziano con o contengono la stringa
#     results = db.execute(
#         "SELECT id, nome, carbo_per_100g FROM cibi WHERE nome ILIKE %s LIMIT 5",
#         (f"%{query}%",)
#     ).fetchall()

#     return jsonify([{"id": r[0], "name": r[1], "carbs": r[2]} for r in results])


# Funzione per recuperare l'ultimo valore dal cloud Dexcom da collegare piu avanti
# def get_dexcom_value(username, password):
#     try:
#         # In Europa è obbligatorio ous=True
#         dexcom = Dexcom(username, password, ous=True)
#         reading = dexcom.get_current_glucose_reading()
#         if reading:
#             return {
#                 "mg_dl": reading.value,
#                 "trend": reading.trend_description,
#                 "time": reading.datetime
#             }
#     except Exception as e:
#         logger.error(f"❌ Errore connessione Dexcom OUS: {e}")
#     return None

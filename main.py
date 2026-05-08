from sqlalchemy import text  # Assicurati che sia importato
import logging
from enum import Enum
from datetime import datetime
from fastapi import HTTPException, Depends
from typing import Optional  # Importante per la chiarezza del tipo

from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, EmailStr

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Per permettere a Flutter di comunicare con python
from fastapi.middleware.cors import CORSMiddleware

#sql alchemy creazione tabella su supbase di postgresql
from datetime import datetime  # <--- Assicurati che ci sia questo
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey  # <--- Aggiungi ForeignKey qui
from sqlalchemy.orm import declarative_base

from flask import Flask, request, jsonify

Base = declarative_base()

# Definizione della tabella per SQLAlchemy
class ProfileModel(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    measurement_unit = Column(String)
    diabetes_type = Column(String)
    diabetes_note = Column(String)
    target_min = Column(Integer)
    target_max = Column(Integer)
    hypo_threshold = Column(Integer)
    email = Column(String)
    phone_number = Column(String)
    password = Column(String)
    
class GlucoseModel(Base):
    __tablename__ = "glucose"
    id = Column(Integer, primary_key=True, index=True)
    # ForeignKey collega questa colonna all'id della tabella profiles
    user_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"))
    sugar_value = Column(Float)
    recorded_at = Column(DateTime)
    source_type = Column(String)  # Es. Manual, CGM
    phase = Column(String)        # Es. Fasting, Pre-Meal
    added_time = Column(DateTime, default=datetime.utcnow)

# --- TABELLA MEALS ---
class MealModel(Base):
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True, index=True)
    # Anche qui colleghiamo l'utente
    user_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"))
    description = Column(String(255))
    carbs_grams = Column(Integer)
    consumed_at = Column(DateTime)
    added_time = Column(DateTime, default=datetime.utcnow)


# Config logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL_ = "postgresql://postgres:Figa1992@localhost:5432/Alyra_DB"

DATABASE_URL = "postgresql://postgres.pmovrnppetzrorgrxsow:Alyra1992!Figa1992!@aws-1-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=require"

# Creazione engine con echo per debug SQL
engine = create_engine(DATABASE_URL, echo=True)
# creazione tabelle
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"❌ ERRORE VALIDAZIONE: {exc.errors()}") # Questo apparirà nel terminale uvicorn
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permette a Flutter di comunicare con Python
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test connessione iniziale
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        logger.info("✅ Connessione al database riuscita")
except Exception as e:
    logger.error(f"❌ Errore connessione DB: {e}")


def get_db():
    db = SessionLocal()
    try:
        logger.info("📦 Nuova sessione DB aperta")
        yield db
    finally:
        db.close()
        logger.info("🔒 Sessione DB chiusa")

# unit measurement mg/dL,mmol/L
# phase Fasting, Pre-Meal, Post-Meal,Night
# source_type Manual, CGM (sensor), Imported


class DiabetType(str, Enum):
    T_1 = "Type 1"
    T_2 = "Type 2"
    GST = "Gestational"
    LADA = "LADA"
    OTHER = "Other"


class UnitMeasure(str, Enum):
    MG_DL = "mg/dL"
    MMOL_L = "mmol/L"


class Phase(str, Enum):
    FASTING = "Fasting"
    PRE_MEAL = "Pre-Meal"
    POST_MEAL = "Post-Meal"
    NIGHT = "Night"


class SourceType(str, Enum):
    MANUAL = "Manual"
    CGM = "CGM"
    IMPORTED = "Imported"


class UserRegister(BaseModel):
    full_name: str
    email: str # Usa str semplice per ora, come suggerito
    password: str
    measurement_unit: str = "mg/dL"
    diabetes_type: str = "Type 1"
    target_min: int = 70
    target_max: int = 180
    # Cambia queste tre righe così:
    hypo_threshold: Optional[int] = 70 
    diabetes_note: str = ""            
    phone_number: str = ""


class GlucoseEntry(BaseModel):
    user_id: int
    sugar_value: float
    recorded_at: datetime
    source_type: SourceType = SourceType.MANUAL
    phase: Phase
# --------------------------------------POST

# USATA PER REGISTRARE NOME EMIAL E PSW

@app.post("/insert/register_user")
def insert_new_profile(user: UserRegister, db=Depends(get_db)):
    logger.info(f"Inserimento profilo per: {user.full_name}")

    if user.hypo_threshold is not None:
        hyp_thres = user.hypo_threshold
    else:
        hyp_thres = 70 if user.measurement_unit == "mg/dL" else 3.9

    # MODIFICA: Aggiungiamo RETURNING id alla fine della query
    query = text("""
    INSERT INTO profiles (
        full_name, measurement_unit, diabetes_type, diabetes_note, 
        target_min, target_max, hypo_threshold, email, phone_number, password
    )
    VALUES (
        :f_name, :m_unit, :diabete, :diabete_n, 
        :t_min, :t_max, :hyp_t, :em, :phone, :password
    )
    RETURNING id;
    """)    

    try:
        # MODIFICA: Eseguiamo la query e recuperiamo il risultato
        result = db.execute(query, {
            "f_name": user.full_name,
            "m_unit": user.measurement_unit,
            "diabete": user.diabetes_type,
            "diabete_n": user.diabetes_note,
            "t_min": user.target_min,
            "t_max": user.target_max,
            "hyp_t": hyp_thres,
            "em": user.email,
            "phone": user.phone_number,
            "password": user.password
        })
        
        # Recuperiamo l'ID appena creato
        new_id = result.fetchone()[0]
        
        db.commit()
        
        # MODIFICA: Ora restituiamo anche l'user_id
        return {
            "status": "success", 
            "user_id": new_id, 
            "message": f"Profilo di {user.full_name} creato"
        }
    except SQLAlchemyError as e:
        db.rollback() 
        logger.error(f"Errore DB: {e}")
        raise HTTPException(
            status_code=500, detail="Errore durante il salvataggio")

@app.post("/login")
def login_user(credentials: dict, db = Depends(get_db)):
    email = credentials.get("email")
    password = credentials.get("password")
    
    # Cerchiamo l'utente nel database
    # Importante: usa lo stesso nome tabella (profiles) e colonne che hai usato nella registrazione
    query = text("SELECT id, full_name FROM profiles WHERE email = :em AND password = :pw")
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
    
@app.post("/insert/glucose_flutter/{user_id}")
def insert_glucose_value_flutter(user_id: int, g: GlucoseEntry, db=Depends(get_db)):
    logger.info(
        f"Tentativo inserimento ultimo pasto utente con id {g.user_id}")

    query = text("""
                 INSERT INTO glucose (user_id, sugar_value, recorded_at, source_type, phase)
                 VALUES (:u_id,:sugar,:record,:source,:phase);
                 """)
    try:
        db.execute(query, {
            "u_id": user_id,
            "sugar": g.sugar_value,
            "record": g.recorded_at,
            "source": g.source_type,
            "phase": g.phase
        })

        db.commit()  # <--- Ricorda le parentesi!
        return {"status": f"Analisi glucosio inserito correttamente per utente con ID{g.user_id}"}
    except SQLAlchemyError as e:
        logger.error(f"❌ Errore nella query: {e}")
        return {"error": "Errore database"}


@app.post("/insert/glucose/{user_id}")
def insert_glucose_value(user_id: int, sugar_value: int, recorded_time: datetime, source_t: SourceType, phase: Phase, db=Depends(get_db)):
    logger.info(f"Tentativo inserimento ultimo pasto utente con id {user_id}")

    query = text("""
                 INSERT INTO glucose (user_id, sugar_value, recorded_at, source_type, phase)
                 VALUES (:u_id,:sugar,:record,:source,:phase);
                 """)
    try:
        db.execute(query, {
            "u_id": user_id,
            "sugar": sugar_value,
            "record": recorded_time,
            "source": source_t,
            "phase": phase
        })

        db.commit()  # <--- Ricorda le parentesi!
        return {"status": f"Analisi glucosio inserito correttamente per utente con ID{user_id}"}
    except SQLAlchemyError as e:
        logger.error(f"❌ Errore nella query: {e}")
        return {"error": "Errore database"}


@app.post("/insert/last_meal")
def insert_last_meal(user_id: int, description: str,  carbs_grams: int, consumed_at: datetime, db=Depends(get_db)):
    logger.info(f"Tentativo inserimento ultimo pasto utente con id {user_id}")

    query = text("""
                 INSERT INTO meals (user_id, description, carbs_grams, consumed_at)
                 VALUES (:u_id,:desc,:carb,:consumed);
                 """)
    try:
        db.execute(query, {
            "u_id": user_id,
            "desc": description,
            "carb": carbs_grams,
            "consumed": consumed_at
        })  # fai la query scritta in sql

        db.commit()  # <--- Ricorda le parentesi!
        return {"status": "Pasto inserito correttamente"}
    except SQLAlchemyError as e:
        logger.error(f"❌ Errore nella query: {e}")
        return {"error": "Errore database"}


# -----------------------------------------------------GET
@app.get("/users/info/{user_id}")
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


@app.get("/analyses/user_health_state/{user_id}")
def get_glucose_state(user_id: int, db=Depends(get_db)):
    logger.info(f"Richiesta stato utente con id {user_id}")

    query = text("""
    SELECT g.sugar_value, p.id, p.target_min, p.target_max, p.hypo_threshold, g.recorded_at
    FROM glucose g
    JOIN profiles p ON g.user_id = p.id
    WHERE p.id = :u_id
    ORDER BY g.recorded_at DESC
        LIMIT 1
""")
    try:
        result = db.execute(query, {"u_id": user_id})
        row = result.mappings().first()

        if not row:
            return {"status": "No Data", "message": "Nessun valore inserito."}

        valore = row['sugar_value']
        t_min = row['target_min']
        t_max = row['target_max']
        # Se non definito nel DB, usiamo 70 mg/dL come default per l'ipoglicemia [cite: 10]
        h_threshold = row['hypo_threshold'] if row['hypo_threshold'] else 70

        # Logica di valutazione del rischio (Fase 2: Analisi Smart) [cite: 13, 14]
        stato = "In Target"
        colore = "green"
        consiglio = "Ottimo lavoro! Continua così."

        if valore < h_threshold:
            stato = "IPOGLICEMIA"
            colore = "blue"
            consiglio = "RISCHIO: Mangia subito zucchero o un succo!"
        elif valore < t_min:
            stato = "Basso"
            colore = "yellow"
            consiglio = "La glicemia è un po' bassa, controlla tra poco."
        elif valore > t_max:
            stato = "IPERGLICEMIA"
            colore = "red"
            consiglio = "La glicemia è alta. Bevi acqua o consulta il piano insulina."

        return {
            "ultimo_valore": valore,
            "stato": stato,
            "colore": colore,
            "consiglio": consiglio,
            "orario": row['recorded_at']
        }

    except SQLAlchemyError as e:
        logger.error(f"❌ Errore: {e}")
        return {"error": "Errore database"}


@app.get("/analyses/last_meal/{user_id}")
def get_last_meal(user_id: int, db=Depends(get_db)):
    logger.info(f"Richiesta ultimo pasto utente con id {user_id}")

    query = text("""
    SELECT p.full_name, m.description
    FROM profiles p
    JOIN meals m ON p.id = m.user_id
    WHERE p.id = :u_id
    ORDER BY m.consumed_at DESC
        LIMIT 1
""")
    try:
        result = db.execute(query, {"u_id": user_id})
        rows = [dict(row._mapping) for row in result]

        logger.info(f"✅ Query eseguita, trovati {len(rows)} risultati")
        return rows
    except SQLAlchemyError as e:
        logger.error(f"❌ Errore nella query: {e}")
        return {"error": "Errore database"}


# @app.get("/analyses/last_meal_total_carbs/{user_id}")
# def get_meal_total_carbs(user_id: int,  )


@app.get('/search_food')
def search_food():
    query = request.args.get('q', '')
    if len(query) < 2: return jsonify([]) # Non cercare per una sola lettera
    
    # Cerchi i cibi che iniziano con o contengono la stringa
    results = db.execute(
        "SELECT id, nome, carbo_per_100g FROM cibi WHERE nome ILIKE %s LIMIT 5", 
        (f"%{query}%",)
    ).fetchall()
    
    return jsonify([{"id": r[0], "name": r[1], "carbs": r[2]} for r in results])

@app.get("/analyses/meal_history/{user_id}")
def get_last_meals_story(user_id: int, db=Depends(get_db)):
    logger.info(f"Richiesta storico pasto utente con id {user_id}")

    query = text("""
    SELECT m.description AS meal, m.consumed_at AS time, m.carbs_grams AS carbs
    FROM profiles p
    JOIN meals m ON p.id = m.user_id
    WHERE p.id = :u_id
    ORDER BY m.consumed_at DESC
        LIMIT 4
""")
    try:
        result = db.execute(query, {"u_id": user_id})
        rows = [dict(row._mapping) for row in result]
        logger.info(f"✅ Query eseguita, trovati {len(rows)} risultati")
        return rows
    except SQLAlchemyError as e:
        logger.error(f"❌ Errore nella query: {e}")
        return {"error": "Errore database"}


@app.get("/analyses/critical_meals/{user_id}")
def get_cibi_critici(user_id: int, db=Depends(get_db)):
    logger.info(f"Analisi cibi critici per utente {user_id}")

    # Query che unisce Pasti, Glicemia e Profilo
    query = text("""
    SELECT 
        m.description AS cibo, 
        MAX(g.sugar_value) AS picco_massimo, 
        p.target_max,
        m.consumed_at
    FROM meals m
    JOIN profiles p ON m.user_id = p.id
    JOIN glucose g ON g.user_id = m.user_id
    WHERE m.user_id = :u_id 
      AND g.recorded_at BETWEEN m.consumed_at AND (m.consumed_at + INTERVAL '2 hours')
      AND g.sugar_value > p.target_max
    GROUP BY m.description, p.target_max, m.consumed_at
    ORDER BY picco_massimo DESC
""")

    try:
        result = db.execute(query, {"u_id": user_id})
        # Usiamo .mappings() per avere un dizionario chiaro per Flutter
        rows = [dict(row) for row in result.mappings()]

        logger.info(f"Analisi completata: trovati {len(rows)} eventi critici")
        return rows
    except SQLAlchemyError as e:
        logger.error(f"Errore analisi critica: {e}")
        return {"error": "Errore nel calcolo dei dati"}


@app.get("/analyses/picchi/{user_id}")
def get_pasti_critici(user_id: int, db=Depends(get_db)):
    logger.info(f"➡️ Richiesta analisi picchi per user_id={user_id}")

    query = text("""
        SELECT m.description, g.value as picco, m.timestamp
        FROM meals m
        JOIN glucose g ON g.timestamp BETWEEN m.timestamp AND (m.timestamp + INTERVAL '2 hours')
        WHERE m.user_id = :u_id AND g.value > (
            SELECT target_max FROM profiles WHERE id = :u_id
        )
    """)

    try:
        result = db.execute(query, {"u_id": user_id})
        rows = [dict(row) for row in result]

        logger.info(f"✅ Query eseguita, trovati {len(rows)} risultati")
        return rows

    except SQLAlchemyError as e:
        logger.error(f"❌ Errore nella query: {e}")
        return {"error": "Errore database"}


@app.get("/ricerca/id_utente")
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


@app.delete("/delete/user/{user_id}")
def delete_user_by_id(user_id: int, db=Depends(get_db)):
    logger.info(f"Provando a eliminare l'utente con ID: {user_id}")

    query_str = text("""
        DELETE FROM profiles 
        WHERE id = :u_id
    """)

    params = {"u_id": user_id}

    try:
        result = db.execute(query_str, params)
        db.commit()  # FONDAMENTALE per rendere effettiva l'eliminazione

        # Controlliamo se è stato effettivamente eliminato qualcuno
        if result.rowcount == 0:
            logger.warning(f"⚠️ Nessun utente trovato con ID {user_id}")
            raise HTTPException(status_code=404, detail="Utente non trovato")

        logger.info(f"✅ Utente {user_id} eliminato con successo")
        return {"status": "success", "message": f"Utente {user_id} rimosso"}

    except SQLAlchemyError as e:
        db.rollback()  # Annulla tutto se c'è un errore
        logger.error(f"❌ Errore database: {e}")
        raise HTTPException(
            status_code=500, detail="Errore interno del server")

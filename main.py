from logger import logger
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Importa i tuoi file router
import get
import post
import brain
import delete
# Importa il database dal tuo file database.py
from database import Base, engine, SessionLocal, DATABASE_URL

# Inizializzazione Database
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creazione Tabelle (Fondamentale!)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Alyra Backend")

# --- COLLEGAMENTO ROUTER ---
app.include_router(get.router)
app.include_router(post.router)
app.include_router(brain.router)
app.include_router(delete.router)

# Middleware CORS per Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gestore errori validazione (molto utile per il debug con Flutter)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"❌ ERRORE VALIDAZIONE: {exc.errors()}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Alyra Backend Attivo e Modulare"}




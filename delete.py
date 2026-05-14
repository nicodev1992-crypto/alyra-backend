from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text  # Importa direttamente la libreria
from database import get_db
from logger import logger
from sqlalchemy.exc import SQLAlchemyError

# tutte le richieste che iniziano per get arrivano qua
router = APIRouter(prefix="/delete")

@router.delete("/user/{user_id}")
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

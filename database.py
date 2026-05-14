from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

DATABASE_URL = "postgresql://postgres.pmovrnppetzrorgrxsow:Alyra1992!Figa1992!@aws-1-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=require"

# 1. CREIAMO LA BASE (Questa è quella che mancava!)
Base = declarative_base()

# 2. CONFIGURAZIONE MOTORE
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. LE TUE CLASSI (Usano la Base appena creata sopra)
class ProfileModel(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    measurement_unit = Column(String)
    diabetes_type = Column(String)
    diabetes_note = Column(String)
    target_min = Column(Integer)
    target_max = Column(Integer)
    target_ideal = Column(Integer, default=110)
    ic_ratio = Column(Float, default=10.0)
    isf = Column(Float, default=50.0)
    insulin_duration = Column(Integer, default=4)
    ketone_threshold = Column(Integer, default=250)
    hypo_threshold = Column(Integer)
    email = Column(String)
    phone_number = Column(String)
    password = Column(String)
    privacy_accepted = Column(Boolean, default=False)
    privacy_timestamp = Column(String)

class GlucoseModel(Base):
    __tablename__ = "glucose"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"))
    sugar_value = Column(Float)
    recorded_at = Column(DateTime)
    source_type = Column(String)
    phase = Column(String)
    added_time = Column(DateTime, default=datetime.utcnow)

class MealModel(Base):
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"))
    description = Column(String(255))
    carbs_grams = Column(Float) # Messo Float per precisione
    consumed_at = Column(DateTime)
    added_time = Column(DateTime, default=datetime.utcnow)
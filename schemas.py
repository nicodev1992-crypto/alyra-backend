from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    MANUAL = "Manual"
    CGM = "CGM"
    IMPORTED = "Imported"


class GlucoseData(BaseModel):
    user_id: int
    sugar_value: float
    recorded_at: datetime
    source_type: str
    phase: str
    insulin_value: float
    insulin_time: datetime


class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str
    measurement_unit: str = "mg/dL"
    diabetes_type: str = "Type 1"
    target_min: int = 70
    target_max: int = 180
    target_ideal: int = 110
    ic_ratio: float = 10.0
    isf: float = 50.0
    insulin_duration: int = 4
    ketone_threshold: int = 250
    hypo_threshold: Optional[int] = 70
    diabetes_note: str = ""
    phone_number: str = ""
    privacy_accepted: bool = False
    privacy_timestamp: Optional[str] = None


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


class MealData(BaseModel):
    user_id: int
    name: str                        # Cambiato da description a name per allinearsi alla query
    carbs_grams: float
    sugars_grams: float              # Mancava
    fats_grams: float                # Mancava
    proteins_grams: float            # Mancava
    fibers_grams: float              # Mancava
    glycemic_index: str              # Mancava
    notes: Optional[str] = None      # Mancava (impostato come opzionale se vuoto)
    consumed_at: datetime


class UnifiedRequest(BaseModel):
    user_id: int
    sugar_value: Optional[float] = None  # Glicemia

    # Dettagli Pasto
    description: Optional[str] = None
    carbs_grams: Optional[float] = None
    sugars_grams: Optional[float] = None
    fats_grams: Optional[float] = None
    proteins_grams: Optional[float] = None
    fibers_grams: Optional[float] = None
    glycemic_index: Optional[str] = None  # Lento, Medio, Veloce
    notes: Optional[str] = None

    # Timing e Fase
    phase: str = "Manual"  # es: pasto, sport, controllo
    event_timing: Optional[str] = None  # pre, post

    # Insulina (per il futuro consiglio o inserimento manuale)
    insulin_units: Optional[float] = None

    recorded_at: datetime = datetime.utcnow()

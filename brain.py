from datetime import datetime, timezone
from datetime import datetime, timedelta, timezone
import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text  # Importa direttamente la libreria
from database import get_db
from logger import logger
import schemas

# tutte le richieste che iniziano per brain arrivano qua
router = APIRouter(prefix="/brain")


@router.post("/glucose_advice")
def add_glucose_and_get_advice(data: schemas.GlucoseCreate, db=Depends(get_db)):
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

    advice = get_smart_advice(
        data.sugar_value,
        data.phase,
        user_profile,
        current_iob
    )

    return {
        "status": "Success",
        "advice": advice,
        "iob": current_iob  # Restituiamo anche l'IOB per la unità di insulina se serve
    }

# Funzione di supporto (sempre in brain.py)


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


def get_smart_advice(sugar, phase, profile, iob):
    d_type = profile['diabetes_type']  # Recuperato da USERDATA.csv

    print(f"Il diabete è {d_type}")
    # 1. EMERGENZA (Uguale per tutti, ma il messaggio cambia con IOB)
    if sugar < profile['hypo_threshold']:
        return getAdviceForDangerousHypo(sugar, iob, profile)

    # 2. DIVISIONE PER TIPO DI DIABETE
    if d_type in ["type1", "LADA"]:
        return getAdviceInsulinDependent(sugar, phase, profile, iob)

    elif d_type == "gestational":
        return getAdviceGestational(sugar, phase, profile)

    else:  # Tipo 2 o "Other"
        return getAdviceType2(sugar, phase, profile)

# SOGLIA IPOGLICEMICA BASSA ATTENZIONE (UGUALE PER TUTTI)


def getAdviceForDangerousHypo(sugar, iob, profile):
    hypo_threshold = profile.get('hypo_threshold', 70)

    # 1. EMERGENZA SEVERA (<55)
    if sugar < 55:
        msg = (f"🚨 EMERGENZA: Glicemia criticamente bassa ({sugar} mg/dL). "
               f"Assumi IMMEDIATAMENTE zuccheri liquidi (succo o acqua e zucchero).")

        if iob > 0:
            msg += f" ATTENZIONE: Hai ancora {iob} unità di insulina attiva che peggioreranno la discesa."
        else:
            msg += " Nonostante l'insulina attiva sia a 0, il valore è pericoloso."

        msg += " Non restare solo. Se hai vertigini o confusione, chiama il 118."
        return msg

    # 2. IPOGLICEMIA CON INSULINA ATTIVA (Effetto trascinamento)
    if sugar < hypo_threshold and iob > 0:
        return (f"⚠️ PERICOLO: Hai {sugar} mg/dL con {iob} UI attive. "
                "L'insulina continuerà ad abbassare il valore. Assumi 15g di zuccheri rapidi "
                "E uno spuntino solido (pane/biscotti) per stabilizzare il valore nel tempo.")

    # 3. IPOGLICEMIA STANDARD
    return (f"Glicemia bassa ({sugar}). Applica la regola dei 15: "
            f"15g di zucchero semplice, attendi 15 minuti e ricontrolla. "
            f"Ripeti finché non superi {hypo_threshold} mg/dL.")

# CONSIGLI PER LADA E DIABETE 1


def getAdviceInsulinDependent(sugar, phase, profile, iob):
    """Correzione della chiamata a digiuno: ora passa tutti i parametri necessari."""
    target_ideal = profile['target_ideal']
    isf = profile['isf']
    target_max = profile['target_max']
    hypo_threshold = profile['hypo_threshold']

    if phase == "notte":
        return getAdviceNightPhaseForInsulinDipendent(sugar, target_max, iob, target_ideal, isf)

    if phase == "digiuno":
        # Passiamo i parametri richiesti dalla firma della funzione
        return getAdviceDuringFastingForInsulinDipendent(sugar, target_max, hypo_threshold, target_ideal, isf)

    return getAdviceCheckForInsulinDipendent(sugar, target_max, iob, target_ideal, isf)

# CONSIGLI PER GESTAZIONALE


def getAdviceGestational(sugar, phase, profile):
    if sugar > profile['target_max']:
        return "Valore sopra il target gestazionale. Prova a bere acqua e fai una camminata leggera di 15 min. Segna cosa hai mangiato nell'ultimo pasto."
    if phase == "notte" and sugar < 95:
        return "Glicemia buona, ma tieni a portata di mano uno spuntino. La stabilità è fondamentale per il bambino."
    return "Ottimo lavoro, sei perfettamente nel range per la tua dolce attesa!"


def getAdviceType2(sugar, phase, profile):
    target_max = profile['target_max']
    target_min = profile['target_min']
    target_ideal = profile['target_ideal']

    # 1. GESTIONE IPERGLICEMIA (Valore Alto)
    if sugar > target_max:
        advice = f"Valore sopra il target ({sugar}). "

        if phase == "notte":
            return advice + "Bevi un bicchiere d'acqua e cerca di riposare. Se il valore persiste alto al risveglio, parlane con il tuo medico per valutare la terapia serale."

        if phase == "digiuno":
            return advice + "Il valore al risveglio è alto. Assicurati di aver assunto correttamente la tua terapia abituale e prediligi una colazione a basso contenuto di zuccheri."

        # Fase Check / Generica
        return advice + "Considera una camminata leggera di 15-20 minuti per aiutare i muscoli a consumare lo zucchero in eccesso e idratati bene."

    # 2. GESTIONE RANGE OTTIMALE
    if target_min <= sugar <= target_max:
        if phase == "notte":
            return "Glicemia perfetta per la notte. Riposa sereno!"
        return f"Ottimo lavoro! Sei nel tuo range ideale ({target_ideal}). Continua così."

    # 3. GESTIONE VALORE BASSO (Ma sopra la soglia di emergenza)
    if sugar < target_min:
        return "Glicemia leggermente bassa. Uno spuntino leggero (es. un frutto piccolo o uno yogurt) può aiutarti a stabilizzare i valori."

    return "Valore registrato correttamente."

# fasi InsulinDipendent


def getAdviceDuringFastingForInsulinDipendent(sugar, target_max, hypo_threshold, target_ideal, isf):
    # CASO 1: Ipoglicemia al risvegliogetAdviceForFastingfORiNSULINdIPENDENT
    if sugar < hypo_threshold:
        return f"Attenzione: sveglia in ipoglicemia ({sugar}). Consuma subito 15g di carboidrati rapidi. Parlane con il medico: la basale potrebbe essere troppo alta."
    # CASO 2: Valore Alto (Iperglicemia mattutina)
    if sugar > target_max:
        # Calcoliamo la correzione necessaria per la colazione
        needed_correction = round((sugar - target_ideal) / isf, 1)
        return (f"Buongiorno. Valore alto al risveglio ({sugar}). "
                f"Valuta di aggiungere {needed_correction} unità di insulina al bolo della colazione "
                f"e attendi 10-15 minuti prima di mangiare per contrastare la resistenza insulinica mattutina.")

    # CASO 3: Valore nel Target
    if sugar <= target_max and sugar >= 100:
        return "Buongiorno! Ottimo risveglio, la tua glicemia è perfettamente nel target. Buona colazione!"

    return "Buongiorno. Sei nel range, ma vicino al limite basso. Inizia la colazione senza attendere troppo."


def getAdviceNightPhaseForInsulinDipendent(sugar, target_max, iob, target_ideal, isf):
    # Calcolo della previsione (Glicemia stimata quando l'insulina finirà l'effetto)
    # Formula: Glicemia Attuale - (Insulina Attiva * Sensibilità)
    predicted_sugar = round(sugar - (iob * isf))

    # Stringa della previsione da aggiungere ai messaggi
    prediction_msg = f"\n\n🔮 Previsione: Quando l'insulina finirà l'effetto, sarai a circa {predicted_sugar} mg/dL."

    # CASO 1: Glicemia Alta
    if sugar > target_max:
        if iob > 0:
            # Se la previsione ci porta già nel target, rassicuriamo l'utente
            if predicted_sugar <= target_max and predicted_sugar >= 80:
                return f"Valore alto ({sugar} mg/dL), ma l'insulina attiva ti porterà a {predicted_sugar} durante la notte. Non correggere." + prediction_msg

            return f"Valore alto ({sugar} mg/dL). Hai {iob} UI attive che ti porteranno a {predicted_sugar}. Attendi che finiscano l'effetto." + prediction_msg

        else:
            # Calcolo prudente per la notte (puntiamo a un target più alto di 30mg/dL per sicurezza)
            safe_target = target_ideal + 30
            needed_correction = round((sugar - safe_target) / isf, 1)
            if needed_correction > 0:
                return f"Glicemia alta e nessuna insulina attiva. Valuta {needed_correction} UI per scendere verso i {safe_target} mg/dL."
            return "Valore leggermente alto, ma sicuro per la notte. Riposa sereno."

    # CASO 2: Glicemia Bassa o al limite
    if sugar < 100:
        if sugar < 70:
            return "⚠️ Emergenza: Glicemia troppo bassa! Assumi zuccheri rapidi (succo o glucosio) e uno spuntino subito."

        # Se siamo al limite e abbiamo pure insulina attiva, è molto rischioso
        if iob > 0:
            return f"Valore al limite ({sugar} mg/dL) e hai ancora insulina attiva! Rischio ipoglicemia grave a {predicted_sugar}. Mangia subito dei carboidrati!" + prediction_msg

        return "Valore al limite per la notte. Considera uno spuntino con carboidrati complessi (es. cracker) per evitare cali."

    # CASO 3: In Target (Glicemia tra 100 e target_max)
    if iob > 0:
        # Se siamo nel target ma la previsione ci porta sotto la soglia di sicurezza
        if predicted_sugar < 90:
            return f"Glicemia attuale ottima ({sugar}), ma l'insulina attiva ti porterà a {predicted_sugar}. Mangia un piccolo spuntino per non scendere troppo." + prediction_msg

        return f"Glicemia perfetta. L'insulina attiva ti porterà a {predicted_sugar} mg/dL, un valore sicuro per la notte." + prediction_msg

    return "Glicemia perfetta e nessuna insulina attiva. Buonanotte!"


def getAdviceCheckForInsulinDipendent(sugar, target_max, iob, target_ideal, isf):
    if sugar > target_max:
        needed_correction = round((sugar - target_ideal) / isf, 1)

        if iob == 0:
            return f"Glicemia alta. Per tornare a {target_ideal} servirebbero {needed_correction} unità di insulina."

        if iob >= needed_correction:
            return f"Glicemia alta, ma coperta da {iob} unità di insulina di insulina attiva. Attendi."

        gap = round(needed_correction - iob, 1)
        return f"L'insulina attiva ({iob} unità di insulina) non basta. Valuta integrazione di {gap} unità di insulina."

    return "Ottimo, sei nel tuo target!"


def getFoodAdviceBasedOnGlucoseValue(df_glucose, user_id, db=Depends(get_db)):
    user_profile = db.execute(
        text("SELECT * FROM profiles WHERE id = :u_id"),
        {"u_id": user_id}
    ).mappings().first()

    if not user_profile:
        raise HTTPException(
            status_code=404, detail="Profilo utente non trovato")
        
    glicemia_attuale = float(df_glucose['sugar_value'])
    fase = df_glucose['phase']

    # Soglie personalizzate (con valori di default medici standard)
    soglia_ipo = user_profile.get('hypo_threshold', 70)
    target_min = user_profile.get('target_min', 80)
    target_max = user_profile.get('target_max', 140)

    # 3. Logica di raccomandazione del CIBO
    consiglio_cibo = ""
    categoria_stato = ""

    # CASO 1: IPOGLICEMIA (Servono zuccheri ultra-rapidi, NO grassi o proteine che rallentano l'assorbimento)
    if glicemia_attuale <= soglia_ipo:
        categoria_stato = "🔴 IPOGLICEMIA IMMEDIATA"
        consiglio_cibo = (
            "Serve zucchero semplice IMMEDIATO (circa 15g di carboidrati veloci).\n"
            "Alimenti consigliati:\n"
            "  - 1/2 bicchiere di Coca-Cola o aranciata (NON zero/diet)\n"
            "  - 1 piccolo succo di frutta (circa 100-150ml)\n"
            "  - 3 cucchiaini o bustine di zucchero sciolti in acqua\n"
            "  - 4 compresse di glucosio/destrosio\n"
            "⚠️ EVITA in questo momento: Cioccolato, merendine o biscotti (i grassi rallentano la risalita dello zucchero)."
        )

    # CASO 2: TENDENZA AL BASSO (Glicemia calante, serve stabilità)
    elif soglia_ipo < glicemia_attuale < target_min:
        categoria_stato = "🟡 GLICEMIA TENDENTE AL BASSO"
        consiglio_cibo = (
            "La glicemia è bassa ma non ancora in emergenza. Serve uno spuntino con carboidrati complessi "
            "abbinati a una piccola quota di proteine o grassi per mantenere il livello stabile nel tempo.\n"
            "Alimenti consigliati:\n"
            "  - 1 pacchetto di cracker integrali\n"
            "  - 1 fetta di pane di segale con un velo di formaggio spalmabile o bresaola\n"
            "  - 1 mela o 1 pera piccola con 3-4 mandorle"
        )

    # CASO 3: IN TARGET (La glicemia va bene)
    elif target_min <= glicemia_attuale <= target_max:
        categoria_stato = "🟢 VALORE IN TARGET"
        if "pasto" in str(fase).lower():
            consiglio_cibo = (
                f"Il valore è ottimo per la fase '{fase}'. Puoi procedere con il tuo pasto standard bilanciato.\n"
                "Alimenti consigliati:\n"
                "  - Un piatto unico con carboidrati complessi a basso indice glicemico (pasta/riso integrale, farro, quinoa)\n"
                "  - Una buona porzione di verdure (fibre) e una fonte proteica (pesce, pollo, legumi)."
            )
        else:
            consiglio_cibo = "Tutto perfetto. Se hai fame, prediligi uno snack leggero e bilanciato (es. uno yogurt bianco magro)."

    # CASO 4: IPERGLICEMIA (Glicemia alta, i carboidrati vanno ridotti a zero)
    else:
        categoria_stato = "🟠 IPERGLICEMIA / VALORE ALTO"
        consiglio_cibo = (
            f"Il valore è alto ({glicemia_attuale} mg/dL). Al momento è fondamentale evitare carboidrati e zuccheri.\n"
            "Cosa fare/mangiare:\n"
            "  - Prima di tutto: Bevi 1 o 2 grandi bicchieri d'acqua per aiutare i reni a smaltire il glucosio.\n"
            "  - Se hai assolutamente fame, scegli alimenti che NON impattano sulla glicemia (Zero Carboidrati):\n"
            "    * Qualche cubetto di parmigiano o grana\n"
            "    * Una manciata di finocchi, sedano o cetrioli crudi\n"
            "    * Un uovo sodo\n"
            "    * Qualche gheriglio di noce o mandorla (senza esagerare)"
        )

    # Output finale pulito
    return  consiglio_cibo
       

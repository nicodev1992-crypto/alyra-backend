LEGAL_DISCLAIMER = (
    "\n"
    "⚠️ NOTA IMPORTANTE\n"
    "Questa applicazione NON sostituisce il medico o il diabetologo.\n"
    "I contenuti sono esclusivamente informativi ed educativi.\n"
    "Per qualsiasi decisione terapeutica seguire sempre il piano "
    "personalizzato indicato dal proprio team medico.\n"
    "In caso di sintomi gravi o dubbi contattare immediatamente "
    "un adulto, il medico o i servizi di emergenza.\n"
)

EMERGENCY_MESSAGE = (
    "\n🚑 CHIAMARE IL 118 O CONTATTARE UN ADULTO SUBITO SE:\n"
    "- forte sonnolenza\n"
    "- confusione\n"
    "- difficoltà a parlare\n"
    "- perdita di coscienza\n"
    "- vomito persistente\n"
    "- difficoltà respiratoria\n"
)


# ============================================================
# IPOGLICEMIA GRAVE
# ============================================================

def getSevereLowGlucoseMessage(
    fase,
    glucose_value,
    current_IOB,
    insulin_duration,
    last_bolus_minutes=None,
    measurement_unit="mg/dL"
):

    fase_msg = getFaseMessage(fase)
    bolus_msg = buildIOBMessage(
        current_IOB=current_IOB,
        insulin_duration=insulin_duration,
        last_bolus_minutes=last_bolus_minutes
    )
    msg = (
        f"🔴 GLICEMIA MOLTO BASSA in fase {fase_msg} \n"

        f"La glicemia attuale è {glucose_value} {measurement_unit}.\n"

        f"⚡ Il corpo ha bisogno di zuccheri rapidi.\n"
        f"✅ Cosa fare:\n"
        f"- avvisa subito un adulto\n"
        f"- assumi zuccheri rapidi secondo il piano indicato dal diabetologo\n"
        f"- ricontrolla la glicemia dopo circa 15 minuti\n"
        f"- resta a riposo\n"

        f"{bolus_msg}\n"

        f"🍬 Esempi di zuccheri rapidi:\n"
        f"- succo di frutta\n"
        f"- bevanda zuccherata NON zero\n"
        f"- glucosio/destrosio\n"
        f"- zucchero sciolto in acqua\n"

        f"❌ Evita:\n"
        f"- attività fisica\n"
        f"- correre\n"
        f"- restare da solo\n"
    )

    return msg + EMERGENCY_MESSAGE


# ============================================================
# GLICEMIA TENDENTE AL BASSO
# ============================================================

def getWarningLowGlucoseMessage(
    fase,
    glucose_value,
    current_IOB,
    insulin_duration,
    last_bolus_minutes=None,
    measurement_unit="mg/dL",
    target_ideal=120
):

    fase_msg = getFaseMessage(fase)
    bolus_msg = buildIOBMessage(
        current_IOB=current_IOB,
        insulin_duration=insulin_duration,
        last_bolus_minutes=last_bolus_minutes
    )
    msg = (f"GLICEMIA BASSA in fase {fase_msg}\n"

           f"Glicemia attuale: {glucose_value} {measurement_unit}\n"
           f"Target indicativo: {target_ideal} {measurement_unit}\n"

           f"{bolus_msg}\n"

           f"✅ Consigli utili:\n"
           f"- controlla eventuali sintomi\n"
           f"- tieni a disposizione zuccheri rapidi\n"
           f"- valuta uno spuntino secondo il piano abituale\n"
           f"- ricontrolla la glicemia nelle prossime misurazioni\n"

           f"👀 Sintomi possibili:\n"
           f"- tremore\n"
           f"- fame improvvisa\n"
           f"- sudorazione\n"
           f"- stanchezza\n"
           f"- difficoltà di concentrazione\n"
           )

    return msg


# ============================================================
# GLICEMIA PERFETTA
# ============================================================

def getPerfectGlucoseMessage(
    fase,
    glucose_value,
    current_IOB,
    insulin_duration,
    last_bolus_minutes=None,
    measurement_unit="mg/dL",
    target_ideal=120
):

    fase_msg = getFaseMessage(fase)
    bolus_msg = buildIOBMessage(
        current_IOB=current_IOB,
        insulin_duration=insulin_duration,
        last_bolus_minutes=last_bolus_minutes
    )
    msg = (
        f"GLICEMIA OTTIMA in fase {fase_msg}\n"

        f"La glicemia è {glucose_value} {measurement_unit}.\n"
        f"Il valore è vicino al target ideale di "
        f"{target_ideal} {measurement_unit}.\n"

        f"{bolus_msg}\n"

        f"✅ Continua così:\n"
        f"- mantieni le abitudini concordate\n"
        f"- bevi acqua regolarmente\n"
        f"- continua il monitoraggio abituale\n"

        f"🎉 Ottimo lavoro!\n"
    )

    return msg


# ============================================================
# GLICEMIA TENDENTE ALL'ALTO
# ============================================================

def getWarningHighGlucoseMessage(
    fase,
    glucose_value,
    current_IOB,
    insulin_duration,
    last_bolus_minutes=None,
    measurement_unit="mg/dL",
    target_ideal=120
):

    fase_msg = getFaseMessage(fase)

    bolus_msg = buildIOBMessage(
        current_IOB=current_IOB,
        insulin_duration=insulin_duration,
        last_bolus_minutes=last_bolus_minutes
    )

    msg = (
        f"GLICEMIA ALTA in fase {fase_msg}\n"

        f"Glicemia attuale: {glucose_value} {measurement_unit}\n"
        f"{bolus_msg}\n"
        f"💧 Consigli utili:\n"
        f"- bevi acqua\n"
        f"- evita zuccheri aggiuntivi\n"
        f"- controlla come ti senti\n"
        f"- ricontrolla la glicemia più tardi\n"

        f"🏃 Movimento leggero può aiutare "
        f"(solo se previsto dal piano medico).\n"

        f"⚠️ Non modificare la terapia senza "
        f"seguire le indicazioni del diabetologo.\n"
    )

    return msg


# ============================================================
# IPERGLICEMIA IMPORTANTE
# ============================================================

def getAlarmHighGlucoseMessage(
    fase,
    glucose_value,
    current_IOB,
    insulin_duration,
    last_bolus_minutes=None,
    measurement_unit="mg/dL"
):

    bolus_msg = buildIOBMessage(
        current_IOB=current_IOB,
        insulin_duration=insulin_duration,
        last_bolus_minutes=last_bolus_minutes
    )

    fase_msg = getFaseMessage(fase)

    msg = (
        f"🔶 GLICEMIA ALTA IN FASE {fase_msg}\n"

        f"Glicemia rilevata: {glucose_value} {measurement_unit}\n"

        f"{fase_msg}\n"
        f"{bolus_msg}\n"
        f"💧 Cosa fare:\n"
        f"- bere acqua\n"
        f"- evitare zuccheri e bevande dolci\n"
        f"- seguire il piano terapeutico concordato\n"
        f"- ricontrollare la glicemia\n"

        f"👀 Controllare eventuali sintomi:\n"
        f"- molta sete\n"
        f"- stanchezza\n"
        f"- nausea\n"
        f"- mal di testa\n"
        f"- bisogno frequente di urinare\n"
    )

    return msg + EMERGENCY_MESSAGE


# ============================================================
# MESSAGGIO BAMBINO FRIENDLY
# ============================================================

def getKidFriendlyMessage(glucose_value):

    if glucose_value < 70:
        return (
            "⚡ Il corpo ha bisogno di energia veloce!\n"
            "Chiama subito un adulto 🍬"
        )

    elif glucose_value <= 180:
        return (
            "🟢 Tutto bene! Ottimo lavoro 🎉"
        )

    else:
        return (
            "💧 Lo zucchero nel sangue è un po' alto.\n"
            "Bevi acqua e avvisa un adulto 😊"
        )


# ============================================================
# BLOCCO AGGIUNTIVO INSULINA ATTIVA (IOB)
# DA AGGIUNGERE AI METODI ESISTENTI
# ============================================================

def buildIOBMessage(
    current_IOB=None,
    insulin_duration=None,
    last_bolus_minutes=None
):
    """
    Restituisce un blocco testuale educativo
    sull'insulina attiva da appendere ai messaggi.

    NON calcola boli.
    NON suggerisce dosi.
    """

    # --------------------------------------------------------
    # VALIDAZIONE SICURA
    # --------------------------------------------------------

    try:
        iob = float(current_IOB) if current_IOB is not None else 0.0
    except (ValueError, TypeError):
        iob = 0.0

    try:
        duration = (
            float(insulin_duration)
            if insulin_duration is not None
            else None
        )
    except (ValueError, TypeError):
        duration = None

    # --------------------------------------------------------
    # NESSUNA IOB
    # --------------------------------------------------------

    if iob <= 0:
        return ""

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    msg = (
        "\n"
        "💉 INSULINA ATTIVA (IOB)\n"
        f"- Sono ancora presenti circa {iob:.1f} U "
        "di insulina attiva.\n"
    )

    # --------------------------------------------------------
    # DURATA INSULINA
    # --------------------------------------------------------

    if duration:

        msg += (
            f"- Durata stimata dell'effetto: "
            f"se non sono passate più di {duration:.1f} ore dall'ultima somministrazione, "
            "evitare un'ulteriore dose per prevenire uno stacking."
        )

    # --------------------------------------------------------
    # TEMPO DALL'ULTIMO BOLO
    # --------------------------------------------------------

    if last_bolus_minutes is not None:

        try:

            mins = int(last_bolus_minutes)

            if mins < 60:

                msg += (
                    "- Il bolo è recente: l'effetto "
                    "potrebbe aumentare nelle prossime ore.\n"
                )

            elif mins < 180:

                msg += (
                    "- L'insulina è ancora nella sua "
                    "fase attiva.\n"
                )

            else:

                msg += (
                    "- L'effetto insulinico dovrebbe "
                    "ridursi progressivamente.\n"
                )

        except:
            pass

    # --------------------------------------------------------
    # EDUCAZIONE
    # --------------------------------------------------------

    msg += (
        "- Controlla frequentemente la glicemia "
        "e segui sempre il piano terapeutico.\n"
    )

    return msg


def getFaseMessage(fase):
    if fase.lower() == "notte":
        fase_msg = (
            "notturna\n"
        )

    elif fase.lower() == "digiuno":
        fase_msg = (
            "di digiuno.\n"
        )

    else:
        fase_msg = (
            "di controllo.\n"
        )

    return fase_msg

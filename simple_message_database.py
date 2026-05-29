LEGAL_DISCLAIMER = (
    "\n\n"
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
    measurement_unit="mg/dL"
):

    if fase.lower() == "notte":
        fase_msg = (
            "🌙 È notte: sveglia subito un adulto e resta a riposo.\n"
        )

    elif fase.lower() == "scuola":
        fase_msg = (
            "🏫 Avvisa immediatamente un insegnante o un adulto.\n"
        )

    else:
        fase_msg = (
            "🛑 Interrompi quello che stai facendo e siediti.\n"
        )

    msg = (
        f"🔴 GLICEMIA MOLTO BASSA\n\n"

        f"La glicemia attuale è {glucose_value} {measurement_unit}.\n\n"

        f"⚡ Il corpo ha bisogno di zuccheri rapidi.\n\n"

        f"✅ Cosa fare:\n"
        f"- avvisa subito un adulto\n"
        f"- assumi zuccheri rapidi secondo il piano indicato dal diabetologo\n"
        f"- ricontrolla la glicemia dopo circa 15 minuti\n"
        f"- resta a riposo\n\n"

        f"🍬 Esempi di zuccheri rapidi:\n"
        f"- succo di frutta\n"
        f"- bevanda zuccherata NON zero\n"
        f"- glucosio/destrosio\n"
        f"- zucchero sciolto in acqua\n\n"

        f"{fase_msg}\n"

        f"❌ Evita:\n"
        f"- attività fisica\n"
        f"- correre\n"
        f"- restare da solo\n"
    )

    return msg + EMERGENCY_MESSAGE + LEGAL_DISCLAIMER


# ============================================================
# GLICEMIA TENDENTE AL BASSO
# ============================================================

def getWarningLowGlucoseMessage(
    fase,
    glucose_value,
    measurement_unit="mg/dL",
    target_ideal=120
):

    if fase.lower() == "notte":
        fase_msg = (
            "🌙 Durante la notte è importante monitorare con attenzione.\n"
        )

    elif fase.lower() == "digiuno":
        fase_msg = (
            "🌅 La glicemia del mattino è leggermente sotto il target.\n"
        )

    else:
        fase_msg = (
            "🟡 La glicemia sta scendendo sotto il target ideale.\n"
        )

    msg = (
        f"{fase_msg}\n\n"

        f"Glicemia attuale: {glucose_value} {measurement_unit}\n"
        f"Target indicativo: {target_ideal} {measurement_unit}\n\n"

        f"✅ Consigli utili:\n"
        f"- controlla eventuali sintomi\n"
        f"- tieni a disposizione zuccheri rapidi\n"
        f"- valuta uno spuntino secondo il piano abituale\n"
        f"- ricontrolla la glicemia nelle prossime misurazioni\n\n"

        f"👀 Sintomi possibili:\n"
        f"- tremore\n"
        f"- fame improvvisa\n"
        f"- sudorazione\n"
        f"- stanchezza\n"
        f"- difficoltà di concentrazione\n"
    )

    return msg + LEGAL_DISCLAIMER


# ============================================================
# GLICEMIA PERFETTA
# ============================================================

def getPerfectGlucoseMessage(
    fase,
    glucose_value,
    measurement_unit="mg/dL",
    target_ideal=120
):

    if fase.lower() == "notte":
        titolo = "🌙 OTTIMO CONTROLLO NOTTURNO"

    elif fase.lower() == "digiuno":
        titolo = "🌅 GLICEMIA IN TARGET"

    else:
        titolo = "🟢 OTTIMO LAVORO"

    msg = (
        f"{titolo}\n\n"

        f"La glicemia è {glucose_value} {measurement_unit}.\n"
        f"Il valore è vicino al target ideale di "
        f"{target_ideal} {measurement_unit}.\n\n"

        f"✅ Continua così:\n"
        f"- mantieni le abitudini concordate\n"
        f"- bevi acqua regolarmente\n"
        f"- continua il monitoraggio abituale\n\n"

        f"🎉 Ottimo lavoro!\n"
    )

    return msg + LEGAL_DISCLAIMER


# ============================================================
# GLICEMIA TENDENTE ALL'ALTO
# ============================================================

def getWarningHighGlucoseMessage(
    fase,
    glucose_value,
    measurement_unit="mg/dL",
    target_ideal=120
):

    if fase.lower() == "notte":
        titolo = "🌙 GLICEMIA LEGGERMENTE ALTA DI NOTTE"

    elif fase.lower() == "digiuno":
        titolo = "🌅 GLICEMIA TENDENTE ALL'ALTO"

    else:
        titolo = "🟡 GLICEMIA SOPRA IL TARGET"

    msg = (
        f"{titolo}\n\n"

        f"Glicemia attuale: {glucose_value} {measurement_unit}\n\n"

        f"💧 Consigli utili:\n"
        f"- bevi acqua\n"
        f"- evita zuccheri aggiuntivi\n"
        f"- controlla come ti senti\n"
        f"- ricontrolla la glicemia più tardi\n\n"

        f"🏃 Movimento leggero può aiutare "
        f"(solo se previsto dal piano medico).\n\n"

        f"⚠️ Non modificare la terapia senza "
        f"seguire le indicazioni del diabetologo.\n"
    )

    return msg + LEGAL_DISCLAIMER


# ============================================================
# IPERGLICEMIA IMPORTANTE
# ============================================================

def getAlarmHighGlucoseMessage(
    fase,
    glucose_value,
    measurement_unit="mg/dL"
):

    if fase.lower() == "notte":
        fase_msg = (
            "🌙 Controllo notturno: avvisa un adulto.\n"
        )

    elif fase.lower() == "scuola":
        fase_msg = (
            "🏫 Informare insegnanti o personale scolastico.\n"
        )

    else:
        fase_msg = (
            "🟠 Valore fuori target.\n"
        )

    msg = (
        f"🔶 GLICEMIA ALTA\n\n"

        f"Glicemia rilevata: {glucose_value} {measurement_unit}\n\n"

        f"{fase_msg}\n"

        f"💧 Cosa fare:\n"
        f"- bere acqua\n"
        f"- evitare zuccheri e bevande dolci\n"
        f"- seguire il piano terapeutico concordato\n"
        f"- ricontrollare la glicemia\n\n"

        f"👀 Controllare eventuali sintomi:\n"
        f"- molta sete\n"
        f"- stanchezza\n"
        f"- nausea\n"
        f"- mal di testa\n"
        f"- bisogno frequente di urinare\n"
    )

    return msg + LEGAL_DISCLAIMER


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

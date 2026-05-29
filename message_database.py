
def getAlarmLowGlucoseMessage(fase, glucose_value, measurement_unit, current_IOB=None, insulin_duration=None):
    # 1. Definizione dell'intestazione e dell'introduzione specifica per fase
    if fase.lower() == "notte":
        header = "🔴 IPOGLICEMIA FASE NOTTURNA"
        intro_fase = (
            "L'ipoglicemia di notte va trattata immediatamente. "
            "Siediti sul letto, accendi la luce e non muoverti finché non hai preso lo zucchero.\n\n"
            "⚠️ Nota: Una volta che la glicemia sarà risalita sopra i 70 mg/dL, "
            "consuma un piccolo spuntino complesso (es. 2-3 cracker o un pezzo di pane) "
            "prima di metterti a dormire, per evitare ricadute."
        )
    elif fase.lower() == "digiuno":
        header = "🔴 IPOGLICEMIA FASE DIGIUNO"
        intro_fase = "Devi far risalire subito i livelli di zucchero nel sangue prima di iniziare qualsiasi attività mattutina o preparare la colazione."
    else:
        header = "🔴 IPOGLICEMIA FASE DI CONTROLLO"
        intro_fase = "Interrompi subito qualsiasi attività tu stia facendo e correggi immediatamente il valore."

    # 2. Costruzione del messaggio principale
    msg = (
        f"{header}\n\n"
        f"{intro_fase}\n\n"
        f"Il tuo valore è pericolosamente basso: {glucose_value} {measurement_unit}.\n"
        f"Applica subito la Regola dei 15 per far risalire i livelli in sicurezza.\n\n"

        f"⚡ Cosa fare ORA (Assumi circa 15g di zuccheri rapidi):\n"
        f" Scegli uno solo tra questi alimenti pronti:\n"
        f"  - 1/2 bicchiere di Coca-Cola o aranciata classica (NON zero/diet)\n"
        f"  - 1 piccolo succo di frutta (circa 100-150 ml)\n"
        f"  - 3 cucchiaini o bustine di zucchero sciolti in un goccio d'acqua\n"
        f"  - 4 compresse di glucosio o destrosio\n\n"

        f"⏱️ Cosa fare DOPO (Aspetta 15 minuti):\n"
        f"  - Resta a riposo e attendi 15 minuti senza mangiare altro cibo.\n"
        f"  - Misura nuovamente la glicemia: se è ancora inferiore a 70 mg/dL, ripeti l'assunzione di 15g di zucchero.\n\n"

        f"❌ Errori gravi da evitare in questo momento:\n"
        f"  - Non mangiare cioccolato, merendine, biscotti o gelato. Contengono grassi che rallentano la digestione, impedendo allo zucchero di entrare rapidamente nel sangue.\n"
    )

    # 3. Controllo dinamico e integrato sull'Insulina Attiva (IOB)
    try:
        iob_val = float(current_IOB) if current_IOB is not None else 0.0
    except (ValueError, TypeError):
        iob_val = 0.0

    if iob_val > 0:
        msg += (
            f"\n⚠️ ATTENZIONE: HAI INSULINA ATTIVA (IOB)\n"
            f"Hai ancora {iob_val:.2f} U di insulina in circolo"
        )
        if insulin_duration and float(insulin_duration) > 0:
            msg += f" (durata totale impostata: {insulin_duration} ore)"

        msg += (
            ".\nQuesto significa che la glicemia tenderà a scendere ulteriormente "
            "e contrasterà l'effetto dello zucchero appena preso. "
            "Potrebbe essere necessario ripetere la correzione dei 15g più volte. "
            "Monitorati con massima frequenza.\n"
        )

    # Nota: puoi appendere qui il tuo trafiletto legale o il consiglio dell'ambulanza
    return msg + CALL_AMBULANCE_ADVICE


def getWarningLowGlucoseMessage(fase, glucose_value, measurement_unit, current_IOB=None, insulin_duration=None, target_ideal=120):
    """
    Genera il messaggio per glicemia tendente al basso (sotto il target ideale ma sopra i 70 mg/dL),
    ottimizzato per le fasi Check, Notte e Digiuno, con gestione dinamica dell'Insulina Attiva (IOB).
    """

    # 1. Definizione dell'intestazione e dell'introduzione specifica per fase
    if fase.lower() == "digiuno":
        header = "🌅 GLICEMIA TENDENTE AL BASSO A DIGIUNO"
        intro_fase = (
            "Il tuo valore è ridotto rispetto al target. Se stai per consumare un pasto principale, "
            "procedi pure normalmente ma evita di calcolare unità di insulina per la correzione, "
            "poiché la glicemia di partenza è già bassa."
        )
        nota_notturna = ""
    elif fase.lower() == "notte":
        header = "🌙 GLICEMIA TENDENTE AL BASSO DI NOTTE"
        intro_fase = "Attenzione: trovandosi nelle ore notturne, questo valore potrebbe continuare a scendere lentamente mentre dormi."
        nota_notturna = (
            "⚠️ Nota notturna: Consuma lo spuntino di stabilizzazione e valuta di impostare una sveglia "
            "dopo 30 minuti per accertarti che il valore si sia stabilizzato prima di riprendere il sonno profondo.\n\n"
        )
    else:
        header = "🟡 GLICEMIA TENDENTE AL BASSO"
        intro_fase = "Il valore sta scendendo sotto il tuo obiettivo ideale. È consigliabile fare uno scudo preventivo per bloccare la discesa."
        nota_notturna = ""

    # 2. Costruzione del messaggio principale
    msg = (
        f"{header}\n\n"
        f"{intro_fase}\n\n"
        f"La tua glicemia attuale è di {glucose_value} {measurement_unit}, quindi sotto il tuo target ideale di {target_ideal} {measurement_unit}.\n\n"

        f"🥪 Spuntino di stabilizzazione (Carboidrati complessi + Grassi o Proteine):\n"
        f"  Per evitare di scivolare in una vera ipoglicemia, scegli un'opzione a lento rilascio che faccia da scudo. Esempi:\n"
        f"  - 1 pacchetto di cracker integrali\n"
        f"  - 1 fetta di pane di segale con un velo di formaggio spalmabile o 2 fette di bresaola\n"
        f"  - 1 mela piccola accompagnata da 3 o 4 mandorle\n\n"

        f"{nota_notturna}"
        f"🛑 Attenzione all'Insulina (NO BOLO):\n"
        f"  - Non somministrare insulina per questo spuntino. Il cibo introdotto serve unicamente a riportare la glicemia in linea e a metterla in sicurezza.\n"
    )

    # 3. Controllo dinamico e sicuro sull'Insulina Attiva (IOB)
    try:
        iob_val = float(current_IOB) if current_IOB is not None else 0.0
    except (ValueError, TypeError):
        iob_val = 0.0

    if iob_val > 0:
        msg += (
            f"\n📊 ATTENZIONE: HAI INSULINA ATTIVA (IOB)\n"
            f"  - Ci sono ancora {iob_val:.2f} U di insulina in circolo nel tuo corpo"
        )
        if insulin_duration and float(insulin_duration) > 0:
            msg += f" (durata totale impostata: {insulin_duration} ore)"

        msg += (
            ".\n  - Cosa significa: L'insulina continuerà a spingere la glicemia verso il basso. "
            "Il rischio di scendere in ipoglicemia (<70 mg/dL) è elevato. "
            "Valuta se consumare carboidrati leggermente più rapidi se senti già sintomi di calo e "
            "ricontrolla tassativamente la glicemia tra 20-30 minuti.\n"
        )

    return msg


def getPerfectGlucoseMessage(fase, glucose_value, measurement_unit, current_IOB=None, insulin_duration=None, target_ideal=120):
    """
    Genera il messaggio di conferma per glicemia perfettamente in target,
    ottimizzato per le fasi Check, Notte e Digiuno.
    Se l'insulina attiva è a 0, nasconde la sezione IOB per un feedback più pulito.
    """

    # 1. Definizione dell'intestazione e dell'introduzione specifica per fase
    if fase.lower() == "digiuno":
        header = "🟢 GLICEMIA PERFETTA A DIGIUNO"
        intro_fase = "La tua glicemia basale è ottimale. Questo indica che la copertura dell'insulina lenta (o basale) è tarata in modo eccellente."
    elif fase.lower() == "notte":
        header = "🌙 OTTIMO CONTROLLO NOTTURNO"
        intro_fase = "La tua glicemia è stabile ed equilibrata. Questo ti garantisce un riposo sicuro e riduce il rischio di oscillazioni durante il sonno."
    else:
        header = "🟢 ECCELLENTE! VALORE PERFETTO"
        intro_fase = "Il tuo valore attuale dimostra una gestione impeccabile del profilo glicemico. Stai facendo un ottimo lavoro! 🎉"

    # 2. Costruzione del messaggio principale
    msg = (
        f"{header}\n\n"
        f"{intro_fase}\n\n"
        f"La tua glicemia è di {glucose_value} {measurement_unit}, esattamente in linea con il tuo target ideale di {target_ideal} {measurement_unit}.\n\n"

        f"⚖️ Cosa fare adesso (Mantenimento):\n"
        f"  - Continua così: Non hai bisogno di assumere zuccheri di emergenza e non devi somministrare alcuna dose di insulina.\n"
        f"  - Se hai fame: Se questo è il momento di uno spuntino programmato, puoi optare per una scelta bilanciata (es. uno yogurt magro, una manciata di frutta secca o un piccolo frutto) senza dover calcolare boli di correzione.\n"
        f"  - Idratazione: Ricordati di bere acqua regolarmente per mantenere stabile questo ottimo livello.\n\n"
    )

    # 3. Controllo dinamico e sicuro sull'Insulina Attiva (IOB)
    try:
        iob_val = float(current_IOB) if current_IOB is not None else 0.0
    except (ValueError, TypeError):
        iob_val = 0.0

    # 4. Integrazione dinamica della sezione IOB (MODIFICATO QUI)
    if iob_val > 0:
        msg += "📊 Stato dell'Insulina Attiva (IOB):\n"
        msg += f"  - Hai ancora {iob_val:.2f} U di insulina in circolo"

        if insulin_duration and float(insulin_duration) > 0:
            msg += f" (durata totale impostata: {insulin_duration} ore)"

        msg += (
            ".\n  - Nota di monitoraggio: Poiché c'è ancora farmaco attivo, questo valore perfetto potrebbe "
            "tendere a scendere nelle prossime ore. Tieni d'occhio la tendenza e valuta un piccolo spuntino "
            "preventivo solo se noti un trend in calo rapido o se devi fare attività fisica.\n"
        )
    # SE È 0: Non aggiunge nulla al messaggio, lasciando il testo pulito e privo di note superflue.

    return msg


def getWarningHighGlucoseMessage(fase, glucose_value, measurement_unit, isf, insulin_duration, target_ideal=120, current_IOB=None):
    """
    Genera il messaggio per glicemia tendente all'alto (sopra il target ideale ma sotto la soglia di iperglicemia),
    ottimizzato per le fasi Check, Notte e Digiuno, calcolando la correzione reale netta integrando l'IOB attuale.
    """

    # 1. Calcolo numerico sicuro dell'Insulina Attiva (IOB)
    try:
        iob_val = float(current_IOB) if current_IOB is not None else 0.0
    except (ValueError, TypeError):
        iob_val = 0.0

    # 2. Calcolo matematico della correzione teorica e reale netta
    try:
        punti_da_scendere = float(glucose_value) - float(target_ideal)
        if punti_da_scendere > 0 and float(isf) > 0:
            unita_correzione_teorica = punti_da_scendere / float(isf)
            unita_correzione_reale = round(
                max(0.0, unita_correzione_teorica - iob_val), 1)
            unita_correzione_teorica = round(unita_correzione_teorica, 1)
        else:
            unita_correzione_teorica = 0.0
            unita_correzione_reale = 0.0
    except (ValueError, TypeError):
        unita_correzione_teorica = None
        unita_correzione_reale = None

    # 3. Definizione dell'intestazione e dell'introduzione specifica per fase
    consiglio_movimento = "  - Fai una leggera attività fisica: una camminata di 10-15 minuti aiuta i muscoli a bruciare il glucosio in eccesso in modo naturale.\n"

    if fase.lower() == "digiuno":
        header = "🌅 GLICEMIA TENDENTE ALL'ALTO A DIGIUNO"
        intro_fase = "Il tuo valore a digiuno è leggermente superiore al target ideale. Spesso un po' di idratazione aiuta a stabilizzare la linea di base."
    elif fase.lower() == "notte":
        header = "🌙 GLICEMIA TENDENTE ALL'ALTO DI NOTTE"
        intro_fase = "Il valore è di poco superiore al target. Evita micro-correzioni prima di riaddormentarti per non rischiare di scendere troppo durante il sonno."
        consiglio_movimento = ""  # Di notte rimosso il consiglio sul movimento
    else:
        header = "🟡 GLICEMIA TENDENTE ALL'ALTO"
        intro_fase = "Ti trovi leggermente sopra il tuo obiettivo ideale. Con piccoli accorgimenti puoi aiutare il corpo a stabilizzarsi."

    # 4. Costruzione del messaggio principale (Consigli base)
    msg = (
        f"{header}\n\n"
        f"{intro_fase}\n\n"
        f"La tua glicemia attuale è di {glucose_value} {measurement_unit}.\n\n"
        f"💧 Consigli pratici:\n"
        f"  - Bevi un bicchiere d'acqua: aiuta i reni a diluire e smaltire il piccolo eccesso di zucchero nel sangue.\n"
        f"{consiglio_movimento}\n"
    )

    # 5 & 6. GESTIONE DINAMICA IN BASE ALL'INSULINA ATTIVA (IOB)
    if fase.lower() == "notte":
        msg += f"⚠️ Trattandosi di un controllo notturno per un valore così vicino al target ({target_ideal} {measurement_unit}), si consiglia di non fare alcuna correzione insulinica per sicurezza. È preferibile solo monitorare."

    elif iob_val > 0:
        # Se c'è insulina attiva, mostriamo l'analisi IOB e ricalcoliamo la correzione netta
        msg += f"💉 Analisi dell'Insulina Attiva (IOB):\n"
        msg += f"  - Hai {iob_val:.2f} U di insulina ancora attiva nel corpo"
        if insulin_duration and float(insulin_duration) > 0:
            msg += f" (durata totale impostata: {insulin_duration} ore)"
        msg += ". Questa insulina sta già lavorando per abbassare la tua glicemia. Evita correzioni affrettate.\n\n"

        # Mostra il calcolo della correzione solo se c'è IOB da compensare
        if unita_correzione_reale == 0.0 and unita_correzione_teorica > 0:
            msg += (
                f"📊 Calcolo Correzione: La distanza dal target richiederebbe teoricamente {unita_correzione_teorica} U, "
                f"ma poiché hai già {iob_val:.2f} U di insulina attiva, la tua correzione reale netta è di 0.0 U. "
                f"L'insulina in circolo è sufficiente, devi solo attendere che finisca il suo effetto."
            )
        elif unita_correzione_reale >= 0.5:
            msg += (
                f"📊 Calcolo Correzione: Sottraendo l'insulina attiva (IOB) dalla dose teorica, "
                f"la tua correzione netta suggerita è di {unita_correzione_reale} U per raggiungere il target di {target_ideal} {measurement_unit}. "
                f"Valuta sempre insieme al tuo medico prima di somministrare boli fuori pasto."
            )
        else:
            msg += f"⚖️ La distanza dal tuo target ideale ({target_ideal} {measurement_unit}) dopo aver calcolato l'insulina attiva è minima. Non è necessaria alcuna dose di correzione."

    else:
        # CASO IOB = 0: Pulito, senza ansia da calcoli matematici/insulina
        if unita_correzione_reale is not None and unita_correzione_reale >= 0.5:
            # Se la glicemia è "tendente all'alto" ma l'ISF è così basso che richiede comunque un bolo (>0.5 U)
            msg += (
                f"📊 Nota sul Target: Per raggiungere il tuo obiettivo ideale di {target_ideal} {measurement_unit} "
                f"il calcolo teorico indicherebbe {unita_correzione_reale} U (ISF: {isf}). "
                f"Trattandosi di una deviazione leggera, valuta con attenzione se necessario un bolo di correzione o se preferisci attendere."
            )
        else:
            # Caso standard: deviazione minima e zero IOB. Non serve l'insulina.
            msg += f"⚖️ Stato attuale: Non hai insulina attiva in circolo, ma lo scostamento dal tuo target ideale ({target_ideal} {measurement_unit}) è minimo. Non è necessaria alcuna correzione insulinica, basta monitorare l'andamento nelle prossime ore."

    return msg


def getAlarmHighGlucoseMessage(fase, glucose_value, measurement_unit, isf, current_IOB=None, insulin_duration=None, target_ideal=120):
    """
    Genera il messaggio per l'allarme iperglicemia, ottimizzato per le fasi Check, Notte e Digiuno,
    calcolando la correzione reale netta per evitare l'insulin stacking.
    Se l'insulina attiva è a 0, omette i dettagli e mostra solo la correzione.
    """

    # 1. Calcolo numerico sicuro dell'Insulina Attiva (IOB)
    try:
        iob_val = float(current_IOB) if current_IOB is not None else 0.0
    except (ValueError, TypeError):
        iob_val = 0.0

    # 2. Calcolo matematico della correzione teorica e reale netta
    try:
        punti_da_scendere = float(glucose_value) - float(target_ideal)
        if punti_da_scendere > 0 and float(isf) > 0:
            unita_correzione_teorica = punti_da_scendere / float(isf)
            # La correzione reale sottrae l'IOB per evitare accumuli, non scende mai sotto 0
            unita_correzione_reale = round(
                max(0.0, unita_correzione_teorica - iob_val), 1)
            unita_correzione_teorica = round(unita_correzione_teorica, 1)
        else:
            unita_correzione_teorica = 0.0
            unita_correzione_reale = 0.0
    except (ValueError, TypeError):
        unita_correzione_teorica = 0.0
        unita_correzione_reale = 0.0

    # 3. Definizione dell'intestazione e dell'introduzione specifica per fase
    if fase.lower() == "digiuno":
        header = "🌅 IPERGLICEMIA A DIGIUNO"
        intro_fase = (
            "Questo valore alto a digiuno potrebbe essere legato all'effetto del pasto della sera precedente, "
            "a una dose di insulina basale insufficiente o al fenomeno dell'alba (il rilascio naturale di glucosio da parte del fegato)."
        )
    elif fase.lower() == "notte":
        header = "🌙 IPERGLICEMIA NOTTURNA"
        intro_fase = "Valore elevato riscontrato durante le ore notturne. Gestisci questo momento con calma e massima prudenza."
    else:
        header = "🟠 IPERGLICEMIA / VALORE ALTO"
        intro_fase = "Il tuo valore attuale è fuori target. Al momento è fondamentale evitare carboidrati e zuccheri."

    # 4. Costruzione del messaggio principale
    msg = (
        f"{header}\n\n"
        f"{intro_fase}\n\n"
        f"Glicemia rilevata: {glucose_value} {measurement_unit}.\n\n"

        f"💧 Idratazione (Prima di tutto):\n"
        f"  - Bevi subito 1 o 2 grandi bicchieri d'acqua: aiuta i reni a filtrare e a smaltire il glucosio in eccesso attraverso le urine.\n\n"

        f"💉 Gestione Insulina e Correzione:\n"
        f"  - Il tuo Fattore di Sensibilità (ISF) impostato è di {isf} {measurement_unit} per unità di insulina.\n"
    )

    # 5. Integrazione dinamica della Correzione Reale e dell'IOB (SISTEMATO QUI)
    if iob_val > 0:
        # Se c'è insulina attiva, mostra tutti gli avvisi sul rischio accumulo (Insulin Stacking)
        if unita_correzione_teorica > 0:
            msg += f"  - La distanza dal target richiede teoricamente una correzione di {unita_correzione_teorica} U.\n"

        msg += f"\n⚠️ Nota sull'Insulina Attiva (IOB):\n  - Hai ancora {iob_val:.2f} U di insulina in circolo nel corpo"
        if insulin_duration and float(insulin_duration) > 0:
            msg += f" (durata totale: {insulin_duration} ore)"
        msg += ".\n"

        if fase.lower() == "notte":
            msg += (
                f"  - Rischio Notturno Elevato: L'insulina precedente sta ancora lavorando. "
                f"Fare un altro bolo ora aumenta drasticamente il rischio di un'ipoglicemia severa mentre dormi.\n"
            )
        else:
            msg += (
                f"  - Rischio Insulin Stacking: C'è già farmaco attivo. Fare un bolo intero adesso "
                f"può causare un pericoloso cumulo, rischiando un'ipoglicemia grave nelle prossime ore.\n"
            )

        if unita_correzione_reale == 0.0:
            msg += f"  - 👉 CORREZIONE SUGGERITA: 0.0 U. L'insulina già attiva ({iob_val:.2f} U) è sufficiente a coprire l'eccesso. Attendi che finisca il suo effetto.\n\n"
        else:
            msg += f"  - 👉 CORREZIONE NETTA SUGGERITA: {unita_correzione_reale} U (già sottratta l'insulina attiva per sicurezza).\n\n"
    else:
        # SE L'INSULINA ATTIVA È 0: Non dice nulla sulla IOB e mostra direttamente la correzione standard
        msg += f"  - 👉 CORREZIONE SUGGERITA: {unita_correzione_teorica} U.\n\n"

    # 6. Sezione snack (Sempre visibile)
    msg += (
        f"🥦 Se hai assolutamente fame (Solo opzioni senza carboidrati):\n"
        f"  Scegli alimenti che non impattano sulla glicemia:\n"
        f"  - Qualche cubetto di parmigiano o grana\n"
        f"  - Una manciata di finocchi, sedano o cetrioli crudi\n"
        f"  - Un uovo sodo\n"
        f"  - Qualche gheriglio di noce o mandorla (senza esagerare)\n\n"
    )

    return msg + CALL_AMBULANCE_ADVICE


# Questo trafiletto legale deve essere appeso alla fine di OGNI consiglio restituito dall'app
LEGAL_DISCLAIMER = (
    "\n"
    "⚠️ NOTA LEGALE\n"
    "I consigli e i calcoli forniti da questa applicazione hanno uno scopo puramente informativo "
    "e simulativo basato sui parametri inseriti. Non costituiscono in alcun modo una prescrizione, "
    "una diagnosi o un parere medico. Qualsiasi decisione terapeutica (inclusa la somministrazione di insulina) "
    "deve essere assunta in base al piano terapeutico stabilito dal proprio medico curante o diabetologo. "
    "In caso di malessere o dubbi, contattare immediatamente il medico o i servizi di emergenza."
)


CALL_AMBULANCE_ADVICE = (
    "\n"
    "🚑 QUANDO CHIAMARE IL 118:\n\n"
    "· STATO ALTERATO: In caso di forte confusione, sonnolenza o difficoltà a deglutire, NON assumere cibo/liquidi e chiama subito i soccorsi.\n"
    "· IPOGLICEMIA PERSISTENTE: Se dopo la 2° correzione (e 15 minuti di attesa) la glicemia resta pericolosamente bassa, chiama il 118.\n"
    "· INCOSCIENZA: Istruisci chi ti è vicino: in caso di svenimento devono chiamare il 118, NON darti cibo/liquidi e somministrare il Glucagone."
)

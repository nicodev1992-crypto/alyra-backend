
def getAlarmLowGlucoseMessage(fase, glucose_value, measurement_unit, insulin_duration=None):
    
    # 1. Definizione dell'intestazione e dell'introduzione specifica per fase
    if fase.lower() == "notte":
        header = "🚨 EMERGENZA IPOGLICEMIA IN DIGIUNO"
        intro_fase = (
            "L'ipoglicemia di notte va trattata immediatamente. "
            "Siediti sul letto, accendi la luce e non muoverti finché non hai preso lo zucchero.\n\n"
            "⚠️ Nota notturna: Una volta che la glicemia sarà risalita sopra i 70 mg/dL, "
            "consuma un piccolo spuntino complesso (es. 2-3 cracker o un pezzo di pane) "
            "prima di risganciarti a dormire, per evitare ricadute."
        )
    elif fase.lower() == "digiuno":
        header = "🌅 IPOGLICEMIA AL RISVEGLIO"
        intro_fase = "Devi far risalire subito i livelli di zucchero nel sangue prima di iniziare qualsiasi attività mattutina o preparare la colazione."
    else:
        header = "🔴 IPOGLICEMIA IMMEDIATA"
        intro_fase = "Interrompi subito qualsiasi attività tu stia facendo e correggi immediatamente il valore."

    # 2. Costruzione del messaggio principale (senza doppi grassetti)
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

    # 3. Controllo pulito sull'Insulina Attiva (IOB)
    if insulin_duration is not None and float(insulin_duration) > 0:
        msg += (
            f"\n⚠️ Attenzione all'Insulina Attiva (IOB):\n"
            f"La tua insulina rimane in circolo per {insulin_duration} ore. Se hai fatto un bolo di recente, "
            f"l'insulina continuerà a spingere la glicemia verso il basso, contrastando l'effetto dello zucchero. "
            f"Monitorati con maggiore frequenza.\n"
        )

    # Nota: puoi appendere qui il tuo trafiletto legale o il consiglio dell'ambulanza
    return msg + CALL_AMBULANCE_ADVICE

def getWarningLowGlucoseMessage(fase, glucose_value, measurement_unit, insulin_duration=None, target_ideal=120):
    """
    Genera il messaggio per glicemia tendente al basso (sotto il target ideale ma sopra i 70 mg/dL),
    ottimizzato per le fasi Check, Notte e Digiuno, con formattazione pulita.
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

    # 3. Controllo pulito sulla durata dell'insulina attiva (IOB)
    if insulin_duration is not None and float(insulin_duration) > 0:
        msg += (
            f"\n📊 Verifica dell'Insulina Attiva (IOB):\n"
            f"  - La tua insulina rimane attiva nel corpo per {insulin_duration} ore. Se hai effettuato un'iniezione di recente, "
            f"  l'ipoglicemia potrebbe essere più vicina perché c'è ancora farmaco in circolo che spinge il valore verso il basso. "
            f"  Ricontrolla la glicemia tra 20-30 minuti.\n"
        )
        
    return msg

def getPerfectGlucoseMessage(fase, glucose_value, measurement_unit, insulin_duration=None, target_ideal=120):
    """
    Genera il messaggio di conferma per glicemia perfettamente in target,
    ottimizzato per le fasi Check, Notte e Digiuno, con formattazione pulita.
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
        
        f"📊 Stato dell'Insulina Attiva (IOB):\n"
    )

    # 3. Controllo pulito sulla durata dell'insulina attiva (IOB)
    if insulin_duration is not None and float(insulin_duration) > 0:
        msg += (
            f"  - La tua insulina rimane attiva nel corpo per {insulin_duration} ore. Se non hai fatto iniezioni nelle ultime ore, "
            f"questo valore perfetto è la tua reale linea di base attuale. Se invece hai un bolo recente, monitora se la tendenza "
            f"rimarrà stabile fino all'esaurimento del suo effetto.\n"
        )
    else:
        msg += "  - Nessuna azione richiesta. Il tuo corpo si trova in una zona di totale sicurezza biologica.\n"

    return msg


def getWarningHighGlucoseMessage(fase, glucose_value, measurement_unit, isf, insulin_duration, target_ideal=120):
    """
    Genera il messaggio per glicemia tendente all'alto (sopra il target ideale ma sotto la soglia di iperglicemia),
    ottimizzato per le fasi Check, Notte e Digiuno, con formattazione pulita.
    """
    
    # 1. Calcolo matematico della correzione teorica
    try:
        punti_da_scendere = float(glucose_value) - float(target_ideal)
        if punti_da_scendere > 0 and float(isf) > 0:
            unita_correzione = round(punti_da_scendere / float(isf), 1)
        else:
            unita_correzione = 0.0
    except (ValueError, TypeError):
        unita_correzione = None

    # 2. Definizione dell'intestazione e dell'introduzione specifica per fase
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

    # 3. Costruzione del messaggio principale
    msg = (
        f"{header}\n\n"
        f"{intro_fase}\n\n"
        f"La tua glicemia attuale è di {glucose_value} {measurement_unit}.\n\n"
        
        f"💧 Consigli pratici:\n"
        f"  - Bevi un bicchiere d'acqua: aiuta i reni a diluire e smaltire il piccolo eccesso di zucchero nel sangue.\n"
        f"{consiglio_movimento}\n"
        f"💉 Verifica dell'Insulina Attiva (IOB):\n"
    )
    
    # 4. Controllo pulito sulla durata dell'insulina attiva (IOB)
    if insulin_duration is not None and float(insulin_duration) > 0:
        msg += (
            f"  - La tua insulina rimane attiva nel corpo per {insulin_duration} ore. Se hai effettuato un'iniezione di recente, "
            f"è molto probabile che il farmaco in circolo debba ancora finire il suo lavoro e che la glicemia scenda da sola. "
            f"Evita correzioni affrettate per prevenire un'ipoglicemia successiva.\n\n"
        )
    
    # 5. Gestione della micro-correzione teorica (esclusa o nascosta se non significativa o se è notte)
    if fase.lower() == "notte":
        msg += f"  - Trattandosi di un controllo notturno per un valore così vicino al target ({target_ideal} {measurement_unit}), generalmente non è necessaria alcuna correzione insulinica. È preferibile solo monitorare."
    elif unita_correzione and unita_correzione >= 0.5:
        msg += f"  - Solo a titolo informativo, la distanza dal tuo target ideale ({target_ideal} {measurement_unit}) corrisponderebbe a circa {unita_correzione} U di correzione teorica basata sul tuo ISF ({isf}). Valuta sempre l'insulina attiva prima di agire."
    else:
        msg += f"  - La distanza dal tuo target ideale ({target_ideal} {measurement_unit}) è minima. Non è necessaria alcuna correzione insulinica, basta monitorare l'andamento."
        
    return msg

def getAlarmHighGlucoseMessage(fase, glucose_value, measurement_unit, isf, insulin_duration=None, target_ideal=120):
    
    # 1. Calcolo matematico della correzione teorica necessaria
    try:
        punti_da_scendere = float(glucose_value) - float(target_ideal)
        if punti_da_scendere > 0 and float(isf) > 0:
            unita_correzione = round(punti_da_scendere / float(isf), 1)
        else:
            unita_correzione = 0.0
    except (ValueError, TypeError):
        unita_correzione = 0.0

    # 2. Definizione dell'intestazione e dell'introduzione specifica per fase
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

    # 3. Costruzione del messaggio principale
    msg = (
        f"{header}\n\n"
        f"{intro_fase}\n\n"
        f"Glicemia rilevata: {glucose_value} {measurement_unit}.\n\n"
        
        f"💧 Idratazione (Prima di tutto):\n"
        f"  - Bevi subito 1 o 2 grandi bicchieri d'acqua: aiuta i reni a filtrare e a smaltire il glucosio in eccesso attraverso le urine.\n\n"
        
        f"💉 Gestione Insulina e Correzione:\n"
        f"  - Il tuo Fattore di Sensibilità (ISF) impostato è di {isf} {measurement_unit} per unità di insulina.\n"
    )
    
    # Mostra la correzione teorica se valida
    if unita_correzione > 0:
        msg += f"  - Per scendere al tuo target di {target_ideal} {measurement_unit}, sarebbero necessarie circa {unita_correzione} U di insulina rapida.\n"
    
    # 4. Controllo pulito sulla durata dell'insulina attiva (IOB) adattato alla fase
    if insulin_duration is not None and float(insulin_duration) > 0:
        msg += f"\n⚠️ Nota sull'Insulina Attiva (IOB):\n  - La tua insulina rimane attiva nel corpo per {insulin_duration} ore. "
        if fase.lower() == "notte":
            msg += (
                f"Trattandosi di una correzione notturna, se hai fatto l'ultimo bolo meno di {insulin_duration} ore fa, "
                f"l'insulina precedente sta ancora lavorando. Fare un altro bolo ora aumenta drasticamente il rischio "
                f"di un'ipoglicemia severa mentre dormi. Valuta con estrema attenzione.\n\n"
            )
        else:
            msg += (
                f"Se hai già effettuato un'iniezione meno di {insulin_duration} ore fa, c'è ancora insulina in circolo. "
                f"Fare un altro bolo adesso può causare un pericoloso cumulo (insulin stacking), rischiando un'ipoglicemia grave nelle prossime ore.\n\n"
            )

    # 5. Sezione snack estratta dal blocco precedente (ora è sempre visibile)
    msg += (
        f"🥦 Se hai assolutamente fame (Solo opzioni senza carboidrati):\n"
        f"  Scegli alimenti che non impattano sulla glicemia:\n"
        f"  - Qualche cubetto di parmigiano o grana\n"
        f"  - Una manciata di finocchi, sedano o cetrioli crudi\n"
        f"  - Un uovo sodo\n"
        f"  - Qualche gheriglio di noce o mandorla (senza esagerare)\n"
    )
    
    return msg + CALL_AMBULANCE_ADVICE





# Questo trafiletto legale deve essere appeso alla fine di OGNI consiglio restituito dall'app
LEGAL_DISCLAIMER = (
    "\n\n---\n"
    "⚠️ **NOTA LEGALE / DISCLAIMER MEDICINE**\n"
    "I consigli e i calcoli forniti da questa applicazione hanno uno scopo puramente informativo "
    "e simulativo basato sui parametri inseriti. Non costituiscono in alcun modo una prescrizione, "
    "una diagnosi o un parere medico. Qualsiasi decisione terapeutica (inclusa la somministrazione di insulina) "
    "deve essere assunta in base al piano terapeutico stabilito dal proprio medico curante o diabetologo. "
    "In caso di malessere o dubbi, contattare immediatamente il medico o i servizi di emergenza."
)


CALL_AMBULANCE_ADVICE = (
    "🚑 QUANDO CHIAMARE IL 118 / SOCCORSI:\n"
    "  · Se avverti forte confusione mentale, sonnolenza estrema o non ti senti in grado di deglutire in sicurezza, "
    "NON assumere liquidi o cibo e fatti aiutare da qualcuno a CHIAMARE IMMEDIATAMENTE IL 118.\n"
    "  · Se dopo aver preso gli zuccheri e aver atteso 15 minuti ripeti la procedura di correzione per la seconda volta, "
    "ma la glicemia continua a scendere o rimane pericolosamente bassa, CHIAMA IL 118.\n"
    "  · Avvisa chi ti sta vicino: se dovessi perdere conoscenza, devono chiamare subito i soccorsi e "
    "NON devono darti nulla da bere o da mangiare (va somministrato il Glucagone se disponibile).\n\n"
)

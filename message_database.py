def getPerfectGlucoseMessage(fase, glucose_value, measurement_unit, insulin_duration=None, target_ideal=120):

    intro_fase = ""
    if fase.lower() == "digiuno":
        intro_fase = "🌅 Buongiorno!\n Svegliarsi in target è il modo migliore per iniziare la giornata.** La tua glicemia basale è perfetta.\n"
    elif fase.lower() == "notte":
        intro_fase = "🌙 Ottimo controllo notturno!\n La tua glicemia è stabile ed equilibrata, il che ti garantisce un riposo sicuro.\n"
    else:
        intro_fase = "🕒 Ottimo controllo (Check)!\n Il tuo valore attuale dimostra una gestione impeccabile.\n"

    msg = (
        f"🟢 **ECCELLENTE! VALORE PERFETTO**\n\n"
        f"{intro_fase}\n"
        f"La tua glicemia è ottimale ({glucose_value} {measurement_unit}) ed è perfettamente in linea con il tuo target ideale di {target_ideal} {measurement_unit}.\n"
        f"Stai facendo un ottimo lavoro nella gestione del tuo profilo glicemico! 🎉\n\n"

        f"⚖️ **Cosa fare adesso (Mantenimento)**:\n"
        f" - **Continua così**: Non hai bisogno di assumere zuccheri per correggere e non devi assolutamente fare insulina.\n"
        f" - **Se hai fame**: Se questo è il momento di uno spuntino standard, puoi optare per una scelta bilanciata (es. uno yogurt magro, una manciata di frutta secca o un piccolo frutto) senza l'ansia di dover correggere anomalie.\n"
        f" - **Idratazione**: Continua a bere acqua regolarmente durante la giornata per mantenere stabile questo ottimo livello.\n\n"

        f"📊 **Stato dell'Insulina Attiva (IOB)**:\n"
    )

    # Controllo sulla durata dell'insulina per dare un feedback avanzato
    if insulin_duration is not None and float(insulin_duration) > 0:
        msg += (
            f" - La tua insulina rimane attiva per **{insulin_duration} ore**. Se non hai fatto iniezioni nelle ultime {insulin_duration} ore, "
            f"significa che questo valore perfetto è la tua reale linea di base attuale. Se invece hai un bolo recente, monitora se la tendenza rimarrà stabile fino all'esaurimento dell'effetto.\n"
        )
    else:
        msg += " - Nessuna azione richiesta. Il tuo corpo si trova in una zona di totale sicurezza biologica.\n"

    return msg

# Cambiato il nome per non sovrascrivere la variabile sopra


def getWarningLowGlucoseMessage(fase, glucose_value, measurement_unit, insulin_duration=None, target_ideal=120):
    intro_fase = ""
    spuntino_extra = ""

    if fase.lower() == "digiuno":
        intro_fase = "🌅 **Tendente al basso al risveglio**: La glicemia è un po' ridotta rispetto al tuo target. Ottima transizione per fare una colazione bilanciata senza esagerare con l'insulina rapida.\n"
    elif fase.lower() == "notte":
        intro_fase = "🌙 **Tendente al basso di notte**: Attenzione, trovandosi nelle ore notturne, questo valore potrebbe scendere ancora mentre dormi.\n"
        spuntino_extra = "⚠️ **CONSIGLIO NOTTURNO**: Trattandosi di un controllo di notte, consuma lo spuntino e imposta una sveglia dopo 30 minuti per assicurarti che la glicemia si sia stabilizzata prima di riprendere sonno.\n\n"
    else:
        intro_fase = "🕒 **Tendente al basso (Controllo Check)**: Il valore sta scendendo sotto il target. Meglio fare uno scudo preventivo.\n"

    msg = (
        f"🟡 **GLICEMIA TENDENTE AL BASSO**\n\n"
        f"{intro_fase}\n"
        f"La tua glicemia ({glucose_value} {measurement_unit}) è sotto il tuo target ideale di {target_ideal} {measurement_unit}.\n\n"
        f"🥪 **Spuntino di stabilizzazione (Carboidrati complessi + Grassi/Proteine)**:\n"
        f" Scegli un'opzione a lento rilascio per fare da scudo (es. 1 pacchetto di cracker integrali o una fetta di pane con bresaola).\n\n"
        f"{spuntino_extra}"
        f"🛑 **Attenzione all'Insulina (NO BOLO)**:\n"
        f" - **NON fare insulina per questo spuntino**: serve solo a stabilizzare il valore.\n"
    )

    # Controllo di sicurezza sulla durata dell'insulina
    if insulin_duration is not None and float(insulin_duration) > 0:
        msg += (
            f" - **Verifica l'Insulina Attiva (IOB)**: La tua insulina rimane in circolo per **{insulin_duration} ore**. "
            f"Se hai fatto un'iniezione di recente (meno di {insulin_duration} ore fa), l'ipoglicemia potrebbe essere più vicina perché c'è ancora 'insulina a bordo' che spinge verso il basso. Ricontrolla la glicemia tra 20-30 minuti.\n"
        )

    return msg


def getWarningHighGlucoseMessage(fase, glucose_value, measurement_unit, isf, insulin_duration, target_ideal=120):
    """
    Genera il messaggio per glicemia tendente all'alto (sopra il target ideale ma sotto la soglia di iperglicemia).
    Fornisce consigli di monitoraggio, idratazione e attività fisica senza stravolgere la terapia.
    """

    # Calcolo matematico della correzione teorica (giusto come dato indicativo)
    try:
        punti_da_scendere = float(glucose_value) - float(target_ideal)
        if punti_da_scendere > 0 and float(isf) > 0:
            unita_correzione = round(punti_da_scendere / float(isf), 1)
        else:
            unita_correzione = 0.0
    except (ValueError, TypeError):
        unita_correzione = None

    intro_fase = ""
    consiglio_movimento = " - **Fai una leggera attività fisica**: una camminata di 10-15 minuti aiuta i muscoli a bruciare il glucosio in eccesso in modo naturale.\n"

    if fase.lower() == "digiuno":
        intro_fase = "🌅 **Tendente all'alto al risveglio**: La glicemia è poco sopra il target ideale. Un ottimo modo per iniziare la giornata è bere acqua e attivarsi subito.\n"
    elif fase.lower() == "notte":
        intro_fase = "🌙 **Tendente all'alto di notte**: Il valore è leggermente superiore al target. Evita assolutamente micro-correzioni prima di riaddormentarti, potresti scendere troppo.\n"
        consiglio_movimento = ""  # Di notte non mandiamo l'utente a camminare!
    else:
        intro_fase = "🕒 **Tendente all'alto (Controllo Check)**: Sei leggermente sopra il tuo obiettivo.\n"

    msg = (
        f"🟡 **GLICEMIA TENDENTE ALL'ALTO**\n\n"
        f"{intro_fase}\n"
        f"Il tuo valore attuale è di {glucose_value} {measurement_unit}.\n\n"
        f"💧 **Consigli pratici**:\n"
        f" - **Bevi un bicchiere d'acqua**: aiuta i reni a diluire lo zucchero nel sangue.\n"
        f"{consiglio_movimento}\n"
        f"💉 **Verifica dell'Insulina Attiva (IOB)**:\n"
    )
    # Controllo di sicurezza sulla durata dell'insulina per spiegare la situazione
    if insulin_duration is not None and float(insulin_duration) > 0:
        msg += (
            f" - La tua insulina rimane attiva per **{insulin_duration} ore**. Se hai fatto un'iniezione di recente (meno di {insulin_duration} ore fa), "
            f"è molto probabile che l'insulina in circolo debba ancora finire il suo lavoro e che la glicemia scenda da sola. **Evita correzioni affrettate** per non rischiare un'ipoglicemia successiva.\n"
        )

    # Mostriamo la micro-correzione teorica solo se significativa (es. almeno 0.5 unità),
    # altrimenti per valori molto piccoli è meglio non suggerire boli ravvicinati.
    if unita_correzione and unita_correzione >= 0.5:
        msg += f" - Solo a titolo informativo, la distanza dal tuo target ideale ({target_ideal} {measurement_unit}) corrisponderebbe a circa **{unita_correzione} U** di correzione teorica basata sul tuo ISF ({isf}). Valuta sempre la presenza di insulina attiva prima di agire.\n"
    else:
        msg += f" - La distanza dal tuo target ideale ({target_ideal} {measurement_unit}) è minima. Generalmente non è necessaria alcuna correzione insulinica, basta monitorare l'andamento.\n"

    return msg


def getAlarmHighGlucoseMessage(fase, glucose_value, measurement_unit, isf, insulin_duration=None, target_ideal=120):
    """
    Genera il messaggio di iperglicemia personalizzato con i dati reali dell'utente.

    :param glucose_value: Valore attuale della glicemia (es. 240)
    :param measurement_unit: Unità di misura (es. 'mg/dL')
    :param isf: Fattore di Sensibilità all'Insulina reale dell'utente (es. 40)
    :param insulin_duration: Durata dell'insulina attiva dell'utente in ore (es. 3.5)
    :param target_ideal: Il target glicemico ideale dell'utente (default: 120 mg/dL)
    """

    # Calcolo matematico della correzione teorica necessaria
    # Formula: (Glicemia Attuale - Glicemia Target) / ISF
    try:
        punti_da_scendere = float(glucose_value) - float(target_ideal)
        if punti_da_scendere > 0 and float(isf) > 0:
            unita_correzione = round(punti_da_scendere / float(isf), 1)
        else:
            unita_correzione = 0.0
    except (ValueError, TypeError):
        unita_correzione = None
    intro_fase = ""
    if fase.lower() == "digiuno":
        intro_fase = "🌅 **Iperglicemia al risveglio**: Questo valore alto a digiuno potrebbe essere causato da un cenone della sera prima, da una dose basale insufficiente o dal fenomeno dell'alba (il fegato rilascia glucosio al mattino).\n\n"
    elif fase.lower() == "notte":
        intro_fase = "🌙 **Iperglicemia notturna**: Svegliarsi con la glicemia alta spezza il sonno. Gestisci questo momento con calma, senza farti prendere dal panico.\n\n"
    else:
        intro_fase = "🕒 **Iperglicemia (Controllo Check)**: Il valore attuale è fuori target. Evita spuntini extra con carboidrati.\n\n"
    # Costruzione del messaggio personalizzato
    msg = (
        f"🟠 **IPERGLICEMIA / VALORE ALTO**\n\n"
        f"{intro_fase}\n"
        f"Il valore è alto ({glucose_value} {measurement_unit}). Al momento è fondamentale evitare carboidrati e zuccheri.\n\n"

        f"💧 **Idratazione (Prima di tutto)**:\n"
        f" - Bevi subito 1 o 2 grandi bicchieri d'acqua: aiuta i reni a filtrare e a smaltire il glucosio in eccesso attraverso le urine.\n\n"

        f"💉 **Gestione Insulina e Correzione Personalizzata**:\n"
        f" - Il tuo Fattore di Sensibilità (ISF) è di **{isf} {measurement_unit}** per unità di insulina.\n"
    )

    # Se il calcolo matematico della correzione è valido, lo mostra nel messaggio
    if unita_correzione and unita_correzione > 0:
        msg += f" - Teoricamente, per scendere al tuo target di {target_ideal} {measurement_unit}, sarebbero necessarie circa **{unita_correzione} U** di insulina rapida.\n"

    if insulin_duration is not None and float(insulin_duration) > 0:
        msg += (
            f" - ⚠️ **ATTENZIONE ALL'INSULINA ATTIVA (IOB)**: La tua insulina rimane attiva nel corpo per **{insulin_duration} ore**. "
            f"Se hai già fatto un'iniezione meno di {insulin_duration} ore fa, c'è ancora 'insulina a bordo' che sta lavorando. "
            f"Fare un altro bolo adesso può causare un pericoloso cumulo (*insulin stacking*), rischiando un'ipoglicemia grave nelle prossime ore. Confrontati sempre con il medico.\n\n"

            f"🥦 **Se hai assolutamente fame (Solo opzioni Zero Carboidrati)**:\n"
            f" - Scegli alimenti che NON impattano sulla glicemia:\n"
            f"   * Qualche cubetto di parmigiano o grana\n"
            f"   * Una manciata di finocchi, sedano o cetrioli crudi\n"
            f"   * Un uovo sodo\n"
            f"   * Qualche gheriglio di noce o mandorla (senza esagerare)"
        )

    return msg + CALL_AMBULANCE_ADVICE


def getAlarmLowGlucoseMessage(fase, glucose_value, measurement_unit, insulin_duration=None):
    """
    Genera il messaggio di ipoglicemia immediata.
    Nota: ISF e IC Ratio non servono. L'insulin_duration serve solo come promemoria 
    se l'ipoglicemia è stata causata da un bolo recente.
    """
    intro_fase = ""
    if fase.lower() == "notte":
        intro_fase = "🚨 **EMERGENZA NOTTURNA**: L'ipoglicemia di notte va trattata immediatamente. Siediti sul letto, accendi la luce e non muoverti finché non hai preso lo zucchero.\n\n"
    elif fase.lower() == "digiuno":
        intro_fase = "🌅 **Ipoglicemia al risveglio**: Devi far risalire subito i livelli di zucchero prima di fare qualsiasi altra attività mattutina.\n\n"
    else:
        intro_fase = "🕒 **Ipoglicemia Immediata (Check)**: Interrompi subito quello che stai facendo e correggi il valore.\n\n"
    msg = (
        f"🔴 **IPOGLICEMIA IMMEDIATA**\n\n"
        f"{intro_fase}\n"
        f"Il valore è pericolosamente basso! ({glucose_value} {measurement_unit}).\n"
        f"È fondamentale agire subito per far risalire la glicemia applicando la **Regola dei 15**.\n\n"

        f"⚡ **Cosa fare ORA (Assumi circa 15g di zuccheri rapidi)**:\n"
        f" Scegli **UN SOLO** alimento tra questi disponibili:\n"
        f"  - 1/2 bicchiere di Coca-Cola o aranciata regolare (NON zero/diet)\n"
        f"  - 1 piccolo succo di frutta (circa 100-150ml)\n"
        f"  - 3 cucchiaini o bustine di zucchero sciolti in un goccio d'acqua\n"
        f"  - 4 compresse di glucosio/destrosio\n\n"

        f"⏱️ **Cosa fare DOPO (Aspetta 15 minuti)**:\n"
        f" - Resta a riposo e **attendi 15 minuti** senza assumere altro cibo.\n"
        f" - Misura nuovamente la glicemia: se è ancora sotto 70 mg/dL, ripeti l'assunzione di 15g di zucchero.\n\n"

        f"⚠️ **Errori gravi da EVITARE in questo momento**:\n"
        f" - **NON mangiare cioccolato, merendine, biscotti o gelato**: contengono grassi che rallentano la digestione, impedendo allo zucchero di entrare rapidamente nel sangue.\n"
    )

    # Se passiamo la durata dell'insulina, ricordiamo all'utente l'effetto della "coda" dell'insulina
    if insulin_duration is not None and float(insulin_duration) > 0:
        msg += (
            f" - **Attenzione all'Insulina Attiva (IOB)**: Ricorda che la tua insulina dura in circolo **{insulin_duration} ore**. "
            f"Se hai fatto un bolo di recente, l'insulina potrebbe continuare a spingere la glicemia verso il basso anche dopo aver preso lo zucchero. Monitorati costantemente.\n"
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

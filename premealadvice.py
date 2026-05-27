import message_database

def getPreMealNearIdealTargetAdvice(glicemia_attuale, user_profile, mealData):
    """
    Orchestratore principale per la glicemia IN TARGET.
    Smista la logica su due funzioni interne dedicate a seconda che il valore
    sia SOPRA o SOTTO il target ideale dell'utente.
    """

    # 1. Estrazione e pulizia dati del cibo (mealData)
    nome_pasto = mealData.name or 'Pasto'
    carbo = float(mealData.carbs_grams or 0.0)
    zuccheri = float(mealData.sugars_grams or 0.0)
    grassi = float(mealData.fats_grams or 0.0)
    proteine = float(mealData.proteins_grams or 0.0)
    fibre = float(mealData.fibers_grams or 0.0)
    indice_glicemico = mealData.glycemic_index or 'Medio'
    peso_alimento = float(mealData.meal_grams or 0.0)

    # 2. Estrazione parametri terapeutici (user_profile)
    ic_ratio = float(user_profile.get('ic_ratio', 10.0))
    isf = float(user_profile.get('isf', 50.0))
    target_ideal = float(user_profile.get('target_ideal', 110.0))
    insulin_duration = user_profile.get('insulin_duration', 4)

    # 3. Calcolo del bolo base per i carboidrati
    unita_pasto = round(carbo / ic_ratio, 1) if ic_ratio > 0 else 0.0

    # -------------------------------------------------------------------------
    # 🟢 METODO INTERNO 1: FASCIA ALTA (Ottimizzazione e Micro-Correzione)
    # -------------------------------------------------------------------------
    def getOverIdealTargetAdvice():
        unita_micro_correzione = round(
            (glicemia_attuale - target_ideal) / isf, 1) if isf > 0 else 0.0
        dose_totale_stimata = round(unita_pasto + unita_micro_correzione, 1)

        testo = (
            f"🟢 GLICEMIA IN TARGET - FASCIA ALTA ({glicemia_attuale}\u00A0mg/dL)\n"
            f"Il tuo valore è buono, ma si trova sopra il tuo obiettivo ideale di {target_ideal}\u00A0mg/dL. "
            f"Applichiamo una strategia di micro-ottimizzazione.\n\n"
        )

        # Motore di ottimizzazione porzioni (attivo solo in fascia alta)
        avviso_ottimizzazione = ""
        if carbo > 100.0:
            carbo_massimi_consigliati = 75.0
            carbo_da_ridurre = round(carbo - carbo_massimi_consigliati, 1)
            avviso_ottimizzazione += (
                f"⚠️ CARICO DI CARBOIDRATI MOLTO ELEVATO:\n"
                f"Il piatto '{nome_pasto}' contiene ben {carbo}\u00A0g di carboidrati. Gestire questa quantità "
                f"mentre sei già nella fascia alta del target aumenta il rischio di un picco post-prandiale importante.\n"
                f"💡 COSA FARE: Ti consiglio di ridurre la porzione di circa -{carbo_da_ridurre}\u00A0g di carboidrati.\n"
            )
            if peso_alimento > 0:
                densita_carbo = carbo / peso_alimento
                grammi_da_togliere_bilancia = round(
                    carbo_da_ridurre / densita_carbo)
                avviso_ottimizzazione += f"👉 In pratica: togli circa {grammi_da_togliere_bilancia}\u00A0g di prodotto dalla porzione sulla bilancia.\n"
            avviso_ottimizzazione += "\n"

        elif carbo > 20.0 and (zuccheri / carbo) > 0.5:
            zuccheri_eccessivi = round(zuccheri - (carbo * 0.25), 1)
            avviso_ottimizzazione += (
                f"🍬 IMPATTO GLICEMICO VERTICALE:\n"
                f"Il cibo selezionato è composto prevalentemente da zuccheri semplici ({zuccheri}\u00A0g su {carbo}\u00A0g di carbo).\n"
                f"Partendo da {glicemia_attuale}\u00A0mg/dL, questo provocherà un'impennata rapida oltre i limiti.\n"
                f"💡 COSA FARE: Ti consiglio di dimezzare questa porzione (riducendo di -{zuccheri_eccessivi}\u00A0g di zuccheri) "
                f"o sostituirla nel piatto con carboidrati complessi/integrali.\n\n"
            )

        if avviso_ottimizzazione:
            testo += avviso_ottimizzazione
            if carbo > 100.0:
                unita_pasto_ottimizzato = round(
                    75.0 / ic_ratio, 1) if ic_ratio > 0 else 0.0
                dose_totale_ottimizzata = round(
                    unita_pasto_ottimizzato + unita_micro_correzione, 1)
                testo += (
                    f"📊 SCELTA DOSAGGIO INSULINA (Include Micro-Correzione di +{unita_micro_correzione}\u00A0U):\n"
                    f"  · SE SEGUI IL CONSIGLIO (Pasto ridotto a 75g carbo): Esegui {dose_totale_ottimizzata}\u00A0U totali.\n"
                    f"  · SE MANGI TUTTO IL PIATTO ORIGINALE: Esegui {dose_totale_stimata}\u00A0U totali.\n\n"
                )
        else:
            testo += (
                f"📋 PIANO TERAPEUTICO DI OTTIMIZZAZIONE:\n"
                f"  · Bolo stimato per i carboidrati del pasto: {unita_pasto}\u00A0U\n"
                f"  · Micro-Correzione per valore di partenza: +{unita_micro_correzione}\u00A0U (ISF: {isf})\n"
                f"  👉 DOSE TOTALE CONSIGLIATA: {dose_totale_stimata}\u00A0U\n\n"
            )
        return testo

    # -------------------------------------------------------------------------
    # 🛡️ METODO INTERNO 2: FASCIA BASSA (Sicurezza, Coda Insulina e Tempismo)
    # -------------------------------------------------------------------------
    def getUnderIdealTargetAdvice():
        testo = (
            f"🟢 GLICEMIA IN TARGET - FASCIA DI SICUREZZA ({glicemia_attuale}\u00A0mg/dL)\n"
            f"Ti trovi nella fascia bassa del tuo target (sotto il valore ideale di {target_ideal}\u00A0mg/dL).\n"
            f"La priorità assoluta in questo momento è consumare il pasto in sicurezza, evitando che l'azione immediata dell'insulina ti spinga in ipoglicemia.\n\n"
            f"📋 PIANO TERAPEUTICO DI PROTEZIONE:\n"
            f"  · Bolo stimato per i carboidrati del pasto: {unita_pasto}\u00A0U\n"
            f"  · Micro-Correzione: 0.0\u00A0U (Nessuna dose aggiuntiva per evitare cali repentini).\n"
            f"  👉 DOSE TOTALE DA ESEGUIRE: {unita_pasto}\u00A0U\n\n"
        )

        # Controllo Coda di Insulina Attiva (Cruciale quando si parte bassi!)
        testo += (
            f"⏱️ MONITORAGGIO INSULINA ATTIVA:\n"
            f"La durata dell'insulina impostata nel tuo profilo è di {insulin_duration} ore. "
            f"Se hai eseguito un bolo nelle ore precedenti, ricorda che hai ancora farmaco attivo nel sangue. "
            f"Con una glicemia di partenza di {glicemia_attuale}\u00A0mg/dL, il rischio di ipoglicemia precoce è elevato. "
            f"Monitora costantemente il sensore durante e dopo il pasto.\n\n"
        )

        # Gestione avanzata del tempismo in base all'Indice Glicemico del piatto
        testo += "⏳ TEMPISMO DEL BOLO DI SICUREZZA:\n"
        if indice_glicemico == "Lento":
            testo += (
                f"  🐢 Il piatto '{nome_pasto}' ha un Indice Glicemico LENTO. Visto che la tua glicemia è già bassa, "
                f"l'insulina agirebbe molto più velocemente della digestione del cibo solido.\n"
                f"  👉 COSA FARE: Posticipa tassativamente il bolo a METÀ PASTO o subito DOPO aver finito di mangiare, "
                f"per dare il tempo ai carboidrati di iniziare a salire ed evitare un crollo iniziale.\n\n"
            )
        elif indice_glicemico == "Veloce":
            testo += (
                f"  ⚡ Il piatto '{nome_pasto}' ha un Indice Glicemico VELOCE. "
                f"Tuttavia, partendo da un valore basso di {glicemia_attuale}\u00A0mg/dL, NON DEVI ANTICIPARE il bolo.\n"
                f"  👉 COSA FARE: Esegui l'insulina esattamente un istante PRIMA del primo boccone (o entro i primi 5 minuti dall'inizio del pasto).\n\n"
            )
        else:
            testo += (
                f"  👉 COSA FARE: Fai l'insulina subito prima di iniziare a mangiare o nei primissimi minuti del pasto. "
                f"Non anticipare mai il bolo di 15 minuti quando parti da questa fascia di sicurezza.\n\n"
            )

        # Assicurazione Nutrizionale (Sotto target ideale le porzioni NON si tagliano!)
        if carbo > 0:
            testo += (
                f"🌾 NOTA SUI CARBOIDRATI:\n"
                f"I {carbo}g di carboidrati presenti in questo pasto sono preziosi per stabilizzare la tua curva e "
                f"riportarti verso il centro del target. Consuma la porzione regolarmente senza tagliarla.\n\n"
            )
        return testo

    # -------------------------------------------------------------------------
    # 🔀 SMISTAMENTO DELL'ORCHESTRATORE PRINCIPALE
    # -------------------------------------------------------------------------
    if glicemia_attuale >= target_ideal:
        consiglio = getOverIdealTargetAdvice()
    else:
        consiglio = getUnderIdealTargetAdvice()

    # -------------------------------------------------------------------------
    # 🌾 ANALISI MACRONUTRIENTI GENERICA (In coda al report generato)
    # -------------------------------------------------------------------------
    consiglio += "🌾 Analisi della composizione del piatto:\n"

    # Tempismo IG generico applicato solo se siamo in fascia alta (per la fascia bassa è già gestito internamente)
    if glicemia_attuale >= target_ideal:
        if indice_glicemico == "Veloce":
            consiglio += "  ⚡ Indice Glicemico Veloce: Anticipa il bolo di 10-15 minuti rispetto al primo boccone per frenare la salita.\n"
        elif indice_glicemico == "Medio":
            consiglio += "  ⚖️ Indice Glicemico Medio: Gestione standard. Puoi fare il bolo circa 5-10 minuti prima del pasto o all'inizio, monitorando l'andamento.\n"
        elif indice_glicemico == "Lento":
            consiglio += "  🐢 Indice Glicemico Lento: Assorbimento prolungato. Fai l'insulina a ridosso del pasto per non scendere all'inizio.\n"

    # 2. CONTROLLO GRASSI/PROTEINE (Protezione contro i None)
    # Usiamo "or 0.0": se il valore è None, Python lo trasforma al volo in 0.0 per fare il calcolo in sicurezza
    val_grassi = grassi if grassi is not None else 0.0
    val_proteine = proteine if proteine is not None else 0.0

    if val_grassi >= 20.0 or val_proteine >= 25.0:
        consiglio += (
            f"  🧀 Effetto tardivo rilevato (Grassi: {val_grassi}g, Proteine: {val_proteine}g).\n"
            f"    Questo blocco rallenta lo svuotamento gastrico. La glicemia rimarrà stabile/ottima nelle prime 2 ore, "
            f"ma potrebbe salire sensibilmente dopo. Monitora l'andamento nelle prossime {insulin_duration} ore "
            f"(durata della tua insulina attiva) e valuta con il medico l'uso di un bolo d'insulina frazionato/prolungato.\n"
        )

    # 3. CONTROLLO FIBRE (Protezione contro i None)
    val_fibre = fibre if fibre is not None else 0.0

    if val_fibre >= 5.0:
        consiglio += f"  🥗 Ottimo l'apporto di fibre ({val_fibre}g): agiscono da scudo naturale rallentando e spalmando l'assorbimento degli zuccheri.\n"

    return consiglio


def getPreMealTooLowAlarmAdvice(glicemia_attuale, user_profile, mealData):
    """
    CASISTICA 1: IPOGLICEMIA PRE-PASTO.
    Priorità: Bloccare l'insulina, trattare l'emergenza immediata, valutare l'impatto 
    della coda di insulina attiva e analizzare i rischi digestivi del piatto inserito.
    """
    # 1. Estrazione sicura dagli attributi dell'oggetto mealData
    nome_pasto = mealData.name or 'Pasto'
    carbo = float(mealData.carbs_grams or 0.0)
    grassi = float(mealData.fats_grams or 0.0)
    proteine = float(mealData.proteins_grams or 0.0)

    # 2. Estrazione parametri del profilo utente
    soglia_ipo = int(user_profile.get('hypo_threshold', 70))
    insulin_duration = user_profile.get('insulin_duration', 4)

    # 3. Allarme iniziale e avviso critico sulla coda di insulina attiva
    consiglio = (
        f"🔴 IPOGLICEMIA IMMEDIATA ({glicemia_attuale}\u00A0mg/dL)\n"
        f"Il tuo valore attuale è inferiore o vicino alla tua soglia di sicurezza di {soglia_ipo}\u00A0mg/dL. "
        "DEVI TASSATIVAMENTE RIMANDARE L'INIZIO DEL PASTO!\n\n"
        f"⏱️ CODA DI INSULINA ATTIVA ({insulin_duration} ORE):\n"
        f"La durata impostata nel tuo profilo indica che l'insulina rimane attiva per {insulin_duration} ore. "
        f"Se hai iniettato un bolo nelle ore precedenti, ricorda che c'è ancora farmaco in circolo che sta "
        f"spingendo attivamente la glicemia verso il basso. In questo scenario, la risalita sarà molto più difficile "
        f"e lenta: monitora il sensore continuamente perché i primi 15g di zucchero potrebbero non bastare.\n\n"
    )

    # 4. Trattamento immediato: Regola dei 15 grammi
    consiglio += (
        "🚨 REGOLA DEI 15 GRAMMI (TRATTA ORA):\n"
        "Assumi IMMEDIATAMENTE 15g di zuccheri ultra-rapidi in formato LIQUIDO. Non consumare cibo solido.\n"
        "Opzioni ideali:\n"
        "  · 1/2 lattina di Coca-Cola o aranciata (NON del tipo zero/diet)\n"
        "  · 1 piccolo succo di frutta (circa 100-150\u00A0ml)\n"
        "  · 3 cucchiaini o bustine di zucchero sciolti in un bicchiere d'acqua\n"
        "👉 Fatto questo, aspetta 15 minuti in totale riposo e ricontrolla il valore glicemico.\n\n"
    )

    # 5. Protocollo di sicurezza e attivazione soccorsi
    consiglio += message_database.CALL_AMBULANCE_ADVICE

    # 6. Analisi chimico-strutturale del pasto bloccato nel form
    if grassi >= 15.0 or proteine >= 20.0:
        consiglio += (
            f"⚠️ PERICOLO DI BLOCCO SU '{nome_pasto}':\n"
            f"Il piatto che hai inserito ha un contenuto elevato di grassi ({grassi}\u00A0g) o proteine ({proteine}\u00A0g).\n"
            f"Non commettere l'errore di iniziare a consumarlo pensando che i suoi carboidrati correggano l'ipoglicemia: "
            f"i grassi rallentano drasticamente lo svuotamento dello stomaco. Questo bloccherà lo zucchero d'emergenza "
            f"impedendogli di entrare rapidamente nel sangue, prolungando il pericolo. Usa PRIMA lo zucchero liquido.\n\n"
        )
    elif carbo > 0:
        consiglio += (
            f"📌 NOTA SUL PIATTO ({nome_pasto}):\n"
            f"Anche se questo cibo contiene {carbo}\u00A0g di carboidrati, si tratta di carboidrati complessi/solidi. "
            f"I loro tempi di digestione sono troppo lunghi per gestire l'urgenza attuale. Risolvi prima l'ipoglicemia.\n\n"
        )

    # 7. Blocco Terapeutico Tassativo
    consiglio += (
        "🛑 INSULINA BLOCCATA:\n"
        "Non eseguire assolutamente il bolo di insulina calcolato per questo pasto in questo momento! "
        "Rinvia qualsiasi dosaggio a quando la glicemia si sarà stabilizzata sopra gli 80\u00A0mg/dL e avrai "
        "risolto completamente i sintomi dell'ipoglicemia."
    )

    return consiglio


def getPreMealGlucoseTooHigh(glicemia_attuale, user_profile, mealData):
    """
    Gestisce il calcolo e i consigli quando la glicemia pre-pasto è troppo alta.
    Incrocia i dati del profilo per calcolare il bolo totale (correzione + carboidrati)
    e suggerisce modifiche dinamiche al piatto (meno grammi o fibre) per abbassare il picco.
    """
    # 1. Estrazione dagli attributi dell'oggetto mealData (Cibo)
    nome_pasto = mealData.name or 'Pasto'
    carbo = float(mealData.carbs_grams or 0.0)
    zuccheri = float(mealData.sugars_grams or 0.0)
    grassi = float(mealData.fats_grams or 0.0)
    proteine = float(mealData.proteins_grams or 0.0)
    fibre = float(mealData.fibers_grams or 0.0)
    indice_glicemico = mealData.glycemic_index or 'Medio'
    peso_alimento = float(mealData.meal_grams or 0.0)

    # 2. Estrazione parametri terapeutici dal profilo utente
    target_max = float(user_profile.get('target_max', 140.0))
    ic_ratio = float(user_profile.get('ic_ratio', 10.0))
    isf = float(user_profile.get('isf', 50.0))
    insulin_duration = user_profile.get('insulin_duration', 4)
    ketone_threshold = float(user_profile.get('ketone_threshold', 250.0))

    # 3. MATEMATICA DELL'INSULINA (Calcolo Bolo di Correzione + Pasto)
    # Calcolo di quante unità servono solo per correggere l'iperglicemia attuale
    punti_da_scendere = glicemia_attuale - target_max
    unita_correzione = round(punti_da_scendere / isf, 1) if isf > 0 else 0.0

    # Calcolo di quante unità servono per coprire i carboidrati inseriti
    unita_pasto = round(carbo / ic_ratio, 1) if ic_ratio > 0 else 0.0

    # Somma totale terapeutica
    dose_totale_raccomandata = round(unita_pasto + unita_correzione, 1)

    # 4. Intestazione dell'allarme (\u00A0 blocca i numeri sulla stessa riga)
    consiglio = (
        f"🟠 VALORE ELEVATO / IPERGLICEMIA ({glicemia_attuale}\u00A0mg/dL)\n"
        f"Il tuo valore supera il limite massimo impostato di {target_max}\u00A0mg/dL.\n\n"
    )

    # -------------------------------------------------------------------------
    # 🚨 BLOCCO EMERGENZA CHETONI (Se la glicemia sale oltre la soglia critica)
    # -------------------------------------------------------------------------
    if glicemia_attuale >= ketone_threshold:
        consiglio += (
            f"⚠️ ATTENZIONE LIVELLO CRITICO:\n"
            f"La tua glicemia è sopra i {ketone_threshold}\u00A0mg/dL. Prima di mangiare, ti raccomandiamo "
            f"tassativamente di MISURARE I CHETONI nel sangue o nelle urine per prevenire la chetoacidosi (DKA).\n"
            f"💧 Bevi subito 2 grandi bicchieri d'acqua naturale per aiutare i reni a smaltire il glucosio.\n\n"
        )

    # -------------------------------------------------------------------------
    # 💉 SEZIONE INSULINA (Calcolo esatto basato sul profilo)
    # -------------------------------------------------------------------------
    consiglio += (
        f"💉 PIANO TERAPEUTICO DI CORREZIONE:\n"
        f"  · Unità per correggere l'iperglicemia: +{unita_correzione}\u00A0U (basato sul tuo ISF di {isf})\n"
        f"  · Unità per coprire il piatto ({carbo}g carbo): {unita_pasto}\u00A0U\n"
        f"  👉 DOSE TOTALE DA ESEGUIRE: {dose_totale_raccomandata}\u00A0U\n\n"
        f"⏳ ANTICIPO BOLO OBBLIGATORIO:\n"
        f"Fai l'insulina e ASPETTA 15-20 minuti prima di toccare il primo boccone. "
        f"Questo tempo di attesa è fondamentale per permettere all'insulina di iniziare a lavorare "
        f"evitando che il cibo spinga la glicemia ancora più in alto.\n\n"
    )

    # -------------------------------------------------------------------------
    # 🧠 MOTORE DI OTTIMIZZAZIONE DEL CIBO ("Ehi, ti consiglio meno...")
    # -------------------------------------------------------------------------
    avviso_cibo = ""

    # Se l'utente è già alto e ha scelto un pasto molto ricco di carboidrati
    if carbo > 55.0:
        carbo_ideali_iper = 40.0  # Riduciamo il target di carbo tollerati visto che siamo alti
        carbo_da_togliere = round(carbo - carbo_ideali_iper, 1)

        avviso_cibo += (
            f"💡 OTTIMIZZAZIONE DELLA PORZIONE SUL PIATTO '{nome_pasto}':\n"
            f"Essendo già in iperglicemia, introdurre {carbo}\u00A0g di carboidrati renderà la discesa molto lenta e faticosa.\n"
            f"👉 Ti consiglio di alleggerire questo pasto togliendo circa -{carbo_da_togliere}\u00A0g di carboidrati.\n"
        )

        # Se abbiamo il peso sulla bilancia, convertiamo i carbo in grammi reali di cibo
        if peso_alimento > 0:
            grammi_da_togliere_bilancia = round(
                carbo_da_togliere / (carbo / peso_alimento))
            avviso_cibo += f"👉 Sulla bilancia: togli circa {grammi_da_togliere_bilancia}\u00A0g di cibo dalla porzione.\n"

        # Calcolo del bolo alternativo se l'utente ascolta l'app
        unita_pasto_ridotto = round(
            carbo_ideali_iper / ic_ratio, 1) if ic_ratio > 0 else 0.0
        dose_totale_ridotta = round(unita_pasto_ridotto + unita_correzione, 1)
        avviso_cibo += f"📉 Se riduci il piatto, la nuova dose totale calcolata sarà di soli: {dose_totale_ridotta}\u00A0U.\n\n"

    # Se l'indice glicemico è veloce, il picco sarà distruttivo
    if indice_glicemico == "Veloce":
        avviso_cibo += (
            "⚡ ALLERTA INDICE GLICEMICO VELOCE:\n"
            f"Questo cibo ha un impatto rapidissimo. Se non puoi ridurlo, valuta se sostituirlo "
            f"o se aggiungere subito della verdura fresca (fibre) come antipasto per frenare la velocità di salita.\n\n"
        )

    # Se gli zuccheri semplici sono dominanti
    if carbo > 0 and (zuccheri / carbo) > 0.4:
        avviso_cibo += (
            f"🍬 NOTA SUGLI ZUCCHERI: Ci sono {zuccheri}g di zuccheri semplici. La spinta iniziale sarà "
            f"estremamente aggressiva. Monitora accuratamente l'andamento.\n\n"
        )

    if avviso_cibo:
        consiglio += "🌾 ANALISI E MODIFICHE DEL CIBO CONSIGLIATE:\n" + avviso_cibo

    # -------------------------------------------------------------------------
    # 🛡️ PROTEZIONE FINALE: DURATA INSULINA ATTIVA
    # -------------------------------------------------------------------------
    consiglio += (
        f"⚠️ MONITORAGGIO DI SICUREZZA:\n"
        f"Dopo aver fatto il bolo ed aver consumato il pasto, monitora la glicemia ma EVITA di fare ulteriori "
        f"boli di correzione ravvicinati nelle prossime {insulin_duration} ore (la durata della tua insulina attiva).\n"
        f"Fare correzioni continue provocherebbe un pericoloso accumulo ('stacking') con conseguente crollo ipoglicemico tardivo."
    )

    return consiglio

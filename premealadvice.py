import message_database

def getPreMealOverTargetIdealAdvice(glicemia_attuale, user_profile, mealData):
    """
    Genera il consiglio pre-pasto completo quando la glicemia è IN TARGET ma nella FASCIA ALTA
    (sopra il target ideale dell'utente ma sotto la soglia di iperglicemia).
    Gestisce micro-correzioni, ottimizzazione delle porzioni, tempistiche del bolo e analisi nutrizionale.
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
    insulin_duration = float(user_profile.get('insulin_duration', 4.0))
    measurement_unit = user_profile.get('measurement_unit', 'mg/dL')

    # 3. Calcoli matematici di base (Dose pasto e Micro-Correzione)
    unita_pasto = round(carbo / ic_ratio, 1) if ic_ratio > 0 else 0.0
    unita_micro_correzione = round((glicemia_attuale - target_ideal) / isf, 1) if isf > 0 else 0.0
    dose_totale_stimata = round(unita_pasto + unita_micro_correzione, 1)

    # 4. Intestazione del messaggio
    msg = (
        f"🟢 GLICEMIA IN TARGET - FASCIA ALTA\n\n"
        f"Il tuo valore attuale è buono ({glicemia_attuale} {measurement_unit}), ma si trova leggermente sopra il tuo obiettivo ideale di {target_ideal} {measurement_unit}.\n"
        f"Adottiamo una strategia di micro-ottimizzazione per il tuo pasto.\n\n"
    )

    # 5. Motore di ottimizzazione delle porzioni (Specifico per quando si parte già alti)
    avviso_ottimizzazione = ""
    if carbo > 100.0:
        carbo_massimi_consigliati = 75.0
        carbo_da_ridurre = round(carbo - carbo_massimi_consigliati, 1)
        avviso_ottimizzazione += (
            f"⚠️ Carico di carboidrati molto elevato:\n"
            f"  Il piatto '{nome_pasto}' contiene ben {carbo} g di carboidrati. Gestire questa quantità "
            f"mentre sei già nella fascia alta del target aumenta il rischio di un picco post-prandiale importante.\n"
            f"  Consiglio: Ti suggerisco di ridurre la porzione di circa -{carbo_da_ridurre} g di carboidrati.\n"
        )
        if peso_alimento > 0:
            densita_carbo = carbo / peso_alimento
            grammi_da_togliere_bilancia = round(carbo_da_ridurre / densita_carbo)
            avviso_ottimizzazione += f"  In pratica: togli circa {grammi_da_togliere_bilancia} g di prodotto dalla porzione sulla bilancia.\n"
        avviso_ottimizzazione += "\n"

    elif carbo > 20.0 and (zuccheri / carbo) > 0.5:
        zuccheri_eccessivi = round(zuccheri - (carbo * 0.25), 1)
        avviso_ottimizzazione += (
            f"🍬 Impatto glicemico verticale:\n"
            f"  Il cibo selezionato è composto prevalentemente da zuccheri semplici ({zuccheri} g su {carbo} g di carboidrati).\n"
            f"  Partendo da {glicemia_attuale} {measurement_unit}, questo provocherà un'impennata rapida oltre i limiti.\n"
            f"  Consiglio: Suggerisco di dimezzare questa porzione (riducendo di -{zuccheri_eccessivi} g di zuccheri semplici) "
            f"o sostituirla nel piatto con carboidrati complessi o integrali.\n\n"
        )

    if avviso_ottimizzazione:
        msg += avviso_ottimizzazione

    # 6. Informazioni sui parametri del profilo applicati
    msg += (
        f"📋 Parametri di calcolo applicati dal tuo profilo:\n"
        f"  - Rapporto I/C (Carbo): 1 U ogni {ic_ratio} g di carboidrati\n"
        f"  - Sensibilità (ISF): 1 U abbatte {isf} {measurement_unit}\n"
    )

    # 7. Controllo di sicurezza sull'Insulina Attiva (IOB)
    if insulin_duration > 0:
        msg += (
            f"  - Durata Insulina Attiva: {insulin_duration} ore.\n\n"
            f"⚠️ Nota di sicurezza sull'Insulina Attiva (IOB):\n"
            f"  Se hai effettuato un bolo di recente (meno di {insulin_duration} ore fa), ricordati che c'è ancora "
            f"  insulina attiva nel tuo corpo che sta lavorando per abbassare la glicemia. In questo caso, "
            f"  valuta di non somministrare la micro-correzione di +{unita_micro_correzione} U per evitare "
            f"  un accumulo di farmaco (insulin stacking) nel corso delle prossime ore.\n\n"
        )

    # 8. Presentazione del Piano Terapeutico e scelta del dosaggio
    if carbo > 100.0:
        unita_pasto_ottimizzato = round(75.0 / ic_ratio, 1) if ic_ratio > 0 else 0.0
        dose_totale_ottimizzata = round(unita_pasto_ottimizzato + unita_micro_correzione, 1)
        msg += (
            f"📊 Scelta del Dosaggio di Insulina:\n"
            f"  - Se segui il consiglio (Pasto ridotto a 75g carbo): Somministra {dose_totale_ottimizzata} U totali (di cui +{unita_micro_correzione} U di micro-correzione).\n"
            f"  - Se decidi di mangiare l'intera porzione originale: Somministra {dose_totale_stimata} U totali.\n\n"
        )
    else:
        msg += (
            f"📊 Piano Terapeutico Consigliato:\n"
            f"  - Unità calcolate per il pasto: {unita_pasto} U\n"
            f"  - Unità per micro-correzione valore di partenza: +{unita_micro_correzione} U\n"
            f"  👉 Dose totale consigliata: {dose_totale_stimata} U\n\n"
        )

    # 9. Analisi dei Macronutrienti e Tempismo del Bolo basato sull'Indice Glicemico
    msg += "🌾 Analisi della composizione del piatto:\n"
    
    if indice_glicemico.lower() == "veloce":
        msg += "  - Indice Glicemico Veloce: Anticipa il bolo di 10-15 minuti rispetto al primo boccone per frenare la salita.\n"
    elif indice_glicemico.lower() == "medio":
        msg += "  - Indice Glicemico Medio: Gestione standard. Puoi fare il bolo circa 5-10 minuti prima del pasto o all'inizio.\n"
    elif indice_glicemico.lower() == "lento":
        msg += "  - Indice Glicemico Lento: Assorbimento prolungato. Fai l'insulina a ridosso del pasto o all'inizio per non scendere nei primi minuti.\n"

    if grassi >= 20.0 or proteine >= 25.0:
        msg += (
            f"  - Effetto tardivo rilevato (Grassi: {grassi} g, Proteine: {proteine} g):\n"
            f"    Questo blocco rallenta lo svuotamento gastrico. La glicemia rimarrà stabile nelle prime 2 ore, "
            f"ma potrebbe salire sensibilmente in seguito.\n"
            f"    👉 Monitoraggio: Controlla l'andamento nelle prossime {insulin_duration} ore "
            f"e valuta con il medico l'uso di un bolo d'insulina frazionato o prolungato.\n"
        )
    
    if fibre >= 5.0:
        msg += f"  - Ottimo apporto di fibre ({fibre} g): agiscono da scudo naturale rallentando e spalmando l'assorbimento degli zuccheri nel tempo.\n"

    return msg

def getPreMealUnderTargetIdealAdvice(glicemia_attuale, user_profile, mealData):
    """
    Genera il consiglio pre-pasto completo quando la glicemia è IN TARGET ma nella FASCIA BASSA
    (sotto il target ideale dell'utente ma sopra la soglia di ipoglicemia).
    Gestisce sconti terapeutici, tempistiche del bolo e analisi nutrizionale in un unico blocco isolato.
    """
    # 1. Estrazione e pulizia dati del cibo (mealData)
    nome_pasto = mealData.name or 'Pasto'
    carbo = float(mealData.carbs_grams or 0.0)
    grassi = float(mealData.fats_grams or 0.0)
    proteine = float(mealData.proteins_grams or 0.0)
    fibre = float(mealData.fibers_grams or 0.0)
    indice_glicemico = mealData.glycemic_index or 'Medio'

    # 2. Estrazione parametri terapeutici (user_profile)
    ic_ratio = float(user_profile.get('ic_ratio', 10.0))
    isf = float(user_profile.get('isf', 50.0))
    target_ideal = float(user_profile.get('target_ideal', 110.0))
    insulin_duration = float(user_profile.get('insulin_duration', 4.0))
    measurement_unit = user_profile.get('measurement_unit', 'mg/dL')

    # 3. Calcoli matematici del Piano Terapeutico di Protezione
    unita_pasto = round(carbo / ic_ratio, 1) if ic_ratio > 0 else 0.0
    punti_sotto_target = target_ideal - glicemia_attuale
    unita_sconto = round(punti_sotto_target / isf, 1) if isf > 0 else 0.0
    
    # Applichiamo lo sconto evitando che la dose totale scenda sotto zero
    dose_totale_protetta = max(0.0, round(unita_pasto - unita_sconto, 1))

    # 4. Costruzione del messaggio - Sezione Glicemia e Calcoli
    msg = (
        f"🟢 GLICEMIA IN TARGET - FASCIA DI SICUREZZA\n\n"
        f"Ti trovi nella fascia bassa del tuo target. Il tuo valore attuale è sicuro ({glicemia_attuale} {measurement_unit}), "
        f"ma è inferiore rispetto al tuo obiettivo ideale di {target_ideal} {measurement_unit}.\n"
        f"La priorità in questo momento è consumare il pasto in sicurezza, evitando che l'azione immediata dell'insulina ti spinga in ipoglicemia.\n\n"
        
        f"📋 Piano Terapeutico di Protezione:\n"
        f"  - Unità base calcolate per i carboidrati ({carbo} g): {unita_pasto} U\n"
        f"  - Sconto protettivo applicato (distanza dal target): -{unita_sconto} U\n"
        f"  👉 Dose totale consigliata: {dose_totale_protetta} U\n\n"
    )

    # 5. Controllo di sicurezza sull'Insulina Attiva (IOB)
    if insulin_duration > 0:
        msg += (
            f"📊 Monitoraggio Insulina Attiva:\n"
            f"  La durata dell'insulina nel tuo profilo è di {insulin_duration} ore. Se hai eseguito un bolo nelle ore precedenti, "
            f"ricorda che c'è ancora farmaco attivo nel sangue. Con una glicemia di partenza di {glicemia_attuale} {measurement_unit}, "
            f"il rischio di un calo precoce è elevato. Monitora il sensore con attenzione durante e dopo il pasto.\n\n"
        )

    # 6. Strategia sul Tempismo del Bolo basata sull'Indice Glicemico (Specifico per Fascia Bassa)
    msg += "⏳ Tempismo del bolo di sicurezza:\n"
    if indice_glicemico.lower() == "lento":
        msg += (
            f"  - Il piatto '{nome_pasto}' ha un Indice Glicemico Lento. Poiché la tua glicemia è già nella fascia bassa, "
            f"l'insulina rapida agirebbe molto più velocemente della digestione del cibo solido.\n"
            f"  👉 Cosa fare: Posticipa il bolo a metà pasto o subito dopo aver finito di mangiare, "
            f"per dare tempo ai carboidrati di entrare in circolo ed evitare un crollo iniziale.\n\n"
        )
    elif indice_glicemico.lower() == "veloce":
        msg += (
            f"  - Il piatto '{nome_pasto}' ha un Indice Glicemico Veloce. "
            f"Tuttavia, partendo da un valore basso di {glicemia_attuale} {measurement_unit}, non devi assolutamente anticipare il bolo.\n"
            f"  👉 Cosa fare: Esegui l'insulina esattamente un istante prima del primo boccone (o entro i primi 5 minuti dall'inizio).\n\n"
        )
    else:
        msg += (
            f"  - Il piatto '{nome_pasto}' ha un Indice Glicemico Medio.\n"
            f"  👉 Cosa fare: Fai l'insulina subito prima di iniziare a mangiare o nei primissimi minuti del pasto. "
            f"Non anticipare mai il bolo di 15 minuti quando parti da questa fascia di sicurezza.\n\n"
        )

    # Nota di rassicurazione sulle porzioni
    if carbo > 0:
        msg += (
            f"🌾 Nota sui carboidrati:\n"
            f"  I {carbo} g di carboidrati presenti in questo pasto sono preziosi per stabilizzare la tua curva e "
            f"riportarti verso il centro del target. Consuma la porzione regolarmente senza tagliarla.\n\n"
        )

    # 7. Analisi dei Macronutrienti (Grassi, Proteine, Fibre)
    msg += "🌾 Analisi della composizione del piatto:\n"
    
    if grassi >= 20.0 or proteine >= 25.0:
        msg += (
            f"  - Effetto tardivo rilevato (Grassi: {grassi} g, Proteine: {proteine} g):\n"
            f"    Questo blocco rallenta lo svuotamento gastrico. La glicemia rimarrà stabile nelle prime 2 ore, "
            f"ma potrebbe salire sensibilmente in seguito.\n"
            f"    👉 Monitoraggio: Controlla l'andamento nelle prossime {insulin_duration} ore "
            f"e valuta con il medico l'uso di un bolo d'insulina frazionato o prolungato.\n"
        )
    
    if fibre >= 5.0:
        msg += f"  - Ottimo apporto di fibre ({fibre} g): agiscono da scudo naturale rallentando e spalmando l'assorbimento degli zuccheri nel tempo.\n"

    return msg

def getPreMealExactTargetIdealAdvice(glicemia_attuale, user_profile, mealData):
    """
    Genera il consiglio pre-pasto completo quando la glicemia è PERFETTAMENTE IN TARGET.
    Infonde il nome reale del pasto per una personalizzazione totale.
    """
    # 1. Estrazione e pulizia dati del cibo (mealData)
    nome_pasto = mealData.name or 'Pasto'
    carbo = float(mealData.carbs_grams or 0.0)
    grassi = float(mealData.fats_grams or 0.0)
    proteine = float(mealData.proteins_grams or 0.0)
    fibre = float(mealData.fibers_grams or 0.0)
    indice_glicemico = mealData.glycemic_index or 'Medio'

    # 2. Estrazione parametri terapeutici (user_profile)
    ic_ratio = float(user_profile.get('ic_ratio', 10.0))
    target_ideal = float(user_profile.get('target_ideal', 110.0))
    insulin_duration = float(user_profile.get('insulin_duration', 4.0))
    measurement_unit = user_profile.get('measurement_unit', 'mg/dL')

    # 3. Calcoli matematici (Solo bolo pasto, correzione a zero)
    unita_pasto = round(carbo / ic_ratio, 1) if ic_ratio > 0 else 0.0

    # 4. Intestazione del messaggio personalizzata con il nome del pasto
    msg = (
        f"🟢 GLICEMIA PERFETTAMENTE IN TARGET | {nome_pasto.upper()}\n\n"
        f"Fantastico! La tua glicemia attuale ({glicemia_attuale} {measurement_unit}) corrisponde esattamente al tuo obiettivo ideale di {target_ideal} {measurement_unit}.\n"
        f"Non serve alcuna correzione glicemica di partenza. Devi calcolare l'insulina unicamente per coprire i carboidrati di: {nome_pasto}.\n\n"
        
        f"📋 Parametri di calcolo applicati dal tuo profilo:\n"
        f"  - Rapporto I/C (Carbo): 1 U ogni {ic_ratio} g di carboidrati\n"
    )

    # 5. Controllo di sicurezza sull'Insulina Attiva (IOB)
    if insulin_duration > 0:
        msg += (
            f"  - Durata Insulina Attiva: {insulin_duration} ore.\n\n"
            f"⚠️ Nota sull'Insulina Attiva (IOB):\n"
            f"  Se hai effettuato un'iniezione nelle ultime ore, tieni presente che l'effetto potrebbe essere ancora parzialmente attivo. "
            f"  Dal momento che ti trovi già sul tuo valore perfetto, monitora che il piatto '{nome_pasto}' e il nuovo bolo entrino in circolo in modo sincrono.\n\n"
        )

    # 6. Presentazione del Piano Terapeutico Calcolato
    msg += (
        f"📊 Piano Terapeutico Calcolato per {nome_pasto}:\n"
        f"  - Unità calcolate per i carboidrati ({carbo} g): {unita_pasto} U\n"
        f"  - Correzione glicemica di partenza: 0.0 U (Sei perfettamente a target)\n"
        f"  👉 Dose totale consigliata: {unita_pasto} U\n\n"
    )

    # 7. Analisi dei Macronutrienti e Tempismo del Bolo basato sull'Indice Glicemico
    msg += f"🌾 Analisi della composizione di: {nome_pasto}\n"
    
    if indice_glicemico.lower() == "veloce":
        msg += f"  - Indice Glicemico Veloce: Provoca una salita rapida. Anticipa il bolo di 10-15 minuti rispetto al primo boccone di {nome_pasto}.\n"
    elif indice_glicemico.lower() == "medio":
        msg += "  - Indice Glicemico Medio: Gestione standard. Puoi fare il bolo circa 5-10 minuti prima del pasto o all'inizio.\n"
    elif indice_glicemico.lower() == "lento":
        msg += f"  - Indice Glicemico Lento: Assorbimento prolungato. Fai l'insulina a ridosso o all'inizio di {nome_pasto} per non scendere nei primi minuti.\n"

    if grassi >= 20.0 or proteine >= 25.0:
        msg += (
            f"  - Effetto tardivo rilevato (Grassi: {grassi} g, Proteine: {proteine} g):\n"
            f"    I grassi/proteine contenuti in '{nome_pasto}' rallentano lo svuotamento gastrico. La glicemia rimarrà stabile nelle prime 2 ore, "
            f"ma potrebbe salire sensibilmente in seguito.\n"
            f"    👉 Monitoraggio: Controlla l'andamento nelle prossime {insulin_duration} ore "
            f"e valuta con il medico l'uso di un bolo d'insulina frazionato o prolungato.\n"
        )
    
    if fibre >= 5.0:
        msg += f"  - Ottimo apporto di fibre ({fibre} g): agiscono da scudo naturale rallentando e spalmando l'assorbimento degli zuccheri nel tempo.\n"

    return msg

def getPreMealTooLowAlarmAdvice(glicemia_attuale, user_profile, mealData):
    """
    Genera il consiglio di emergenza pre-pasto quando la glicemia è in IPOGLICEMIA.
    Calcola matematicamente i carboidrati di correzione precisi basati su ISF e IC Ratio.
    """
    # 1. Estrazione e pulizia dati del cibo (mealData)
    nome_pasto = mealData.name or 'Pasto'
    carbo = float(mealData.carbs_grams or 0.0)
    grassi = float(mealData.fats_grams or 0.0)
    proteine = float(mealData.proteins_grams or 0.0)
    fibre = float(mealData.fibers_grams or 0.0)
    indice_glicemico = mealData.glycemic_index or 'Medio'

    # 2. Estrazione parametri terapeutici (user_profile)
    ic_ratio = float(user_profile.get('ic_ratio', 10.0))
    isf = float(user_profile.get('isf', 50.0))
    target_ideal = float(user_profile.get('target_ideal', 110.0))
    insulin_duration = float(user_profile.get('insulin_duration', 4.0))
    measurement_unit = user_profile.get('measurement_unit', 'mg/dL')
    soglia_ipo = int(user_profile.get('hypo_threshold', 70))

    # 3. CALCOLO MATEMATICO PERSONALIZZATO DELLA CORREZIONE IPO
    unita_pasto_teoriche = round(carbo / ic_ratio, 1) if ic_ratio > 0 else 0.0
    punti_sotto_target = target_ideal - glicemia_attuale
    
    # Quanta insulina servirebbe per risalire? (Rapporto inverso usando ISF e IC_Ratio)
    if isf > 0 and ic_ratio > 0:
        carbo_correzione_precisi = round((punti_sotto_target / isf) * ic_ratio, 1)
        # Limiti di sicurezza clinica: mai meno di 15g, mai più di 30g per singolo step di soccorso
        carbo_soccorso_reali = max(15.0, min(30.0, carbo_correzione_precisi))
    else:
        carbo_soccorso_reali = 15.0

    # 4. Intestazione dell'allarme d'emergenza
    msg = (
        f"🔴 IPOGLICEMIA IMMEDIATA | {nome_pasto.upper()}\n\n"
        f"ATTENZIONE: Il tuo valore attuale ({glicemia_attuale} {measurement_unit}) è inferiore o vicino alla tua soglia di sicurezza di {soglia_ipo} {measurement_unit}.\n"
        f"Il tuo obiettivo ideale impostato è di {target_ideal} {measurement_unit}. DEVI TASSATIVAMENTE RIMANDARE L'INIZIO DEL PASTO!\n\n"
    )

    # 5. Trattamento personalizzato basato sul calcolo matematico
    msg += (
        f"🚨 TRATTAMENTO DI SOCCORSO PERSONALIZZATO:\n"
        f"  Per colmare la distanza di -{punti_sotto_target} {measurement_unit} dal tuo target ideale, il calcolo matematico "
        f"indica che devi assumere esattamente {carbo_soccorso_reali} g di carboidrati rapidi.\n\n"
        f"  Assumi IMMEDIATAMENTE questa quota in formato esclusivamente LIQUIDO. Non consumare cibo solido.\n"
        f"  Opzioni di somministrazione stimate per raggiungere circa {carbo_soccorso_reali} g:\n"
        f"    - Succo di frutta: circa {round(carbo_soccorso_reali * 7.5)} ml (controlla i carboidrati totali sulla confezione)\n"
        f"    - Coca-Cola o Aranciata classica (NON zero): circa {round(carbo_soccorso_reali * 9.5)} ml\n"
        f"    - Zucchero bianco sciolto in acqua: {round(carbo_soccorso_reali / 5.0)} bustine/cucchiaini da caffè pieni\n"
        f"  👉 Fatto questo, aspetta 15 minuti in totale riposo e ricontrolla la glicemia.\n\n"
    )

    # 6. Monitoraggio Insulina Attiva (IOB)
    if insulin_duration > 0:
        msg += (
            f"📊 Monitoraggio Insulina Attiva ({insulin_duration} ore):\n"
            f"  La durata impostata nel tuo profilo indica che l'insulina rimane attiva per {insulin_duration} ore. "
            f"Se hai iniettato un bolo nelle ore precedenti, ricorda che c'è ancora farmaco in circolo che sta "
            f"spingendo la glicemia verso il basso.\n"
            f"  Con questa spinta contraria attiva, la risalita sarà rallentata: monitora il sensore continuamente "
            f"perché i {carbo_soccorso_reali} g appena calcolati potrebbero essere neutralizzati dall'insulina a bordo.\n\n"
        )

    # 7. Analisi dei rischi digestivi e strutturali del piatto (Uso di grassi, proteine, fibre e IG)
    msg += f"⚠️ Analisi dei pericoli sul piatto '{nome_pasto}':\n"
    
    if grassi >= 15.0 or proteine >= 20.0:
        msg += (
            f"  - Pericolo di blocco dello stomaco (Grassi: {grassi} g, Proteine: {proteine} g):\n"
            f"    Il cibo inserito ha un contenuto elevato di grassi o proteine. Non commettere l'errore di iniziare a consumarlo "
            f"pensando che i suoi carboidrati correggano l'ipoglicemia. Questo blocco rallenta drasticamente lo svuotamento gastrico, "
            f"impedendo allo zucchero d'emergenza liquido di entrare rapidamente nel sangue. Usa prima lo zucchero liquido.\n"
        )
    elif carbo > 0:
        msg += (
            f"  - Carboidrati solidi rilevati ({carbo} g): Anche se questo cibo contiene carboidrati, si tratta di complessi strutturali solidi "
            f"con un Indice Glicemico stimato come '{indice_glicemico}'. I loro tempi di scomposizione e digestione sono troppo lunghi "
            f"per gestire l'urgenza attuale. Risolvi prima l'ipoglicemia.\n"
        )

    if fibre >= 5.0:
        msg += (
            f"  - Presenza di fibre ({fibre} g): Le fibre aumentano ulteriormente l'effetto barriera nello stomaco, "
            f"rallentando l'assorbimento di qualsiasi alimento solido consumato adesso. Conferma la necessità di usare solo liquidi puri.\n"
        )
    msg += "\n"

    # 8. Protocollo di sicurezza e attivazione soccorsi
    msg += f"{message_database.CALL_AMBULANCE_ADVICE}\n\n"

    # 9. Blocco Terapeutico Tassativo (Uso del calcolo teorico basato sull'IC Ratio)
    msg += (
        f"🛑 INSULINA BLOCCATA:\n"
        f"  - Unità teoriche calcolate per il pasto (Rapporto I/C di 1 U ogni {ic_ratio} g): {unita_pasto_teoriche} U\n"
        f"  👉 AZIONE TRASVERSALE: Non eseguire assolutamente questo bolo in questo momento!\n"
        f"  Rinvia qualsiasi somministrazione a quando la glicemia si sarà stabilizzata stabilmente sopra gli 80 {measurement_unit} "
        f"e avrai risolto completamente tutti i sintomi dell'ipoglicemia."
    )

    return msg


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

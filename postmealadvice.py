from datetime import datetime, timezone
import message_database


def getPostMealTooLowAlarmAdvice(glicemia_attuale, user_profile, mealData, current_IOB=None):
    """
    Genera un messaggio esclusivamente informativo di supporto in caso di glicemia bassa POST-PASTO.
    Fornisce indicazioni basate su simulazioni matematiche dei parametri inseriti dall'utente.
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

    # 3. CALCOLO INFORMATIVO DELLA CORREZIONE
    punti_sotto_target = target_ideal - glicemia_attuale

    if isf > 0 and ic_ratio > 0:
        carbo_correzione_precisi = round((punti_sotto_target / isf) * ic_ratio, 1)
        carbo_soccorso_reali = max(15.0, min(30.0, carbo_correzione_precisi))
    else:
        carbo_soccorso_reali = 15.0

    # 4. Intestazione informativa Post-Pranzo
    msg = (
        f"ℹ️ NOTA INFORMATIVA: Simulazione andamento POST-PASTO ({nome_pasto.upper()})\n\n"
        f"Il valore registrato ({glicemia_attuale} {measurement_unit}) risulta inferiore alla "
        f"soglia di attenzione teorica di {soglia_ipo} {measurement_unit}.\n"
        f"In base alla cronologia, questo andamento potrebbe indicare che l'azione dell'insulina ha temporaneamente "
        f"superato la velocità di assimilazione dei carboidrati solidi.\n\n"
    )

    # 5. Formulazione dei suggerimenti ipotetici ("Suggerirei / Consiglierei")
    ml_stimati = round((carbo_soccorso_reali / 15.0) * 150)
    bustine_stimate = round(carbo_soccorso_reali / 5.0)

    msg += (
        f"📊 COSA SUGGERIREBBE L'ALGORITMO:\n"
        f"Per favorire il riallineamento matematico verso il target ideale ({target_ideal} {measurement_unit}), "
        f"l'app calcola un fabbisogno teorico di circa {carbo_soccorso_reali} g di carboidrati ad azione rapida.\n\n"
        f"In questi casi, dal punto di vista puramente informativo, io consiglierei l'uso di sorgenti liquide "
        f"perché permettono una risalita più immediata. Ad esempio, farei riferimento a:\n"
        f"- Succo di frutta o bibita zuccherata classica (NON zero): circa {ml_stimati} ml\n"
        f"- Zucchero bianco sciolto in acqua: circa {bustine_stimate} bustine/cucchiaini\n\n"
        f"Le buone pratiche generali suggerirebbero di attendere circa 15 minuti a riposo prima di effettuare un nuovo controllo.\n\n"
    )

    # 6. Informazione sull'Insulina Attiva (IOB)
    if insulin_duration > 0:
        msg += (
            f"📈 Nota tecnica sull'Insulina Attiva:\n"
            f"Il profilo impostato prevede una durata dell'insulina di {insulin_duration} ore. "
            f"Essendo il pasto già avvenuto, l'insulina del bolo potrebbe essere ancora pienamente attiva. "
            f"Io consiglierei di monitorare la coda di questa azione per evitare che contrasti la risalita dei carboidrati rapidi.\n\n"
        )

    # 7. Analisi teorica del pasto
    msg += f"🥗 Analisi nutrizionale simulata per '{nome_pasto}':\n"

    if grassi >= 15.0 or proteine >= 20.0:
        msg += (
            f"- Presenza di Grassi ({grassi} g) o Proteine ({proteine} g): Questa combinazione tende a "
            f"rallentare lo svuotamento dello stomaco. Dal punto di vista nutrizionale, io farei notare che questo "
            f"può creare un ritardo: l'insulina agisce subito, mentre il cibo arriva in circolo più tardi. "
            f"Suggerirei quindi di fare attenzione a possibili risalite tardive nelle prossime ore.\n"
        )
    
    if fibre >= 5.0:
        msg += (
            f"- Contenuto di Fibre ({fibre} g): Le fibre rallentano i tempi di assimilazione del pasto solido.\n"
        )

    if carbo > 0 and (grassi < 15.0 and proteine < 20.0):
        msg += (
            f"- Carboidrati dichiarati ({carbo} g): Il piatto conteneva carboidrati con indice glicemico '{indice_glicemico}'. "
            f"Se il calo è avvenuto nonostante un pasto leggero, l'algoritmo farebbe ipotizzare un leggero sovraddosaggio del bolo "
            f"rispetto al fabbisogno del momento.\n"
        )
    msg += "\n"

    # 8. Disclaimer Medico Legale OBBLIGATORIO
    msg += (
        f"⚠️ DISCLAIMER MEDICO FONDAMENTALE:\n"
        f"Questo software non è un dispositivo medico e non eroga prescrizioni. I valori e le indicazioni sopra riportate "
        f"sono modelli matematici e teorici basati esclusivamente sui dati inseriti dall'utente. "
        f"Qualsiasi decisione terapeutica, modifica dei dosaggi o gestione delle emergenze deve tassativamente seguire "
        f"i protocolli concordati con il proprio medico specialista o diabetologo. In caso di malessere, contatta subito i soccorsi (112)."
    )

    return msg

def getPostMealGlucoseTooHigh(glicemia_attuale, user_profile, mealData, current_IOB=None):
    """
    Genera un messaggio esclusivamente informativo di supporto quando la glicemia POST-PASTO è sopra il target massimo.
    Fornisce simulazioni matematiche sulla dose di correzione e considerazioni sull'andamento del pasto appena consumato.
    """
    # 1. Estrazione dagli attributi dell'oggetto mealData (Cibo già consumato)
    nome_pasto = mealData.name or 'Pasto'
    carbo = float(mealData.carbs_grams or 0.0)
    zuccheri = float(mealData.sugars_grams or 0.0)
    grassi = float(mealData.fats_grams or 0.0)
    proteine = float(mealData.proteins_grams or 0.0)
    fibre = float(mealData.fibers_grams or 0.0)
    indice_glicemico = mealData.glycemic_index or 'Medio'

    # 2. Estrazione parametri terapeutici dal profilo utente
    target_max = float(user_profile.get('target_max', 140.0))
    ic_ratio = float(user_profile.get('ic_ratio', 10.0))
    isf = float(user_profile.get('isf', 50.0))
    insulin_duration = user_profile.get('insulin_duration', 4)
    ketone_threshold = float(user_profile.get('ketone_threshold', 250.0))

    # 3. MATEMATICA TEORICA DELLA CORREZIONE POST-PASTO
    punti_da_scendere = glicemia_attuale - target_max
    unita_correzione_teorica = round(punti_da_scendere / isf, 1) if isf > 0 else 0.0

    # 4. Intestazione dell'allarme informativa Post-Pranzo
    consiglio = (
        f"🟠 VALORE SOPRA IL TARGET NELL'ANDAMENTO POST-PASTO ({glicemia_attuale}\u00A0mg/dL)\n"
        f"Il valore attuale registrato dopo il consumo di '{nome_pasto.upper()}' si trova al di sopra del limite massimo di {target_max}\u00A0mg/dL.\n\n"
    )

    # -------------------------------------------------------------------------
    # 🚨 SEZIONE INFORMATIVA CHETONI (Soglia critica)
    # -------------------------------------------------------------------------
    if glicemia_attuale >= ketone_threshold:
        consiglio += (
            f"⚠️ NOTA SUI LIVELLI CRITICI NELL'IPERGLICEMIA:\n"
            f"Considerando che il valore ha superato la soglia di attenzione di {ketone_threshold}\u00A0mg/dL, le linee guida generali "
            f"suggerirebbero di effettuare una VALUTAZIONE DEI CHETONI per monitorare la sicurezza metabolica.\n"
            f"💧 In queste situazioni, consiglierei di bere acqua naturale per supportare l'organismo nel corretto smaltimento del glucosio in eccesso.\n\n"
        )

    # -------------------------------------------------------------------------
    # 💉 SEZIONE INSULINA (Calcolo teorico di bolo integrativo)
    # -------------------------------------------------------------------------
    consiglio += (
        f"💉 SIMULAZIONE TEORICA DELLA CORREZIONE EXTRA:\n"
        f"  · Stima unità teoriche necessarie per correggere l'iperglicemia attuale: {unita_correzione_teorica}\u00A0U (basato su ISF di {isf})\n\n"
    )

    # Nota sull'Insulina Attiva (IOB) - ASSOLUTAMENTE CRUCIALE NEL POST-PASTO
    if current_IOB is not None and current_IOB > 0:
        # Calcoliamo quanta correzione rimarrebbe teoricamente al netto della IOB
        correzione_al_netto_iob = max(0.0, round(unita_correzione_teorica - current_IOB, 1))
        
        consiglio += (
            f"📊 Nota fondamentale sull'Insulina Attiva (IOB):\n"
            f"  Il sistema rileva circa {current_IOB}\u00A0U di insulina ancora attiva in circolo (derivante dal bolo del pasto).\n"
            f"  👉 Al netto dell'insulina attiva, l'algoritmo calcolerebbe una correzione residua di: {correzione_al_netto_iob}\u00A0U.\n"
            f"  ⚠️ Consiglio vivamente di valutare questo dato insieme al proprio medico prima di effettuare boli correttivi ravvicinati, "
            f"per evitare l'effetto di sovrapposizione dell'insulina (insulin stacking) e il conseguente rischio di ipoglicemia tardiva.\n\n"
        )
    else:
        consiglio += (
            f"📊 Nota sull'Insulina Attiva:\n"
            f"  Non viene rilevata insulina attiva residua in circolo. Se sono passate diverse ore dal pasto, "
            f"suggerirei di valutare con il medico se la dose teorica di {unita_correzione_teorica}\u00A0U sia indicata per il rientro a target.\n\n"
        )

    # -------------------------------------------------------------------------
    # 🧠 MOTORE DI ANALISI DEL PASTO CONSUMATO (Consultivo/Retrospettivo)
    # -------------------------------------------------------------------------
    avviso_cibo = ""

    # Se il pasto era molto abbondante, spieghiamo perché la glicemia è alta adesso
    if carbo > 55.0:
        avviso_cibo += (
            f"💡 Valutazione sui carboidrati del pasto ({carbo}\u00A0g):\n"
            f"Hai assunto una quota consistente di carboidrati nel piatto appena consumato. "
            f"Farei notare che un carico glicemico elevato può generare una spinta prolungata nello stomaco, "
            f"rendendo l'azione del bolo iniziale più lenta nel contrastare la salita.\n\n"
        )

    # Impatto tardivo di grassi e proteine (Onda quadra/doppio bolo mancato)
    if grassi >= 15.0 or proteine >= 20.0:
        avviso_cibo += (
            f"🍕 Effetto ritardato da Grassi ({grassi}\u00A0g) o Proteine ({proteine}\u00A0g):\n"
            f"Il pasto consumato presenta un livello importante di grassi o proteine. "
            f"Desidero evidenziare che questi nutrienti rallentano notevolmente la digestione. Di conseguenza, "
            f"i carboidrati potrebbero entrare nel sangue molte ore dopo il pasto, quando l'insulina iniziale ha ormai esaurito il suo effetto. "
            f"Consiglierei un monitoraggio attento nelle prossime ore per valutare questo andamento tardivo.\n\n"
        )

    # Analisi degli zuccheri veloci che creano picchi immediati
    if indice_glicemico.lower() == "veloce" or (carbo > 0 and (zuccheri / carbo) > 0.4):
        avviso_cibo += (
            f"⚡ Impatto da Indice Glicemico Alto / Zuccheri Semplici ({zuccheri}\u00A0g):\n"
            f"Questo alimento conteneva zuccheri ad assorbimento molto rapido. "
            f"Farei notare che in questi casi la velocità del cibo supera nettamente la velocità d'azione dell'insulina sottocutanea, "
            f"creando un picco temporaneo. Se l'insulina è stata somministrata senza anticipo, l'iperglicemia potrebbe essere dovuta a questo disallineamento.\n\n"
        )

    if avviso_cibo:
        consiglio += "🌾 ANALISI E VALUTAZIONI NUTRIZIONALI RETROSPETTIVE:\n\n" + avviso_cibo

    # -------------------------------------------------------------------------
    # ⚠️ DISCLAIMER MEDICO LEGALE OBBLIGATORIO
    # -------------------------------------------------------------------------
    consiglio += (
        f"⚠️ DISCLAIMER MEDICO FONDAMENTALE:\n"
        f"Questo software esegue esclusivamente modelli matematici e simulazioni teoriche basate sui dati inseriti dall'utente. "
        f"Non è un dispositivo medico e non sostituisce in alcun modo le indicazioni del medico o del diabetologo. "
        f"Qualsiasi decisione in merito a boli di correzione, variazioni terapeutiche o gestione degli stati iperglicemici "
        f"deve tassativamente seguire i protocolli personalizzati concordati con il proprio centro di cura. "
        f"In presenza di malessere o sintomi gravi, contatta immediatamente il servizio d'emergenza (112)."
    )

    return consiglio

def getPostMealExactTargetIdealAdvice(glicemia_attuale, user_profile, mealData, current_IOB=None):
    """
    Genera un messaggio esclusivamente informativo di supporto post-pasto quando la glicemia è IN TARGET IDEALE.
    Fornisce un'analisi retrospettiva sull'andamento del pasto e sul bilanciamento teorico dei parametri.
    """
    # 1. Estrazione e pulizia dati del cibo (mealData già consumato)
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

    # 3. Calcoli matematici puramente teorici (Bolo integrativo a zero)
    unita_pasto_stimata = round(carbo / ic_ratio, 1) if ic_ratio > 0 else 0.0

    # 4. Intestazione del messaggio personalizzata Post-Pranzo
    msg = (
        f"🟢 GLICEMIA IN TARGET IDEALE | MONITORAGGIO POST-PASTO ({nome_pasto.upper()})\n\n"
        f"Il valore attuale registrato ({glicemia_attuale} {measurement_unit}) corrisponde esattamente all'obiettivo ideale di {target_ideal} {measurement_unit}.\n"
        f"Questo andamento indicherebbe un ottimo bilanciamento temporaneo tra i carboidrati assimilati e l'azione dell'insulina somministrata per la copertura di: {nome_pasto}.\n\n"
        f"📋 Parametri teorici di calcolo associati al profilo:\n"
        f"  - Rapporto I/C (Carbo): 1 U ogni {ic_ratio} g di carboidrati\n"
    )

    # 5. Controllo informativo sull'Insulina Attiva (IOB) nel post-pasto
    if insulin_duration > 0 and current_IOB is not None:
        msg += (
            f"  - Durata Insulina predefinita: {insulin_duration} ore.\n\n"
            f"📊 Nota sull'Insulina Attiva (IOB):\n"
            f"  Il sistema stima circa {current_IOB} U di insulina ancora attiva in circolo. "
            f"Poiché la glicemia è perfettamente a target, consiglierei semplicemente di monitorare le ore successive. "
            f"Farei notare che la presenza di IOB residua continuerà ad agire, quindi suggerirei di verificare che non vi siano spinte al ribasso nel lungo periodo.\n\n"
        )

    # 6. Presentazione dell'Elaborazione Teorica della Correzione (A zero)
    msg += (
        f"📊 Bilancio Matematico Simulato per {nome_pasto}:\n"
        f"  - Copertura teorica stimata per il piatto ({carbo} g carbo): {unita_pasto_stimata} U\n"
        f"  - Necessità di bolo correttivo integrativo: 0.0 U (Valore ottimale)\n"
        f"  👉 Dose di correzione suggerita dall'algoritmo: 0.0 U\n\n"
    )

    # 7. Analisi Retrospettiva dei Macronutrienti e dell'Indice Glicemico
    msg += f"🥗 Analisi della composizione e risposta all'alimento '{nome_pasto}':\n"

    if indice_glicemico.lower() == "veloce":
        msg += (
            f"  - Risposta a Indice Glicemico Veloce: Questo piatto conteneva carboidrati ad assorbimento rapido. "
            f"Trovarsi a target in questa fase farebbe ipotizzare che il tempismo del bolo iniziale sia stato efficace nel contrastare il picco iniziale.\n\n"
        )
    elif indice_glicemico.lower() == "medio":
        msg += (
            f"  - Risposta a Indice Glicemico Medio: Gestione lineare. L'assimilazione del cibo e la curva dell'insulina "
            f"sembrano aver viaggiato con una sincronia ottimale.\n\n"
        )
    elif indice_glicemico.lower() == "lento":
        msg += (
            f"  - Risposta a Indice Glicemico Lento: Questo alimento prevede un rilascio molto graduale. "
            f"Essendo il valore attuale ottimale, consiglierei comunque di prestare attenzione alla coda del pasto, "
            f"poiché i carboidrati complessi potrebbero terminare l'assorbimento più tardi rispetto alla durata dell'insulina.\n\n"
        )

    if grassi >= 20.0 or proteine >= 25.0:
        msg += (
            f"  - Caratteristiche dei macronutrienti (Grassi: {grassi} g, Proteine: {proteine} g):\n"
            f"    Desidero evidenziare che una presenza elevata di grassi o proteine può rallentare significativamente lo svuotamento gastrico. "
            f"    Anche se la glicemia adesso è ottimale, la curva potrebbe subire variazioni tardive.\n"
            f"    👉 Consiglierei di estendere il monitoraggio nelle prossime {insulin_duration} ore, confrontandosi "
            f"con il proprio medico per valutare se l'andamento del pasto richieda strategie dedicate nei futuri utilizzi.\n\n"
        )

    if fibre >= 5.0:
        msg += f"  - Impatto delle fibre ({fibre} g): L'ottimo apporto di fibre ha presumibilmente contribuito a mantenere stabile e costante il flusso degli zuccheri nel sangue.\n\n"

    # 8. Disclaimer Medico Legale Obbligatorio
    msg += (
        f"⚠️ DISCLAIMER MEDICO FONDAMENTALE:\n"
        f"Questo software non è un dispositivo medico. Le analisi e le stime sopra riportate costituiscono esclusivamente "
        f"modelli matematici e simulazioni teoriche a scopo didattico e informativo. "
        f"Qualsiasi valutazione sul piano terapeutico, la gestione dei boli o il monitoraggio dei dati deve "
        f"seguire tassativamente le linee guida stabilite dal proprio diabetologo o centro di cura."
    )

    return msg

def getPostMealUnderTargetIdealAdvice(glicemia_attuale, user_profile, mealData, current_IOB=None):
    """
    Genera un messaggio esclusivamente informativo di supporto post-pasto quando la glicemia è IN TARGET ma nella FASCIA BASSA
    (sotto il target ideale dell'utente ma sopra la soglia di ipoglicemia).
    Fornisce analisi retrospettive sulla stabilità glicemica e sulla coda dell'insulina attiva.
    """
    # 1. Estrazione e pulizia dati del cibo (mealData già consumato)
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

    # 3. Calcoli matematici puramente teorici (Modello di scostamento)
    punti_sotto_target = target_ideal - glicemia_attuale
    unita_sconto_teorico = round(punti_sotto_target / isf, 1) if isf > 0 else 0.0

    # 4. Costruzione del messaggio - Sezione Glicemia e Calcoli Post-Pranzo
    msg = (
        f"🟢 GLICEMIA IN TARGET - FASCIA DI ATTENZIONE POST-PASTO ({nome_pasto.upper()})\n\n"
        f"Il valore attuale ({glicemia_attuale} {measurement_unit}) risulta sicuro, ma si colloca nella fascia inferiore "
        f"rispetto al tuo obiettivo ideale di {target_ideal} {measurement_unit}.\n"
        f"Nell'andamento post-prandiale, questa situazione potrebbe indicare che l'insulina ha agito con una velocità "
        f"leggermente superiore rispetto al rilascio dei carboidrati nello stomaco.\n\n"

        f"📋 Elaborazione Tecnica dello Scostamento:\n"
        f"  - Distanza matematica dal centro del target: -{punti_sotto_target} {measurement_unit}\n"
        f"  - Valore teorico dell'equivalente in insulina (sconto): {unita_sconto_teorico} U\n"
        f"  👉 Necessità di boli correttivi integrativi: 0.0 U\n\n"
    )

    # 5. Controllo informativo sull'Insulina Attiva (IOB) - FONDAMENTALE IN FASCIA BASSA POST-PASTO
    if insulin_duration > 0 and current_IOB is not None:
        msg += (
            f"📊 Nota sull'Insulina Attiva (IOB):\n"
            f"  Il sistema stima circa {current_IOB} U di insulina ancora attiva nel sangue. "
            f"Considerando che la glicemia si trova già nella parte bassa del target, farei notare che la spinta residua della IOB "
            f"potrebbe accentuare la tendenza alla discesa. "
            f"Suggerirei un monitoraggio particolarmente attento del sensore per intercettare tempestivamente un eventuale trend verso l'ipoglicemia.\n\n"
        )

    # 6. Considerazioni Retrospettive sull'Andamento basate sull'Indice Glicemico
    msg += f"⏳ Analisi della risposta all'alimento '{nome_pasto}':\n"
    if indice_glicemico.lower() == "lento":
        msg += (
            f"  - Risposta a Indice Glicemico Lento: Questo tipo di piatto prevede un assorbimento molto graduale. "
            f"La presenza di una glicemia tendente al basso in questa fase suggerirebbe che l'insulina rapida ha avuto un picco iniziale "
            f"mentre i carboidrati complessi sono ancora in fase di digestione. In futuro, io consiglierei di confrontarsi con il medico "
            f"per valutare se per cibi così lenti sia preferibile gestire il tempo del bolo in modo differente (es. a ridosso del pasto).\n\n"
        )
    elif indice_glicemico.lower() == "veloce":
        msg += (
            f"  - Risposta a Indice Glicemico Veloce: Il piatto conteneva zuccheri rapidi. "
            f"Trovarsi nella fascia bassa dopo un cibo veloce potrebbe indicare che il bolo calcolato inizialmente era leggermente "
            f"generoso, oppure che c'è stato un impatto significativo di attività fisica non pianificata prima o dopo il pasto.\n\n"
        )
    else:
        msg += (
            f"  - Risposta a Indice Glicemico Medio: Gestione ordinaria. "
            f"Suggerirei semplicemente di verificare se la curva si stabilizza in questa fascia o se prosegue la discesa.\n\n"
        )

    # Nota informativa sui carboidrati assunti
    if carbo > 0:
        msg += (
            f"🌾 Nota sui carboidrati consumati:\n"
            f"  I {carbo} g di carboidrati introdotti sono attualmente in fase di assimilazione. "
            f"  Dal punto di vista teorico, se la discesa dovesse continuare a causa dell'insulina attiva, consiglierei di valutare "
            f"  insieme al proprio medico una piccolissima correzione preventiva (es. 5-10g di carboidrati rapidi) solo se il trend del sensore mostra frecce di discesa netta.\n\n"
        )

    # 7. Analisi dei Macronutrienti (Grassi, Proteine, Fibre)
    msg += f"🥗 Impatto dei macronutrienti sulla stabilità tardiva:\n"

    if grassi >= 20.0 or proteine >= 25.0:
        msg += (
            f"  - Caratteristiche nutrizionali (Grassi: {grassi} g, Proteine: {proteine} g):\n"
            f"    L'importante presenza di grassi o proteine nel piatto appena consumato tende a rallentare vistosamente lo svuotamento gastrico. "
            f"    Questo potrebbe spiegare il valore basso attuale (l'insulina è partita, il cibo è bloccato). "
            f"    👉 Io farei notare che questo scenario richiede attenzione: la glicemia potrebbe risalire in modo marcato nelle prossime ore. "
            f"    Consiglierei di monitorare l'andamento per l'intera durata dell'insulina ({insulin_duration} ore).\n\n"
        )

    if fibre >= 5.0:
        msg += f"  - Apporto di fibre ({fibre} g): Il buon contenuto di fibre sta contribuendo a rendere più costante e rallentato il rilascio del glucosio nel sangue.\n\n"

    # 8. Disclaimer Medico Legale Obbligatorio
    msg += (
        f"⚠️ DISCLAIMER MEDICO FONDAMENTALE:\n"
        f"Questo software non rilascia prescrizioni né consigli medici. Le analisi fornite costituiscono esclusivamente "
        f"elaborazioni matematiche e simulazioni teoriche basate sui dati storici inseriti. "
        f"Qualsiasi scelta terapeutica o gestione delle tendenze glicemiche deve rigorosamente seguire i protocolli "
        f"stabiliti dal proprio medico curante o dal centro di diabetologia."
    )

    return msg

def getPostMealOverTargetIdealAdvice(glicemia_attuale, user_profile, mealData, current_IOB=None):
    """
    Genera un messaggio esclusivamente informativo di supporto post-pasto quando la glicemia è IN TARGET ma nella FASCIA ALTA
    (sopra il target ideale dell'utente ma sotto la soglia di iperglicemia).
    Gestisce l'analisi retrospettiva sull'impatto dei nutrienti e considerazioni sulla sicurezza della IOB.
    """
    # 1. Estrazione e pulizia dati del cibo (mealData già consumato)
    nome_pasto = mealData.name or 'Pasto'
    carbo = float(mealData.carbs_grams or 0.0)
    zuccheri = float(mealData.sugars_grams or 0.0)
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

    # 3. Calcoli matematici puramente teorici (Scostamento e Micro-Correzione)
    unita_pasto_stimata = round(carbo / ic_ratio, 1) if ic_ratio > 0 else 0.0
    punti_sopra_target = glicemia_attuale - target_ideal
    unita_micro_correzione = round(punti_sopra_target / isf, 1) if isf > 0 else 0.0

    # 4. Intestazione del messaggio Post-Pranzo
    msg = (
        f"🟢 GLICEMIA IN TARGET - FASCIA ALTA POST-PASTO ({nome_pasto.upper()})\n\n"
        f"Il valore attuale registrato ({glicemia_attuale} {measurement_unit}) si trova in una fascia sicura, "
        f"ma risulta leggermente superiore rispetto al tuo obiettivo ideale di {target_ideal} {measurement_unit}.\n"
        f"In questa fase post-prandiale, l'analisi si concentra sulla comprensione della risposta digestiva e sulla sicurezza della stabilità.\n\n"
    )

    # 5. Analisi retrospettiva sull'impatto delle porzioni consumate
    avviso_retrospettivo = ""
    if carbo > 100.0:
        avviso_retrospettivo += (
            f"⚠️ Valutazione sul carico di carboidrati elevato:\n"
            f"  Il piatto '{nome_pasto}' conteneva un quantitativo importante di carboidrati ({carbo} g). "
            f"  Farei notare che la gestione di volumi così consistenti può rendere più complessa la perfetta sincronia "
            f"  del bolo, giustificando il posizionamento temporaneo in questa fascia alta del target.\n\n"
        )
    elif carbo > 20.0 and (zuccheri / carbo) > 0.5:
        avviso_retrospettivo += (
            f"🍬 Valutazione sull'impatto degli zuccheri:\n"
            f"  Desidero evidenziare che il pasto presentava una prevalenza di zuccheri semplici ({zuccheri} g su {carbo} g totali). "
            f"  Questo fattore favorisce incrementi rapidi e verticali della curva, che potrebbero spiegare la tendenza attuale "
            f"  verso la parte superiore dell'obiettivo.\n\n"
        )

    if avviso_retrospettivo:
        msg += avviso_retrospettivo

    # 6. Informazioni sui parametri del profilo applicati
    msg += (
        f"📋 Parametri di riferimento del profilo:\n"
        f"  - Rapporto I/C associato: 1 U ogni {ic_ratio} g di carboidrati\n"
        f"  - Sensibilità teorica (ISF): 1 U attenua circa {isf} {measurement_unit}\n\n"
    )

    # 7. Controllo di sicurezza fondamentale sull'Insulina Attiva (IOB) - Evitare l'Insulin Stacking
    if insulin_duration > 0 and current_IOB is not None:
        msg += (
            f"⚠️ NOTA CRITICA SULL'INSULINA ATTIVA (IOB):\n"
            f"  Il sistema rileva circa {current_IOB} U di insulina ancora attiva nel corpo. "
            f"  Poiché il bolo del pasto è ancora in fase di azione, consiglierei la massima prudenza: "
            f"  l'aggiunta immediata di una micro-correzione per contrastare questi {punti_sopra_target} {measurement_unit} di scostamento "
            f"  potrebbe generare un accumulo di farmaco (insulin stacking), aumentando il rischio di cali successivi.\n"
            f"  Suggerirei di attendere il completamento della durata dell'insulina prima di rivalutare variazioni.\n\n"
        )

    # 8. Presentazione del Modello Matematico Teorico
    msg += (
        f"📊 Elaborazione Tecnica dello Scostamento:\n"
        f"  - Distanza teorica dal centro del target: +{punti_sopra_target} {measurement_unit}\n"
        f"  - Fabbisogno teorico stimato per il riallineamento: +{unita_micro_correzione} U\n"
        f"  👉 Nota: Se è presente insulina attiva (IOB), la dose correttiva suggerita a livello prudenziale rimane provvisoriamente a 0.0 U.\n\n"
    )

    # 9. Analisi dei Macronutrienti e Dinamica della Risposta Glicemica
    msg += f"🥗 Riflessione sulle caratteristiche del piatto '{nome_pasto}':\n"

    if indice_glicemico.lower() == "veloce":
        msg += (
            f"  - Andamento a Indice Glicemico Veloce: I carboidrati rapidi hanno già espresso la maggior parte della loro spinta. "
            f"  Se la curva tende a stabilizzarsi in questa fascia, l'effetto del cibo potrebbe considerarsi quasi concluso.\n\n"
        )
    elif indice_glicemico.lower() == "medio":
        msg += (
            f"  - Andamento a Indice Glicemico Medio: L'assimilazione sta procedendo in modo ordinario, mantenendo il profilo "
            f"  all'interno di intervalli di sicurezza pur se nella metà superiore.\n\n"
        )
    elif indice_glicemico.lower() == "lento":
        msg += (
            f"  - Andamento a Indice Glicemico Lento: Questo alimento rilascia glucosio in modo molto graduale. "
            f"  Trovarsi nella fascia alta in questo momento suggerirebbe che la spinta del cibo potrebbe prolungarsi, "
            f"  sostenendo il valore attuale o stimolando una salita successiva.\n\n"
        )

    if grassi >= 20.0 or proteine >= 25.0:
        msg += (
            f"  - Monitoraggio dell'effetto tardivo (Grassi: {grassi} g, Proteine: {proteine} g):\n"
            f"    La presenza significativa di questi macronutrienti prolunga i tempi di svuotamento gastrico. "
            f"    È opportuno ipotizzare che la glicemia possa mostrare un'ulteriore tendenza alla salita nelle prossime ore.\n"
            f"    👉 Consiglierei di prolungare il controllo del sensore per le prossime {insulin_duration} ore, "
            f"    valutando con la propria équipe medica se adottare strategie correttive dedicate per i pasti complessi.\n\n"
        )

    if fibre >= 5.0:
        msg += f"  - Ruolo delle fibre ({fibre} g): L'apporto di fibre sta contribuendo positivamente a moderare e distribuire la velocità di rilascio degli zuccheri.\n\n"

    # 10. Disclaimer Medico Legale Obbligatorio
    msg += (
        f"⚠️ DISCLAIMER MEDICO FONDAMENTALE:\n"
        f"Questo strumento non fornisce pareri medici né raccomandazioni terapeutiche. Le stime e i calcoli proposti "
        f"sono semplici simulazioni teoriche basate su modelli matematici standard. "
        f"Qualsiasi decisione relativa alla somministrazione di correzioni o modifiche terapeutiche deve "
        f"esclusivamente fare riferimento alle prescrizioni del proprio diabetologo."
    )

    return msg
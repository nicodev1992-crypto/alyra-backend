from datetime import datetime, timezone
import message_database


def getPreMealOverTargetIdealAdvice(glicemia_attuale, user_profile, mealData, current_IOB=None):
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
    unita_micro_correzione = round(
        (glicemia_attuale - target_ideal) / isf, 1) if isf > 0 else 0.0
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
            grammi_da_togliere_bilancia = round(
                carbo_da_ridurre / densita_carbo)
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
        unita_pasto_ottimizzato = round(
            75.0 / ic_ratio, 1) if ic_ratio > 0 else 0.0
        dose_totale_ottimizzata = round(
            unita_pasto_ottimizzato + unita_micro_correzione, 1)
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


def getPreMealUnderTargetIdealAdvice(glicemia_attuale, user_profile, mealData, current_IOB=None):
    """
    Genera un messaggio informativo pre-pasto quando la glicemia è IN TARGET ma nella FASCIA BASSA
    (sotto il target ideale dell'utente ma sopra la soglia di ipoglicemia).
    Fornisce analisi nutrizionali e considerazioni teoriche sui tempi del bolo.
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

    # 3. Calcoli matematici puramente teorici
    unita_pasto = round(carbo / ic_ratio, 1) if ic_ratio > 0 else 0.0
    punti_sotto_target = target_ideal - glicemia_attuale
    unita_sconto = round(punti_sotto_target / isf, 1) if isf > 0 else 0.0

    # Calcolo della stima teorica protetta
    dose_totale_protetta = max(0.0, round(unita_pasto - unita_sconto, 1))

    # 4. Costruzione del messaggio - Sezione Glicemia e Calcoli
    msg = (
        f"🟢 GLICEMIA IN TARGET - FASCIA DI ATTENZIONE\n\n"
        f"Il valore attuale ({glicemia_attuale} {measurement_unit}) è sicuro, ma si trova nella fascia inferiore "
        f"rispetto al tuo obiettivo ideale di {target_ideal} {measurement_unit}.\n"
        f"Le buone pratiche suggeriscono di gestire il pasto in modo da favorire la stabilità glicemica, "
        f"evitando che l'azione iniziale dell'insulina possa causare cali precoci.\n\n"

        f"📋 Elaborazione Teorica dei Parametri:\n"
        f"  - Stima unità base per i carboidrati ({carbo} g): {unita_pasto} U\n"
        f"  - Sconto teorico calcolato (distanza dal target): -{unita_sconto} U\n"
        f"  👉 Valore teorico indicativo della dose: {dose_totale_protetta} U\n\n"
    )

    # 5. Controllo informativo sull'Insulina Attiva (IOB)
    if insulin_duration > 0 and current_IOB is not None:
        msg += (
            f"📊 Nota sull'Insulina Attiva:\n"
            f"Il tuo profilo indica una durata dell'insulina di {insulin_duration} ore. Se hai somministrato un bolo nelle ore "
            f"precedenti, ricorda che la presenza di farmaco ancora attivo nel sangue potrebbe accentuare la tendenza al calo. "
            f"Si raccomanda un monitoraggio attento del sensore durante e dopo il pasto.\n\n"
        )

    # 6. Considerazioni sul Tempismo del Bolo basate sull'Indice Glicemico
    msg += f"⏳ Considerazioni sul tempismo del bolo (Fascia Bassa):\n"
    if indice_glicemico.lower() == "lento":
        msg += (
            f"  - Il piatto '{nome_pasto}' ha un Indice Glicemico Lento. Poiché parti da un valore vicino al limite inferiore, "
            f"l'insulina rapida potrebbe agire prima che i carboidrati solidi vengano assimilati dallo stomaco.\n"
            f"  👉 Indicazione generale: Le linee guida in questi casi suggeriscono di valutare, insieme al proprio medico, "
            f"di posticipare il bolo a metà pasto o subito dopo, per assecondare i tempi della digestione.\n\n"
        )
    elif indice_glicemico.lower() == "veloce":
        msg += (
            f"  - Il piatto '{nome_pasto}' ha un Indice Glicemico Veloce. "
            f"Tuttavia, considerando il valore iniziale di {glicemia_attuale} {measurement_unit}, le consuete raccomandazioni "
            f"suggeriscono di non anticipare la somministrazione rispetto al pasto.\n"
            f"  👉 Indicazione generale: Di norma si consiglia di effettuare l'insulina in concomitanza del primo boccone "
            f"o nei primissimi minuti dall'inizio del pasto.\n\n"
        )
    else:
        msg += (
            f"  - Il piatto '{nome_pasto}' ha un Indice Glicemico Medio.\n"
            f"  👉 Indicazione generale: Solitamente si suggerisce di somministrare il bolo a ridosso dell'inizio del pasto. "
            f"In questa fascia glicemica, anticipare l'insulina di molti metri rispetto al cibo potrebbe aumentare il rischio di cali.\n\n"
        )

    # Nota informativa sulle porzioni
    if carbo > 0:
        msg += (
            f"🌾 Nota sui carboidrati:\n"
            f"I {carbo} g di carboidrati dichiarati per questo pasto sono utili per stabilizzare la curva glicemica "
            f"e supportare il ritorno verso il centro del target ideale. È opportuno seguire le indicazioni del proprio piano nutrizionale.\n\n"
        )

    # 7. Analisi dei Macronutrienti (Grassi, Proteine, Fibre)
    msg += f"🥗 Analisi della composizione del piatto:\n"

    if grassi >= 20.0 or proteine >= 25.0:
        msg += (
            f"  - Caratteristiche nutrizionali (Grassi: {grassi} g, Proteine: {proteine} g):\n"
            f"    Questo piatto presenta un contenuto significativo di grassi o proteine, elementi noti per prolungare i tempi di "
            f"digestione. La glicemia potrebbe mantenersi stabile nelle ore immediate, per poi mostrare una tendenza alla salita più tardiva.\n"
            f"    👉 Suggerimento: Monitora l'andamento nelle prossime {insulin_duration} ore e confrontati con l'équipe medica "
            f"per valutare le migliori strategie di gestione (es. l'eventuale uso di boli prolungati o frazionati, se previsti dal dispositivo).\n\n"
        )

    if fibre >= 5.0:
        msg += f"  - Apporto di fibre ({fibre} g): La presenza di fibre contribuisce a rendere più graduale e costante nel tempo l'assorbimento dei carboidrati.\n\n"

    return msg


def getPreMealExactTargetIdealAdvice(glicemia_attuale, user_profile, mealData, current_IOB=None):
    """
    Genera un messaggio informativo pre-pasto quando la glicemia è IN TARGET IDEALE.
    Fornisce analisi nutrizionali, stime teoriche dell'insulina per i carboidrati
    e considerazioni generali sulle tempistiche di somministrazione.
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

    # 3. Calcoli matematici puramente teorici (Solo bolo pasto, correzione a zero)
    unita_pasto = round(carbo / ic_ratio, 1) if ic_ratio > 0 else 0.0

    # 4. Intestazione del messaggio personalizzata con il nome del pasto
    msg = (
        f"🟢 GLICEMIA IN TARGET IDEALE | {nome_pasto.upper()}\n\n"
        f"Il valore attuale registrato ({glicemia_attuale} {measurement_unit}) corrisponde al tuo obiettivo ideale di {target_ideal} {measurement_unit}.\n"
        f"In questa condizione non è prevista una quota di correzione per la glicemia di partenza; i calcoli teorici "
        f"fanno riferimento esclusivamente alla copertura dei carboidrati dichiarati per: {nome_pasto}.\n\n"

        f"📋 Parametri di calcolo configurati nel profilo:\n"
        f"  - Rapporto I/C (Carbo): 1 U ogni {ic_ratio} g di carboidrati\n"
    )

    # 5. Controllo informativo sull'Insulina Attiva (IOB)
    if insulin_duration > 0 and current_IOB is not None:
        msg += (
            f"  - Durata Insulina Attiva: {insulin_duration} ore.\n\n"
            f"📊 Nota sull'Insulina Attiva (IOB):\n"
            f"  Se è presente dell'insulina ancora attiva in circolo da somministrazioni precedenti, ricorda che potrebbe "
            f"influire sull'andamento post-prandiale. Si raccomanda di verificare che l'assimilazione di '{nome_pasto}' "
            f"e l'azione del nuovo bolo siano bilanciate.\n\n"
        )

    # 6. Presentazione dell'Elaborazione Teorica del Piano
    msg += (
        f"📊 Elaborazione Teorica per {nome_pasto}:\n"
        f"  - Stima unità per i carboidrati ({carbo} g): {unita_pasto} U\n"
        f"  - Correzione glicemica di partenza: 0.0 U (Valore a target ideale)\n"
        f"  👉 Valore teorico indicativo della dose: {unita_pasto} U\n\n"
    )

    # 7. Analisi dei Macronutrienti e Considerazioni sul Tempismo basate sull'Indice Glicemico
    msg += f"🥗 Analisi della composizione di: {nome_pasto}\n"

    if indice_glicemico.lower() == "veloce":
        msg += (
            f"  - Indice Glicemico Veloce: Questo tipo di piatto favorisce un rapido incremento della glicemia. "
            f"Le consuete linee guida, quando si parte da un valore a target, suggeriscono di valutare una somministrazione "
            f"del bolo anticipata di circa 10-15 minuti rispetto al pasto, secondo le indicazioni del proprio medico.\n\n"
        )
    elif indice_glicemico.lower() == "medio":
        msg += (
            f"  - Indice Glicemico Medio: Gestione ordinaria. Le buone pratiche generali indicano solitamente come "
            f"opportuno eseguire il bolo circa 5-10 minuti prima del pasto o in concomitanza dell'inizio.\n\n"
        )
    elif indice_glicemico.lower() == "lento":
        msg += (
            f"  - Indice Glicemico Lento: Questo alimento prevede un assorbimento più graduale e prolungato nel tempo. "
            f"In questi casi, le raccomandazioni standard suggeriscono di effettuare il bolo a ridosso dell'inizio del pasto "
            f"per evitare temporanei cali glicemici nelle fasi iniziali.\n\n"
        )

    if grassi >= 20.0 or proteine >= 25.0:
        msg += (
            f"  - Caratteristiche nutrizionali (Grassi: {grassi} g, Proteine: {proteine} g):\n"
            f"    La presenza significativa di grassi o proteine può prolungare i tempi di svuotamento dello stomaco. "
            f"La curva glicemica potrebbe mantenersi stabile nelle prime due ore per poi mostrare un incremento successivo.\n"
            f"    👉 Suggerimento: Si consiglia di monitorare l'andamento nelle prossime {insulin_duration} ore e di confrontarsi "
            f"con il proprio medico per valutare l'adeguatezza di strategie specifiche (es. boli prolungati o frazionati, se previsti).\n\n"
        )

    if fibre >= 5.0:
        msg += f"  - Apporto di fibre ({fibre} g): L'ottimo contenuto di fibre contribuisce a rendere più costante e graduale il rilascio degli zuccheri nel sangue.\n\n"

    return msg


def getPreMealTooLowAlarmAdvice(glicemia_attuale, user_profile, mealData, current_IOB=None):
    """
    Genera un messaggio informativo di supporto in caso di glicemia bassa pre-pasto.
    Fornisce indicazioni basate sui parametri inseriti dall'utente nel profilo, 
    ricordando sempre di seguire i protocolli medici personalizzati.
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
    unita_pasto_teoriche = round(carbo / ic_ratio, 1) if ic_ratio > 0 else 0.0
    punti_sotto_target = target_ideal - glicemia_attuale

    # Calcolo puramente indicativo basato sui fattori inseriti dall'utente
    if isf > 0 and ic_ratio > 0:
        carbo_correzione_precisi = round(
            (punti_sotto_target / isf) * ic_ratio, 1)
        # Regola generale standard (Range 15g - 30g come riferimento informativo)
        carbo_soccorso_reali = max(15.0, min(30.0, carbo_correzione_precisi))
    else:
        carbo_soccorso_reali = 15.0

    # 4. Intestazione informativa
    msg = (
        f"ℹ️ INFORMAZIONE: Glicemia sotto il target prima di: {nome_pasto.upper()}\n\n"
        f"Il valore attuale registrato ({glicemia_attuale} {measurement_unit}) si trova al di sotto o vicino alla "
        f"soglia di attenzione impostata di {soglia_ipo} {measurement_unit}.\n"
        f"In queste condizioni, le linee guida generali suggeriscono di dare la precedenza al ripristino della glicemia "
        f"prima di iniziare il pasto vero e proprio.\n\n"
    )

    # 5. Indicazioni sui carboidrati a rapido assorbimento (Regola dei 15g)
    # Calcolo liquidi corretto: 15g di carbo equivalgono a circa 150ml di bevanda zuccherata/succo
    ml_stimati = round((carbo_soccorso_reali / 15.0) * 150)
    bustine_stimate = round(carbo_soccorso_reali / 5.0)

    # BUG CORRETTO: Cambiato = in += per non cancellare l'intestazione precedente
    msg += (
        f"🍎 GESTIONE INFORMATIVA DELLA GLICEMIA BASSA:\n"
        f"In base ai parametri del profilo, per favorire il ritorno al target ideale ({target_ideal} {measurement_unit}), "
        f"potrebbe essere utile assumere circa {carbo_soccorso_reali} g di carboidrati a rapida azione.\n\n"
        f"Le linee guida suggeriscono l'uso di opzioni liquide per una risalita più rapida, come ad esempio:\n"
        f"- Succo di frutta o bibita zuccherata classica (NON zero): circa {ml_stimati} ml\n"
        f"- Zucchero bianco sciolto in acqua: circa {bustine_stimate} bustine/cucchiaini\n\n"
        f"Dopo l'assunzione, è consigliabile attendere 15 minutes a riposo e verificare nuovamente il valore glicemico.\n\n"
    )

    # 6. Informazione sull'Insulina Attiva (IOB)
    if insulin_duration > 0 and current_IOB is not None:
        msg += (
            f"📊 Nota sull'Insulina Attiva:\n"
            f"Il profilo indica una durata dell'insulina di {insulin_duration} ore. Se è presente dell'insulina ancora attiva "
            f"in circolo, l'azione dei carboidrati rapidi potrebbe essere parzialmente contrastata. "
            f"Si consiglia di monitorare con attenzione l'andamento del sensore.\n\n"
        )

    # 7. Informazioni sulla composizione del pasto e confronto carboidrati
    msg += f"🥗 Analisi nutrizionale del piatto '{nome_pasto}':\n"

    if carbo < carbo_soccorso_reali and carbo > 0:
        msg += (
            f"- Nota sui carboidrati del pasto: Il piatto contiene {carbo} g di carboidrati, una quota inferiore "
            f"ai {carbo_soccorso_reali} g teoricamente necessari per correggere il valore attuale. Una volta risolta l'emergenza con "
            f"i liquidi, potrebbe essere necessario rivalutare la composizione del pasto per stabilizzare i valori successivi.\n"
        )

    if grassi >= 15.0 or proteine >= 20.0:
        msg += (
            f"- Presenza di Grassi ({grassi} g) o Proteine ({proteine} g): I pasti ricchi di grassi o proteine tendono a "
            f"rallentare la digestione. Per questo motivo, in caso di glicemia bassa, i cibi solidi complessi potrebbero non essere "
            f"sufficientemente rapidi nel far risalire i valori rispetto alle soluzioni liquide.\n"
        )
    elif carbo > 0 and carbo >= carbo_soccorso_reali:
        msg += (
            f"- Carboidrati nel pasto ({carbo} g): Questo piatto contiene carboidrati solidi con indice glicemico '{indice_glicemico}'. "
            f"Ricorda che i carboidrati complessi richiedono tempi di digestione più lunghi e non sostituiscono l'efficacia del "
            f"carboidrato liquido in condizioni di urgenza.\n"
        )

    if fibre >= 5.0:
        msg += (
            f"- Contenuto di Fibre ({fibre} g): Le fibre rallentano ulteriormente l'assorbimento gastrico, prolungando i tempi "
            f"di assimilazione del pasto solido.\n"
        )
    msg += "\n"

    # 8. Protocollo di sicurezza e nota medica fondamentale
    msg += (
        f"⚠️ NOTA MEDICA FONDAMENTALE:\n"
        f"Questa applicazione fornisce esclusivamente calcoli teorici e informazioni di supporto basate sui dati inseriti. "
        f"Non sostituisce in alcun modo il parere del medico o del diabetologo. In presenza di sintomi severi, malessere "
        f"o se la glicemia non risale dopo i tentativi di correzione, contatta immediatamente il medico o i soccorsi d'emergenza.\n\n"
    )

    # 9. Informazione sul Bolo
    msg += (
        f"🛑 NOTA SULL'INSULINA DEL PASTO:\n"
        f"Il calcolo teorico per questo pasto (Rapporto I/C) prevede {unita_pasto_teoriche} U.\n"
        f"In caso di valori bassi, le buone pratiche suggeriscono di posticipare l'erogazione del bolo del pasto a quando "
        f"la glicemia si sarà stabilizzata in sicurezza ed i sintomi saranno completamente passati."
    )

    return msg


def getPreMealGlucoseTooHigh(glicemia_attuale, user_profile, mealData, current_IOB=None):
    """
    Genera un messaggio informativo di supporto quando la glicemia pre-pasto è sopra il target massimo.
    Fornisce elaborazioni teoriche sulla dose di correzione e considerazioni nutrizionali
    per favorire una gestione consapevole del pasto.
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

    # 3. MATEMATICA TEORICA DELL'INSULINA
    punti_da_scendere = glicemia_attuale - target_max
    unita_correzione = round(punti_da_scendere / isf, 1) if isf > 0 else 0.0
    unita_pasto = round(carbo / ic_ratio, 1) if ic_ratio > 0 else 0.0

    # Somma totale terapeutica teorica
    dose_totale_raccomandata = round(unita_pasto + unita_correzione, 1)

    # 4. Intestazione dell'allarme informativa
    consiglio = (
        f"🟠 VALORE SOPRA IL TARGET ({glicemia_attuale}\u00A0mg/dL)\n"
        f"Il valore attuale registrato si trova al di sopra del limite massimo impostato nel tuo profilo di {target_max}\u00A0mg/dL.\n\n"
    )

    # -------------------------------------------------------------------------
    # 🚨 SEZIONE INFORMATIVA CHETONI (Soglia critica)
    # -------------------------------------------------------------------------
    if glicemia_attuale >= ketone_threshold:
        consiglio += (
            f"⚠️ NOTA SUI LIVELLI CRITICI:\n"
            f"Considerando che il valore ha superato i {ketone_threshold}\u00A0mg/dL, le linee guida generali "
            f"raccomandano di effettuare una VALUTAZIONE DEI CHETONI (ematici o urinari) per monitorare la sicurezza metabolica.\n"
            f"💧 È consigliabile bere acqua naturale per supportare l'organismo nel corretto smaltimento del glucosio in eccesso.\n\n"
        )

    # -------------------------------------------------------------------------
    # 💉 SEZIONE INSULINA (Elaborazione teorica basata sul profilo)
    # -------------------------------------------------------------------------
    consiglio += (
        f"💉 PIANO TEORICO DI CORREZIONE E COPERTURA:\n"
        f"  · Stima unità per correzione iperglicemia: +{unita_correzione}\u00A0U (basato su ISF di {isf})\n"
        f"  · Stima unità per copertura piatto ({carbo}g carbo): {unita_pasto}\u00A0U\n"
        f"  👉 Valore teorico indicativo della dose totale: {dose_totale_raccomandata}\u00A0U\n\n"
    )

    # Nota integrata sull'Insulina Attiva (IOB) se presente
    if current_IOB is not None and current_IOB > 0:
        consiglio += (
            f"📊 Nota sull'Insulina Attiva (IOB):\n"
            f"  Il sistema rileva circa {current_IOB}\u00A0U di insulina ancora attiva in circolo. Ricorda di valutare "
            f"questo dato insieme al tuo medico per l'eventuale storno dalla dose di correzione totale.\n\n"
        )

    consiglio += (
        f"⏳ Considerazioni sul tempismo del bolo:\n"
        f"In caso di valori di partenza elevati, le buone pratiche suggeriscono di valutare, d'intesa con il proprio medico, "
        f"un adeguato tempo di attesa (indicativamente 15-20 minuti) tra la somministrazione del bolo e l'inizio del pasto, "
        f"per consentire all'insulina di iniziare la sua azione di contrasto al picco post-prandiale.\n\n"
    )

    # -------------------------------------------------------------------------
    # 🧠 MOTORE DI OTTIMIZZAZIONE DEL CIBO (Consultivo)
    # -------------------------------------------------------------------------
    avviso_cibo = ""

    if carbo > 55.0:
        carbo_ideali_iper = 40.0
        carbo_da_togliere = round(carbo - carbo_ideali_iper, 1)

        avviso_cibo += (
            f"💡 Considerazioni sulla porzione di '{nome_pasto}':\n"
            f"Con una glicemia di partenza sopra il target, l'introduzione di una quota consistente di carboidrati ({carbo}\u00A0g) "
            f"potrebbe rendere il ritorno al target più graduale e prolungato.\n"
            f"👉 Potrebbe essere utile valutare una riduzione del piatto di circa -{carbo_da_togliere}\u00A0g di carboidrati.\n"
        )

        if peso_alimento > 0:
            grammi_da_togliere_bilancia = round(
                carbo_da_togliere / (carbo / peso_alimento))
            avviso_cibo += f"👉 Riferimento indicativo sulla bilancia: circa -{grammi_da_togliere_bilancia}\u00A0g rispetto alla porzione impostata.\n"

        unita_pasto_ridotto = round(
            carbo_ideali_iper / ic_ratio, 1) if ic_ratio > 0 else 0.0
        dose_totale_ridotta = round(unita_pasto_ridotto + unita_correzione, 1)
        avviso_cibo += f"📉 In caso di riduzione della porzione, il valore teorico indicativo della dose calcolata diventerebbe: {dose_totale_ridotta}\u00A0U.\n\n"

    if indice_glicemico.lower() == "veloce":
        avviso_cibo += (
            "⚡ Nota sull'Indice Glicemico Veloce:\n"
            f"Questo alimento ha un impatto molto rapido sui valori. Se non è possibile ridurlo, le strategie comuni "
            f"suggeriscono di valutare l'inserimento di una porzione di verdura fresca ricca di fibre come antipasto, "
            f"per aiutare a rallentare la velocità di assorbimento degli zuccheri.\n\n"
        )

    if carbo > 0 and (zuccheri / carbo) > 0.4:
        avviso_cibo += (
            f"🍬 Analisi degli Zuccheri Semplici:\n"
            f"Il piatto presenta una percentuale rilevante di zuccheri semplici ({zuccheri}g). "
            f"Si raccomanda un attento monitoraggio della curva successiva per intercettare tempestivamente la spinta iniziale.\n\n"
        )

    if avviso_cibo:
        consiglio += "🌾 ANALISI E VALUTAZIONI NUTRIZIONALI:\n\n" + avviso_cibo


    return consiglio


def calcola_iob_istantanea(insulin_units: float, insulin_time_raw, insulin_duration: float) -> float:
    """
    Calcola l'Insulina Attiva (IOB) in tempo reale basandosi su unità,
    orario dell'iniezione e durata dell'insulina dell'utente.
    """
    if not insulin_units or insulin_units <= 0 or not insulin_time_raw:
        return 0.0

    if not insulin_duration or insulin_duration <= 0:
        return 0.0

    # 1. Convertiamo l'orario in un oggetto datetime (se arriva come stringa)
    # Se insulin_time_raw è già un datetime, saltiamo questo step
    if isinstance(insulin_time_raw, str):
        # Gestisce il formato ISO standard che arriva da Flutter (es. 2026-05-27T15:04:13Z)
        # Rimuoviamo la 'Z' finale o i millisecondi se necessario, o usiamo fromisoformat
        try:
            # Rimpiazza la Z con +00:00 per renderlo leggibile da Python
            orario_pulito = insulin_time_raw.replace('Z', '+00:00')
            ora_iniezione = datetime.fromisoformat(orario_pulito)
        except Exception:
            # Fallback se il formato è leggermente diverso
            return 0.0
    else:
        ora_iniezione = insulin_time_raw

    # 2. Rendiamo tutto omogeneo in UTC per non sballare con i fusi orari
    if ora_iniezione.tzinfo is None:
        ora_iniezione = ora_iniezione.replace(tzinfo=timezone.utc)

    ora_attuale = datetime.now(timezone.utc)

    # 3. Calcolo del tempo passato
    differenza_tempo = ora_attuale - ora_iniezione
    ore_trascorse = differenza_tempo.total_seconds() / 3600.0

    # Se il tempo trascorso è negativo (orario nel futuro per errore) o ha superato la durata, l'IOB è zero
    if ore_trascorse <= 0 or ore_trascorse >= insulin_duration:
        return 0.0

    # 4. Formula lineare di decadimento dell'insulina attiva
    percentuale_residua = 1.0 - (ore_trascorse / insulin_duration)
    iob = insulin_units * percentuale_residua

    return round(iob, 1)

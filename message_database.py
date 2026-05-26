low_glucose_no_meal_data = (
    "🔴 **IPOGLICEMIA IMMEDIATA**\n\n"
    "Serve zucchero semplice IMMEDIATO (circa 15g di carboidrati veloci).\n\n"
    "Alimenti consigliati:\n"
    " - 1/2 bicchiere di Coca-Cola o aranciata (NON zero/diet)\n"
    " - 1 piccolo succo di frutta (circa 100-150ml)\n"
    " - 3 cucchiaini o bustine di zucchero sciolti in acqua\n"
    " - 4 compresse di glucosio/destrosio\n\n"
    "⚠️ **EVITA in questo momento**: Cioccolato, merendine o biscotti (i grassi rallentano la risalita dello zucchero)."
)

# Cambiato il nome per non sovrascrivere la variabile sopra
warning_low_glucose_no_meal_data = (
    "🟡 **GLICEMIA TENDENTE AL BASSO**\n\n"
    "La glicemia è bassa ma non ancora in emergenza. Serve uno spuntino con carboidrati complessi "
    "abbinati a una piccola quota di proteine o grassi per mantenere il livello stabile nel tempo.\n\n"
    "Alimenti consigliati:\n"
    " - 1 pacchetto di cracker integrali\n"
    " - 1 fetta di pane di segale con un velo di formaggio spalmabile o bresaola\n"
    " - 1 mela o 1 pera piccola con 3-4 mandorle"
)

perfect_glucose_no_meal_data = (
    "🟢 **VALORE IN TARGET**\n\n"
    "Alimenti consigliati:\n"
    " - Un piatto unico con carboidrati complessi a basso indice glicemico (pasta/riso integrale, farro, quinoa)\n"
    " - Una buona porzione di verdure (fibre) e una fonte proteica (pesce, pollo, legumi)."
)


def getAlarmHighGlucoseMessage(glucose_value, measurement_unit):
    return (
        f"🟠 **IPERGLICEMIA / VALORE ALTO**\n\n"
        f"Il valore è alto ({glucose_value} {measurement_unit}). Al momento è fondamentale evitare carboidrati e zuccheri.\n\n"
        f"Cosa fare/mangiare:\n"
        f" - Prima di tutto: Bevi 1 o 2 grandi bicchieri d'acqua per aiutare i reni a smaltire il glucosio.\n"
        f" - Se hai assolutamente fame, scegli alimenti che NON impattano sulla glicemia (Zero Carboidrati):\n"
        f"   * Qualche cubetto di parmigiano o grana\n"
        f"   * Una manciata di finocchi, sedano o cetrioli crudi\n"
        f"   * Un uovo sodo\n"
        f"   * Qualche gheriglio di noce o mandorla (senza esagerare)"
    )


def getAlarmLowGlucoseMessage(glucose_value, measurement_unit):
    # Corretto anche il nome della funzione (M maiuscola su Message per consistenza)
    return (
        f"🔴 **IPOGLICEMIA IMMEDIATA**\n\n"
        f"Il valore è troppo basso! ({glucose_value} {measurement_unit}).\n"
        f"Serve zucchero semplice IMMEDIATO (circa 15g di carboidrati veloci).\n\n"
        f"Alimenti consigliati:\n"
        f" - 1/2 bicchiere di Coca-Cola o aranciata (NON zero/diet)\n"
        f" - 1 piccolo succo di frutta (circa 100-150ml)\n"
        f" - 3 cucchiaini o bustine di zucchero sciolti in acqua\n"
        f" - 4 compresse di glucosio/destrosio\n\n"
        f"⚠️ **EVITA in questo momento**: Cioccolato, merendine o biscotti (i grassi rallentano la risalita dello zucchero)."
    )

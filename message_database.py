low_glucose_no_meal_data = (
    "🔴 IPOGLICEMIA IMMEDIATA"
    "Serve zucchero semplice IMMEDIATO (circa 15g di carboidrati veloci).\n"
    "Alimenti consigliati:\n"
    "  - 1/2 bicchiere di Coca-Cola o aranciata (NON zero/diet)\n"
    "  - 1 piccolo succo di frutta (circa 100-150ml)\n"
    "  - 3 cucchiaini o bustine di zucchero sciolti in acqua\n"
    "  - 4 compresse di glucosio/destrosio\n"
    "⚠️ EVITA in questo momento: Cioccolato, merendine o biscotti (i grassi rallentano la risalita dello zucchero)."
)

low_glucose_no_meal_data = (
    "🟡 GLICEMIA TENDENTE AL BASSO"
    "La glicemia è bassa ma non ancora in emergenza. Serve uno spuntino con carboidrati complessi "
    "abbinati a una piccola quota di proteine o grassi per mantenere il livello stabile nel tempo.\n"
    "Alimenti consigliati:\n"
    "  - 1 pacchetto di cracker integrali\n"
    "  - 1 fetta di pane di segale con un velo di formaggio spalmabile o bresaola\n"
    "  - 1 mela o 1 pera piccola con 3-4 mandorle")

perfect_glucose_no_meal_data = (
    "🟢 VALORE IN TARGET"
    "Alimenti consigliati:\n"
    "  - Un piatto unico con carboidrati complessi a basso indice glicemico (pasta/riso integrale, farro, quinoa)\n"
    "  - Una buona porzione di verdure (fibre) e una fonte proteica (pesce, pollo, legumi)."
)


def getAlarmHighGlucoseMessage(glucose_value,measurement_unit):
    return ("🟠 IPERGLICEMIA / VALORE ALTO"
            f"Il valore è alto ({glucose_value} {measurement_unit}). Al momento è fondamentale evitare carboidrati e zuccheri.\n"
            "Cosa fare/mangiare:\n"
            "  - Prima di tutto: Bevi 1 o 2 grandi bicchieri d'acqua per aiutare i reni a smaltire il glucosio.\n"
            "  - Se hai assolutamente fame, scegli alimenti che NON impattano sulla glicemia (Zero Carboidrati):\n"
            "    * Qualche cubetto di parmigiano o grana\n"
            "    * Una manciata di finocchi, sedano o cetrioli crudi\n"
            "    * Un uovo sodo\n"
            "    * Qualche gheriglio di noce o mandorla (senza esagerare)")


def getAlarmLowGlucosemessage(glucose_value, measurement_unit):
    return ("🔴 IPOGLICEMIA IMMEDIATA"
            f"Il valore è troppo basso! ({glucose_value} {measurement_unit})."
            "Serve zucchero semplice IMMEDIATO (circa 15g di carboidrati veloci).\n"
            "Alimenti consigliati:\n"
            "  - 1/2 bicchiere di Coca-Cola o aranciata (NON zero/diet)\n"
            "  - 1 piccolo succo di frutta (circa 100-150ml)\n"
            "  - 3 cucchiaini o bustine di zucchero sciolti in acqua\n"
            "  - 4 compresse di glucosio/destrosio\n"
            "⚠️ EVITA in questo momento: Cioccolato, merendine o biscotti (i grassi rallentano la risalita dello zucchero)."
            )

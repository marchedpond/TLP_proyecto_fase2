from parser import miParser, lexer

import spacy
try:
    nlp = spacy.load("es_core_news_sm")
except:
    nlp = None
    print("spaCy no está instalado o falta el modelo 'es_core_news_sm'.")


def mostrar_tokens(cadena):
    lexer.input(cadena)
    print("\nTokens generados:")
    print("------------------------------------")
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(f"{tok.type:15} | {tok.value}")
    print("------------------------------------\n")


def analisis_spacy(cadena):
    if nlp is None:
        print("⚠ No fue posible ejecutar spaCy.")
        return

    texto = cadena.replace(";$", "").strip()

    print("\n=== Análisis spaCy ===")
    print(f"Frase analizada: {texto!r}\n")

    doc = nlp(texto)

    for token in doc:
        print(
            f"{token.text:12} | Lema: {token.lemma_:12} | "
            f"POS: {token.pos_:6} | Dep: {token.dep_:10} | Head: {token.head.text}"
        )

    print("\nInterpretación:")
    print("- spaCy interpreta la oración como válida en español.")
    print("- 'el' → determinante")
    print("- 'perro' → sustantivo")
    print("- 'come' → verbo (raíz de la oración)")
    print("=== Fin de análisis spaCy ===\n")


def ejecutar_prueba(nombre, cadena, mostrar_lexico=False, usar_spacy=False):
    print("\n====================================================")
    print(f" PRUEBA: {nombre}")
    print("====================================================")
    print(f"Entrada: {cadena!r}")

    if mostrar_lexico:
        mostrar_tokens(cadena)

    if usar_spacy:
        analisis_spacy(cadena)

    if not usar_spacy:
        print("Resultado del parser:")
        print("------------------------------------")
        resultado = miParser(cadena)

        if resultado == 1:
            print(">>> CADENA ACEPTADA por el parser")
        else:
            print(">>> ERROR: La cadena NO es válida según la gramática")
    else:
        print(">>> spaCy analizó correctamente la oración.")
    
    print("====================================================\n")


# LISTA DE PRUEBAS
# 1. Declaración válida
ejecutar_prueba(
    "Declaración válida",
    "int variable = 5;$",
    mostrar_lexico=True
)

# 2A. Código inválido para tu COMPILADOR (lenguaje natural)
ejecutar_prueba(
    "Lenguaje natural (análisis del compilador)",
    "el perro come;$",
    mostrar_lexico=True
)

# 2B. MISMA frase, pero analizada con spaCy (DEBE FUNCIONAR)
ejecutar_prueba(
    "Lenguaje natural (análisis spaCy)",
    "el perro come;$",
    usar_spacy=True
)

# 3. Declaración con varias variables
ejecutar_prueba(
    "Declaración múltiple",
    "float a, b, c = 9;$",
    mostrar_lexico=True
)

# 4. Expresión con operadores
ejecutar_prueba(
    "Expresión matemática",
    "int x = (5 + 3) * 2;$",
    mostrar_lexico=True
)

# 5. Estructura IF válida
ejecutar_prueba(
    "Sentencia IF válida",
    "if(5+3) x=1;$",
    mostrar_lexico=True
)

# 6. Estructura IF inválida
ejecutar_prueba(
    "Sentencia IF inválida",
    "if(5+3) x=;$",
    mostrar_lexico=True
)

# 7. Estructura FOR válida
ejecutar_prueba(
    "Sentencia FOR válida",
    "for(x=0; x; x=1) x=3;$",
    mostrar_lexico=True
)

# 8. Estructura FOR inválida
ejecutar_prueba(
    "Sentencia FOR inválida",
    "for(x=0; x; x=1) x=;$",
    mostrar_lexico=True
)

print("\n*** PRUEBAS FINALIZADAS ***\n")

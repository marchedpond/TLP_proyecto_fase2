# ------------------------------------------------------------
# Archivo de pruebas para parser.py
# ------------------------------------------------------------

from parser import miParser, lexer

# Función auxiliar: imprime tokens generados (para debugging ordenado)
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


# Función para ejecutar una prueba
def ejecutar_prueba(nombre, cadena, mostrar_lexico=False):
    print("\n====================================================")
    print(f" PRUEBA: {nombre}")
    print("====================================================")
    print(f"Entrada: {cadena!r}")

    if mostrar_lexico:
        mostrar_tokens(cadena)

    print("Resultado del parser:")
    print("------------------------------------")
    resultado = miParser(cadena)

    if resultado == 1:
        print(">>>CADENA ACEPTADA por el parser")
    else:
        print(">>>ERROR: La cadena NO es válida según la gramática")

    print("====================================================\n")


# ------------------------------------------------------------
# LISTA DE PRUEBAS
# ------------------------------------------------------------

# 1. Declaración válida
ejecutar_prueba(
    "Declaración válida",
    "int variable = 5;$",
    mostrar_lexico=True
)

# 2. Código inválido (lenguaje natural con eof)
ejecutar_prueba(
    "Frase en lenguaje natural con EOF",
    "el perro come;$",
    mostrar_lexico=True
)

# 3. Declaración con varias variables
ejecutar_prueba(
    "Declaración múltiple",
    "float a, b, c = 9;$",
    mostrar_lexico=True
)


# 5. Expresión con operadores
ejecutar_prueba(
    "Expresión matemática",
    "int x = (5 + 3) * 2;$",
    mostrar_lexico=True
)

# 6. Estructura IF válida
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

# 7. Estructura FOR inválida
ejecutar_prueba(
    "Sentencia FOR inválida",
    "for(x=0; x; x=1) x=;$",
    mostrar_lexico=True
)


print("\n\n*** PRUEBAS FINALIZADAS ***\n")

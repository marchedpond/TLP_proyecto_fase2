# ------------------------------------------------------------
# Pruebas para Fase 2 - Parser de Lenguaje Natural
# ------------------------------------------------------------

from parser_natural import parsear_oracion, tokenizar, ParseError, mostrar_estructura
import spacy

# Cargar modelo de spaCy
try:
    nlp = spacy.load("es_core_news_sm")
    SPACY_DISPONIBLE = True
except:
    nlp = None
    SPACY_DISPONIBLE = False
    print("spaCy no está disponible. Algunas pruebas no se ejecutarán.\n")


def analizar_con_spacy(texto):
    """Analiza un texto con spaCy y muestra el resultado"""
    if not SPACY_DISPONIBLE:
        return None
    
    doc = nlp(texto)
    
    print("\nAnálisis con spaCy:")
    print("=" * 60)
    print(f"Texto: '{texto}'\n")
    
    print(f"{'Palabra':<15} {'Lema':<15} {'POS':<10} {'Dependencia':<15} {'Head':<10}")
    print("-" * 60)
    
    for token in doc:
        print(
            f"{token.text:<15} {token.lemma_:<15} {token.pos_:<10} "
            f"{token.dep_:<15} {token.head.text:<10}"
        )
    
    print("\nspaCy acepta la oración como válida")
    print("=" * 60)
    
    return doc


def ejecutar_prueba_fase2(nombre, texto, esperado_valido=True, usar_spacy=True):
    """Ejecuta una prueba del parser de lenguaje natural"""
    print("\n" + "=" * 70)
    print(f" PRUEBA: {nombre}")
    print("=" * 70)
    print(f"Entrada: '{texto}'\n")
    
    # Mostrar tokens generados
    tokens = tokenizar(texto)
    print("Tokens generados:")
    print("-" * 40)
    for token in tokens:
        print(f"  {token.tipo:<20} | '{token.valor}'")
    print()
    
    # Intentar parsear con nuestro parser
    print("Análisis con Parser Descendente Recursivo:")
    print("-" * 40)
    
    try:
        resultado = parsear_oracion(texto)
        print("✅ ORACIÓN ACEPTADA")
        print("\n📋 Estructura parseada:")
        mostrar_estructura(resultado)
        
        if not esperado_valido:
            print("\n⚠️  ADVERTENCIA: Se esperaba que la oración fuera inválida")
        
    except ParseError as e:
        print(f"❌ ERROR: {e.mensaje}")
        if e.posicion is not None:
            print(f"   Posición del error: {e.posicion}")
        
        if esperado_valido:
            print("\n⚠️  ADVERTENCIA: Se esperaba que la oración fuera válida")
    
    # Comparar con spaCy si está disponible
    if usar_spacy and SPACY_DISPONIBLE:
        analizar_con_spacy(texto)
    
    print("\n" + "=" * 70 + "\n")


# ============================================================
# PRUEBAS - Ejemplos Válidos
# ============================================================

print("\n" + "=" * 70)
print(" FASE 2 - PRUEBAS DEL PARSER DE LENGUAJE NATURAL")
print("=" * 70)

# Prueba 1: Oración básica SVO con determinante
ejecutar_prueba_fase2(
    "Oración básica SVO (Sujeto-Verbo-Objeto)",
    "El perro come carne.",
    esperado_valido=True
)

# Prueba 2: Oración sin determinante en sujeto
ejecutar_prueba_fase2(
    "Oración sin determinante en sujeto",
    "Perro come carne.",
    esperado_valido=True
)

# Prueba 3: Oración con adjetivo en sujeto
ejecutar_prueba_fase2(
    "Oración con adjetivo en sujeto",
    "El perro grande come carne.",
    esperado_valido=True
)

# Prueba 4: Oración con adjetivo en objeto
ejecutar_prueba_fase2(
    "Oración con adjetivo en objeto",
    "El niño lee libro nuevo.",
    esperado_valido=True
)

# Prueba 5: Oración sin objeto
ejecutar_prueba_fase2(
    "Oración sin objeto (verbo intransitivo)",
    "El niño corre.",
    esperado_valido=True
)

# Prueba 6: Oración con determinante en objeto
ejecutar_prueba_fase2(
    "Oración con determinante en objeto",
    "La niña bebe el agua.",
    esperado_valido=True
)

# Prueba 7: Oración con pregunta
ejecutar_prueba_fase2(
    "Oración interrogativa",
    "El gato duerme?",
    esperado_valido=True
)

# ============================================================
# PRUEBAS - Ejemplos Inválidos
# ============================================================

# Prueba 8: Orden incorrecto (VSO en lugar de SVO)
ejecutar_prueba_fase2(
    "Orden incorrecto (Verbo-Sujeto-Objeto)",
    "Come el perro carne.",
    esperado_valido=False,
    usar_spacy=False
)

# Prueba 9: Falta verbo
ejecutar_prueba_fase2(
    "Falta verbo",
    "El perro carne.",
    esperado_valido=False,
    usar_spacy=False
)

# Prueba 10: Palabra desconocida
ejecutar_prueba_fase2(
    "Palabra fuera del vocabulario",
    "El elefante come hierba.",
    esperado_valido=False,
    usar_spacy=True  # spaCy puede manejarlo
)

# Prueba 11: Estructura incompleta
ejecutar_prueba_fase2(
    "Estructura incompleta",
    "El perro.",
    esperado_valido=False,
    usar_spacy=False
)

# ============================================================
# COMPARACIÓN FINAL
# ============================================================

print("\n" + "=" * 70)
print(" ANÁLISIS COMPARATIVO: Parser Formal vs NLP Moderno")
print("=" * 70)

print("""
📊 RESUMEN DE DIFERENCIAS:

1. ROBUSTEZ:
   - Parser Formal: Solo acepta estructuras exactas según la gramática
   - spaCy: Maneja variaciones, palabras desconocidas, y estructuras flexibles

2. AMBIGÜEDAD:
   - Parser Formal: No puede resolver ambigüedades (requiere gramática no ambigua)
   - spaCy: Utiliza contexto y estadísticas para desambiguar

3. ESCALABILIDAD:
   - Parser Formal: Limitado al vocabulario predefinido (30 palabras)
   - spaCy: Vocabulario extenso, puede manejar miles de palabras

4. APLICABILIDAD PRÁCTICA:
   - Parser Formal: Útil para dominios específicos con reglas claras
   - spaCy: Útil para procesamiento general de lenguaje natural

5. VELOCIDAD:
   - Parser Formal: Muy rápido para oraciones válidas
   - spaCy: Más lento pero más potente

6. MANEJO DE ERRORES:
   - Parser Formal: Rechaza inmediatamente cualquier desviación
   - spaCy: Intenta interpretar incluso con errores o variaciones
""")

print("=" * 70)
print("✅ PRUEBAS FINALIZADAS")
print("=" * 70 + "\n")


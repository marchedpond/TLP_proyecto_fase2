try:
    from parser import miParser
except ImportError:
    print("Error: No se pudo encontrar el archivo 'mi_parser_c.py'.")
    print("Por favor, guarda tu parser en un archivo con ese nombre.")
    exit()

try:
    import spacy
    # Carga el modelo de español
    nlp = spacy.load("es_core_news_sm")
except ImportError:
    print("Error: La librería 'spacy' no está instalada.")
    print("Por favor, instálala ejecutando: pip install spacy")
    exit()
except IOError:
    print("Error: El modelo de español de spaCy no está instalado.")
    print("Por favor, instálalo ejecutando: python -m spacy download es_core_news_sm")
    exit()


codigo_c_valido = "int variable = 5;$"
miParser(codigo_c_valido)

print("-------------------------------------------------\n")

frase_natural_con_eof = "el perro come;$"
miParser(frase_natural_con_eof)

print("--- PRUEBA 3: Librería NLP (spaCy) con Lenguaje Natural ---")
# La misma frase, pero limpia (sin '$')
frase_natural_limpia = "el perro come"
print(f"Input: '{frase_natural_limpia}'")

# Procesar la frase con spaCy
doc = nlp(frase_natural_limpia)

print("\nResultado de spaCy (SÍ funciona y entiende la estructura):")
print(f"{'Palabra':<10} | {'Categoría (POS)':<15} | {'Dependencia (DEP)':<15}")
print("-" * 44)
for token in doc:
    print(f"{token.text:<10} | {token.pos_:<15} | {token.dep_:<15}")

print("\n[NOTA DE ANÁLISIS]: spaCy procesa la frase correctamente.")
print("Identifica cada palabra y su función gramatical,")
print("demostrando la robustez de las herramientas modernas de NLP.")
print("-------------------------------------------------\n")
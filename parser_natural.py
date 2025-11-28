# ------------------------------------------------------------
# Parser Descendente Recursivo para Español Simplificado
# Fase 2 - Proyecto TLP
# ------------------------------------------------------------

class Token:
    """Representa un token del lenguaje natural"""
    def __init__(self, tipo, valor, posicion=0):
        self.tipo = tipo
        self.valor = valor
        self.posicion = posicion
    
    def __repr__(self):
        return f"Token({self.tipo}, '{self.valor}')"


class ParseError(Exception):
    """Excepción para errores de parsing"""
    def __init__(self, mensaje, posicion=None):
        self.mensaje = mensaje
        self.posicion = posicion
        super().__init__(self.mensaje)


# Vocabulario limitado para el subconjunto de español
VOCABULARIO = {
    # Determinantes
    'el': 'DETERMINANTE',
    'la': 'DETERMINANTE',
    'los': 'DETERMINANTE',
    'las': 'DETERMINANTE',
    'un': 'DETERMINANTE',
    'una': 'DETERMINANTE',
    
    # Sustantivos
    'perro': 'SUSTANTIVO',
    'gato': 'SUSTANTIVO',
    'casa': 'SUSTANTIVO',
    'carne': 'SUSTANTIVO',
    'agua': 'SUSTANTIVO',
    'niño': 'SUSTANTIVO',
    'niña': 'SUSTANTIVO',
    'libro': 'SUSTANTIVO',
    'mesa': 'SUSTANTIVO',
    'coche': 'SUSTANTIVO',
    
    # Verbos
    'come': 'VERBO',
    'bebe': 'VERBO',
    'lee': 'VERBO',
    'corre': 'VERBO',
    'juega': 'VERBO',
    'duerme': 'VERBO',
    'camina': 'VERBO',
    'escribe': 'VERBO',
    
    # Adjetivos
    'grande': 'ADJETIVO',
    'pequeño': 'ADJETIVO',
    'rojo': 'ADJETIVO',
    'azul': 'ADJETIVO',
    'bonito': 'ADJETIVO',
    'rápido': 'ADJETIVO',
    'lento': 'ADJETIVO',
    'nuevo': 'ADJETIVO',
    'viejo': 'ADJETIVO',
    
    # Puntuación
    '.': 'PUNTO',
    '?': 'INTERROGACION',
    '!': 'EXCLAMACION',
}


def tokenizar(texto):
    """
    Tokeniza un texto en español simplificado.
    Convierte el texto a tokens según el vocabulario definido.
    """
    tokens = []
    palabras = texto.lower().split()
    
    for i, palabra in enumerate(palabras):
        # Limpiar puntuación al final
        palabra_limpia = palabra.rstrip('.,!?')
        puntuacion = palabra[len(palabra_limpia):] if len(palabra_limpia) < len(palabra) else None
        
        # Buscar en vocabulario
        if palabra_limpia in VOCABULARIO:
            tokens.append(Token(VOCABULARIO[palabra_limpia], palabra_limpia, i))
        else:
            # Si no está en el vocabulario, intentar como sustantivo genérico
            # (esto permite flexibilidad pero marca la limitación del parser)
            tokens.append(Token('DESCONOCIDO', palabra_limpia, i))
        
        # Agregar puntuación si existe
        if puntuacion:
            if puntuacion in VOCABULARIO:
                tokens.append(Token(VOCABULARIO[puntuacion], puntuacion, i))
    
    return tokens


# ============================================================
# GRAMÁTICA LIBRE DE CONTEXTO
# ============================================================
# ORACION -> SUJETO VERBO OBJETO [PUNTO]
# SUJETO -> DETERMINANTE SUSTANTIVO [ADJETIVO] | SUSTANTIVO [ADJETIVO] | ADJETIVO SUSTANTIVO
# OBJETO -> DETERMINANTE SUSTANTIVO [ADJETIVO] | SUSTANTIVO [ADJETIVO] | ADJETIVO SUSTANTIVO | vacío
# Nota: [ADJETIVO] significa adjetivo opcional después del sustantivo
# ============================================================


class ParserNatural:
    """Parser descendente recursivo para español simplificado"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.errores = []
    
    def token_actual(self):
        """Obtiene el token actual sin consumirlo"""
        if self.posicion < len(self.tokens):
            return self.tokens[self.posicion]
        return None
    
    def consumir(self, tipo_esperado=None):
        """Consume el token actual si coincide con el tipo esperado"""
        if self.posicion >= len(self.tokens):
            raise ParseError(f"Se esperaba {tipo_esperado} pero se terminó la entrada")
        
        token = self.tokens[self.posicion]
        
        if tipo_esperado and token.tipo != tipo_esperado:
            raise ParseError(
                f"Se esperaba {tipo_esperado} pero se encontró {token.tipo} ('{token.valor}')",
                token.posicion
            )
        
        self.posicion += 1
        return token
    
    def es_tipo(self, tipo):
        """Verifica si el token actual es de un tipo específico"""
        token = self.token_actual()
        return token and token.tipo == tipo
    
    def parse(self):
        """Método principal: parsea una oración completa"""
        try:
            resultado = self.parse_oracion()
            
            # Verificar que no queden tokens sin procesar
            if self.posicion < len(self.tokens):
                token_restante = self.token_actual()
                raise ParseError(
                    f"Tokens adicionales encontrados: '{token_restante.valor}' (tipo: {token_restante.tipo})",
                    token_restante.posicion
                )
            
            return resultado
        except ParseError as e:
            self.errores.append(str(e))
            raise
    
    def parse_oracion(self):
        """ORACION -> SUJETO VERBO OBJETO [PUNTO]"""
        sujeto = self.parse_sujeto()
        verbo = self.parse_verbo()
        objeto = self.parse_objeto()
        
        # Punto opcional
        if self.es_tipo('PUNTO') or self.es_tipo('INTERROGACION') or self.es_tipo('EXCLAMACION'):
            puntuacion = self.consumir()
        else:
            puntuacion = None
        
        return {
            'tipo': 'ORACION',
            'sujeto': sujeto,
            'verbo': verbo,
            'objeto': objeto,
            'puntuacion': puntuacion.valor if puntuacion else None
        }
    
    def parse_sujeto(self):
        """SUJETO -> DETERMINANTE SUSTANTIVO [ADJETIVO] | SUSTANTIVO [ADJETIVO] | ADJETIVO SUSTANTIVO"""
        adjetivo_antes = None
        adjetivo_despues = None
        
        if self.es_tipo('DETERMINANTE'):
            determinante = self.consumir('DETERMINANTE')
            sustantivo = self.consumir('SUSTANTIVO')
            # Adjetivo opcional después del sustantivo
            if self.es_tipo('ADJETIVO'):
                adjetivo_despues = self.consumir('ADJETIVO').valor
            
            resultado = {
                'tipo': 'SUJETO',
                'determinante': determinante.valor,
                'sustantivo': sustantivo.valor
            }
            if adjetivo_despues:
                resultado['adjetivo'] = adjetivo_despues
            return resultado
            
        elif self.es_tipo('ADJETIVO'):
            # Adjetivo antes del sustantivo
            adjetivo_antes = self.consumir('ADJETIVO')
            sustantivo = self.consumir('SUSTANTIVO')
            return {
                'tipo': 'SUJETO',
                'adjetivo': adjetivo_antes.valor,
                'sustantivo': sustantivo.valor
            }
        elif self.es_tipo('SUSTANTIVO'):
            sustantivo = self.consumir('SUSTANTIVO')
            # Adjetivo opcional después del sustantivo
            if self.es_tipo('ADJETIVO'):
                adjetivo_despues = self.consumir('ADJETIVO').valor
            
            resultado = {
                'tipo': 'SUJETO',
                'sustantivo': sustantivo.valor
            }
            if adjetivo_despues:
                resultado['adjetivo'] = adjetivo_despues
            return resultado
        else:
            raise ParseError(
                f"Se esperaba SUJETO (DETERMINANTE, ADJETIVO o SUSTANTIVO) pero se encontró {self.token_actual().tipo}",
                self.token_actual().posicion if self.token_actual() else None
            )
    
    def parse_verbo(self):
        """VERBO -> VERBO"""
        verbo = self.consumir('VERBO')
        return {
            'tipo': 'VERBO',
            'valor': verbo.valor
        }
    
    def parse_objeto(self):
        """OBJETO -> DETERMINANTE SUSTANTIVO [ADJETIVO] | SUSTANTIVO [ADJETIVO] | ADJETIVO SUSTANTIVO | vacío"""
        # Objeto es opcional, puede ser vacío
        if not self.token_actual():
            return None
        
        # Si el siguiente token es puntuación, el objeto es vacío
        if self.es_tipo('PUNTO') or self.es_tipo('INTERROGACION') or self.es_tipo('EXCLAMACION'):
            return None
        
        adjetivo_despues = None
        
        if self.es_tipo('DETERMINANTE'):
            determinante = self.consumir('DETERMINANTE')
            sustantivo = self.consumir('SUSTANTIVO')
            # Adjetivo opcional después del sustantivo
            if self.es_tipo('ADJETIVO'):
                adjetivo_despues = self.consumir('ADJETIVO').valor
            
            resultado = {
                'tipo': 'OBJETO',
                'determinante': determinante.valor,
                'sustantivo': sustantivo.valor
            }
            if adjetivo_despues:
                resultado['adjetivo'] = adjetivo_despues
            return resultado
            
        elif self.es_tipo('ADJETIVO'):
            # Adjetivo antes del sustantivo
            adjetivo = self.consumir('ADJETIVO')
            sustantivo = self.consumir('SUSTANTIVO')
            return {
                'tipo': 'OBJETO',
                'adjetivo': adjetivo.valor,
                'sustantivo': sustantivo.valor
            }
        elif self.es_tipo('SUSTANTIVO'):
            sustantivo = self.consumir('SUSTANTIVO')
            # Adjetivo opcional después del sustantivo
            if self.es_tipo('ADJETIVO'):
                adjetivo_despues = self.consumir('ADJETIVO').valor
            
            resultado = {
                'tipo': 'OBJETO',
                'sustantivo': sustantivo.valor
            }
            if adjetivo_despues:
                resultado['adjetivo'] = adjetivo_despues
            return resultado
        else:
            # Objeto vacío es válido
            return None


def parsear_oracion(texto):
    """
    Función principal para parsear una oración en español simplificado.
    
    Args:
        texto: String con la oración a parsear
    
    Returns:
        dict: Estructura parseada de la oración
    """
    tokens = tokenizar(texto)
    parser = ParserNatural(tokens)
    return parser.parse()


def mostrar_estructura(estructura, nivel=0):
    """Muestra la estructura parseada de forma legible"""
    indent = "  " * nivel
    
    if isinstance(estructura, dict):
        if estructura.get('tipo') == 'ORACION':
            print(f"{indent}ORACION:")
            print(f"{indent}  Sujeto: {estructura['sujeto']}")
            print(f"{indent}  Verbo: {estructura['verbo']['valor']}")
            if estructura['objeto']:
                print(f"{indent}  Objeto: {estructura['objeto']}")
            else:
                print(f"{indent}  Objeto: (vacío)")
            if estructura['puntuacion']:
                print(f"{indent}  Puntuación: {estructura['puntuacion']}")
        else:
            for key, value in estructura.items():
                if isinstance(value, dict):
                    print(f"{indent}{key}:")
                    mostrar_estructura(value, nivel + 1)
                else:
                    print(f"{indent}{key}: {value}")


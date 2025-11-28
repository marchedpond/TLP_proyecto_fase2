# ------------------------------------------------------------
# Lexer para C
# ------------------------------------------------------------
import ply.lex as lex

S=0
S2=1
T=2
T2=3
F=4

# List of token names.   This is always required
tokens = (
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'LPAREN',
   'RPAREN',
   
   
   'if',              
   'for',             
   'keyword',         
   'identificador',
   'inicioBloque',
   'finBloque',
   'finInstruccion',
   'asignacion',
   'comentario',
   'comentario_bloque',
   'cadena',
   'coma',
   'eof',
   'int',
   'float',
   'string'
   #'vacia'
)

# Regular expression rules for simple tokens
t_PLUS     = r'\+'
t_MINUS    = r'-'
t_TIMES    = r'\*'
t_DIVIDE   = r'/' 
t_LPAREN   = r'\('
t_RPAREN   = r'\)'
t_inicioBloque = r'\{'
t_finBloque = r'\}'
t_finInstruccion = r'\;'
t_asignacion = r'\='
t_coma= r'\,'
t_eof= r'\$'


#t_vacia= r'\'

def t_int(t):
    r'(int)'
    return t

def t_float(t):
    r'(float)'
    return t


# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'



def t_if(t):
    r'if'
    return t

def t_for(t):
    r'for'
    return t

def t_keyword(t):
    r'(char)|(return)|(else)|(do)|(while)|(void)' 
    return t

def t_identificador(t):
    r'([a-z]|[A-Z]|_)([a-z]|[A-Z]|\d|_)*'
    
    return t



def t_cadena(t):
    r'\".*\"'
    return t

def t_comentario(t):
    r'\/\/.*'
    return t

def t_comentario_bloque(t):
    r'\/\*(.|\n)*\*\/'
   

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)    
    return t


tabla = [
    ['S', 'int',            ['DCL']],
    ['S', 'float',          ['DCL']],
    ['S', 'string',         ['DCL']],
    ['S', 'identificador',  ['INST']],
    
    ['S', 'if',             ['IF']],   
    ['S', 'for',            ['FOR']], 
    
    ['DCL', 'int',          ['TIPO', 'identificador', 'D']],
    ['DCL', 'float',        ['TIPO', 'identificador', 'D']],
    ['DCL', 'string',       ['TIPO', 'identificador', 'D']],
    ['TIPO', 'int',         ['int']],
    ['TIPO', 'float',       ['float']],
    ['TIPO', 'string',      ['string']],
    ['D', 'coma',           ['coma', 'identificador', 'D']],
    ['D', 'asignacion',     ['asignacion', 'E', 'finInstruccion']],
    ['D', 'finInstruccion', ['finInstruccion']],
    
    ['INST', 'identificador', ['identificador', 'asignacion', 'E', 'finInstruccion']],
    ['INST0', 'identificador', ['identificador', 'asignacion', 'E']],
    
    ['IF', 'if', ['if', 'LPAREN', 'E', 'RPAREN', 'INST']],
    
    ['FOR', 'for',  
        ['for', 'LPAREN', 'INST', 'E', 'finInstruccion', 'INST0', 'RPAREN', 'INST']
    ],
    
    ['E', 'identificador', ['T', "E'"]],
    ['E', 'NUMBER',        ['T', "E'"]],
    ['E', 'LPAREN',        ['T', "E'"]],
    ["E'", 'PLUS',         ['PLUS', 'T', "E'"]],
    ["E'", 'MINUS',        ['MINUS', 'T', "E'"]],
    ["E'", 'RPAREN',       ['vacia']],
    ["E'", 'finInstruccion',['vacia']],
    ['T', 'identificador', ['F', "T'"]],
    ['T', 'NUMBER',        ['F', "T'"]],
    ['T', 'LPAREN',        ['F', "T'"]],
    ["T'", 'TIMES',        ['TIMES', 'F', "T'"]],
    ["T'", 'DIVIDE',       ['DIVIDE', 'F', "T'"]],
    ["T'", 'PLUS',         ['vacia']],
    ["T'", 'MINUS',        ['vacia']],
    ["T'", 'RPAREN',       ['vacia']],
    ["T'", 'finInstruccion',['vacia']],
    ['F', 'identificador', ['identificador']],
    ['F', 'NUMBER',        ['NUMBER']],
    ['F', 'LPAREN',        ['LPAREN', 'E', 'RPAREN']]
]


stack = ['eof', 'S']


# Build the lexer
lexer = lex.lex()

def miParser(cadena):
    global stack
    stack = ['eof', 'S']  # Reiniciar pila por cada parseo

    lexer.input(cadena)
    
    tok = lexer.token()
    if not tok:
        print("Error: Cadena de entrada vacia o solo caracteres ignorados.")
        return 0

    x = stack[-1]
    while True:
        if x == tok.type and x == 'eof':
            print("Cadena reconocida exitosamente")
            return 1 
        else:
            if x == tok.type and x != 'eof':
                stack.pop()
                x = stack[-1]
                tok = lexer.token()
                
                if not tok:
                    print("Error: Se termino la entrada inesperadamente.")
                    print("Stack restante:", stack)
                    return 0
            
            if x in tokens and x != tok.type:
                print(f"Error: Se esperaba '{x}' pero se encontro '{tok.type}' ('{tok.value}')")
                return 0
            
            if x not in tokens: # no terminal
                celda = buscar_en_tabla(x, tok.type)                                  
                if celda is None:
                    print(f"Error: NO se esperaba '{tok.type}' ('{tok.value}')")
                    print("En posicion:", tok.lexpos)
                    print(f"El No-Terminal '{x}' no tiene regla para '{tok.type}'")
                    return 0
                else:
                    stack.pop()
                    agregar_pila(celda)
                    x = stack[-1]             

        #if not tok:
            #break
        #print(tok)
        #print(tok.type, tok.value, tok.lineno, tok.lexpos)

def buscar_en_tabla(no_terminal, terminal):
    for i in range(len(tabla)):
        if( tabla[i][0] == no_terminal and tabla[i][1] == terminal):
            return tabla[i][2]
    return None 
def agregar_pila(produccion):
    for elemento in reversed(produccion):
        if elemento != 'vacia': 
            stack.append(elemento)        
        
        

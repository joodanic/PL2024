import ply.lex as lex

# Lista de tokens
tokens = [
    # Palavras reservadas
    'PROGRAM', 'BEGIN', 'END', 'VAR', 'INTEGER', 'IF', 'THEN', 'ELSE',
    'WHILE', 'DO', 'FOR', 'TO', 'DOWNTO','WRITELN', 'WRITE','READLN', 'BOOLEAN', 'BOOLEAN_LITERAL','STRING_TYPE',
    'FUNCTION', 'MOD',
    # Outros tokens
    'IDENTIFIER', 'NUMBER', 'STRING',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'ASSIGN', 'EQ',
    'LT', 'GT', 'LE', 'GE', 'NE',
    'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET',
    'SEMICOLON', 'COLON', 'COMMA', 'DOT', 'RANGE', 'AND', 'OR', 'NOT','ARRAY','OF','LENGTH'
]

# Expressões regulares para tokens simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_ASSIGN = r':='
t_EQ = r'='
t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_NE = r'<>'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'
t_COLON = r':'
t_COMMA = r','
t_DOT = r'\.'
t_RANGE = r'\.\.'

# Ignorar espaços, tabulações e quebras de linha
t_ignore = " \t"

# Palavras reservadas definidas como funções
def t_PROGRAM(t):
    r'program'
    return t

def t_BEGIN(t):
    r'begin'
    return t

def t_END(t):
    r'end'
    return t

def t_VAR(t):
    r'var'
    return t

def t_INTEGER(t):
    r'[Ii]nteger'
    return t

def t_DIVIDE(t):
    r'div'
    return t

def t_IF(t):
    r'if'
    return t

def t_THEN(t):
    r'then'
    return t

def t_ELSE(t):
    r'else'
    return t

def t_WHILE(t):
    r'while'
    return t

def t_DO(t):
    r'\bdo\b'
    return t

def t_FOR(t):
    r'for'
    return t

def t_TO(t):
    r'\bto\b'
    return t

def t_DOWNTO(t):
    r'downto'
    return t

def t_LENGTH(t):
    r'[Ll]ength'
    return t

def t_WRITE(t):
    r'\b[Ww]rite\b'
    return t

def t_WRITELN(t):
    r'[Ww]rite[Ll]n'
    return t

def t_READLN(t):
    r'[Rr]ead[Ll]n'
    return t

def t_BOOLEAN(t):
    r'boolean'
    return t

def t_ARRAY(t):
    r'array'
    return t

def t_OF(t):
    r'of'
    return t

def t_BOOLEAN_LITERAL(t):
    r'\b([Tt]rue|[Ff]alse)\b'
    t.value = 1 if t.value.lower() == 'true' else 0  # Converte para integer: true -> 1, false -> 0
    return t

def t_STRING_TYPE(t):
    r'string'
    return t

def t_FUNCTION(t):
    r'function'
    return t

def t_MOD(t):
    r'mod'
    return t

def t_AND(t):
    r'and'
    return t

def t_OR(t):
    r'or'
    return t

def t_NOT(t):
    r'not'
    return t

# Identificadores
def t_IDENTIFIER(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    return t

# Números inteiros
def t_NUMBER(t):
    r'-?\d+'
    t.value = int(t.value)  # Converte para inteiro
    return t

# Strings entre aspas simples
def t_STRING(t):
    r'"[^"]*"|\'[^\']*\''
    t.value = t.value[1:-1]  # Remove aspas
    return t

# Comentários (ignorar)
def t_COMMENT(t):
    r'\{.*?\}'
    t.lexer.lineno += t.value.count('\n')  # Conta quebras de linha nos comentários
    pass  # Ignora comentários

# Tratamento de erros
def t_error(t):
    print(f"Caractere ilegal: '{t.value[0]}' na linha {t.lineno}")
    t.lexer.skip(1)

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

# Construir o lexer
lexer = lex.lex()

# Código de teste (programa "Olá, Mundo!")
code = """
program BinarioParaInteiro;
var
bin: string;
i, valor, potencia: integer;
begin
writeln('Introduza uma string binária:');
readln(bin);
valor := 0;
potencia := 1;
for i := length(bin) downto 1 do
begin
if bin[i] = '1' then
valor := valor + potencia;
potencia := potencia * 2;
end;
writeln('O valor inteiro correspondente é: ', valor);
end.
"""

# Alimentar o lexer com o código
lexer.input(code)

# Iterar sobre os tokens gerados
print("Tokens gerados para o programa 'Olá, Mundo!':")
while True:
    tok = lexer.token()
    if not tok:
        break
    print(f"Token: {tok.type}, Valor: {tok.value}, Linha: {tok.lineno}")
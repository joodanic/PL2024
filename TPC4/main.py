import ply.lex as lex

tokens = (
    'SELECT',
    'FROM',
    'WHERE',
    'NAMES',
    'NUMBER',
    'COMMA',
    'SINAL',
)

t_COMMA = r','
t_SINAL    = r'>= | <= | > | < | ='

reserved = {
    'Select': 'SELECT',
    'From': 'FROM',
    'Where': 'WHERE',
}

def t_NAMES(t):
    r'[a-zA-Z_]+'
    t.type = reserved.get(t.value, 'NAMES')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = ' \t'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

data = 'Select id, nome, salario From empregados Where salario >= 820'
lexer.input(data)

for tok in lexer:
    print(tok)
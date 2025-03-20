import ply.lex as lex

tokens = ('NUM', 'MUL', 'SUB', 'ADD', 'DIV')

t_NUM = r'\d+'
t_MUL = r'\*'
t_SUB = r'\-'
t_ADD = r'\+'
t_DIV = r'/'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = '\t '

def t_error(t):
    print('Carácter desconhecido: ', t.value[0], 'Linha: ', t.lexer.lineno)
    t.lexer.skip(1)

lexer = lex.lex()

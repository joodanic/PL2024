import ply.lex as lex

tokens=('COMMENT','SELECT','ATALHO','FRASE','WHERE','LIMIT','ABRIRP','FECHARP','PONTO','ID','VAR','NUMBER')

def t_SELECT(t):  r'(?i:\bselect\b)'                               ; return t

def t_WHERE(t):   r'(?i:\bwhere\b)'                                ; return t

def t_LIMIT(t):   r'(?i:\blimit\b)'                                ; return t 

def t_ATALHO(t):  r'\ba\b'                                         ; return t

def t_PONTO(t):   r'\.'                                            ; return t

def t_ABRIRP(t):  r'\{'                                            ; return t

def t_FECHARP(t): r'\}'                                            ; return t

def t_VAR(t):     r'\?[a-zA-Z_]\w*'                                ; return t

def t_FRASE(t):   r'"[^"]*"(?:@[a-z]{2,})?'                        ; return t

def t_ID(t):      r'[a-zA-Z]+:[a-zA-Z]\w*'                         ; return t

def t_NUMBER(t):  r'\d+'                    ; t.value=int(t.value) ; return t

def t_COMMENT(t): r'\#.*' ; return t

def t_newline(t): r'\n+'                                ; t.lexer.lineno = len(t.value)

def t_error(t): print(f"Carácter ilegal {t.value[0]}")  ; t.lexer.skip(1)

t_ignore = ' \t\n'

lexer = lex.lex()

data = '''
# DBPedia: obras de Chuck Berry
select ?nome ?desc where {
?s a dbo:MusicalArtist.
?s foaf:name "Chuck Berry"@en .
?w dbo:artist ?s.
?w foaf:name ?nome.
?w dbo:abstract ?desc
} LIMIT 1000
'''

lexer.input(data)

while tok := lexer.token(): 
    print(tok)

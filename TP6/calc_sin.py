# ----------------------
# Gramática (sem precedência de operadores):
# Expr    → NUM Expr'
# Expr'   → ('+' | '-' | '*' | '/') NUM Expr' | ε
#
# ----------------------

from calc_analex import lexer

prox_simb = None

def parserError(simb):
    print("Erro sintático, token inesperado: ", simb)

def rec_term(simb):
    global prox_simb
    if prox_simb and prox_simb.type == simb:
        prox_simb = lexer.token()
    else:
        parserError(prox_simb)

def rec_NUM():
    global prox_simb
    if prox_simb is None:
        parserError(prox_simb)
        return 0
    if prox_simb.type == 'NUM':
        valor = int(prox_simb.value)
        rec_term('NUM')
        return valor
    else:
        parserError(prox_simb)
        return 0

def rec_Expr():
    global prox_simb
    valor = rec_NUM()
    while prox_simb and prox_simb.type in ('ADD', 'SUB', 'MUL', 'DIV'):
        if prox_simb.type == 'ADD':
            rec_term('ADD')
            valor += rec_NUM()
        elif prox_simb.type == 'SUB':
            rec_term('SUB')
            valor -= rec_NUM()
        elif prox_simb.type == 'MUL':
            rec_term('MUL')
            valor *= rec_NUM()
        elif prox_simb.type == 'DIV':
            rec_term('DIV')
            valor //= rec_NUM()
    return valor

def rec_Parser(data):
    global prox_simb
    lexer.input(data)
    prox_simb = lexer.token()
    if prox_simb is None:
        print("Erro: expressão vazia ou inválida.")
        return
    resultado = rec_Expr()
    print("Resultado da expressão:", resultado)

rec_Parser("2 + 3 * 5")
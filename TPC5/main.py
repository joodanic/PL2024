import sys
import ply.lex as lex

tokens = (
    'LISTAR',
    'MOEDA',
    'SELECIONAR',
    'SAIR',
)

t_LISTAR = r'\bLISTAR\b'

def t_SELECIONAR(t):
    r'\bSELECIONAR\b\s+[A-Z0-9]+'
    return t

def t_MOEDA(t):
    r'\bMOEDA\b\s+(2e|1e|50c|20c|10c|5c|2c|1c)'
    return t

def t_SAIR(t):
    r'\bSAIR\b'
    return t

t_ignore = ' \t\n'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

saldo_Total = 0
stock = [
    {"cod": "A1", "nome": "Sumo", "quant": 8, "preco": 100},
    {"cod": "A2", "nome": "Agua", "quant": 5, "preco": 60},
    {"cod": "A3", "nome": "Bolo", "quant": 10, "preco": 100},
]

def process_token(token):
    global saldo_Total
    if token.type == 'LISTAR':
        listar_stock()
    elif token.type == 'MOEDA':
        value = token.value.split()[1]
        if value.endswith('e'):
            saldo_Total += int(value[:-1]) * 100
        else:
            saldo_Total += int(value[:-1])
        print(f"Saldo = {saldo_Total / 100:.2f}€")
    elif token.type == 'SELECIONAR':
        code = token.value.split()[1]
        comprar_produto(code)
    elif token.type == 'SAIR':
        print("Até à próxima")

def listar_stock():
    print("Código | Nome | Quantidade | Preço")
    for produto in stock:
        print(f"{produto['cod']} | {produto['nome']} | {produto['quant']} | {produto['preco'] / 100:.2f}€")

def comprar_produto(codigo):
    global saldo_Total
    for produto in stock:
        if produto['cod'] == codigo:
            if produto['quant'] == 0:
                print(f"Produto esgotado: '{produto['nome']}'")
                return
            elif produto['preco'] <= saldo_Total:
                produto['quant'] -= 1
                saldo_Total -= produto['preco']
                print(f"Pode retirar o produto dispensado '{produto['nome']}'")
                print(f"Saldo = {saldo_Total / 100:.2f}€")
                return
            else:
                print(f"Saldo insuficiente. Saldo = {saldo_Total / 100:.2f}€, Necessário = {produto['preco'] / 100:.2f}€")

def process_input():
    print("Vending machine is ready. Input commands:")
    for linha in sys.stdin:
        linha = linha.strip()
        if not linha:
            continue
        lexer.input(linha)
        token = lexer.token()
        if not token:
            print(f"INVALIDO: {linha}")
            continue
        if token.type == 'SAIR':
            print("Até à próxima")
            break
        process_token(token)

process_input()
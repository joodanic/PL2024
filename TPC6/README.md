## TPC6

# Resumo:
Construir uma gramática independente de contexto LL(1) para interpretar comandos de uma linguagem de programação simples.

Comandos como o seguinte:
- `? a`
- `b = a * 2 / (27 - 3)`
- `! a + b`
- `c = a * b / ( a / b )`



# Gramática Independente de Contexto LL(1)

## Terminais:

- **Números**: `num`
- **Variáveis**: `var`
- **Operadores Aritméticos**: `+ | - | * | /`
- **Parênteses**: `( | )`
- **Igualdade**: `=`
- **Leitura**: `?`
- **Impressão**: `!`

## Não-Terminais:

- **Programa**: `P`
- **Atribuição**: `A`
- **Expressão**: `E`
- **Termo**: `T`
- **Fator**: `F`

## Regras de Produção:

- p1. `P -> A P | ε`
- p2. `A -> var = E | ? var | ! E`
- p3. `E -> T | + T E | - T E`
- p4. `T -> F | * F T | / F T`
- p5.  `F -> ( E ) | num | var`

## Lookahead:

- **P**: `var | ? | !`
- **A**: `var | ? | !`
- **E**: `+ | - | ( | num | var`
- **T**: `* | / | ( | num | var`
- **F**: `( | num | var`

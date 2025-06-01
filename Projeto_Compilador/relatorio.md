# Relatório do Projeto: Compilador para Pascal Standard

### Elementos

- **Nome**: João Carvalho  **Número**: A94015
- **Nome**:  **Número**:

## Introdução

Este relatório descreve a implementação de um compilador para a linguagem *Pascal Standard*, desenvolvido no âmbito da disciplina de Processamento de Linguagens 2025. O objetivo principal foi construir um compilador capaz de analisar, interpretar e traduzir código Pascal para código executável numa máquina virtual (EWVM) fornecida pelos professores. O compilador abrange as etapas de análise léxica, análise sintática, análise semântica e geração de código, com testes realizados para validar a sua funcionalidade.

A implementação foi realizada utilizando as ferramentas `ply.lex` para a análise léxica e `ply.yacc` para a análise sintática, seguindo as especificações do projeto. O compilador suporta as principais construções da linguagem Pascal, incluindo declarações de variáveis, expressões aritméticas, comandos de controlo de fluxo (`if`, `while`, `for`), funções e manipulação de *arrays* e *strings*. Este relatório detalha a gramática utilizada, as verificações semânticas implementadas, os resultados obtidos e possíveis melhorias.

---

## Gramática da Linguagem

A gramática foi definida para suportar programas *Pascal Standard*, incluindo declarações de variáveis, controlo de fluxo, entrada/saída e funções. Abaixo são apresentados os **terminais**, **não-terminais** e a **gramática completa**.

### Terminais

Os terminais correspondem aos *tokens* definidos no analisador léxico (`PascalLexer.py`). São eles:

- **Palavras reservadas**: `PROGRAM`, `BEGIN`, `END`, `VAR`, `INTEGER`, `IF`, `THEN`, `ELSE`, `WHILE`, `DO`, `FOR`, `TO`, `DOWNTO`, `WRITELN`, `WRITE`, `READLN`, `BOOLEAN`, `BOOLEAN_LITERAL`, `STRING_TYPE`, `FUNCTION`, `MOD`, `AND`, `OR`, `NOT`, `ARRAY`, `OF`, `LENGTH`.
- **Outros tokens**: `IDENTIFIER`, `NUMBER`, `STRING`, `PLUS`, `MINUS`, `TIMES`, `DIVIDE`, `ASSIGN`, `EQ`, `LT`, `GT`, `LE`, `GE`, `NE`, `LPAREN`, `RPAREN`, `LBRACKET`, `RBRACKET`, `SEMICOLON`, `COLON`, `COMMA`, `DOT`, `RANGE`.

Os terminais foram definidos com expressões regulares para reconhecer palavras-chave, identificadores, números, *strings*, operadores e símbolos especiais. Comentários `{...}` são ignorados, e quebras de linha são contabilizadas para rastreamento de erros.

### Não-Terminais

Os não-terminais representam as construções sintáticas da linguagem Pascal, organizadas de forma hierárquica. São eles:

- `program`: Estrutura principal do programa.
- `block`: Bloco de código (`begin ... end`).
- `var_decls`: Lista de declarações de variáveis.
- `var_decl_list`: Lista de declarações individuais.
- `var_decl`: Declaração de variáveis com tipo.
- `id_list`: Lista de identificadores.
- `type`: Tipo de dados (simples ou *array*).
- `array_type`: Tipo *array* com índices e tipo base.
- `simple_type`: Tipos simples (`integer`, `boolean`, `string`).
- `function_decls`: Lista de declarações de funções.
- `function_decl`: Declaração de uma função.
- `param_list`: Lista de parâmetros de uma função.
- `param`: Parâmetro de uma função.
- `stmt_list`: Lista de comandos.
- `stmt`: Comando (atribuição, condicional, ciclo, etc.).
- `assign_stmt`: Comando de atribuição.
- `var_ref`: Referência a variável (simples ou acesso a *array*).
- `if_stmt`: Comando condicional (`if`).
- `while_stmt`: Ciclo `while`.
- `for_stmt`: Ciclo `for`.
- `write_stmt`: Comando `write`.
- `writeln_stmt`: Comando `writeln`.
- `readln_stmt`: Comando `readln`.
- `block_stmt`: Bloco de comandos.
- `func_call`: Chamada de função.
- `expr_list`: Lista de expressões.
- `logic_expr`: Expressão lógica.
- `rel_expr`: Expressão relacional.
- `expr`: Expressão aritmética.
- `term`: Termo aritmético.
- `factor`: Fator (literal, variável, etc.).
- `primary`: Elemento primário (número, *string*, etc.).
- `empty`: Produção vazia.

### Gramática Completa

A gramática foi implementada no ficheiro `PascalPly.py` usando `ply.yacc`. Abaixo está a gramática completa, conforme definida:

```bnf
program : PROGRAM IDENTIFIER SEMICOLON function_decls block DOT

block : var_decls BEGIN stmt_list END

var_decls : VAR var_decl_list
          | empty

var_decl_list : var_decl_list var_decl
              | var_decl

var_decl : id_list COLON type SEMICOLON

id_list : id_list COMMA IDENTIFIER
        | IDENTIFIER

type : INTEGER
     | BOOLEAN
     | STRING_TYPE
     | array_type

array_type : ARRAY LBRACKET NUMBER RANGE NUMBER RBRACKET OF simple_type

simple_type : INTEGER
            | BOOLEAN
            | STRING_TYPE

function_decls : function_decls function_decl
               | empty

function_decl : FUNCTION IDENTIFIER LPAREN param_list RPAREN SEMICOLON block SEMICOLON
              | FUNCTION IDENTIFIER LPAREN param_list RPAREN COLON type SEMICOLON block SEMICOLON

param_list : param_list SEMICOLON param
           | param
           | empty

param : id_list COLON type

stmt_list : stmt_list SEMICOLON stmt
          | stmt_list SEMICOLON
          | stmt
          | empty

stmt : assign_stmt
     | if_stmt
     | while_stmt
     | for_stmt
     | writeln_stmt
     | readln_stmt
     | write_stmt
     | block_stmt
     | func_call

assign_stmt : var_ref ASSIGN logic_expr

var_ref : IDENTIFIER
        | IDENTIFIER LBRACKET logic_expr RBRACKET

if_stmt : IF logic_expr THEN stmt
        | IF logic_expr THEN stmt ELSE stmt

while_stmt : WHILE logic_expr DO stmt

for_stmt : FOR IDENTIFIER ASSIGN logic_expr TO logic_expr DO stmt
         | FOR IDENTIFIER ASSIGN logic_expr DOWNTO logic_expr DO stmt

write_stmt : WRITE LPAREN expr_list RPAREN

writeln_stmt : WRITELN LPAREN expr_list RPAREN
             | WRITELN

readln_stmt : READLN LPAREN var_ref RPAREN

block_stmt : BEGIN stmt_list END

func_call : IDENTIFIER LPAREN expr_list RPAREN

expr_list : expr_list COMMA logic_expr
          | logic_expr
          | empty

logic_expr : logic_expr AND rel_expr
           | logic_expr OR rel_expr
           | NOT rel_expr
           | rel_expr

rel_expr : rel_expr EQ expr
         | rel_expr NE expr
         | rel_expr LT expr
         | rel_expr GT expr
         | rel_expr LE expr
         | rel_expr GE expr
         | expr

expr : expr PLUS term
     | expr MINUS term
     | term

term : term TIMES factor
     | term DIVIDE factor
     | term MOD factor
     | factor

factor : LENGTH LPAREN expr RPAREN
       | primary

primary : NUMBER
        | STRING
        | BOOLEAN_LITERAL
        | var_ref
        | func_call
        | LPAREN logic_expr RPAREN

empty :

```

Esta gramática cobre as principais construções do *Pascal Standard*, incluindo suporte para *arrays*, funções, expressões lógicas e aritméticas, e comandos de entrada/saída.

## Análise Léxica

A análise léxica foi implementada no ficheiro `PascalLexer.py` utilizando `ply.lex`. O analisador léxico converte o código-fonte Pascal numa sequência de *tokens*, reconhecendo:

- **Palavras reservadas**: Como `program`, `begin`, `end`, entre outras, definidas como funções `t_NOME` para cada palavra.
- **Identificadores**: Sequências de letras e dígitos começando por uma letra (`[a-zA-Z][a-zA-Z0-9]*`).
- **Números**: Inteiros representados por `-?\d+`, convertidos para valores inteiros.
- **Strings**: Sequências entre aspas simples ou duplas (`"[^"]*"|'[^\']*\'`), com as aspas removidas.
- **Operadores e símbolos**: Como `+`, `-`, `:=`, `=`, `<`, etc., definidos com expressões regulares.
- **Comentários**: Ignorados usando a regra `\{.*?\}`.
- **Mudanças de linha**: Contabilizadas para saber onde occoreram os erros.

Erros léxicos, como caracteres inválidos, são reportados com a linha correspondente. O *lexer* foi testado com os diversos programas de exemplo gerando *tokens* corretamente.

## Análise Sintática

A análise sintática foi implementada no ficheiro `PascalPly.py` usando `ply.yacc`. O *parser* constrói uma **Árvore de Sintaxe Abstrata (AST)** a partir dos *tokens* gerados pelo *lexer*. A classe `Node` é usada para representar os nós da AST, com atributos `type`, `children` e `value`.

O *parser* segue a gramática apresentada, validando a estrutura do código Pascal. Cada produção cria um nó na AST, que é posteriormente usado na análise semântica e geração de código. Erros de sintaxe, como *tokens* inesperados ou EOF inesperado, são reportados com a linha correspondente.

A AST gerada para o programa exemplo `BinarioParaInteiro` foi impressa, confirmando a correta construção da estrutura do programa, incluindo declarações de variáveis, comandos de entrada/saída e ciclos.

## Análise Semântica

A análise semântica foi implementada na classe `CodeGenerator`, no método `get_expr_type` e em verificações específicas durante a geração de código. As principais verificações semânticas incluem:

### Verificação de Tipos

- Para expressões aritméticas (`+`, `-`, `*`, `div`, `mod`), verifica-se que os operandos são do tipo `integer`.
- Para expressões relacionais (`>`, `<`, `=`, `<>`, `<=`, `>=`), verifica-se que os operandos são do mesmo tipo (`integer` ou `string`).
- Para expressões lógicas (`and`, `or`), verifica-se que os operandos são do tipo `boolean`.
- Para a função `length`, verifica-se que o operando é do tipo `string`.
- Para atribuições, verifica-se a compatibilidade entre o tipo da variável e o da expressão. Para variáveis *boolean*, permite-se literais inteiros `0` ou `1`.

### Declaração de Variáveis

- Verifica-se se variáveis (globais ou locais) estão declaradas antes de serem usadas.
- Para *arrays*, verifica-se se a variável é um *array* e se o índice é do tipo `integer`. Índices literais são validados contra os limites do *array*.

### Funções

- Verifica-se se funções chamadas estão declaradas.
- Valida-se o número e tipos dos argumentos nas chamadas de funções, comparando com os parâmetros declarados.
- Para funções com tipo de retorno explícito, verifica-se a compatibilidade do tipo na atribuição ao nome da função.

### Controlo de Fluxo

- Para comandos `if` e `while`, verifica-se que a condição é do tipo `boolean` ou literal inteiro `0`/`1`.
- Para ciclos `for`, verifica-se que a variável de controlo e as expressões de início e fim são do tipo `integer`.

### Acessos a Arrays e Strings

- Para acessos a *arrays* (`var[i]`), valida-se o tipo do índice e os limites (se o índice for literal).
- Para *strings*, suporta-se acesso a caracteres via `var[i]` e a função `length`.

### Grafo de Chamadas

- Um grafo de chamadas é construído para detetar ciclos em chamadas de funções, usando ordenação topológica.

Estas verificações garantem a coerência semântica do código, prevenindo erros como tipos incompatíveis, variáveis não declaradas ou chamadas de funções inválidas. A análise é realizada durante a geração de código, levantando exceções quando erros são detetados.

## Geração de Código

A geração de código foi implementada na classe `CodeGenerator`, que traduz a AST para instruções da máquina virtual fornecida. As principais características incluem:

### Gestão de Variáveis

- Variáveis globais são mapeadas para posições na pilha global (`var_map`) e inicializadas com `PUSHI 0` ou `PUSHS ""` (para *strings*).
- Variáveis locais são mapeadas para *offsets* relativos ao `fp` (*frame pointer*) da função atual.
- *Arrays* são alocados com `ALLOCN`, e acessos são gerados com `PADD` e `LOAD`/`STORE`.

### Controlo de Fluxo

- Para `if`, usa `JZ` (*jump if zero*) para saltar para o fim do bloco `then` ou `else`.
- Para `while`, usa labels para o início e fim do ciclo, com `JZ` para sair.
- Para `for`, inicializa a variável de controlo, usa `INFEQ` ou `SUPEQ` (dependendo de `to` ou `downto`) e atualiza a variável com `ADD` ou `SUB`.

### Entrada/Saída

- Comandos `write` e `writeln` geram `WRITEI` (inteiros), `WRITES` (*strings*) ou `WRITELN` (nova linha).
- `readln` gera `READ` para *strings*, com conversão via `ATOI` para inteiros.

### Funções

- Cada função tem um label e usa `PUSHFP`, `CALL` e `RETURN` para gerir a stack de chamadas.
- Parâmetros e variáveis locais são alocados na stack com *offsets* negativos.

### Expressões

- Expressões aritméticas, relacionais e lógicas geram instruções como `ADD`, `SUB`, `MUL`, `DIV`, `MOD`, `SUP`, `INF`, `EQUAL`, `AND`, `OR`, etc.
- A função `length` gera `STRLEN` para *strings*.

O código gerado para o programa exemplo `BinarioParaInteiro` foi impresso, demonstrando a tradução correta para instruções da VM.

## Testes

Os testes foram implementados no ficheiro `testes.py`, que processa programas Pascal na pasta `testes`. Foram fornecidos 11 programas válidos e 5 programas com erros:

### Programas Válidos

1. **Olá, Mundo!**: Testa saída básica com `writeln`.
2. **Maior de 3**: Testa entrada (`readln`), condicionais (`if`) e variáveis.
3. **Fatorial**: Testa ciclos `for` e operações aritméticas.
4. **Número Primo**: Testa ciclos `while`, condições e *booleanos*.
5. **Soma de Array**: Testa *arrays* e ciclos `for`.
6. **Binário para Decimal**: Testa *strings*, função `length` e ciclos `for`.
7. **Binário para Decimal (com função)**: Testa declaração e chamada de funções.
8. **Funcionamento do not**: Testa o `not` em diversos casos 
9. **Inteiros negativos**: Testa operações aritmeticas com `integer` negativos 
10. **Conta Palavras**: Diversifica ainda mais os testes que ja tinhamos, testando alguns operadores que ainda não tinham sido usados
11. **Conta Palavras com func**: O mesmo do caso de cima, mas usando uma função

### Programas com Erros

- Incluem erros léxicos, sintáticos e semânticos, como variáveis não declaradas, tipos incompatíveis e sintaxe inválida.

Os resultados foram guardados na pasta `results`, com ficheiros `.txt` contendo o código gerado ou mensagens de erro. Todos os programas válidos foram processados corretamente, enquanto os erros foram detetados e reportados adequadamente.

## Melhorias Possíveis

Embora o compilador atenda aos requisitos do projeto, algumas melhorias podem ser consideradas:

### Suporte a Procedures

- A implementação atual suporta apenas `function`, mas não `procedure`. Adicionar suporte a *procedures* envolveria modificar a gramática para incluir a produção `procedure_decl` e ajustar a geração de código para lidar com subprogramas sem retorno.

### Análise Semântica Mais Robusta

- **Controlo de Inicialização**: Poderia ser adicionada uma verificação para garantir que variáveis são inicializadas antes de serem usadas.
- **Tipos Compostos**: Suportar tipos mais complexos, como registros (`record`) ou apontadores, para estar em maior conformidade com *Pascal Standard*.
- **Constantes**: Adicionar suporte para declarações de constantes (`const`) e verificar o seu uso correto.

### Otimização de Código

- Implementar ainda mais otimizações, por exemplo, reduzindo o número de instruções geradas, como combinar operações redundantes.

### Melhor Gestão de Erros

- Fornecer mensagens de erro mais detalhadas, incluindo sugestões de correção.
- Implementar recuperação de erros no *parser* para continuar a análise após um erro sintático.

### Suporte a Mais Construções

- Adicionar suporte para `case`, `repeat-until` e outras construções do *Pascal Standard*.

## Conclusão

O compilador desenvolvido cumpre os objetivos do projeto, implementando análise léxica, sintática, semântica e geração de código para a linguagem *Pascal Standard*. A gramática definida cobre as principais construções da linguagem, e as verificações semânticas garantem a coerência do código. Os testes realizados validaram a funcionalidade para programas válidos e a deteção de erros.

Como trabalho futuro poderiamos aplicar as melhorias que referimos acima, fazendo com que o projeto se tornasse mais completo ainda.O projeto proporcionou uma compreensão profunda dos conceitos de compiladores, desde a análise léxica até a geração de código, e foi uma oportunidade valiosa para aplicar ferramentas como `ply.lex` e `ply.yacc`.

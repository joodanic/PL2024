# TPC4 - Analisador Léxico

# João Carvalho, A94015  

## Resumo
Foi feito um analisador léxico com o objetivo de processar consultas SPARQL simples.

Para a realização desta tarefa, o programa:

Reconhece palavras-chave como SELECT, WHERE e LIMIT de forma case-insensitive;

Identifica variáveis SPARQL (?var), literais ("texto"@en) e identificadores (dbo:MusicalArtist);

Captura e ignora comentários iniciados por #;

Trata corretamente a pontuação, como . e {};

## Resultado

O analisador lexico pode ser encontrado em [GitHub](https://github.com/joodanic/PL2024/blob/main/TP4/bd_analex.py).
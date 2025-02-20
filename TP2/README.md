# TPC2 - Análise de um dataset de obras musicais  

# João Carvalho, A94015  

## Resumo  

Para este trabalho, foi-nos proposta a análise de um dataset contendo informações sobre obras musicais. O objetivo era processar os dados sem recorrer ao módulo CSV do Python e gerar resultados específicos a partir das informações extraídas.  

Para a realização desta tarefa, o programa deveria:  

1. Ler o dataset de entrada contendo informações sobre as obras musicais;  
2. Corrigir erros no ficheiro utilizando expressões regulares para normalizar os dados;  
3. Extrair e ordenar alfabeticamente a lista de compositores musicais; 
4. Determinar a distribuição das obras por período, contabilizando quantas obras existem em cada período;  
5. Criar um dicionário que associa cada período a uma lista ordenada alfabeticamente com os títulos das obras pertencentes a esse período.  

A implementação foi feita utilizando expressões regulares para a limpeza dos dados, bem como manipulação de listas e dicionários para a organização e contagem das informações.  

## Resultado  

O script de limpeza do CSV pode ser encontrado em [GitHub](https://github.com/joodanic/PL2024/blob/main/TP2/file.py).  
A resolução das queries pode ser encontrada em [GitHub](https://github.com/joodanic/PL2024/blob/main/TP2/tpc2.py).
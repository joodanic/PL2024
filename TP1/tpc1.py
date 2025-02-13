def rec(l):
    res = 0
    estado = 1
    i = 0
    while i<len(l):
        valor = 0
        palavra = ""
        if l[i] in "0123456789":
            while i < len(l) and l[i] in "0123456789":
                valor = valor*10+int(l[i])
                i = i+1
            if estado:
                res= res + valor
        elif l[i] in "OoNnFf":
            while i < len(l) and l[i] in "OoNnFf":
                palavra+=l[i]
                i = i+1
            temp = palavra.lower()
            if temp == "on":
                estado = 1
            elif temp == "off":
                estado = 0
        elif l[i] == "=":
            print(res)
            i=i+1
        else:
            i=i+1
    print(res)

rec("Hoje, 7 de Fevereiro de 2025, o professor de Processamento de Linguagens deu-nos este trabalho para fazer.= E deu-nos 7= dias para o fazer... Cada trabalho destes vale 0.25 valores da nota final!")
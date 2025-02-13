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

rec("Dia 8 de Fevereiro de 2025 off = vou fazer 18 anos, on e vou realizar 3 projetos")
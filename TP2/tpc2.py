import re

def queries():
    compositores=[]
    obrasP = {}
    titulosP = {}
    file = open('obrasCorrigidas.csv','r')
    for line in file:
        if "nome" in line:
            continue
        nome,desc,anoCriacao,periodo,compositor,duracao,_id = re.split(r';',line)
        compositores.append(compositor)

        if periodo in obrasP:
            value = obrasP[periodo]
            value+=1
            obrasP[periodo] = value
        else:
            obrasP[periodo] = 1
        
        if periodo in titulosP:
            lista = titulosP[periodo]
            lista.append(nome)
            lista.sort()
            titulosP[periodo] = lista
        else:
            lista=[]
            lista.append(nome)
            titulosP[periodo] = lista
    file.close()
    compositores.sort()
    print("COMPOSTIORES:")
    print(compositores)
    print("\n")
    print("NUMERO OBRAS POR PERIODO:")
    print(obrasP)
    print("\n")
    print("OBRAS POR PERIODO:")
    print(titulosP)

queries()
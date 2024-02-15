import sys

modalidades = set()
grupo_idades={}
idades = []
total=0
aptos=0
inaptos=0
idade_minima = 200
idade_maxima = 0

file = open("emd.csv","r")
file.readline()

for line in file:
    _,_,_,_,_,idade,_,_,modalidade,_,_,_,resultado = line.split(",")

    total+=1
    modalidades.add(modalidade)

    new_resultado,_ = resultado.split("\n")
    if(new_resultado=="true"):
        aptos+=1
    elif(new_resultado=="false"):
        inaptos+=1
    
    new_idade = int(idade)
    idades.append(new_idade)

    if(new_idade<=idade_minima):
        idade_minima=new_idade
    
    if(new_idade>=idade_maxima):
        idade_maxima=new_idade
    

file.close()

sum=0

for age in range(idade_minima, idade_maxima+1, 5):
    if age+4 < idade_maxima:
        chave = f"[{age},{age+4}]"
        grupo_idades[chave]=0
        for idade in idades:
            if idade>=age and idade<=age+4:
                grupo_idades[chave]+=1
    else:
        chave = f"[{age},{idade_maxima}]"
        grupo_idades[chave]=0
        for idade in idades:
            if idade>=age and idade<idade_maxima+1:
                grupo_idades[chave]+=1
    
    sum=1

    



modalidades = sorted(modalidades)
print(f"modalidades:{modalidades}")

percentagem_aptos= (aptos/total)*100
percentagem_inaptos=(inaptos/total)*100

print(f"aptos:{percentagem_aptos}%")
print(f"inaptos:{percentagem_inaptos}%")

for grupo_idades, quantos in grupo_idades.items():
    print(f"{grupo_idades}: {quantos} atletas")

print(total)

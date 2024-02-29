import re

text = 'ola123 = esoffta 24 tudOn 12 ='
print(text)

encontrados = re.findall(r'\d+|[Oo][Nn]|[Oo][Ff]{2}|=', text)

somador=0
estado = 1

for elem in encontrados:
    if elem.isdigit() and estado == 1:
        somador += int(elem)
    elif elem.lower() == 'on':
        estado = 1
    elif elem.lower() == 'off':
        estado = 0
    elif elem == '=':
        print(f"soma: {somador}")

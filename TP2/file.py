import re

def corrige():
    file = open('obras.csv','r')
    text = file.read()
    file.close()
    corrigido = re.sub(r'\n\s+'," ", text)
    corrigido2 = re.sub(r'(".*?);(.*?")',r'\1,\2',corrigido)
    newfile = open('obrasCorrigidas.csv','w')
    newfile.write(corrigido2)
    newfile.close()

corrige()
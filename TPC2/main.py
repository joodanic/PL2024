import re

file_name = 'README.md'

with open(file_name, 'r') as file:
    markdown_content = file.read()

#cabecalhos
markdown_content = re.sub(r'### (.*)', r'<h3>\1</h3>', markdown_content)
markdown_content = re.sub(r'## (.*)', r'<h2>\1</h2>', markdown_content)
markdown_content = re.sub(r'# (.*)', r'<h1>\1</h1>', markdown_content)

#bold
markdown_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', markdown_content)

#italico
markdown_content = re.sub(r'\*(.*?)\*', r'<i>\1</i>', markdown_content)

#listas numeradas
markdown_content = re.sub(r'^(\d+\.)\s+(.*)', r'<li>\2</li>', markdown_content, flags=re.MULTILINE)

lista = re.findall(r'<li>.*</li>', markdown_content)
if lista:
    markdown_content = markdown_content.replace(lista[0], '<ol>\n'+ lista[0])
    markdown_content = markdown_content.replace(lista[-1],lista[-1] + '\n</ol>')


#links
markdown_content = re.sub(r'\[(.*)\]\((.*)\)', r'<a href="\2">\1</a>', markdown_content)

#imagens
markdown_content = re.sub(r'!\[(.*)\]\((.*)\)', r'<img src="\2" alt="\1"/>', markdown_content)

print(markdown_content)
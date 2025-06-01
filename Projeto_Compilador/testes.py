import os
from PascalLexer import lexer
from PascalPly import parser, CodeGenerator

# caminhos de entrada e saída
TESTS_DIR = "testes"
RESULTS_DIR = "results"

# Criar pasta de resultados, se não existir
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

def process_file(file_path, output_path):
    try:
        # Ler o conteúdo do ficheiro
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Configurar o lexer
        lexer.input(code)
        
        # parsing do código
        ast = parser.parse(code, lexer=lexer)
        if not ast:
            return "Erro: Falha ao gerar AST (sintaxe inválida ou incompleta)"

        # Gerar código para a VM
        generator = CodeGenerator()
        generator.generate(ast)
        generated_code = generator.get_code()
        
        # Retornar o código gerado
        return generated_code

    except Exception as e:
        # Capturar e retornar qualquer erro
        return f"Erro: {str(e)}"

def run_tests():
    # Verificar se a pasta de testes existe
    if not os.path.exists(TESTS_DIR):
        print(f"Erro: Pasta '{TESTS_DIR}' não encontrada")
        return

    # Iterar sobre os ficheiros na pasta de testes
    for filename in os.listdir(TESTS_DIR):
        if filename.endswith(".pas"):  # Processar apenas ficheiros .pas
            input_path = os.path.join(TESTS_DIR, filename)
            output_filename = os.path.splitext(filename)[0] + ".txt"
            output_path = os.path.join(RESULTS_DIR, output_filename)

            print(f"Processando ficheiro: {filename}")
            result = process_file(input_path, output_path)

            # Guardar o resultado no ficheiro de saída
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"Resultado guardado em: {output_path}")

if __name__ == "__main__":
    run_tests()
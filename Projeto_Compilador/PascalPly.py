from PascalLexer import tokens, lexer
import ply.yacc as yacc

# --- Classe Node cria a AST ---
class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children if children is not None else []
        self.value = value

    def __str__(self, level=0):
        indent = "  " * level
        result = f"{indent}Node({self.type}, value={self.value}, children={len(self.children)})\n"
        for child in self.children:
            if isinstance(child, list):
                for subchild in child:
                    result += subchild.__str__(level + 1)
            else:
                result += child.__str__(level + 1)
        return result

class CodeGenerator:
    def __init__(self):
        self.code = []
        self.label_count = 0
        self.var_map = {}  # Variáveis globais
        self.variables = []  # Lista de variáveis globais
        self.array_map = {}  # Arrays (tamanho, índice inicial)
        self.string_map = {}  # Strings globais
        self.local_var_map = {}  # Variáveis locais por função
        self.local_string_map = {}  # Strings locais por função
        self.current_func = None  # Função atual sendo processada
        self.local_offsets = {}  # Offsets para variáveis locais por função
        self.for_count = 0
        self.if_count = 0
        self.while_count = 0
        self.call_graph = {}  # Grafo de chamadas: {func: [called_funcs]}
        self.functions = {}  # Mapa de nós de funções: {func_name: Node}
        self.var_types = {}  # Tipos de variáveis globais: {var_name: type}
        self.local_var_types = {}  # Tipos de variáveis locais por função: {func_name: {var_name: type}}
        self.func_return_types = {}  # Tipos de retorno das funções: {func_name: type}

    def new_label(self):
        self.label_count += 1
        return f"label{self.label_count}"

    def new_for_labels(self):
        self.for_count += 1
        return f"forstart{self.for_count}", f"forend{self.for_count}"

    def new_if_label(self):
        self.if_count += 1
        return f"endif{self.if_count}"

    def new_while_labels(self):
        self.while_count += 1
        return f"whilestart{self.while_count}", f"whileend{self.while_count}"

    def emit(self, instruction):
        self.code.append(instruction)

    def get_expr_type(self, node):
        """Infere o tipo de uma expressão."""
        if node.type == 'Literal':
            if isinstance(node.value, int):
                return 'integer'
            elif isinstance(node.value, str):
                return 'string'
            elif isinstance(node.value, bool):
                return 'boolean'
        elif node.type == 'Var':
            var_name = node.value
            if self.current_func and var_name == self.current_func:
                return self.func_return_types.get(self.current_func, 'integer')  # Padrão para integer se não especificado
            if self.current_func and var_name in self.local_var_types.get(self.current_func, {}):
                return self.local_var_types[self.current_func][var_name].lower()  # transforar para minúsculas
            elif var_name in self.var_types:
                return self.var_types[var_name].lower()  # transformar para minúsculas
            else:
                raise Exception(f"Erro semântico: Variável '{var_name}' não declarada")
        elif node.type == 'Binary':
            left_type = self.get_expr_type(node.children[0]).lower()  # transformar para minúsculas
            right_type = self.get_expr_type(node.children[1]).lower()  # transformar para minúsculas
            op = node.value
            if op in ['+', '-', '*', 'div', 'mod']:
                if left_type == 'integer' and right_type == 'integer':
                    return 'integer'
                else:
                    raise Exception(f"Erro semântico: Operação '{op}' requer operandos do tipo integer, encontrado {left_type} e {right_type}")
            elif op in ['>', '<', '=', '<>', '<=', '>=']:
                if left_type == right_type and left_type in ['integer', 'string']:
                    return 'boolean'
                else:
                    raise Exception(f"Erro semântico: Operação '{op}' requer operandos do mesmo tipo (integer ou string), encontrado {left_type} e {right_type}")
            elif op in ['and', 'or']:
                if left_type == 'boolean' and right_type == 'boolean':
                    return 'boolean'
                else:
                    raise Exception(f"Erro semântico: Operação '{op}' requer operandos do tipo boolean, encontrado {left_type} e {right_type}")
        elif node.type == 'Unary':
            operand_type = self.get_expr_type(node.children[0]).lower()
            if node.value == 'not':
                if operand_type == 'boolean':
                    return 'boolean'
                elif operand_type == 'integer':
                    if node.children[0].type == 'Literal' and node.children[0].value in [0, 1]:
                        return 'boolean'
                    else:
                        raise Exception(f"Erro semântico: 'not' requer operando boolean ou literal 0/1, encontrado integer não-literal")
                else:
                    raise Exception(f"Erro semântico: 'not' requer operando boolean, encontrado {operand_type}")
        elif node.type == 'ArrayAccess':
            array_var = node.children[0].value
            if self.current_func and array_var in self.local_var_types.get(self.current_func, {}):
                return self.local_var_types[self.current_func][array_var].lower()  # transformar para minúsculas
            elif array_var in self.var_types:
                return self.var_types[array_var].lower()  # transformar para minúsculas
            else:
                raise Exception(f"Erro semântico: Array '{array_var}' não declarado")
        elif node.type == 'FuncCall':
            func_name = node.value
            if func_name not in self.functions:
                raise Exception(f"Erro semântico: Função '{func_name}' não declarada")
            return self.func_return_types.get(func_name, 'integer').lower()  # transformar para minúsculas
        elif node.type == 'Length':
            expr_type = self.get_expr_type(node.children[0]).lower()  # transformar para minúsculas
            if expr_type != 'string':
                raise Exception(f"Erro semântico: 'length' requer operando do tipo string, encontrado {expr_type}")
            return 'integer'  # length retorna sempre integer
        return None

    def topological_sort(self):
        """Realiza ordenação topológica das funções com base no grafo de chamadas."""
        def dfs(func, visited, stack, path):
            visited.add(func)
            path.add(func)
            for called_func in self.call_graph.get(func, []):
                if called_func not in visited:
                    dfs(called_func, visited, stack, path)
                elif called_func in path:
                    raise Exception(f"Erro semântico: Ciclo detectado no grafo de chamadas envolvendo '{called_func}'")
            path.remove(func)
            if func in self.functions:
                stack.append(func)

        visited = set()
        stack = []
        path = set()
        for func in self.call_graph:
            if func not in visited:
                dfs(func, visited, stack, path)
        return stack[::-1]

    def collect_functions_and_calls(self, node):
        if not node:
            return
        if node.type == 'Function':
            func_name = node.value['name']
            self.functions[func_name] = node
            self.call_graph.setdefault(func_name, set())
            self.local_var_types[func_name] = {}
            self.func_return_types[func_name] = node.value['return'] or 'integer'  # Padrão para integer
        elif node.type == 'FuncCall':
            func_name = node.value
            if self.current_func:
                self.call_graph.setdefault(self.current_func, set()).add(func_name)
                self.call_graph.setdefault(func_name, set())
        for child in node.children:
            if isinstance(child, Node):
                self.collect_functions_and_calls(child)
            elif isinstance(child, list):
                for subchild in child:
                    if isinstance(subchild, Node):
                        self.collect_functions_and_calls(subchild)


    def check_array_access(self, array_var, index_expr):
        index_type = self.get_expr_type(index_expr)
        if index_type != 'integer':
            raise Exception(f"Erro semântico: Índice de array deve ser integer, encontrado {index_type}")
        if array_var not in self.array_map and not (self.current_func and array_var in self.local_string_map.get(self.current_func, {})) and array_var not in self.string_map:
            raise Exception(f"Erro semântico: '{array_var}' não é um array nem string")
        # Static checks para os indices
        if index_expr.type == 'Literal' and isinstance(index_expr.value, int):
            index_value = index_expr.value
            if array_var in self.array_map:
                low = self.array_map[array_var][1]
                high = self.array_map[array_var][1] + self.array_map[array_var][0] - 1
                if index_value < low:
                    raise Exception(f"Erro semântico: Índice {index_value} menor que o limite inferior {low} do array '{array_var}'")
                if index_value > high:
                    raise Exception(f"Erro semântico: Índice {index_value} maior que o limite superior {high} do array '{array_var}'")
            
    def generate(self, node):
        if not node:
            print("Erro: Nó da AST é None")
            return

        if node.type == 'Program':
            self.collect_functions_and_calls(node)
            for child in node.children:
                if child.type == 'Block':
                    for subchild in child.children:
                        if subchild.type == 'VarDecls':
                            self.generate(subchild)
            for var_name in self.variables:
                if var_name not in self.array_map and var_name not in self.string_map:
                    self.emit('PUSHI 0')
                elif var_name in self.string_map:
                    self.emit(f'PUSHS ""')
            for array_name, (size, _) in self.array_map.items():
                self.emit(f'PUSHI {size}')
                self.emit('ALLOCN')
                self.emit(f'STOREG {self.var_map[array_name]}')
            self.emit('START')
            for child in node.children:
                if child.type == 'Block':
                    self.generate(child)
            self.emit('STOP')
            for func_name in self.topological_sort():
                self.generate(self.functions[func_name])

        elif node.type == 'Function':
            func_name = node.value['name']
            self.current_func = func_name
            self.local_var_map[func_name] = {}
            self.local_string_map[func_name] = {}
            self.local_offsets[func_name] = 0
            params = node.children[0]
            body = node.children[1]
            self.emit(f"{func_name}:")
            self.emit('PUSHFP')

            for param in params.children:
                param_type = param.value
                for id_node in param.children:
                    var_name = id_node.value
                    self.local_var_map[func_name][var_name] = -1 - self.local_offsets[func_name]
                    self.local_var_types[func_name][var_name] = param_type
                    if param_type == 'string':
                        self.local_string_map[func_name][var_name] = self.local_var_map[func_name][var_name]
                    self.local_offsets[func_name] += 1
                    if param_type == 'string':
                        self.emit('PUSHS ""')
                    else:
                        self.emit('PUSHI 0')

            for child in body.children:
                if child.type == 'VarDecls':
                    for decl in child.children:
                        decl_type = decl.value
                        for id_node in decl.children:
                            var_name = id_node.value
                            self.local_var_map[func_name][var_name] = -1 - self.local_offsets[func_name]
                            self.local_var_types[func_name][var_name] = decl_type
                            if decl_type == 'string':
                                self.local_string_map[func_name][var_name] = self.local_var_map[func_name][var_name]
                            self.local_offsets[func_name] += 1
                            if decl_type == 'string':
                                self.emit('PUSHS ""')
                            else:
                                self.emit('PUSHI 0')

            self.generate(body)
            self.emit('RETURN')
            self.current_func = None

        elif node.type == 'ParamList':
            pass

        elif node.type == 'Block':
            for child in node.children:
                if child.type != 'VarDecls':
                    self.generate(child)

        elif node.type == 'VarDecls':
            for decl in node.children:
                self.generate(decl)

        elif node.type == 'VarDecl':
            for id_node in node.children:
                if id_node.type == 'Id':
                    var_name = id_node.value
                    if self.current_func:
                        self.local_var_map[self.current_func][var_name] = -1 - self.local_offsets[self.current_func]
                        self.local_var_types[self.current_func][var_name] = node.value  # registar tipo
                        if node.value == 'string':
                            self.local_string_map[self.current_func][var_name] = self.local_var_map[self.current_func][var_name]
                        self.local_offsets[self.current_func] += 1
                    else:
                        self.var_map[var_name] = len(self.variables)
                        self.var_types[var_name] = node.value  # registar tipo global
                        self.variables.append(var_name)
                    if isinstance(node.value, Node) and node.value.type == 'ArrayType':
                        size = node.value.value['high'] - node.value.value['low'] + 1
                        low = node.value.value['low']
                        self.array_map[var_name] = (size, low)
                        self.var_types[var_name] = node.value.value['type']  # Tipo base do array
                    elif node.value == 'string':
                        self.string_map[var_name] = len(self.string_map)

        elif node.type == 'StmtList':
            for stmt in node.children:
                self.generate(stmt)

        elif node.type == 'Write':
            for expr in node.children:
                self.generate(expr)
                expr_type = self.get_expr_type(expr)
                if expr_type == 'string':
                    self.emit('WRITES')
                else:
                    self.emit('WRITEI')

        elif node.type == 'Writeln':
            for expr in node.children:
                self.generate(expr)
                expr_type = self.get_expr_type(expr)
                if expr_type == 'string':
                    self.emit('WRITES')
                else:
                    self.emit('WRITEI')
            self.emit('WRITELN')

        elif node.type == 'Readln':
            for var_ref in node.children:
                self.emit('READ')
                var_type = self.get_expr_type(var_ref)
                if var_type == 'string':
                    if var_ref.type == 'Var':
                        if self.current_func and var_ref.value in self.local_string_map.get(self.current_func, {}):
                            self.emit(f'STOREL {self.local_string_map[self.current_func][var_ref.value]}')
                        else:
                            self.emit(f'STOREG {self.var_map[var_ref.value]}')
                else:
                    self.emit('ATOI')
                    if var_ref.type == 'ArrayAccess':
                        array_var = var_ref.children[0].value
                        index_expr = var_ref.children[1]
                        self.check_array_access(array_var, index_expr)
                        if array_var not in self.array_map:
                            raise Exception(f"Erro semântico: '{array_var}' não é um array")
                        self.emit(f'PUSHG {self.var_map[array_var]}')
                        self.generate(index_expr)
                        low = self.array_map[array_var][1]
                        self.emit(f'PUSHI {low}')
                        self.emit('SUB')
                        self.emit('PADD')
                        self.emit('SWAP')
                        self.emit('STORE 0')
                    else:
                        var_name = var_ref.value
                        if self.current_func and var_name in self.local_var_map.get(self.current_func, {}):
                            self.emit(f'STOREL {self.local_var_map[self.current_func][var_name]}')
                        else:
                            self.emit(f'STOREG {self.var_map[var_name]}')

        elif node.type == 'FuncCall':
            func_name = node.value
            # Verificação semântica: função deve estar declarada
            if func_name not in self.functions:
                raise Exception(f"Erro semântico: Função '{func_name}' não declarada")
            # Verificação semântica: número e tipos de argumentos
            args = node.children
            param_list = self.functions[func_name].children[0].children  # Lista de parâmetros da função
            if len(args) != len(param_list):
                raise Exception(f"Erro semântico: Função '{func_name}' espera {len(param_list)} argumentos, mas {len(args)} foram fornecidos")
            for i, (arg, param) in enumerate(zip(args, param_list)):
                arg_type = self.get_expr_type(arg)
                param_type = param.value
                if arg_type != param_type:
                    raise Exception(f"Erro semântico: Argumento {i+1} da função '{func_name}' deve ser {param_type}, mas é {arg_type}")
            for arg in args:
                self.generate(arg)
            self.emit(f'PUSHA {func_name}')
            self.emit('CALL')

        elif node.type == 'If':
            condition = node.children[0]
            then_stmt = node.children[1]
            else_stmt = node.children[2] if len(node.children) > 2 else None
            cond_type = self.get_expr_type(condition)
            if cond_type == 'integer':
                if condition.type == 'Literal' and condition.value in [0, 1]:
                    pass
                else:
                    raise Exception(f"Erro semântico: Condição do 'if' de tipo integer só permite literais 0 ou 1, encontrado {cond_type}")
            elif cond_type != 'boolean':
                raise Exception(f"Erro semântico: Condição do 'if' deve ser boolean, encontrado {cond_type}")
            self.generate(condition)
            end_label = self.new_if_label()
            self.emit(f'JZ {end_label}')
            self.generate(then_stmt)
            if else_stmt:
                final_label = self.new_label()
                self.emit(f'JUMP {final_label}')
                self.emit(f'{end_label}:')
                self.generate(else_stmt)
                self.emit(f'{final_label}:')
            else:
                self.emit(f'{end_label}:')

        elif node.type == 'For':
            var = node.children[0].value
            start_expr = node.children[1]
            end_expr = node.children[2]
            body = node.children[3]
            start_type = self.get_expr_type(start_expr)
            end_type = self.get_expr_type(end_expr)
            var_type = self.local_var_types[self.current_func][var] if self.current_func and var in self.local_var_types.get(self.current_func, {}) else self.var_types.get(var)
            if start_type != 'integer' or end_type != 'integer' or var_type != 'integer':
                raise Exception(f"Erro semântico: 'for' requer variável e expressões de tipo integer, encontrado {var_type}, {start_type}, {end_type}")
            self.generate(start_expr)
            if self.current_func and var in self.local_var_map.get(self.current_func, {}):
                self.emit(f'STOREL {self.local_var_map[self.current_func][var]}')
            else:
                self.emit(f'STOREG {self.var_map[var]}')
            loop_start, loop_end = self.new_for_labels()
            self.emit(f'{loop_start}:')
            if self.current_func and var in self.local_var_map.get(self.current_func, {}):
                self.emit(f'PUSHFP')
                self.emit(f'LOAD {self.local_var_map[self.current_func][var]}')
            else:
                self.emit(f'PUSHG {self.var_map[var]}')
            self.generate(end_expr)
            self.emit('SUPEQ' if node.value == 'downto' else 'INFEQ')
            self.emit(f'JZ {loop_end}')
            self.generate(body)
            if self.current_func and var in self.local_var_map.get(self.current_func, {}):
                self.emit(f'PUSHFP')
                self.emit(f'LOAD {self.local_var_map[self.current_func][var]}')
            else:
                self.emit(f'PUSHG {self.var_map[var]}')
            self.emit('PUSHI 1')
            self.emit('SUB' if node.value == 'downto' else 'ADD')
            if self.current_func and var in self.local_var_map.get(self.current_func, {}):
                self.emit(f'STOREL {self.local_var_map[self.current_func][var]}')
            else:
                self.emit(f'STOREG {self.var_map[var]}')
            self.emit(f'JUMP {loop_start}')
            self.emit(f'{loop_end}:')

        elif node.type == 'While':
            condition = node.children[0]
            body = node.children[1]
            cond_type = self.get_expr_type(condition)
            if cond_type == 'integer':
                if condition.type == 'Literal' and condition.value in [0, 1]:
                    pass
                else:
                    raise Exception(f"Erro semântico: Condição do 'while' de tipo integer só permite literais 0 ou 1, encontrado {cond_type}")
            elif cond_type != 'boolean':
                raise Exception(f"Erro semântico: Condição do 'while' deve ser boolean, encontrado {cond_type}")
            loop_start, loop_end = self.new_while_labels()
            self.emit(f'{loop_start}:')
            self.generate(condition)
            self.emit(f'JZ {loop_end}')
            self.generate(body)
            self.emit(f'JUMP {loop_start}')
            self.emit(f'{loop_end}:')

        elif node.type == 'Assign':
            var_ref = node.children[0]
            expr = node.children[1]
            var_type = self.get_expr_type(var_ref)
            expr_type = self.get_expr_type(expr)
            if self.current_func and var_ref.type == 'Var' and var_ref.value == self.current_func:
                expected_return_type = self.func_return_types.get(self.current_func, 'integer')
                if expr_type != expected_return_type:
                    raise Exception(f"Erro semântico: Retorno da função '{self.current_func}' deve ser {expected_return_type}, mas é {expr_type}")
            elif var_type == 'boolean' and expr_type == 'integer':
                if expr.type == 'Literal' and expr.value in [0, 1]:
                    pass  # permitir 0 ou 1 como boolean
                else:
                    raise Exception(f"Erro semântico: Atribuição a variável boolean só permite literais 0 ou 1, encontrado {expr_type}")
            elif var_type != expr_type:
                raise Exception(f"Erro semântico: Atribuição de {expr_type} a variável de tipo {var_type}")
            self.generate(expr)
            if var_ref.type == 'ArrayAccess':
                array_var = var_ref.children[0].value
                index_expr = var_ref.children[1]
                self.check_array_access(array_var, index_expr)
                if array_var not in self.array_map:
                    raise Exception(f"Erro semântico: '{array_var}' não é um array")
                self.emit(f'PUSHG {self.var_map[array_var]}')
                self.generate(index_expr)
                low = self.array_map[array_var][1]
                self.emit(f'PUSHI {low}')
                self.emit('SUB')
                self.emit('PADD')
                self.emit('SWAP')
                self.emit('STORE 0')
            else:
                var_name = var_ref.value
                if self.current_func and var_name == self.current_func:
                    pass  # Valor já está na pilha
                elif self.current_func and var_name in self.local_var_map.get(self.current_func, {}):
                    self.emit(f'STOREL {self.local_var_map[self.current_func][var_name]}')
                else:
                    self.emit(f'STOREG {self.var_map[var_name]}')

            
        elif node.type == 'ArrayAccess':
            array_var = node.children[0].value
            index_expr = node.children[1]
            self.check_array_access(array_var, index_expr)

            if self.current_func and array_var in self.local_string_map.get(self.current_func, {}):
                self.generate(index_expr)
                self.emit('PUSHI 1')
                self.emit('SUB')
                self.emit(f'PUSHFP')
                self.emit(f'LOAD {self.local_string_map[self.current_func][array_var]}')
                self.emit('SWAP')
                self.emit('CHARAT')
            elif array_var in self.string_map:
                self.generate(index_expr)
                self.emit('PUSHI 1')
                self.emit('SUB')
                self.emit(f'PUSHG {self.var_map[array_var]}')
                self.emit('SWAP')
                self.emit('CHARAT')
            else:
                self.emit(f'PUSHG {self.var_map[array_var]}')
                self.generate(index_expr)
                low = self.array_map[array_var][1]
                self.emit(f'PUSHI {low}')
                self.emit('SUB')
                self.emit('PADD')
                self.emit('LOAD 0')

        elif node.type == 'Length':
            expr = node.children[0]
            expr_type = self.get_expr_type(expr)
            if expr_type != 'string':
                raise Exception(f"Erro semântico: 'length' requer operando do tipo string, encontrado {expr_type}")
            self.generate(expr)
            self.emit('STRLEN')

        elif node.type == 'Binary':
            left = node.children[0]
            right = node.children[1]
            # Validar tipos antes de gerar código
            result_type = self.get_expr_type(node)  # Chama get_expr_type para validar
            self.generate(left)
            self.generate(right)
            if node.value == '>':
                self.emit('SUP')
            elif node.value == '=':
                self.emit('EQUAL')
            elif node.value == '<>':
                self.emit('EQUAL')
                self.emit('NOT')
            elif node.value == '*':
                self.emit('MUL')
            elif node.value == '-':
                self.emit('SUB')
            elif node.value == '+':
                self.emit('ADD')
            elif node.value == 'div':
                self.emit('DIV')
            elif node.value == 'mod':
                self.emit('MOD')
            elif node.value == '<':
                self.emit('INF')
            elif node.value == '<=':
                self.emit('INFEQ')
            elif node.value == '>=':
                self.emit('SUPEQ')
            elif node.value == 'and':
                self.emit('AND')
            elif node.value == 'or':
                self.emit('OR')
        
        elif node.type == 'Unary' and node.value == 'not':
            self.generate(node.children[0])
            self.emit('NOT')

        elif node.type == 'Var':
            var_name = node.value
            # Verificar se variável está declarada
            if not (self.current_func and var_name in self.local_var_types.get(self.current_func, {})) and var_name not in self.var_types:
                raise Exception(f"Erro semântico: Variável '{var_name}' não declarada")
            if self.current_func and var_name in self.local_var_map.get(self.current_func, {}):
                self.emit(f'PUSHFP')
                self.emit(f'LOAD {self.local_var_map[self.current_func][var_name]}')
            else:
                self.emit(f'PUSHG {self.var_map[var_name]}')

        elif node.type == 'Literal':
            if isinstance(node.value, str):
                if len(node.value) == 1:
                    self.emit(f'PUSHI {ord(node.value)}')
                else:
                    self.emit(f'PUSHS "{node.value}"')
            elif isinstance(node.value, int):
                self.emit(f'PUSHI {node.value}')
            elif isinstance(node.value, bool):
                self.emit(f'PUSHI {1 if node.value else 0}')

        elif node.type == 'Id':
            pass

        else:
            for child in node.children:
                if isinstance(child, Node):
                    self.generate(child)
                elif isinstance(child, list):
                    for subchild in child:
                        if isinstance(subchild, Node):
                            self.generate(subchild)

    def get_code(self):
        return '\n'.join(self.code)

# --- Regras da gramática ---
def p_program(p):
    '''program : PROGRAM IDENTIFIER SEMICOLON function_decls block DOT'''
    p[0] = Node('Program', children=[p[4], p[5]], value=p[2])
    print("Program ->")


# ver isto com mais atencao logo '''block : var_decls BEGIN stmt_list SEMICOLON END''' regra original
def p_block(p):
    '''block : var_decls BEGIN stmt_list END'''
    p[0] = Node('Block', children=[p[1], Node('StmtList', children=p[3])])

def p_var_decls(p):
    '''var_decls : VAR var_decl_list
                 | empty'''
    p[0] = Node('VarDecls', children=p[2] if len(p) == 3 else [])
    print(f"{p[0]}")

def p_var_decl_list(p):
    '''var_decl_list : var_decl_list var_decl
                     | var_decl'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_var_decl(p):
    '''var_decl : id_list COLON type SEMICOLON'''
    p[0] = Node('VarDecl', children=p[1], value=p[3])

def p_id_list(p):
    '''id_list : id_list COMMA IDENTIFIER
               | IDENTIFIER'''
    if len(p) == 4:
        p[0] = p[1] + [Node('Id', value=p[3])]
    else:
        p[0] = [Node('Id', value=p[1])]

def p_type(p):
    '''type : INTEGER
            | BOOLEAN
            | STRING_TYPE
            | array_type'''
    p[0] = p[1]

def p_array_type(p):
    '''array_type : ARRAY LBRACKET NUMBER RANGE NUMBER RBRACKET OF simple_type'''
    p[0] = Node('ArrayType', value={'low': p[3], 'high': p[5], 'type': p[8]})

def p_simple_type(p):
    '''simple_type : INTEGER
                   | BOOLEAN
                   | STRING_TYPE'''
    p[0] = p[1]

def p_function_decls(p):
    '''function_decls : function_decls function_decl
                      | empty'''
    if len(p) == 3:
        p[0] = Node('FunctionDecls', children=p[1].children + [p[2]])
    else:
        p[0] = Node('FunctionDecls', children=[])

def p_function_decl(p):
    '''function_decl : FUNCTION IDENTIFIER LPAREN param_list RPAREN SEMICOLON block SEMICOLON
                     | FUNCTION IDENTIFIER LPAREN param_list RPAREN COLON type SEMICOLON block SEMICOLON'''
    if len(p) == 9:  # Sem tipo de retorno explícito
        p[0] = Node('Function', children=[Node('ParamList', children=p[4]), p[7]], value={'name': p[2], 'return': None})
    else:  # Com tipo de retorno
        p[0] = Node('Function', children=[Node('ParamList', children=p[4]), p[9]], value={'name': p[2], 'return': p[7]})

def p_param_list(p):
    '''param_list : param_list SEMICOLON param
                  | param
                  | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_param(p):
    '''param : id_list COLON type'''
    p[0] = Node('Param', children=p[1], value=p[3])

def p_stmt_list(p):
    '''stmt_list : stmt_list SEMICOLON stmt
                 | stmt_list SEMICOLON
                 | stmt
                 | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 3:
        p[0] = p[1]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []
    print(f"stmt_list: {p[0]}")

def p_stmt(p):
    '''stmt : assign_stmt
            | if_stmt
            | while_stmt
            | for_stmt
            | writeln_stmt
            | readln_stmt
            | write_stmt
            | block_stmt
            | func_call'''
    p[0] = p[1]

def p_assign_stmt(p):
    '''assign_stmt : var_ref ASSIGN logic_expr'''
    p[0] = Node('Assign', children=[p[1], p[3]])

def p_var_ref(p):
    '''var_ref : IDENTIFIER
               | IDENTIFIER LBRACKET logic_expr RBRACKET'''
    if len(p) == 2:
        p[0] = Node('Var', value=p[1])
    else:
        p[0] = Node('ArrayAccess', children=[Node('Var', value=p[1]), p[3]])

def p_if_stmt(p):
    '''if_stmt : IF logic_expr THEN stmt
               | IF logic_expr THEN stmt ELSE stmt'''
    if len(p) == 5:
        p[0] = Node('If', children=[p[2], p[4]])
    else:
        p[0] = Node('If', children=[p[2], p[4], p[6]])

def p_while_stmt(p):
    '''while_stmt : WHILE logic_expr DO stmt'''
    p[0] = Node('While', children=[p[2], p[4]])

def p_for_stmt(p):
    '''for_stmt : FOR IDENTIFIER ASSIGN logic_expr TO logic_expr DO stmt
                | FOR IDENTIFIER ASSIGN logic_expr DOWNTO logic_expr DO stmt'''
    p[0] = Node('For', value='to' if p[5] == 'to' else 'downto', children=[Node('Var', value=p[2]), p[4], p[6], p[8]])

def p_write_stmt(p):
    '''write_stmt : WRITE LPAREN expr_list RPAREN'''
    p[0] = Node('Write', children=p[3])

def p_writeln_stmt(p):
    '''writeln_stmt : WRITELN LPAREN expr_list RPAREN
                    | WRITELN'''
    if len(p) == 5:
        p[0] = Node('Writeln', children=p[3])
    else:
        p[0] = Node('Writeln', children=[])

def p_readln_stmt(p):
    '''readln_stmt : READLN LPAREN var_ref RPAREN'''
    p[0] = Node('Readln', children=[p[3]])

def p_block_stmt(p):
    '''block_stmt : BEGIN stmt_list END'''
    p[0] = Node('Block', children=p[2])

def p_func_call(p):
    '''func_call : IDENTIFIER LPAREN expr_list RPAREN'''
    p[0] = Node('FuncCall', children=p[3], value=p[1])

def p_expr_list(p):
    '''expr_list : expr_list COMMA logic_expr
                 | logic_expr
                 | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_logic_expr(p):
    '''logic_expr : logic_expr AND rel_expr
                  | logic_expr OR rel_expr
                  | NOT rel_expr
                  | rel_expr'''
    if len(p) == 4:
        p[0] = Node('Binary', children=[p[1], p[3]], value=p[2])
    elif len(p) == 3:
        p[0] = Node('Unary', children=[p[2]], value=p[1])
    else:
        p[0] = p[1]

def p_rel_expr(p):
    '''rel_expr : rel_expr EQ expr
                | rel_expr NE expr
                | rel_expr LT expr
                | rel_expr GT expr
                | rel_expr LE expr
                | rel_expr GE expr
                | expr'''
    if len(p) == 4:
        p[0] = Node('Binary', children=[p[1], p[3]], value=p[2])
    else:
        p[0] = p[1]

def p_expr(p):
    '''expr : expr PLUS term
            | expr MINUS term
            | term'''
    if len(p) == 4:
        p[0] = Node('Binary', children=[p[1], p[3]], value=p[2])
    else:
        p[0] = p[1]

def p_term(p):
    '''term : term TIMES factor
            | term DIVIDE factor
            | term MOD factor
            | factor'''
    if len(p) == 4:
        p[0] = Node('Binary', children=[p[1], p[3]], value=p[2])
    else:
        p[0] = p[1]

def p_factor(p):
    '''factor : LENGTH LPAREN expr RPAREN
              | primary'''
    if len(p) == 5:
        p[0] = Node('Length', children=[p[3]])
    else:
        p[0] = p[1]

def p_primary(p):
    '''primary : NUMBER
               | STRING
               | BOOLEAN_LITERAL
               | var_ref
               | func_call
               | LPAREN logic_expr RPAREN'''
    if len(p) == 2:
        if isinstance(p[1], Node):
            p[0] = p[1]
        elif isinstance(p[1], str):  # trata strings como '1'
            p[0] = Node('Literal', value=p[1])
        else:
            p[0] = Node('Literal', value=p[1])
    else:
        p[0] = p[2]

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    if p:
        print(f"Erro de sintaxe na linha {p.lineno}: Token inesperado '{p.value}'")
    else:
        print("Erro de sintaxe: Fim de ficheiro inesperado")

# Construir o parser
parser = yacc.yacc()

# Código de teste
code = """
program BinarioParaInteiro;
var
bin: string;
i, valor, potencia: integer;
begin
writeln('Introduza uma string binária:');
readln(bin);
valor := 0;
potencia := 1;
for i := length(bin) downto 1 do
begin
if bin[i] = '1' then
valor := valor + potencia;
potencia := potencia * 2;
end;
writeln('O valor inteiro correspondente é: ', valor);
end.
"""

# parsing do código
print("Parseando o programa 'BinarioParaInteiro':")
ast = parser.parse(code)
if ast:
    print("AST gerada:")
    print(ast)

# Gerar código para a VM
generator = CodeGenerator()
try:
    generator.generate(ast)
    print("\nCódigo gerado para a VM:")
    print(generator.get_code())
except Exception as e:
    print(f"Erro durante a geração de código: {e}")
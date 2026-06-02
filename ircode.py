from dataclasses import dataclass
from typing import Any
from model import *

# Definición de instrucción según la especificación
Instruction = tuple

@dataclass
class IRFunction:
    name: str
    params: list
    return_type: str
    instructions: list

@dataclass
class IRProgram:
    globals: list
    functions: list

class IRCodeGen:
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.instructions = []
        self.symtab = {}  # Tabla de símbolos para rastrear tipos de variables

    # ==================================================
    # Helpers
    # ==================================================
    def new_temp(self) -> str:
        self.temp_count += 1
        return f"R{self.temp_count}"

    def new_label(self, prefix: str = "L") -> str:
        self.label_count += 1
        return f"{prefix}{self.label_count}"

    def emit(self, *inst):
        self.instructions.append(inst)

    def get_suffix(self, type_name: str) -> str:
        """Devuelve el sufijo correcto para la instrucción según el tipo de B-Minor"""
        if type_name == "integer": return "I"
        if type_name == "float": return "F"
        if type_name == "boolean": return "B"
        if type_name == "char": return "B"
        if type_name == "string": return "S"
        return "I"

    # ==================================================
    # Programa
    # ==================================================
    def generate(self, program: Program) -> IRProgram:
        functions = []
        globals_list = []
        self.symtab = {}

        # Pasada 1: Registrar variables globales en la tabla de símbolos
        for decl in program.declarations:
            if isinstance(decl, VarDeclaration):
                self.symtab[decl.name] = decl.type_name
                # Emitir directiva de datos para variables globales
                val = None
                if decl.value is not None:
                    val = decl.value.value if hasattr(decl.value, 'value') else decl.value
                globals_list.append(("DATAS", decl.name, val))

        # Pasada 2: Procesar los cuerpos de las funciones
        for decl in program.declarations:
            if isinstance(decl, Function):
                functions.append(self.visit_Function(decl))

        return IRProgram(
            globals=globals_list,
            functions=functions
        )

    # ==================================================
    # Funciones
    # ==================================================
    def visit_Function(self, node: Function) -> IRFunction:
        self.instructions = []
        
        # Registrar parámetros locales en la tabla de símbolos
        for param in node.params:
            if isinstance(param, tuple) and len(param) == 2:
                self.symtab[param[0]] = param[1]
            elif hasattr(param, 'name') and hasattr(param, 'type_name'):
                self.symtab[param.name] = param.type_name

        # Procesar sentencias del cuerpo
        for stmt in node.body:
            self.visit(stmt)

        return IRFunction(
            name=node.name,
            params=node.params,
            return_type=node.return_type,
            instructions=list(self.instructions)
        )

    # ==================================================
    # Dispatcher
    # ==================================================
    def visit(self, node: Any) -> Any:
        method = getattr(self, f"visit_{type(node).__name__}", None)
        if not method:
            raise NotImplementedError(f"No existe visitor para {type(node).__name__}")
        return method(node)

    # ==================================================
    # Literales (Retornan: temporal, tipo)
    # ==================================================
    def visit_IntLiteral(self, node: IntLiteral):
        temp = self.new_temp()
        self.emit("MOVI", node.value, temp)
        return temp, "integer"

    def visit_FloatLiteral(self, node: FloatLiteral):
        temp = self.new_temp()
        self.emit("MOVF", node.value, temp)
        return temp, "float"

    def visit_BooleanLiteral(self, node: BooleanLiteral):
        temp = self.new_temp()
        self.emit("MOVB", 1 if node.value else 0, temp)
        return temp, "boolean"

    def visit_StringLiteral(self, node: StringLiteral):
        temp = self.new_temp()
        self.emit("MOVS", node.value, temp)
        return temp, "string"

    def visit_CharLiteral(self, node: CharLiteral):
        temp = self.new_temp()
        # Se almacena el valor entero ASCII o el carácter plano
        val = ord(node.value) if (isinstance(node.value, str) and len(node.value) == 1) else node.value
        self.emit("MOVB", val, temp)
        return temp, "char"

    # ==================================================
    # Variables
    # ==================================================
    def visit_Identifier(self, node: Identifier):
        temp = self.new_temp()
        var_type = self.symtab.get(node.name, "integer")
        suffix = self.get_suffix(var_type)
        self.emit(f"LOAD{suffix}", node.name, temp)
        return temp, var_type

    # ==================================================
    # Declaraciones y Asignaciones
    # ==================================================
    def visit_VarDeclaration(self, node: VarDeclaration):
        self.symtab[node.name] = node.type_name
        if node.value is None:
            return

        temp, val_type = self.visit(node.value)
        suffix = self.get_suffix(node.type_name)
        self.emit(f"STORE{suffix}", temp, node.name)

    def visit_Assignment(self, node: Assignment):
        temp, val_type = self.visit(node.value)
        var_type = self.symtab.get(node.name, val_type)
        suffix = self.get_suffix(var_type)
        self.emit(f"STORE{suffix}", temp, node.name)
        return temp, var_type

    # ==================================================
    # Expresiones Binarias
    # ==================================================
    def visit_BinaryOp(self, node: BinaryOp):
        left, left_type = self.visit(node.left)
        right, right_type = self.visit(node.right)
        result = self.new_temp()

        # Coerción simple de tipo (Float domina sobre Integer)
        expr_type = "float" if (left_type == "float" or right_type == "float") else "integer"

        arithmetic = {
            "+": "ADD",
            "-": "SUB",
            "*": "MUL",
            "/": "DIV"
        }

        comparison = {"==", "!=", "<", "<=", ">", ">="}

        if node.op in arithmetic:
            suffix = "F" if expr_type == "float" else "I"
            self.emit(f"{arithmetic[node.op]}{suffix}", left, right, result)
            return result, expr_type

        if node.op in comparison:
            # Suffix de comparación basado en los operandos originales
            suffix = "F" if (left_type == "float" or right_type == "float") else ("B" if left_type == "boolean" else "I")
            self.emit(f"CMP{suffix}", node.op, left, right, result)
            return result, "boolean"

        if node.op in {"&&", "||"}:
            op_code = "AND" if node.op == "&&" else "OR"
            self.emit(op_code, left, right, result)
            return result, "boolean"

        raise NotImplementedError(f"Operador {node.op} no soportado")

    # ==================================================
    # Unarios
    # ==================================================
    def visit_UnaryOp(self, node: UnaryOp):
        value, expr_type = self.visit(node.operand)
        result = self.new_temp()

        if node.op == "-":
            suffix = "F" if expr_type == "float" else "I"
            zero = self.new_temp()
            self.emit(f"MOV{suffix}", 0.0 if suffix == "F" else 0, zero)
            self.emit(f"{'SUBF' if suffix == 'F' else 'SUBI'}", zero, value, result)
            return result, expr_type

        if node.op == "!":
            self.emit("XOR", value, 1, result)
            return result, "boolean"

        raise NotImplementedError(f"Operador unario {node.op} no soportado")

    # ==================================================
    # Sentencias de Flujo y Control
    # ==================================================
    def visit_FunctionCall(self, node: FunctionCall):
        args = []
        for arg in node.args:
            arg_temp, _ = self.visit(arg)
            args.append(arg_temp)

        result = self.new_temp()
        self.emit("CALL", node.name, args, result)
        return result, "integer"  # Por simplicidad asume entero; escalable con firmas de función

    def visit_PrintStmt(self, node: PrintStmt):
        for expr in node.args:
            temp, expr_type = self.visit(expr)
            suffix = self.get_suffix(expr_type)
            self.emit(f"PRINT{suffix}", temp)

    def visit_ReturnStmt(self, node: ReturnStmt):
        if node.expr:
            value, _ = self.visit(node.expr)
            self.emit("RET", value)
        else:
            self.emit("RET")

    def visit_ExprStmt(self, node: ExprStmt):
        self.visit(node.expr)

    def visit_BlockStmt(self, node: BlockStmt):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_IfStmt(self, node: IfStmt):
        cond, _ = self.visit(node.condition)

        then_label = self.new_label("Lthen")
        else_label = self.new_label("Lelse")
        end_label = self.new_label("Lend")

        target_else = else_label if node.else_block else end_label
        self.emit("CBRANCH", cond, then_label, target_else)

        self.emit("LABEL", then_label)
        if isinstance(node.then_block, list):
            for stmt in node.then_block: self.visit(stmt)
        elif node.then_block is not None:
            self.visit(node.then_block)

        if node.else_block:
            self.emit("BRANCH", end_label)
            self.emit("LABEL", else_label)
            if isinstance(node.else_block, list):
                for stmt in node.else_block: self.visit(stmt)
            elif node.else_block is not None:
                self.visit(node.else_block)

        self.emit("LABEL", end_label)

    def visit_WhileStmt(self, node: WhileStmt):
        test_label = self.new_label("Ltest")
        body_label = self.new_label("Lbody")
        end_label = self.new_label("Lend")

        self.emit("LABEL", test_label)
        cond, _ = self.visit(node.condition)
        self.emit("CBRANCH", cond, body_label, end_label)

        self.emit("LABEL", body_label)
        if isinstance(node.body, list):
            for stmt in node.body: self.visit(stmt)
        elif node.body is not None:
            self.visit(node.body)

        self.emit("BRANCH", test_label)
        self.emit("LABEL", end_label)
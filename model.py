from typing import Any, Optional

# =====================================================
# Nodo base
# =====================================================
class Node:
    def __init__(self, lineno: int = 0):
        self.lineno = lineno

# =====================================================
# Programa
# =====================================================
class Program(Node):
    def __init__(self, declarations: Optional[list[Any]] = None, lineno: int = 0):
        super().__init__(lineno)
        self.declarations = declarations if declarations is not None else []

# =====================================================
# Literales
# =====================================================
class IntLiteral(Node):
    def __init__(self, value: int, lineno: int = 0):
        super().__init__(lineno)
        self.value = value

class FloatLiteral(Node):
    def __init__(self, value: float, lineno: int = 0):
        super().__init__(lineno)
        self.value = value

class BooleanLiteral(Node):
    def __init__(self, value: bool, lineno: int = 0):
        super().__init__(lineno)
        self.value = value

class StringLiteral(Node):
    def __init__(self, value: str, lineno: int = 0):
        super().__init__(lineno)
        self.value = value

class CharLiteral(Node):
    def __init__(self, value: str, lineno: int = 0):
        super().__init__(lineno)
        self.value = value

# =====================================================
# Expresiones
# =====================================================
class Identifier(Node):
    def __init__(self, name: str, lineno: int = 0):
        super().__init__(lineno)
        self.name = name

class BinaryOp(Node):
    def __init__(self, op: str, left: Any, right: Any, lineno: int = 0):
        super().__init__(lineno)
        self.op = op
        self.left = left
        self.right = right

class UnaryOp(Node):
    def __init__(self, op: str, operand: Any, lineno: int = 0):
        super().__init__(lineno)
        self.op = op
        self.operand = operand

class FunctionCall(Node):
    def __init__(self, name: str, args: Optional[list[Any]] = None, lineno: int = 0):
        super().__init__(lineno)
        self.name = name
        self.args = args if args is not None else []

# =====================================================
# Declaraciones
# =====================================================
class VarDeclaration(Node):
    def __init__(self, name: str, type_name: str, value: Optional[Any] = None, lineno: int = 0):
        super().__init__(lineno)
        self.name = name
        self.type_name = type_name
        self.value = value

class Function(Node):
    def __init__(self, name: str, return_type: str = "void", params: Optional[list[Any]] = None, body: Optional[list[Any]] = None, lineno: int = 0):
        super().__init__(lineno)
        self.name = name
        self.return_type = return_type
        self.params = params if params is not None else []
        self.body = body if body is not None else []

# =====================================================
# Sentencias
# =====================================================
class BlockStmt(Node):
    def __init__(self, statements: Optional[list[Any]] = None, lineno: int = 0):
        super().__init__(lineno)
        self.statements = statements if statements is not None else []

class ExprStmt(Node):
    def __init__(self, expr: Any, lineno: int = 0):
        super().__init__(lineno)
        self.expr = expr

class Assignment(Node):
    def __init__(self, name: str, value: Any, lineno: int = 0):
        super().__init__(lineno)
        self.name = name
        self.value = value

class IfStmt(Node):
    def __init__(self, condition: Any, then_block: Optional[list[Any]] = None, else_block: Optional[list[Any]] = None, lineno: int = 0):
        super().__init__(lineno)
        self.condition = condition
        self.then_block = then_block if then_block is not None else []
        self.else_block = else_block

class WhileStmt(Node):
    def __init__(self, condition: Any, body: Optional[list[Any]] = None, lineno: int = 0):
        super().__init__(lineno)
        self.condition = condition
        self.body = body if body is not None else []

class PrintStmt(Node):
    def __init__(self, args: Optional[list[Any]] = None, lineno: int = 0):
        super().__init__(lineno)
        self.args = args if args is not None else []

class ReturnStmt(Node):
    def __init__(self, expr: Optional[Any] = None, lineno: int = 0):
        super().__init__(lineno)
        self.expr = expr
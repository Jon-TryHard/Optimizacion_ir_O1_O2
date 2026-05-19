# model.py
from dataclasses import dataclass, field
from typing import Any, List, Optional, Union

@dataclass
class Node:
    lineno: int = 0

# ---------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------

@dataclass
class Type(Node):
    pass

@dataclass
class IntegerType(Type):
    def __str__(self): return "integer"

@dataclass
class FloatType(Type):
    def __str__(self): return "float"

@dataclass
class BooleanType(Type):
    def __str__(self): return "boolean"

@dataclass
class CharType(Type):
    def __str__(self): return "char"

@dataclass
class StringType(Type):
    def __str__(self): return "string"

@dataclass
class VoidType(Type):
    def __str__(self): return "void"

# ---------------------------------------------------------------------
# Expresiones
# ---------------------------------------------------------------------

@dataclass
class Expression(Node):
    pass

@dataclass
class IntegerLiteral(Expression):
    value: int

@dataclass
class FloatLiteral(Expression):
    value: float

@dataclass
class BooleanLiteral(Expression):
    value: bool

@dataclass
class CharLiteral(Expression):
    value: str

@dataclass
class StringLiteral(Expression):
    value: str

@dataclass
class VarLoc(Expression):
    name: str

@dataclass
class BinOp(Expression):
    op: str
    left: Expression
    right: Expression

@dataclass
class UnaryOp(Expression):
    op: str
    expr: Expression

@dataclass
class CallExpr(Expression):
    func_name: str
    args: List[Expression]

@dataclass
class ConditionalExpr(Expression):
    cond: Expression
    true_val: Expression
    false_val: Expression

# ---------------------------------------------------------------------
# Sentencias (Statements)
# ---------------------------------------------------------------------

@dataclass
class Statement(Node):
    pass

@dataclass
class Block(Statement):
    statements: List[Statement]

@dataclass
class VarDeclaration(Statement):
    name: str
    type_name: Type
    value: Optional[Expression] = None
    array_sizes: List[int] = field(default_factory=list)

# Alias para compatibilidad con astopt.py
VarDecl = VarDeclaration

@dataclass
class IfStmt(Statement):
    condition: Expression
    then_block: Statement
    else_block: Optional[Statement] = None

@dataclass
class WhileStmt(Statement):
    condition: Expression
    body: Statement

@dataclass
class PrintStmt(Statement):
    expressions: List[Expression]

@dataclass
class ReturnStmt(Statement):
    value: Optional[Expression] = None

@dataclass
class ExprStmt(Statement):
    expr: Expression

@dataclass
class FunctionDeclaration(Statement):
    name: str
    params: List[tuple]
    return_type: Type
    body: Optional[Block] = None

@dataclass
class ClassDeclaration(Statement):
    name: str
    fields: List[VarDeclaration]
    methods: List[FunctionDeclaration]

# ---------------------------------------------------------------------
# Raíz del Programa
# ---------------------------------------------------------------------

@dataclass
class Program(Node):
    declarations: List[Union[VarDeclaration, FunctionDeclaration, ClassDeclaration]]
# ircode.py
from dataclasses import dataclass
from typing import Any, Optional

# Una instrucción es simplemente una tupla de Python
# Ej: ("ADDI", "R1", "R2", "R3")
Instruction = tuple[Any, ...]

# Clase base para representar tipos en B-Minor (mock para que no falle la importación)
class Type:
    pass

class IntegerType(Type):
    def __str__(self): return "integer"

class VoidType(Type):
    def __str__(self): return "void"

@dataclass
class IRFunction:
    name: str
    params: list[tuple[str, Type]]
    return_type: Type
    instructions: list[Instruction]

@dataclass
class IRProgram:
    globals: list[Instruction]
    functions: list[IRFunction]
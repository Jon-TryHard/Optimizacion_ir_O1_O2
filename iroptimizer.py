"""IR Optimizer para B-Minor con soporte -O0, -O1, -O2

Implementa optimizaciones de representación intermedia según:
- -O0: Sin optimización (IR tal como sale de IRCodeGen)
- -O1: Optimizaciones locales simples (constant folding, algebraic simplification, etc.)
- -O2: O1 + eliminación de temporales muertos (dead code elimination)
"""

from __future__ import annotations

from typing import Any, Optional
from ircode import IRProgram, IRFunction, Instruction


class IROptimizer:
    """Optimizador de código intermedio para B-Minor."""

    def __init__(self, level: int = 0):
        self.level = level

    @classmethod
    def optimize(cls, program: IRProgram, level: int = 0) -> IRProgram:
        """Optimiza un programa completo según el nivel especificado."""
        return cls(level).visit_program(program)

    def visit_program(self, program: IRProgram) -> IRProgram:
        """Aplica optimizaciones a todas las funciones del programa."""
        if self.level <= 0:
            return program

        new_globals = list(program.globals)
        new_functions: list[IRFunction] = []

        for fn in program.functions:
            new_insts = self.optimize_instruction_list(fn.instructions)
            new_functions.append(
                IRFunction(
                    name=fn.name,
                    params=list(fn.params),
                    return_type=fn.return_type,
                    instructions=new_insts,
                )
            )

        return IRProgram(globals=new_globals, functions=new_functions)

    def optimize_instruction_list(self, instructions: list[Instruction]) -> list[Instruction]:
        """Optimiza una lista de instrucciones según el nivel."""
        insts = list(instructions)

        if self.level >= 1:
            # Hacer múltiples pasadas ya que una optimización puede habilitar otra
            for _ in range(5):
                old_insts = list(insts)
                insts = self.constant_fold_and_simplify(insts)
                insts = self.remove_unreachable(insts)
                insts = self.remove_branch_to_next_label(insts)
                if insts == old_insts:
                    break

        if self.level >= 2:
            insts = self.remove_unused_temp_definitions(insts)

        return insts

    # -------------------------------------------------
    # Nivel O1: Optimizaciones locales simples
    # -------------------------------------------------

    def constant_fold_and_simplify(self, instructions: list[Instruction]) -> list[Instruction]:
        """Realiza constant folding y simplificación algebraica."""
        const: dict[str, Any] = {}  # Mapea registros a valores constantes
        out: list[Instruction] = []

        def _val(x):
            """Obtiene el valor de x si es literal o está en const."""
            if isinstance(x, (int, float, bool)):
                return x
            if isinstance(x, str) and x in const:
                return const[x]
            return None

        for inst in instructions:
            op = inst[0]

            # Rastrear asignaciones de constantes
            if op in {"MOVI", "MOVF", "MOVB"} and len(inst) == 3:
                value, dst = inst[1], inst[2]
                const[dst] = value
                out.append(inst)
                continue

            # Operaciones aritméticas: Constant folding y simplificación algebraica
            if op in {"ADDI", "SUBI", "MULI", "DIVI", "ADDF", "SUBF", "MULF", "DIVF"} and len(inst) == 4:
                a, b, dst = inst[1], inst[2], inst[3]
                val_a = _val(a)
                val_b = _val(b)

                # Constant folding: ambos operandos son constantes
                if val_a is not None and val_b is not None:
                    try:
                        result = None
                        if "I" in op:  # Operaciones enteras
                            if op == "ADDI":
                                result = val_a + val_b
                            elif op == "SUBI":
                                result = val_a - val_b
                            elif op == "MULI":
                                result = val_a * val_b
                            elif op == "DIVI" and val_b != 0:
                                result = int(val_a // val_b)
                        else:  # Operaciones flotantes
                            if op == "ADDF":
                                result = val_a + val_b
                            elif op == "SUBF":
                                result = val_a - val_b
                            elif op == "MULF":
                                result = val_a * val_b
                            elif op == "DIVF" and val_b != 0:
                                result = val_a / val_b

                        if result is not None:
                            new_op = "MOVI" if "I" in op else "MOVF"
                            const[dst] = result
                            out.append((new_op, result, dst))
                            continue
                    except (ZeroDivisionError, ValueError):
                        pass

                # Simplificación algebraica: propiedades especiales
                # x + 0 = x, 0 + x = x
                if op in {"ADDI", "ADDF"} and val_a == 0:
                    const.pop(dst, None)
                    out.append(inst)
                    continue
                if op in {"ADDI", "ADDF"} and val_b == 0 and val_a is not None:
                    new_op = "MOVI" if op == "ADDI" else "MOVF"
                    const[dst] = val_a
                    out.append((new_op, val_a, dst))
                    continue

                # x - 0 = x
                if op in {"SUBI", "SUBF"} and val_b == 0 and val_a is not None:
                    new_op = "MOVI" if op == "SUBI" else "MOVF"
                    const[dst] = val_a
                    out.append((new_op, val_a, dst))
                    continue

                # x * 0 = 0, 0 * x = 0
                if op in {"MULI", "MULF"}:
                    if val_a == 0 or val_b == 0:
                        new_op = "MOVI" if op == "MULI" else "MOVF"
                        const[dst] = 0
                        out.append((new_op, 0, dst))
                        continue

                # x * 1 = x, 1 * x = x
                if op in {"MULI", "MULF"}:
                    if val_a == 1 and val_a is not None:
                        new_op = "MOVI" if op == "MULI" else "MOVF"
                        const[dst] = val_b if val_b is not None else None
                        if val_b is not None:
                            out.append((new_op, val_b, dst))
                            continue
                    elif val_b == 1 and val_b is not None:
                        new_op = "MOVI" if op == "MULI" else "MOVF"
                        const[dst] = val_a if val_a is not None else None
                        if val_a is not None:
                            out.append((new_op, val_a, dst))
                            continue

                # 0 / x = 0 (si x != 0)
                if op in {"DIVI", "DIVF"} and val_a == 0 and val_b not in {0, None}:
                    new_op = "MOVI" if op == "DIVI" else "MOVF"
                    const[dst] = 0
                    out.append((new_op, 0, dst))
                    continue

                # x / 1 = x
                if op in {"DIVI", "DIVF"} and val_b == 1 and val_a is not None:
                    new_op = "MOVI" if op == "DIVI" else "MOVF"
                    const[dst] = val_a
                    out.append((new_op, val_a, dst))
                    continue

                # Si no se optimizó, limpiar constante del destino
                const.pop(dst, None)
                out.append(inst)
                continue

            # Comparaciones constantes
            if op in {"CMPI", "CMPF", "CMPB"} and len(inst) == 5:
                cmp_oper, a, b, dst = inst[1], inst[2], inst[3], inst[4]
                val_a = _val(a)
                val_b = _val(b)

                if val_a is not None and val_b is not None:
                    result = 1 if self.eval_cmp(cmp_oper, val_a, val_b) else 0
                    const[dst] = result
                    out.append(("MOVI", result, dst))
                    continue

                const.pop(dst, None)
                out.append(inst)
                continue

            # Ramas condicionales constantes
            if op == "CBRANCH" and len(inst) == 4:
                test, true_label, false_label = inst[1], inst[2], inst[3]
                val_test = _val(test)

                if val_test is not None:
                    target = true_label if val_test != 0 else false_label
                    out.append(("BRANCH", target))
                    continue

                out.append(inst)
                continue

            # Instrucciones conservadoras
            dst = self.defined_temp(inst)
            if dst is not None:
                const.pop(dst, None)

            out.append(inst)

        return out

    def remove_unreachable(self, instructions: list[Instruction]) -> list[Instruction]:
        """Elimina código inalcanzable después de BRANCH o RET."""
        out: list[Instruction] = []
        unreachable = False

        for inst in instructions:
            op = inst[0]

            if op == "LABEL":
                unreachable = False

            if unreachable and op != "LABEL":
                continue

            out.append(inst)

            if op in {"BRANCH", "RET"}:
                unreachable = True

        return out

    def remove_branch_to_next_label(self, instructions: list[Instruction]) -> list[Instruction]:
        """Elimina saltos redundantes a la siguiente instrucción."""
        out: list[Instruction] = []

        for i in range(len(instructions)):
            inst = instructions[i]

            if (
                inst[0] == "BRANCH"
                and i + 1 < len(instructions)
                and instructions[i + 1][0] == "LABEL"
                and inst[1] == instructions[i + 1][1]
            ):
                continue

            out.append(inst)

        return out

    # -------------------------------------------------
    # Nivel O2: Eliminación de temporales muertos
    # -------------------------------------------------

    def remove_unused_temp_definitions(self, instructions: list[Instruction]) -> list[Instruction]:
        """Elimina definiciones de temporales que nunca se usan."""
        used: set[str] = set()
        result_reversed: list[Instruction] = []

        for inst in reversed(instructions):
            dst = self.defined_temp(inst)
            args = self.used_temps(inst)

            if dst is not None and dst not in used and self.is_pure_definition(inst):
                pass
            else:
                result_reversed.append(inst)

            if dst is not None:
                used.discard(dst)
            used.update(args)

        return list(reversed(result_reversed))

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def defined_temp(self, inst: Instruction) -> Optional[str]:
        """Retorna el temporal definido por la instrucción, o None."""
        op = inst[0]

        if op in {"MOVI", "MOVF", "MOVB", "ADDR"} and len(inst) == 3:
            dst = inst[2]
            return dst if isinstance(dst, str) and dst.startswith("R") else None

        if op in {"ADDI", "SUBI", "MULI", "DIVI", "ADDF", "SUBF", "MULF", "DIVF", "AND", "OR", "XOR"} and len(inst) == 4:
            dst = inst[3]
            return dst if isinstance(dst, str) and dst.startswith("R") else None

        if op in {"CMPI", "CMPF", "CMPB"} and len(inst) == 5:
            dst = inst[4]
            return dst if isinstance(dst, str) and dst.startswith("R") else None

        if op.startswith("LOAD") and len(inst) == 3:
            dst = inst[2]
            return dst if isinstance(dst, str) and dst.startswith("R") else None

        return None

    def used_temps(self, inst: Instruction) -> set[str]:
        """Retorna el conjunto de temporales usados por la instrucción."""
        op = inst[0]

        if op in {"MOVI", "MOVF", "MOVB", "LABEL", "BRANCH", "DATAS", "ADDR"}:
            return set()

        if op.startswith("STORE"):
            return self.temps_in(inst[1:2])

        if op.startswith("PRINT"):
            return self.temps_in(inst[1:])

        if op == "CBRANCH":
            return self.temps_in(inst[1:2])

        if op == "RET":
            return self.temps_in(inst[1:])

        if op in {"ADDI", "SUBI", "MULI", "DIVI", "ADDF", "SUBF", "MULF", "DIVF", "AND", "OR", "XOR"}:
            return self.temps_in(inst[1:3])

        if op in {"CMPI", "CMPF", "CMPB"}:
            return self.temps_in(inst[2:4])

        return self.temps_in(inst[1:])

    def temps_in(self, values) -> set[str]:
        """Extrae todos los temporales de una lista."""
        return {x for x in values if isinstance(x, str) and x.startswith("R")}

    def is_pure_definition(self, inst: Instruction) -> bool:
        """Retorna True si la instrucción es pura."""
        op = inst[0]
        return op in {
            "MOVI", "MOVF", "MOVB", "ADDR",
            "ADDI", "SUBI", "MULI", "DIVI",
            "ADDF", "SUBF", "MULF", "DIVF",
            "AND", "OR", "XOR",
            "CMPI", "CMPF", "CMPB",
        } or op.startswith("LOAD")

    def eval_cmp(self, oper: str, a: Any, b: Any) -> bool:
        """Evalúa una comparación de valores constantes."""
        if oper == "==":
            return a == b
        if oper == "!=":
            return a != b
        if oper == "<":
            return a < b
        if oper == "<=":
            return a <= b
        if oper == ">":
            return a > b
        if oper == ">=":
            return a >= b
        raise NotImplementedError(f"Comparador no soportado: {oper}")


def parse_opt_level(value: str) -> int:
    """Analiza una especificación de nivel de optimización."""
    text = str(value).strip()

    if text.startswith("-O"):
        text = text[2:]
    elif text.startswith("O"):
        text = text[1:]

    if not text.isdigit():
        raise ValueError(f"Nivel de optimización inválido: {value!r}")

    level = int(text)

    if level < 0 or level > 4:
        raise ValueError("El nivel de optimización debe estar entre 0 y 4")

    return level


def main():
    """Función principal para ejecutar desde línea de comandos."""
    import sys

    if len(sys.argv) < 2:
        print("Uso: python iroptimizer.py <archivo.bminor> [-O0|-O1|-O2]")
        print()
        print("Niveles de optimización:")
        print("  -O0: Sin optimización (por defecto)")
        print("  -O1: Optimizaciones locales simples")
        print("  -O2: O1 + Eliminación de temporales muertos")
        sys.exit(1)

    filename = sys.argv[1]
    level = 0

    if len(sys.argv) >= 3:
        try:
            level = parse_opt_level(sys.argv[2])
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    print(f"Optimizando {filename} con nivel -O{level}...", file=sys.stderr)


if __name__ == "__main__":
    main()

from ircode import IRProgram, IRFunction

class IROptimizer:
    def __init__(self, level=0):
        self.level = level

    @classmethod
    def optimize(cls, program, level=0):
        return cls(level).visit_program(program)

    # ==================================================
    # Programa
    # ==================================================
    def visit_program(self, program):
        if self.level <= 0:
            return program

        functions = []
        for fn in program.functions:
            insts = list(fn.instructions)

            if self.level >= 1:
                insts = self.constant_fold(insts)
                insts = self.remove_unreachable(insts)
                insts = self.remove_redundant_branches(insts)

            if self.level >= 2:
                insts = self.dead_code_elimination(insts)

            functions.append(
                IRFunction(
                    name=fn.name,
                    params=fn.params,
                    return_type=fn.return_type,
                    instructions=insts
                )
            )

        return IRProgram(program.globals, functions)

    # ==================================================
    # O1: Constant Folding y Simplificación
    # ==================================================
    def constant_fold(self, instructions):
        constants = {}
        result = []

        for inst in instructions:
            op = inst[0]

            # 1. Asignaciones directas
            if op in ("MOVI", "MOVF", "MOVB") and len(inst) == 3:
                value = inst[1]
                dest = inst[2]
                constants[dest] = value
                result.append(inst)
                continue

            # 2. Operaciones Aritméticas y Lógicas
            if op in ("ADDI", "SUBI", "MULI", "DIVI", "ADDF", "SUBF", "MULF", "DIVF", "AND", "OR", "XOR") and len(inst) == 4:
                left = inst[1]
                right = inst[2]
                dest = inst[3]

                a = constants.get(left, left)
                b = constants.get(right, right)

                a_is_const = isinstance(a, (int, float))
                b_is_const = isinstance(b, (int, float))

                # Regla: No optimizar división por cero
                if op in ("DIVI", "DIVF") and b_is_const and b == 0:
                    constants.pop(dest, None)
                    result.append(inst)
                    continue

                if a_is_const and b_is_const:
                    val = 0
                    mov_op = "MOVF" if "F" in op else "MOVI"

                    if op in ("ADDI", "ADDF"): val = a + b
                    elif op in ("SUBI", "SUBF"): val = a - b
                    elif op in ("MULI", "MULF"): val = a * b
                    elif op == "DIVI": val = int(a // b)
                    elif op == "DIVF": val = a / b
                    elif op == "AND": val = int(a) & int(b)
                    elif op == "OR": val = int(a) | int(b)
                    elif op == "XOR": val = int(a) ^ int(b)

                    constants[dest] = val
                    result.append((mov_op, val, dest))
                    continue

                # Simplificación algebraica que resulta en una constante fija (ej: x * 0 = 0)
                if op in ("MULI", "MULF"):
                    if (a_is_const and a == 0) or (b_is_const and b == 0):
                        val = 0.0 if "F" in op else 0
                        mov_op = "MOVF" if "F" in op else "MOVI"
                        constants[dest] = val
                        result.append((mov_op, val, dest))
                        continue

                constants.pop(dest, None)
                result.append(inst)
                continue

            # 3. Comparaciones
            if op in ("CMPI", "CMPF", "CMPB") and len(inst) == 5:
                cmpop = inst[1]
                left = inst[2]
                right = inst[3]
                dest = inst[4]

                a = constants.get(left, left)
                b = constants.get(right, right)

                if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                    val = int(self.eval_cmp(cmpop, a, b))
                    constants[dest] = val
                    result.append(("MOVI", val, dest))
                    continue

                constants.pop(dest, None)
                result.append(inst)
                continue

            # 4. Ramas Condicionales (CBRANCH)
            if op == "CBRANCH" and len(inst) == 4:
                cond = inst[1]
                true_lbl = inst[2]
                false_lbl = inst[3]

                val_cond = constants.get(cond, cond)
                if isinstance(val_cond, (int, float)):
                    if val_cond:
                        result.append(("BRANCH", true_lbl))
                    else:
                        result.append(("BRANCH", false_lbl))
                    continue

            # Invalida temporales para operaciones impuras (ej. LOAD, CALL)
            dst_temp = self.defined_temp(inst)
            if dst_temp:
                constants.pop(dst_temp, None)

            result.append(inst)

        return result

    # ==================================================
    # O1: Código inalcanzable
    # ==================================================
    def remove_unreachable(self, instructions):
        output = []
        dead = False

        for inst in instructions:
            op = inst[0]
            if op == "LABEL":
                dead = False
            
            if not dead:
                output.append(inst)
            
            if op in ("BRANCH", "RET"):
                dead = True

        return output

    # ==================================================
    # O1: BRANCH redundante
    # ==================================================
    def remove_redundant_branches(self, instructions):
        output = []
        i = 0
        while i < len(instructions):
            inst = instructions[i]
            if (
                inst[0] == "BRANCH"
                and i + 1 < len(instructions)
                and instructions[i + 1][0] == "LABEL"
                and instructions[i + 1][1] == inst[1]
            ):
                i += 1
                continue
            output.append(inst)
            i += 1
        return output

    # ==================================================
    # O2: Eliminación de temporales muertos
    # ==================================================
    def dead_code_elimination(self, instructions):
        live = set()
        output = []

        for inst in reversed(instructions):
            dest = self.defined_temp(inst)
            used = self.used_temps(inst)

            if dest and dest not in live and self.is_pure(inst):
                continue

            if dest:
                live.discard(dest)

            live.update(used)
            output.append(inst)

        output.reverse()
        return output

    # ==================================================
    # Helpers Expandidos (Tipos, Llamadas y Arrays)
    # ==================================================
    def defined_temp(self, inst):
        op = inst[0]
        if op in ("MOVI", "MOVF", "MOVB", "MOVS", "ADDR") and len(inst) == 3:
            return inst[2] if isinstance(inst[2], str) and inst[2].startswith("R") else None
        
        if op in ("ADDI", "SUBI", "MULI", "DIVI", "ADDF", "SUBF", "MULF", "DIVF", "AND", "OR", "XOR") and len(inst) == 4:
            return inst[3] if isinstance(inst[3], str) and inst[3].startswith("R") else None
        
        if op in ("CMPI", "CMPF", "CMPB") and len(inst) == 5:
            return inst[4] if isinstance(inst[4], str) and inst[4].startswith("R") else None
        
        if op.startswith("LOAD") and len(inst) == 3:
            return inst[2] if isinstance(inst[2], str) and inst[2].startswith("R") else None
            
        if op == "CALL" and len(inst) == 4:
            return inst[3] if isinstance(inst[3], str) and inst[3].startswith("R") else None
            
        return None

    def used_temps(self, inst):
        op = inst[0]
        
        if op in ("MOVI", "MOVF", "MOVB", "MOVS", "LABEL", "BRANCH", "DATAS", "ADDR"):
            return set()
            
        if op.startswith("STORE"):
            return self.extract_temps(inst[1:2])
            
        if op.startswith("PRINT"):
            return self.extract_temps(inst[1:])
            
        if op == "RET":
            return self.extract_temps(inst[1:])
            
        if op in ("ADDI", "SUBI", "MULI", "DIVI", "ADDF", "SUBF", "MULF", "DIVF", "AND", "OR", "XOR"):
            return self.extract_temps(inst[1:3])
            
        if op in ("CMPI", "CMPF", "CMPB"):
            return self.extract_temps(inst[2:4])
            
        if op == "CBRANCH":
            return self.extract_temps(inst[1:2])
            
        if op == "CALL":
            return self.extract_temps(inst[2])
            
        return self.extract_temps(inst[1:])

    def extract_temps(self, values):
        """Helper para extraer sólo los valores que representan un registro."""
        return {x for x in values if isinstance(x, str) and x.startswith("R")}

    def is_pure(self, inst):
        op = inst[0]
        return op in (
            "MOVI", "MOVF", "MOVB", "MOVS", "ADDR",
            "ADDI", "SUBI", "MULI", "DIVI",
            "ADDF", "SUBF", "MULF", "DIVF",
            "AND", "OR", "XOR",
            "CMPI", "CMPF", "CMPB"
        ) or op.startswith("LOAD")

    def eval_cmp(self, op, a, b):
        if op == "==": return a == b
        if op == "!=": return a != b
        if op == "<": return a < b
        if op == "<=": return a <= b
        if op == ">": return a > b
        if op == ">=": return a >= b
        raise ValueError(f"Comparador inválido: {op}")
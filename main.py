import sys

from lexer import Lexer
from parser import Parser
from checker import Checker
from ircode import IRCodeGen
from iroptimizer import IROptimizer

# =====================================================
# Impresión de IR
# =====================================================
def print_ir(ir_program):
    """Muestra la representación intermedia completa, incluyendo globales y funciones."""
    if ir_program.globals:
        print("=" * 60)
        print("GLOBAL VARIABLES / DATA SECTION")
        print("=" * 60)
        for g in ir_program.globals:
            print(g)
            
    for fn in ir_program.functions:
        print()
        print("=" * 60)
        print(f"FUNCTION {fn.name}")
        print("=" * 60)

        for inst in fn.instructions:
            print(inst)

# =====================================================
# Lectura de archivo
# =====================================================
def read_source(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

# =====================================================
# Compilación
# =====================================================
def compile_file(filename, opt_level=0):
    # 1. Leer fuente
    source = read_source(filename)

    # 2. Lexer
    lexer = Lexer()
    tokens = lexer.tokenize(source)

    # 3. Parser
    parser = Parser(tokens)
    ast = parser.parse()

    # 4. Checker (Validación Semántica)
    checker = Checker()
    checker.check(ast)

    # 5. AST -> IR (Generación de Código Intermedio)
    generator = IRCodeGen()
    ir = generator.generate(ast)

    # 6. Optimización (Niveles O0, O1 o O2)
    ir = IROptimizer.optimize(ir, level=opt_level)

    return ir

# =====================================================
# CLI (Interfaz de Línea de Comandos)
# =====================================================
def usage():
    print(
        "Uso:\n"
        "  python main.py archivo.bminor\n"
        "  python main.py archivo.bminor -O0\n"
        "  python main.py archivo.bminor -O1\n"
        "  python main.py archivo.bminor -O2\n\n"
        "Formatos avanzados permitidos:\n"
        "  python main.py archivo.bminor -O 2\n"
        "  python main.py archivo.bminor 2"
    )

def parse_opt_level(value: str) -> int:
    """Valida y extrae de forma flexible el nivel de optimización según la rúbrica."""
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

def parse_arguments():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    filename = sys.argv[1]
    opt_level = 0

    # Manejo estándar: python main.py archivo.bminor -O1 (o variantes directas como '2')
    if len(sys.argv) == 3:
        try:
            opt_level = parse_opt_level(sys.argv[2])
        except ValueError as e:
            print(f"Error de argumentos: {e}")
            usage()
            sys.exit(1)

    # Manejo con separación por espacios: python main.py archivo.bminor -O 2
    elif len(sys.argv) == 4:
        if sys.argv[2] in ("-O", "O"):
            try:
                opt_level = parse_opt_level(sys.argv[3])
            except ValueError as e:
                print(f"Error de argumentos: {e}")
                usage()
                sys.exit(1)
        else:
            print(f"Opción desconocida: {sys.argv[2]}")
            usage()
            sys.exit(1)
            
    elif len(sys.argv) > 4:
        usage()
        sys.exit(1)

    return filename, opt_level

# =====================================================
# Main
# =====================================================
def main():
    try:
        filename, opt_level = parse_arguments()

        ir = compile_file(filename, opt_level)

        print()
        print(f"Optimization level: -O{opt_level}")
        print_ir(ir)

    except FileNotFoundError:
        print(f"Error: El archivo '{filename}' no fue encontrado.")
    except Exception as e:
        print(f"Compilation error: {e}")

if __name__ == "__main__":
    main()
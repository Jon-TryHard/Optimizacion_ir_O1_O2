from model import *


class SemanticError(Exception):
    pass


class Checker:

    def __init__(self):
        self.functions = {}
        self.variables = set()

    # ==========================================
    # Entrada principal
    # ==========================================

    def check(self, program):

        if not isinstance(program, Program):
            raise SemanticError("AST inválido")

        #
        # Registrar funciones
        #

        for decl in program.declarations:

            if isinstance(decl, Function):

                if decl.name in self.functions:
                    raise SemanticError(
                        f"Función duplicada: {decl.name}"
                    )

                self.functions[decl.name] = decl

        #
        # Debe existir main
        #

        if "main" not in self.functions:
            raise SemanticError(
                "No existe función main"
            )

        #
        # Revisar cuerpos
        #

        for fn in program.declarations:

            if isinstance(fn, Function):
                self.check_function(fn)

    # ==========================================
    # Funciones
    # ==========================================

    def check_function(self, fn):

        self.variables = set()

        for stmt in fn.body:
            self.visit(stmt)

    # ==========================================
    # Dispatcher
    # ==========================================

    def visit(self, node):

        method = getattr(
            self,
            f"visit_{type(node).__name__}",
            self.generic_visit
        )

        return method(node)

    def generic_visit(self, node):
        return

    # ==========================================
    # Variables
    # ==========================================

    def visit_VarDeclaration(self, node):

        if node.name in self.variables:

            raise SemanticError(
                f"Variable duplicada: {node.name}"
            )

        self.variables.add(node.name)

        if node.value:
            self.visit(node.value)

    def visit_Assignment(self, node):

        if node.name not in self.variables:

            raise SemanticError(
                f"Variable no declarada: {node.name}"
            )

        self.visit(node.value)

    def visit_Identifier(self, node):

        if node.name not in self.variables:

            raise SemanticError(
                f"Variable no declarada: {node.name}"
            )

    # ==========================================
    # Expresiones
    # ==========================================

    def visit_BinaryOp(self, node):

        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOp(self, node):

        self.visit(node.operand)

    def visit_FunctionCall(self, node):

        if node.name not in self.functions:

            raise SemanticError(
                f"Función no definida: {node.name}"
            )

        for arg in node.args:
            self.visit(arg)

    # ==========================================
    # Control de flujo
    # ==========================================

    def visit_IfStmt(self, node):

        self.visit(node.condition)

        for stmt in node.then_block:
            self.visit(stmt)

        if node.else_block:

            for stmt in node.else_block:
                self.visit(stmt)

    def visit_WhileStmt(self, node):

        self.visit(node.condition)

        for stmt in node.body:
            self.visit(stmt)

    # ==========================================
    # Print / Return
    # ==========================================

    def visit_PrintStmt(self, node):

        for expr in node.args:
            self.visit(expr)

    def visit_ReturnStmt(self, node):

        if node.expr:
            self.visit(node.expr)

    def visit_ExprStmt(self, node):

        self.visit(node.expr)

    # ==========================================
    # Literales
    # ==========================================

    def visit_IntLiteral(self, node):
        pass

    def visit_FloatLiteral(self, node):
        pass

    def visit_BooleanLiteral(self, node):
        pass
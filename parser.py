from model import *

class Parser:
    # Precedencia ajustada para incluir lógicos
    PRECEDENCE = {
        "OR": 1,
        "AND": 2,

        "EQL": 3,
        "NEQ": 3,

        "LT": 4,
        "LEQ": 4,
        "GT": 4,
        "GEQ": 4,

        "PLUS": 5,
        "MINUS": 5,

        "MULT": 6,
        "DIV": 6,
        "MOD": 6,
    }

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ==================================================
    # Helpers
    # ==================================================

    def peek(self, offset=0):
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def consume(self, expected=None):
        tok = self.peek()

        if tok is None:
            raise Exception("Fin inesperado del archivo")

        if expected and tok["type"] != expected:
            raise Exception(
                f"Se esperaba {expected} y se obtuvo {tok['type']} "
                f"(línea {tok['line']})"
            )

        self.pos += 1
        return tok

    # ==================================================
    # Programa
    # ==================================================

    def parse(self):
        declarations = []
        while self.peek():
            declarations.append(self.parse_function())

        return Program(declarations=declarations)

    # ==================================================
    # Funciones
    # ==================================================

    def parse_function(self):
        name_tok = self.consume("ID")

        self.consume("COLON")
        self.consume("FUNC")

        ret_type = self.parse_type()

        self.consume("LPAREN")
        
        # Parsear parámetros: (x: integer, y: boolean)
        params = []
        if self.peek() and self.peek()["type"] != "RPAREN":
            while True:
                p_name = self.consume("ID")["value"]
                self.consume("COLON")
                p_type = self.parse_type()
                
                params.append((p_name, p_type))
                
                if self.peek() and self.peek()["type"] == "COMMA":
                    self.consume("COMMA")
                else:
                    break

        self.consume("RPAREN")
        self.consume("ASSIGN")

        body = self.parse_block()

        # Asume que el nodo Function acepta 'params'
        return Function(
            name=name_tok["value"],
            params=params, 
            return_type=ret_type,
            body=body.statements,
            lineno=name_tok["line"]
        )

    def parse_type(self):
        tok = self.peek()
        if tok["type"] == "VOID":
            return self.consume()["value"]
        if tok["type"] == "TYPE":
            return self.consume()["value"]

        raise Exception(f"Tipo inválido en línea {tok['line']}")

    # ==================================================
    # Bloques
    # ==================================================

    def parse_block(self):
        lbrace = self.consume("LBRACE")
        stmts = []

        while self.peek() and self.peek()["type"] != "RBRACE":
            stmts.append(self.parse_statement())

        self.consume("RBRACE")

        return BlockStmt(
            statements=stmts,
            lineno=lbrace["line"]
        )

    # ==================================================
    # Sentencias
    # ==================================================

    def parse_statement(self):
        tok = self.peek()

        if tok["type"] == "LBRACE":
            return self.parse_block()
        if tok["type"] == "IF":
            return self.parse_if()
        if tok["type"] == "WHILE":
            return self.parse_while()
        if tok["type"] == "PRINT":
            return self.parse_print()
        if tok["type"] == "RETURN":
            return self.parse_return()

        # Declaración
        if tok["type"] == "ID" and self.peek(1) and self.peek(1)["type"] == "COLON":
            return self.parse_var_decl()

        # Asignación
        if tok["type"] == "ID" and self.peek(1) and self.peek(1)["type"] == "ASSIGN":
            return self.parse_assignment()

        # Expresión
        expr = self.parse_expression()
        self.consume("SEMI")

        return ExprStmt(
            expr=expr,
            lineno=tok["line"]
        )

    # ==================================================
    # Variables
    # ==================================================

    def parse_var_decl(self):
        name_tok = self.consume("ID")
        self.consume("COLON")
        type_tok = self.parse_type()
        
        value = None
        if self.peek() and self.peek()["type"] == "ASSIGN":
            self.consume("ASSIGN")
            value = self.parse_expression()

        self.consume("SEMI")

        return VarDeclaration(
            name=name_tok["value"],
            type_name=type_tok,
            value=value,
            lineno=name_tok["line"]
        )

    def parse_assignment(self):
        name_tok = self.consume("ID")
        self.consume("ASSIGN")
        value = self.parse_expression()
        self.consume("SEMI")

        return Assignment(
            name=name_tok["value"],
            value=value,
            lineno=name_tok["line"]
        )

    # ==================================================
    # IF
    # ==================================================

    def parse_if(self):
        tok = self.consume("IF")
        
        # Eliminados los consume("LPAREN") y ("RPAREN") para soportar "if 1 < 2 {"
        cond = self.parse_expression()

        then_stmt = self.parse_statement()
        
        if isinstance(then_stmt, BlockStmt):
            then_block = then_stmt.statements
        else:
            then_block = [then_stmt]

        else_block = None
        if self.peek() and self.peek()["type"] == "ELSE":
            self.consume("ELSE")
            stmt = self.parse_statement()
            if isinstance(stmt, BlockStmt):
                else_block = stmt.statements
            else:
                else_block = [stmt]

        return IfStmt(
            condition=cond,
            then_block=then_block,
            else_block=else_block,
            lineno=tok["line"]
        )

    # ==================================================
    # WHILE
    # ==================================================

    def parse_while(self):
        tok = self.consume("WHILE")
        
        # Soportamos "while x < 10 {" igual que el IF
        cond = self.parse_expression()

        stmt = self.parse_statement()
        if isinstance(stmt, BlockStmt):
            body = stmt.statements
        else:
            body = [stmt]

        return WhileStmt(
            condition=cond,
            body=body,
            lineno=tok["line"]
        )

    # ==================================================
    # PRINT
    # ==================================================

    def parse_print(self):
        tok = self.consume("PRINT")
        args = []

        if self.peek()["type"] == "LPAREN":
            self.consume("LPAREN")
            args.append(self.parse_expression())
            
            while self.peek()["type"] == "COMMA":
                self.consume("COMMA")
                args.append(self.parse_expression())
            self.consume("RPAREN")
        else:
            args.append(self.parse_expression())

        self.consume("SEMI")

        return PrintStmt(
            args=args,
            lineno=tok["line"]
        )

    # ==================================================
    # RETURN
    # ==================================================

    def parse_return(self):
        tok = self.consume("RETURN")
        expr = None

        if self.peek()["type"] != "SEMI":
            expr = self.parse_expression()

        self.consume("SEMI")

        return ReturnStmt(
            expr=expr,
            lineno=tok["line"]
        )

    # ==================================================
    # Expresiones
    # ==================================================

    def parse_expression(self, min_prec=1):
        left = self.parse_unary()

        while True:
            tok = self.peek()
            if not tok:
                break

            prec = self.PRECEDENCE.get(tok["type"])
            if prec is None or prec < min_prec:
                break

            op_tok = self.consume()
            right = self.parse_expression(prec + 1)

            left = BinaryOp(
                op=op_tok["value"],
                left=left,
                right=right,
                lineno=op_tok["line"]
            )

        return left

    def parse_unary(self):
        tok = self.peek()
        if tok["type"] in ("MINUS", "NOT"):
            op_tok = self.consume()
            operand = self.parse_unary()
            return UnaryOp(
                op=op_tok["value"],
                operand=operand,
                lineno=op_tok["line"]
            )

        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()

        if tok["type"] == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_expression()
            self.consume("RPAREN")
            return expr

        tok = self.consume()

        if tok["type"] == "NUMBER":
            return IntLiteral(value=int(tok["value"]), lineno=tok["line"])

        if tok["type"] == "FLOAT_LITERAL":
            return FloatLiteral(value=float(tok["value"]), lineno=tok["line"])
            
        if tok["type"] == "STRING":
            return StringLiteral(value=tok["value"], lineno=tok["line"])
            
        if tok["type"] == "CHAR":
            return CharLiteral(value=tok["value"], lineno=tok["line"])

        if tok["type"] == "TRUE":
            return BooleanLiteral(value=True, lineno=tok["line"])

        if tok["type"] == "FALSE":
            return BooleanLiteral(value=False, lineno=tok["line"])

        if tok["type"] == "ID":
            if self.peek() and self.peek()["type"] == "LPAREN":
                self.consume("LPAREN")
                args = []
                if self.peek()["type"] != "RPAREN":
                    args.append(self.parse_expression())
                    while self.peek()["type"] == "COMMA":
                        self.consume("COMMA")
                        args.append(self.parse_expression())

                self.consume("RPAREN")

                return FunctionCall(
                    name=tok["value"],
                    args=args,
                    lineno=tok["line"]
                )

            return Identifier(name=tok["value"], lineno=tok["line"])

        raise Exception(f"Expresión inválida en línea {tok['line']}: se encontró {tok['type']}")
"""
Analizador léxico para B-Minor simplificado.

Convierte el código fuente en una secuencia de tokens
utilizada posteriormente por el parser.
"""

import re

class Lexer:
    def __init__(self):
        self.token_specification = [
            # ==========================================
            # Comentarios (Deben ir antes del DIV '/')
            # ==========================================
            ('BLOCK_COMMENT', r'/\*[\s\S]*?\*/'),
            ('LINE_COMMENT', r'//[^\n]*'),

            # ==========================================
            # Literales
            # ==========================================
            ('FLOAT_LITERAL', r'\d+\.\d+'),
            ('NUMBER', r'\d+'),
            ('STRING', r'"(?:[^"\\]|\\.)*"'),
            ('CHAR', r"'(?:[^'\\]|\\.)'"),
            ('TRUE', r'\btrue\b'),
            ('FALSE', r'\bfalse\b'),

            # ==========================================
            # Tipos
            # ==========================================
            ('TYPE', r'\b(integer|boolean|char|string|float)\b'),
            ('VOID', r'\bvoid\b'),

            # ==========================================
            # Palabras reservadas
            # ==========================================
            ('FUNC', r'\bfunction\b'),
            ('RETURN', r'\breturn\b'),
            ('PRINT', r'\bprint\b'),
            ('IF', r'\bif\b'),
            ('ELSE', r'\belse\b'),
            ('WHILE', r'\bwhile\b'),

            # ==========================================
            # Identificadores
            # ==========================================
            ('ID', r'[A-Za-z_][A-Za-z0-9_]*'),

            # ==========================================
            # Comparaciones
            # ==========================================
            ('EQL', r'=='),
            ('NEQ', r'!='),
            ('LEQ', r'<='),
            ('GEQ', r'>='),
            ('LT', r'<'),
            ('GT', r'>'),

            # ==========================================
            # Operadores lógicos
            # ==========================================
            ('AND', r'&&'),
            ('OR', r'\|\|'),
            ('NOT', r'!'),

            # ==========================================
            # Operadores aritméticos
            # ==========================================
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('MULT', r'\*'),
            ('DIV', r'/'),
            ('MOD', r'%'),

            # ==========================================
            # Delimitadores
            # ==========================================
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('COLON', r':'),
            ('ASSIGN', r'='),
            ('COMMA', r','),
            ('SEMI', r';'),

            # ==========================================
            # Espacios
            # ==========================================
            ('SPACE', r'\s+'),
        ]

        self.tok_regex = re.compile(
            '|'.join(
                f'(?P<{name}>{pattern})'
                for name, pattern in self.token_specification
            )
        )

    # ==================================================
    # API pública
    # ==================================================

    def tokenize(self, source):
        tokens = []
        line_num = 1
        pos = 0

        while pos < len(source):
            match = self.tok_regex.match(source, pos)
            
            if not match:
                ch = source[pos]
                if ch == '\n':
                    line_num += 1
                    pos += 1
                    continue

                raise Exception(
                    f"Carácter inválido en línea {line_num}: {repr(ch)}"
                )

            token_type = match.lastgroup
            value = match.group()
            pos = match.end()

            # Si el token es espacio o comentario, actualizamos la línea y continuamos
            if token_type in {'SPACE', 'BLOCK_COMMENT', 'LINE_COMMENT'}:
                line_num += value.count('\n')
                continue

            tokens.append({
                'type': token_type,
                'value': value,
                'line': line_num
            })

        return tokens


# ======================================================
# Utilidad rápida para pruebas
# ======================================================

if __name__ == "__main__":
    code = """
    main: function void() = {
        // Este es un comentario de línea
        x: integer = 2 + 3;
        
        /* Comentario de
           bloque multilinea */
        mi_url: string = "http://ejemplo.com/test"; // Comentario tras código
        
        if (x < 10) {
            print(x);
        }

        return;
    }
    """

    lexer = Lexer()

    for token in lexer.tokenize(code):
        print(token)
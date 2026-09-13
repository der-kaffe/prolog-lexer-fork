from __future__ import annotations

from .comments import CommentScanning
from .cursor import Cursor, is_ascii_digit, is_ascii_letter
from .identifiers import IdentifierScanning
from .models import LexicalError, Token
from .numbers import NumberScanning
from .quoted import QuotedScanning
from .token_tables import DELIMITERS, MULTI_CHAR_OPERATORS, SINGLE_CHAR_OPERATORS


class PrologLexer(
    Cursor,
    CommentScanning,
    QuotedScanning,
    NumberScanning,
    IdentifierScanning,
):
    """Analizador léxico para el subconjunto de Prolog definido en la tarea.

    La clase compone, por herencia, un escáner por categoría léxica:
    - ``Cursor``: recorrido de caracteres, posición y emisión de tokens/errores.
    - ``CommentScanning``: comentarios de línea y de bloque.
    - ``QuotedScanning``: átomos citados y cadenas.
    - ``NumberScanning``: números enteros y reales.
    - ``IdentifierScanning``: átomos sin comillas, variables y operadores-palabra.

    Lo único que queda en este archivo es el bucle de despacho (``tokenize``):
    decide, carácter por carácter, a qué escáner delegar.

    Decisiones de alcance:
    - Los signos + y - siempre se reconocen como operadores. Por tanto, -25 se
      tokeniza como OP_RESTA seguido de NUMERO_ENTERO.
    - Los reales admitidos son dígitos '.' dígitos, por ejemplo 3.14.
    - Átomos citados y cadenas admiten escape con barra invertida.
    - No se admiten saltos de línea crudos dentro de átomos citados/cadenas.
    - Los comentarios de bloque pueden anidarse; esto es compatible con
      SWI-Prolog, aunque la tarea solo exige reconocer /* ... */.
    - Se realiza únicamente análisis léxico.
    - Átomos, variables y números se restringen a ASCII puro, en
      concordancia con las expresiones regulares documentadas
      ([a-z][A-Za-z0-9_]*, etc.). Una letra acentuada o ñ fuera de un
      átomo citado o cadena se reporta como CARACTER_NO_ADMITIDO en
      lugar de aceptarse silenciosamente como parte del identificador.
    """

    def tokenize(self) -> tuple[list[Token], list[LexicalError]]:
        while self._peek():
            ch = self._peek()

            if ch in " \t\r\n":
                self._advance()
                continue

            if ch == "%":
                self._scan_line_comment()
                continue

            if ch == "/" and self._peek(1) == "*":
                self._scan_block_comment()
                continue

            if ch == "'":
                self._scan_quoted(
                    "'",
                    "ATOMO_CITADO",
                    "ATOMO_SIN_CIERRE",
                    "Átomo entre comillas simples",
                )
                continue

            if ch == '"':
                self._scan_quoted(
                    '"',
                    "CADENA",
                    "CADENA_SIN_CIERRE",
                    "Cadena entre comillas dobles",
                )
                continue

            if is_ascii_digit(ch):
                self._scan_number()
                continue

            if is_ascii_letter(ch) or ch == "_":
                self._scan_identifier()
                continue

            matched = False
            # Máxima coincidencia: operadores más largos antes que sus prefijos.
            for operator, token_type in MULTI_CHAR_OPERATORS:
                if self.source.startswith(operator, self.i):
                    line, column = self.line, self.column
                    for _ in operator:
                        self._advance()
                    self._emit(token_type, operator, line, column)
                    matched = True
                    break

            if matched:
                continue

            if ch in SINGLE_CHAR_OPERATORS:
                line, column = self.line, self.column
                self._advance()
                self._emit(
                    SINGLE_CHAR_OPERATORS[ch],
                    ch,
                    line,
                    column,
                )
                continue

            if ch in DELIMITERS:
                line, column = self.line, self.column
                self._advance()
                self._emit(DELIMITERS[ch], ch, line, column)
                continue

            line, column = self.line, self.column
            self._advance()
            self._add_error(
                "CARACTER_NO_ADMITIDO",
                ch,
                line,
                column,
                f"Carácter no admitido: {ch!r}.",
            )

        return self.tokens, self.errors


def tokenize(
    text: str,
) -> tuple[list[Token], list[LexicalError], list[tuple[int, str, str]]]:
    lexer = PrologLexer(text)
    tokens, errors = lexer.tokenize()
    return tokens, errors, lexer.lexemes.entries

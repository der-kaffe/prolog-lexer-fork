"""Cursor de caracteres compartido por todos los escáneres léxicos.

Concentra el recorrido de izquierda a derecha del código fuente, el
seguimiento de línea/columna, y la emisión de tokens/errores hacia las
estructuras definidas en ``models.py``. Las clases de escaneo por
categoría (comentarios, citados, números, identificadores) heredan de
``Cursor`` y solo agregan el método de su propia categoría.
"""

from __future__ import annotations

from .models import LexemeTable, LexicalError, Token
from .token_tables import INTERNED_CATEGORIES

# Letras y dígitos ASCII puros, usados para restringir átomos, variables y
# números al alfabeto declarado en la especificación (Sección 4 del informe:
# [a-z][A-Za-z0-9_]*, etc.). Una letra acentuada o "ñ" no pertenece a este
# alfabeto y por lo tanto no puede formar parte de un identificador.
ASCII_LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
ASCII_DIGITS = "0123456789"
ASCII_ALNUM = ASCII_LETTERS + ASCII_DIGITS


def is_ascii_letter(ch: str) -> bool:
    return ch != "" and ch in ASCII_LETTERS


def is_ascii_digit(ch: str) -> bool:
    return ch != "" and ch in ASCII_DIGITS


def is_ascii_alnum(ch: str) -> bool:
    return ch != "" and ch in ASCII_ALNUM


class Cursor:
    """Recorrido de caracteres con posición (línea, columna) y emisión."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.i = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []
        self.errors: list[LexicalError] = []
        self.lexemes = LexemeTable()

    def _peek(self, offset: int = 0) -> str:
        pos = self.i + offset
        return self.source[pos] if pos < len(self.source) else ""

    def _advance(self) -> str:
        if self.i >= len(self.source):
            return ""
        ch = self.source[self.i]
        self.i += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _emit(self, token_type: str, lexeme: str, line: int, column: int) -> None:
        attribute = None
        if token_type in INTERNED_CATEGORIES:
            attribute = self.lexemes.intern(token_type, lexeme)
        self.tokens.append(Token(token_type, lexeme, line, column, attribute))

    def _add_error(
        self,
        error_type: str,
        fragment: str,
        line: int,
        column: int,
        message: str,
    ) -> None:
        self.errors.append(
            LexicalError(error_type, fragment, line, column, message)
        )

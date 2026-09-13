"""Escaneo de números enteros y reales.

Corresponde a la categoría "Números enteros y reales ..." del enunciado.
El signo (+/-) nunca se consume aquí: se trata siempre como operador
aritmético aparte (ver decisión de alcance documentada en ``lexer.py``).
"""

from __future__ import annotations

from .cursor import is_ascii_alnum, is_ascii_digit, is_ascii_letter


class NumberScanning:
    """Mixin que asume un ``Cursor`` (_peek/_advance/_emit/_add_error)."""

    def _scan_number(self) -> None:
        start_line, start_column, start_i = self.line, self.column, self.i

        while is_ascii_digit(self._peek()):
            self._advance()

        is_real = False
        # El punto solo pertenece al número si después existe al menos un dígito.
        # Esto permite distinguir 25. (entero + punto de cláusula) de 25.0.
        if self._peek() == "." and is_ascii_digit(self._peek(1)):
            is_real = True
            self._advance()
            while is_ascii_digit(self._peek()):
                self._advance()

        # Caso léxico inválido documentado por el proyecto: 12abc, 3.14valor.
        if is_ascii_letter(self._peek()) or self._peek() == "_":
            while self._peek() and (
                is_ascii_alnum(self._peek()) or self._peek() == "_"
            ):
                self._advance()

            fragment = self.source[start_i:self.i]
            self._add_error(
                "NUMERO_MAL_FORMADO",
                fragment,
                start_line,
                start_column,
                "Número mal formado: un literal numérico no puede continuar "
                "inmediatamente con letras o '_'.",
            )
            return

        token_type = "NUMERO_REAL" if is_real else "NUMERO_ENTERO"
        self._emit(
            token_type,
            self.source[start_i:self.i],
            start_line,
            start_column,
        )

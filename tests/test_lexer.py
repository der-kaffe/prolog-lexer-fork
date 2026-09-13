from __future__ import annotations

import unittest
from pathlib import Path

from prolog_lexer import PrologLexer

ROOT = Path(__file__).parent
VALID = ROOT / "corpus" / "valid"
INVALID = ROOT / "corpus" / "invalid"


class LexerFocusedTests(unittest.TestCase):
    def lex(self, text: str):
        lexer = PrologLexer(text)
        tokens, errors = lexer.tokenize()
        return lexer, tokens, errors

    def test_maximal_munch_operators(self):
        _, tokens, errors = self.lex(r"\== \= == =.. = :- :")
        self.assertEqual(errors, [])
        self.assertEqual(
            [t.tipo for t in tokens],
            [
                "OP_DIF_IDENTICO",
                "OP_NO_UNIFICA",
                "OP_IDENTICO",
                "OP_UNIV",
                "OP_UNIFICA",
                "OP_REGLA",
                "DOS_PUNTOS",
            ],
        )

    def test_anonymous_vs_named_variable(self):
        _, tokens, errors = self.lex("_ _Temporal _1 X")
        self.assertEqual(errors, [])
        self.assertEqual(
            [t.tipo for t in tokens],
            ["VARIABLE_ANONIMA", "VARIABLE", "VARIABLE", "VARIABLE"],
        )

    def test_number_and_final_period(self):
        _, tokens, errors = self.lex("25. 3.14.")
        self.assertEqual(errors, [])
        self.assertEqual(
            [t.tipo for t in tokens],
            ["NUMERO_ENTERO", "PUNTO", "NUMERO_REAL", "PUNTO"],
        )

    def test_ascii_numbers_and_whitespace(self):
        _, tokens, errors = self.lex("25 3.14")
        self.assertEqual(errors, [])
        self.assertEqual([t.tipo for t in tokens], ["NUMERO_ENTERO", "NUMERO_REAL"])

        _, tokens, errors = self.lex("a \t\r\n b.")
        self.assertEqual(errors, [])
        self.assertEqual([t.tipo for t in tokens], ["ATOMO", "ATOMO", "PUNTO"])

    def test_unicode_digits_are_not_numbers(self):
        cases = [
            ("١٢", [], ["١", "٢"]),
            ("１２", [], ["１", "２"]),
            ("²", [], ["²"]),
            ("٣.١٤", ["PUNTO"], ["٣", "١", "٤"]),
        ]
        for text, token_types, error_fragments in cases:
            with self.subTest(text=text):
                _, tokens, errors = self.lex(text)
                self.assertEqual(
                    [t.tipo for t in tokens],
                    token_types,
                )
                self.assertNotIn("NUMERO_ENTERO", [t.tipo for t in tokens])
                self.assertNotIn("NUMERO_REAL", [t.tipo for t in tokens])
                self.assertEqual(
                    [error.tipo for error in errors],
                    ["CARACTER_NO_ADMITIDO"] * len(error_fragments),
                )
                self.assertEqual(
                    [error.fragmento for error in errors],
                    error_fragments,
                )

    def test_unicode_whitespace_is_not_ignored(self):
        _, tokens, errors = self.lex("a.\u2003X.")
        self.assertEqual(
            [t.tipo for t in tokens],
            ["ATOMO", "PUNTO", "VARIABLE", "PUNTO"],
        )
        self.assertEqual([t.lexema for t in tokens], ["a", ".", "X", "."])
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].tipo, "CARACTER_NO_ADMITIDO")
        self.assertEqual(errors[0].fragmento, "\u2003")
        self.assertEqual((errors[0].linea, errors[0].columna), (1, 3))

    def test_sign_is_operator(self):
        _, tokens, errors = self.lex("-25 +3")
        self.assertEqual(errors, [])
        self.assertEqual(
            [t.tipo for t in tokens],
            ["OP_RESTA", "NUMERO_ENTERO", "OP_SUMA", "NUMERO_ENTERO"],
        )

    def test_positions(self):
        _, tokens, errors = self.lex("padre(a,\n  X).")
        self.assertEqual(errors, [])
        x = next(t for t in tokens if t.lexema == "X")
        self.assertEqual((x.linea, x.columna), (2, 3))

    def test_lexeme_table_deduplicates(self):
        lexer, tokens, errors = self.lex("padre(X). padre(X).")
        self.assertEqual(errors, [])
        atoms = [e for e in lexer.lexemes.entries if e[1] == "ATOMO"]
        variables = [e for e in lexer.lexemes.entries if e[1] == "VARIABLE"]
        self.assertEqual(len(atoms), 1)
        self.assertEqual(len(variables), 1)

    def test_nested_block_comments(self):
        _, tokens, errors = self.lex("a. /* uno /* dos */ fin */ b.")
        self.assertEqual(errors, [])
        self.assertEqual([t.lexema for t in tokens if t.tipo == "ATOMO"], ["a", "b"])

    def test_identifiers_are_ascii_only(self):
        # 'ñ' y vocales acentuadas no pertenecen a [A-Za-z0-9_] y deben
        # cortar el identificador, reportando el resto como carácter
        # no admitido en vez de aceptarlo silenciosamente.
        _, tokens, errors = self.lex("nio(X).")
        self.assertEqual(errors, [])
        self.assertEqual(tokens[0].tipo, "ATOMO")
        self.assertEqual(tokens[0].lexema, "nio")

        _, tokens, errors = self.lex("niño(X).")
        # 'ñ' corta el identificador en 'ni'; al no ser letra ASCII ni
        # operador/delimitador válido, se reporta como error y el
        # recorrido continúa, retomando 'o' como un nuevo ATOMO.
        self.assertEqual([t.lexema for t in tokens if t.tipo == "ATOMO"], ["ni", "o"])
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].tipo, "CARACTER_NO_ADMITIDO")
        self.assertEqual(errors[0].fragmento, "ñ")

    def test_quoted_atom_and_string_allow_non_ascii(self):
        # La restricción a ASCII solo aplica a átomos/variables sin
        # comillas; dentro de comillas simples o dobles cualquier
        # carácter (excepto salto de línea sin escapar) es válido.
        _, tokens, errors = self.lex("'Muñoz' \"café con leche\".")
        self.assertEqual(errors, [])
        self.assertEqual(
            [t.tipo for t in tokens if t.tipo in ("ATOMO_CITADO", "CADENA")],
            ["ATOMO_CITADO", "CADENA"],
        )

    def test_complete_valid_program(self):
        text = (ROOT / "corpus" / "programa_valido.pl").read_text(encoding="utf-8")
        _, tokens, errors = self.lex(text)
        self.assertEqual(errors, [])
        self.assertGreater(len(tokens), 20)

    def test_complete_error_program_recovers(self):
        text = (ROOT / "corpus" / "programa_errores.pl").read_text(encoding="utf-8")
        _, tokens, errors = self.lex(text)
        self.assertGreaterEqual(len(errors), 4)
        self.assertTrue(any(t.lexema == "padre" for t in tokens))


def _make_valid_test(path: Path):
    def test(self):
        lexer = PrologLexer(path.read_text(encoding="utf-8"))
        _, errors = lexer.tokenize()
        self.assertEqual(errors, [], msg=f"Errores en {path.name}: {errors}")
    return test


def _make_invalid_test(path: Path):
    def test(self):
        lexer = PrologLexer(path.read_text(encoding="utf-8"))
        _, errors = lexer.tokenize()
        self.assertGreaterEqual(len(errors), 1, msg=f"Se esperaba error en {path.name}")
    return test


for idx, path in enumerate(sorted(VALID.glob("*.pl")), 1):
    setattr(
        LexerFocusedTests,
        f"test_corpus_valido_{idx:02d}_{path.stem}",
        _make_valid_test(path),
    )

for idx, path in enumerate(sorted(INVALID.glob("*.pl")), 1):
    setattr(
        LexerFocusedTests,
        f"test_corpus_invalido_{idx:02d}_{path.stem}",
        _make_invalid_test(path),
    )


if __name__ == "__main__":
    unittest.main()

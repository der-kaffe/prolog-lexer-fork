# Analizador léxico de Prolog - INFO1148

Implementación de un analizador léxico para el subconjunto de Prolog especificado en la tarea de **Teoría de la Computación (INFO1148)**.

## Alcance

Reconoce:

- átomos no entrecomillados y átomos entre comillas simples;
- variables y variable anónima `_`;
- enteros y reales;
- cadenas entre comillas dobles;
- operadores `:-`, `?-`, `-->`, `=`, `\=`, `==`, `\==`, `=..`, `<`, `=<`, `>`, `>=`, `+`, `-`, `*`, `/`, `//`, `**`, `is`, `mod`, `\+`, `!`, `;`, `:`;
- coma y delimitadores `()[]{ }|.`;
- comentarios `% ...` y `/* ... */`;
- espacios en blanco, preservando línea y columna.

El proyecto **no** realiza análisis sintáctico, semántico, unificación, resolución de consultas ni manejo de ámbitos.

## Decisiones del subconjunto

1. `+` y `-` son siempre operadores. Por ejemplo, `-25` produce `OP_RESTA` y `NUMERO_ENTERO`.
2. Un real tiene forma `[0-9]+\.[0-9]+`.
3. Átomos citados y cadenas permiten escapes mediante `\`.
4. Un salto de línea sin escapar antes de la comilla de cierre se reporta como error.
5. La máxima coincidencia se implementa probando primero los operadores de mayor longitud.
6. Los comentarios de bloque se ignoran y se admite anidamiento.
7. La tabla de lexemas registra sin duplicados átomos, variables (excepto `_`) y literales.
8. Átomos y variables se restringen al alfabeto ASCII (`[A-Za-z0-9_]`) y los números a dígitos ASCII (`[0-9]`). Una letra acentuada o `ñ` fuera de un átomo citado o cadena corta el identificador y se reporta como `CARACTER_NO_ADMITIDO`; dentro de comillas simples o dobles cualquier carácter es válido.

## Ejecución

Requiere Python 3.11 o superior.

```bash
python main.py tests/corpus/programa_valido.pl
```

Con tabla de lexemas e índices:

```bash
python main.py tests/corpus/programa_valido.pl --tabla --atributos
```

## Pruebas

```bash
python -m unittest discover -s tests -v
```

El repositorio incluye:

- 20 archivos válidos;
- 8 archivos inválidos;
- 1 programa completo sin errores;
- 1 programa completo con varios errores recuperables;
- pruebas específicas de máxima coincidencia, posiciones, tabla de lexemas, signo y recuperación.

## Formato de token

```text
<TIPO_TOKEN, 'lexema', línea, columna>
```

Ejemplo:

```text
<ATOMO, 'padre', 2, 1>
<PARENTESIS_IZQ, '(', 2, 6>
<ATOMO, 'juan', 2, 7>
```

## Estructura

```text
prolog_lexer/
├── main.py
├── prolog_lexer/
│   ├── __init__.py
│   ├── models.py           # Token, LexicalError, LexemeTable
│   ├── token_tables.py     # tablas de operadores y delimitadores
│   ├── cursor.py           # recorrido de caracteres, posición, emisión
│   ├── comments.py         # comentarios de línea y de bloque
│   ├── quoted.py           # átomos citados y cadenas
│   ├── numbers.py          # números enteros y reales
│   ├── identifiers.py      # átomos, variables y operadores-palabra
│   └── lexer.py            # PrologLexer: compone todo + bucle de despacho
├── tests/
│   ├── test_lexer.py
│   └── corpus/
│       ├── valid/
│       ├── invalid/
│       ├── programa_valido.pl
│       └── programa_errores.pl
└── docs/
    └── automatas/
```

## Referencias principales

- SWI-Prolog Reference Manual: https://www.swi-prolog.org/pldoc/man?section=syntax
- SWI-Prolog, ISO Syntax Support: https://www.swi-prolog.org/pldoc/man?section=isosyntax
- SWI-Prolog, strings: https://www.swi-prolog.org/pldoc/man?section=string

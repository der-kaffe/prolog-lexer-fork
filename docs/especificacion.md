# Especificación léxica resumida

| Token | Expresión regular / patrón del subconjunto | Ejemplos |
|---|---|---|
| ATOMO | `[a-z][A-Za-z0-9_]*` | `padre`, `persona_1` |
| ATOMO_CITADO | `'([^'\\\n]|\\.)*'` | `'Juan Pérez'`, `':-'` |
| VARIABLE | `[A-Z][A-Za-z0-9_]*` o `_[A-Za-z0-9_]+` | `X`, `Persona`, `_Tmp` |
| VARIABLE_ANONIMA | `_` | `_` |
| NUMERO_ENTERO | `[0-9]+` | `25` |
| NUMERO_REAL | `[0-9]+\.[0-9]+` | `3.14` |
| CADENA | `"([^"\\\n]|\\.)*"` | `"hola"` |
| OP_REGLA | `:-` | `:-` |
| OP_CONSULTA | `\?-` | `?-` |
| OP_DCG | `-->` | `-->` |
| OP_UNIFICACION/COMPARACION | lista finita | `=`, `\=`, `==`, `\==`, `=..`, `<`, `=<`, `>`, `>=` |
| OP_ARITMETICO | lista finita | `+`, `-`, `*`, `/`, `//`, `**`, `is`, `mod` |
| OP_CONTROL | lista finita | `\+`, `!`, `;` |
| DOS_PUNTOS | `:` | `:` |
| COMA | `,` | `,` |
| DELIMITADOR | `[()\[\]{}|.]` | `(`, `]`, `|`, `.` |
| COMENTARIO_LINEA | `%[^\n]*` | `% comentario` |
| COMENTARIO_BLOQUE | `/* ... */` | `/* comentario */` |
| BLANCO | `[ \t\r\n]+` | espacio, tab, salto |

## Prioridad y máxima coincidencia

Se aplica **máxima coincidencia (longest match)**. Los operadores se prueban desde los más largos a los más cortos.

- `\==` se elige antes que `\=`.
- `=..` se elige antes que `=`.
- `:-` se elige antes que `:`.
- `_` se reconoce como `VARIABLE_ANONIMA`, mientras `_Variable` se reconoce como `VARIABLE`.

Para números, el punto se incorpora al literal solo si está seguido por un dígito. Así, `25.` produce `NUMERO_ENTERO('25')` seguido de `PUNTO('.')`, mientras `25.0` produce un único `NUMERO_REAL`.

# Optimizador IR para B-Minor: Niveles -O1 y -O2

## Descripción General

Este proyecto implementa un optimizador de código intermedio (IR) para el lenguaje B-Minor con dos niveles de optimización según la especificación en `especificacion_optimizacion_ir_O1_O2.md`.

### Niveles de Optimización

| Nivel | Descripción | Transformaciones |
|-------|-------------|------------------|
| **-O0** | Sin optimización | IR original sin cambios |
| **-O1** | Optimizaciones locales simples | Constant folding, simplificación algebraica, eliminación de código inalcanzable |
| **-O2** | O1 + Eliminación de temporales muertos | Todas las optimizaciones de O1 + análisis de liveness |

---

## Archivos Principales

### 1. `iroptimizer.py` ✓ COMPLETO
Optimizador de IR con la siguiente estructura:

#### Clase Principal: `IROptimizer`
```python
class IROptimizer:
    def optimize(program: IRProgram, level: int = 0) -> IRProgram
    def optimize_instruction_list(instructions: list[Instruction]) -> list[Instruction]
```

#### Métodos de Optimización O1:
- `constant_fold_and_simplify()`: Transforma operaciones con constantes
  - Constant folding: `ADDI R1(2), R2(3), R3` → `MOVI 5, R3`
  - Simplificación algebraica: `x+0 → x`, `x*1 → x`, `x*0 → 0`, etc.
  - Comparaciones constantes: `CMPI <, 4, 5, R3` → `MOVI 1, R3`
  - Ramas constantes: `CBRANCH R1(1), L1, L2` → `BRANCH L1`

- `remove_unreachable()`: Elimina código después de BRANCH o RET
  - Detecta secciones inalcanzables
  - Mantiene etiquetas para restaurar flujo de control

- `remove_branch_to_next_label()`: Elimina saltos redundantes
  - `BRANCH L1` seguido de `LABEL L1` se elimina

#### Métodos de Optimización O2:
- `remove_unused_temp_definitions()`: Eliminación de temporales muertos
  - Análisis hacia atrás (backward liveness)
  - Identifica temporales definidos pero nunca usados
  - Elimina solo instrucciones puras (sin efectos laterales)

#### Funciones Auxiliares:
- `defined_temp()`: Extrae el temporal definido por una instrucción
- `used_temps()`: Extrae los temporales usados por una instrucción
- `is_pure_definition()`: Determina si una instrucción es pura
- `eval_cmp()`: Evalúa comparaciones con operandos constantes

### 2. `lexer.py` ✓ ACTUALIZADO
Se añadió soporte para la palabra clave `class`:
```python
('CLASS', r'\bclass\b'),  # Palabra clave class
```

### 3. `parser.py` ✓ ACTUALIZADO
Se actualizó la detección de clases para usar el token CLASS:
- Línea 529: Cambio de `tok['type'] == 'ID' and tok['value'] == 'class'` → `tok['type'] == 'CLASS'`
- Línea 487: `consume('CLASS')` para leer el token de clase

### 4. `model.py` ✓ VERIFICADO
Contiene las clases de AST necesarias:
- `ClassDeclaration`: Para representar clases
- `FunctionDeclaration`: Para representar métodos
- `VarDeclaration`: Para campos de clase

### 5. `ircode.py` ✓ VERIFICADO
Define la estructura base de IR:
- `IRProgram`: Estructura raíz del programa
- `IRFunction`: Funciones con instrucciones
- `Instruction`: Tuplas que representan instrucciones de 3 direcciones

---

## Uso desde Línea de Comandos

```bash
# Sin optimización
python iroptimizer.py programa.bminor -O0

# Optimización local simple
python iroptimizer.py programa.bminor -O1

# Optimización local + eliminación de temporales muertos
python iroptimizer.py programa.bminor -O2

# Formatos alternativos soportados
python iroptimizer.py programa.bminor O0
python iroptimizer.py programa.bminor -O 0
```

---

## Suite de Pruebas

### Archivo: `test_iroptimizer.py`
Contiene 12 casos de prueba que validan:

✓ **Constant Folding**: `ADDI R1(2), R2(3), R3` → `MOVI 5, R3`  
✓ **Simplificación Algebraica**: `ADDI R1(10), R2(0), R3` → `MOVI 10, R3`  
✓ **Comparaciones Constantes**: `CMPI <, R1(4), R2(5), R3` → `MOVI 1, R3`  
✓ **Ramas Constantes**: `CBRANCH R1(1), L1, L2` → `BRANCH L1`  
✓ **Código Inalcanzable**: Se elimina código entre `BRANCH L1` y `LABEL L1`  
✓ **Código Inalcanzable después de RET**: Se elimina código después de `RET`  
✓ **Saltos Redundantes**: `BRANCH L1` + `LABEL L1` se eliminan  
✓ **Multiplicación por Cero**: `MULI R1(5), R2(0), R3` → `MOVI 0, R3`  
✓ **División por Uno**: `DIVI R1(42), R2(1), R3` → `MOVI 42, R3`  
✓ **Protección División por Cero**: `DIVI R1(10), R2(0), R3` se conserva  
✓ **Temporales Muertos (-O2)**: `MOVI 99, R2` se elimina si R2 nunca se usa  
✓ **Sin Cambios (-O0)**: La IR se mantiene idéntica  

#### Ejecutar Pruebas:
```bash
cd /home/jonathan/Documentos/Compiladores/Nota\ 2
python3 test_iroptimizer.py
```

**Resultado Esperado**: 12/12 tests passed

---

## Archivos de Prueba B-Minor

### 1. `test_basic_O1.bminor`
Programa simple para validar optimizaciones -O1:
- Constant folding: `2 + 3 * 4` → `14`
- Simplificación: `a + 0` → `a`
- Simplificación: `c * 1` → `c`
- Simplificación: `d - 0` → `d`

### 2. `test_oop_O2.bminor`
Programa con clase para validar soporte OOP:
```c
class Point {
    x: integer;
    y: integer;
    
    getX: function integer () = {
        return x;
    }
    
    getY: function integer () = {
        return y;
    }
}
```

---

## Transformaciones Implementadas

### Constant Folding
Realiza evaluación de operaciones en tiempo de compilación:
```
ADDI R1(2), R2(3), R3  →  MOVI 5, R3
MULI R1(4), R2(5), R3  →  MOVI 20, R3
DIVI R1(10), R2(2), R3 →  MOVI 5, R3
CMPI <, R1(1), R2(2), R3 → MOVI 1, R3
```

### Simplificación Algebraica
Elimina operaciones redundantes usando identidades:
```
ADDI R1(x), R2(0), R3  →  MOVI x, R3    (x + 0 = x)
SUBI R1(x), R2(0), R3  →  MOVI x, R3    (x - 0 = x)
MULI R1(x), R2(1), R3  →  MOVI x, R3    (x * 1 = x)
MULI R1(x), R2(0), R3  →  MOVI 0, R3    (x * 0 = 0)
DIVI R1(x), R2(1), R3  →  MOVI x, R3    (x / 1 = x)
```

### Ramas Condicionales Constantes
Convierte ramas condicionales a incondicionales:
```
MOVI 1, R1
CBRANCH R1, L1, L2     →  BRANCH L1
```

### Eliminación de Código Inalcanzable
Remueve instrucciones inaccesibles:
```
BRANCH L1
MOVI 99, R9            ← se elimina
PRINTI R9              ← se elimina
LABEL L1
```

### Saltos Redundantes
Elimina saltos a la siguiente etiqueta:
```
BRANCH L1
LABEL L1               ← se convierte en:  LABEL L1
```

### Eliminación de Temporales Muertos (-O2)
Remueve definiciones de temporales nunca utilizados:
```
MOVI 2, R1
MOVI 99, R2            ← se elimina (R2 nunca se usa)
PRINTI R1
```

---

## Manejo de Casos Especiales

### Division por Cero
**NO SE OPTIMIZA** por seguridad:
```
DIVI R1(10), R2(0), R3  →  Se conserva (no se optimiza)
```

### Instrucciones con Efectos Laterales
**NO SE ELIMINAN** en -O2:
- `STOREI`, `STOREF`, `STOREB`, `STORES`: Escritura en memoria
- `PRINTI`, `PRINTF`, `PRINTB`, `PRINTS`: Salida
- `CALL`: Llamadas a función (pueden tener efectos)
- `BRANCH`, `CBRANCH`, `RET`: Control de flujo
- `LABEL`, `DATAS`: Metadatos

### Instrucciones Puras (Candidatas a -O2)
```
MOVI, MOVF, MOVB, ADDR
ADDI, SUBI, MULI, DIVI
ADDF, SUBF, MULF, DIVF
AND, OR, XOR
CMPI, CMPF, CMPB
LOADI, LOADF, LOADB, LOADS
```

---

## Estructura de Datos de IR

Cada instrucción es una tupla de Python:

```python
("MOVI", 2, "R1")           # MOV inmediato
("ADDI", "R1", "R2", "R3")  # Suma de enteros
("CMPI", "<", "R1", "R2", "R3")  # Comparación
("CBRANCH", "R1", "L1", "L2")    # Rama condicional
("BRANCH", "L1")             # Rama incondicional
("LABEL", "L1")              # Etiqueta
("PRINTI", "R1")             # Imprimir entero
("RET", "R1")                # Retornar
```

---

## Soporte para Programación Orientada a Objetos

Se han realizado los siguientes cambios para soportar clases:

### 1. Lexer (lexer.py)
- ✓ Añadida palabra clave `CLASS` al reconocimiento de tokens

### 2. Parser (parser.py)
- ✓ Actualizado el método `parse_class_declaration()` para usar el token `CLASS`
- ✓ Detección correcta de declaraciones de clase con la sintaxis: `class NombreClase { ... }`

### 3. Model (model.py)
- ✓ `ClassDeclaration`: Contiene campos (fields) y métodos (methods)
- ✓ Método de clase representado como `FunctionDeclaration` dentro de la clase

### Sintaxis de Clase en B-Minor

```c
class Nombre {
    campo1: integer;
    campo2: float;
    
    metodo1: function integer () = {
        return campo1;
    }
    
    metodo2: function void () = {
        print campo1;
    }
}
```

---

## Ejemplo de Optimización Completa

### Programa Original (sin optimización)
```c
main: function integer () = {
    a: integer = 2 + 3 * 4;
    b: integer = a + 0;
    c: integer = b * 1;
    d: integer = c - 0;
    
    print d;
    return 0;
}
```

### IR Original (-O0)
```
MOVI 2, R1
MOVI 3, R2
MOVI 4, R3
MULI R2, R3, R4      # 3 * 4 = 12
ADDI R1, R4, R5      # 2 + 12 = 14
STOREI R5, a
LOADI a, R6
MOVI 0, R7
ADDI R6, R7, R8      # a + 0 = a
STOREI R8, b
...
```

### IR Optimizado (-O1)
```
MOVI 14, R5          # Constant folding: 2 + 3*4 = 14
STOREI R5, a
LOADI a, R6
MOVI 14, R8          # Algebraic: a + 0 = a
STOREI R8, b
...
```

### IR Optimizado (-O2)
```
MOVI 14, R5          # Constant folding
STOREI R5, a
MOVI 14, R8          # Algebraic simplification
STOREI R8, b
...
                     # Temporales muertos eliminados
```

---

## Notas de Implementación

### Algoritmo de Constant Folding
1. Rastrear valores de temporales en un diccionario
2. Para cada instrucción aritmética, verificar si ambos operandos son constantes
3. Si es así, evaluar la operación y reemplazar con MOVI/MOVF
4. Conservar el resultado en el diccionario de constantes

### Algoritmo de Eliminación de Temporales Muertos
1. Recorrer instrucciones hacia atrás
2. Mantener un conjunto de temporales usados
3. Para cada instrucción pura que define un temporal no usado, omitirla
4. Actualizar el conjunto de temporales usados

### Múltiples Pasadas
Para maximizar optimizaciones, el optimizador realiza hasta 5 pasadas sobre el código:
- Cada pasada ejecuta: constant folding → unreachable removal → branch simplification
- Se detiene cuando no hay cambios en una pasada
- Esto permite que optimizaciones de una pasada habiliten nuevas optimizaciones

---

## Limitaciones Conocidas

1. **No construye CFG**: Las optimizaciones son locales, sin análisis global de flujo
2. **No utiliza SSA**: Análisis simple de registros sin forma estática única
3. **No optimiza saltos a etiquetas no usadas**: Requeriría análisis global
4. **Conservador con llamadas a función**: `CALL` se trata como instrucción con efectos

---

## Validación y Testing

```bash
# Ejecutar suite de pruebas
python3 test_iroptimizer.py

# Resultados esperados
# ============================================================
# Test Suite: IROptimizer -O1 y -O2
# ============================================================
# Test constant_folding_addi:
#   ✓ PASSED
# ...
# Results: 12 passed, 0 failed
```

---

## Referencias

- `especificacion_optimizacion_ir_O1_O2.md`: Especificación oficial del proyecto
- `ircode.py`: Definiciones de estructuras de IR
- `model.py`: Definiciones de AST
- `parser.py`: Parser recursivo descendente
- `lexer.py`: Análisis léxico

---

## Autor y Fecha

Implementación completada: 2026-05-18

Niveles implementados:
- ✓ -O0 (Sin optimización)
- ✓ -O1 (Optimizaciones locales simples)
- ✓ -O2 (O1 + Eliminación de temporales muertos)
- ✓ Soporte para clases y programación orientada a objetos


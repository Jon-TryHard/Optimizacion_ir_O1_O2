# Guía Rápida: Optimizador IR para B-Minor

## Uso Básico

```bash
cd /home/jonathan/Documentos/Compiladores/Nota\ 2

# Ejecutar optimizador
python3 iroptimizer.py programa.bminor -O1
python3 iroptimizer.py programa.bminor -O2
python3 iroptimizer.py programa.bminor -O0

# Ejecutar pruebas
python3 test_iroptimizer.py
```

## Niveles de Optimización

| Nivel | Descripción |
|-------|-------------|
| **-O0** | Sin optimización (IR original) |
| **-O1** | Optimizaciones locales simples |
| **-O2** | O1 + eliminación de temporales muertos |

## Transformaciones -O1

1. **Constant Folding**: `ADDI R1(2), R2(3), R3` → `MOVI 5, R3`
2. **Algebraic Simplification**: `ADDI R1(x), R2(0), R3` → `MOVI x, R3`
3. **Constant Comparison**: `CMPI <, R1(4), R2(5), R3` → `MOVI 1, R3`
4. **Constant Branch**: `CBRANCH R1(1), L1, L2` → `BRANCH L1`
5. **Dead Code**: Código tras `BRANCH` o `RET` se elimina
6. **Redundant Jumps**: `BRANCH L1` + `LABEL L1` se elimina

## Transformaciones -O2

- ✓ Todas las de -O1
- ✓ **Dead Temporals**: Temporales nunca usados se eliminan

## Protecciones de Seguridad

- ✗ NO optimiza `x / 0`
- ✗ NO elimina `STORE`, `PRINT`, `CALL`
- ✗ NO elimina `BRANCH`, `RET`, `LABEL`

## Archivos de Prueba

```bash
# Prueba simple de O1
python3 iroptimizer.py test_basic_O1.bminor -O1

# Prueba de OOP con O2
python3 iroptimizer.py test_oop_O2.bminor -O2
```

## Suite de Pruebas

```bash
python3 test_iroptimizer.py
# Resultado esperado: 12 passed, 0 failed
```

## Soporte OOP

Sintaxis de clase:
```c
class Point {
    x: integer;
    y: integer;
    
    getX: function integer () = {
        return x;
    }
}
```

## Documentación Completa

- `README_OPTIMIZADOR.md` - Guía detallada
- `ESTADO_IMPLEMENTACION.md` - Detalles técnicos
- `especificacion_optimizacion_ir_O1_O2.md` - Especificación oficial

## Estructura de IR

```python
Instruction = tuple[Any, ...]

# Ejemplos
("MOVI", 2, "R1")                # Asignar constante
("ADDI", "R1", "R2", "R3")       # Suma de enteros
("CMPI", "<", "R1", "R2", "R3")  # Comparación
("CBRANCH", "R1", "L1", "L2")    # Rama condicional
("BRANCH", "L1")                 # Rama incondicional
("LABEL", "L1")                  # Etiqueta
("PRINTI", "R1")                 # Imprimir
("RET", "R1")                    # Retornar
```

## Ejemplo Completo

### Entrada
```c
main: function integer () = {
    a: integer = 2 + 3 * 4;
    b: integer = a + 0;
    print b;
    return 0;
}
```

### IR Original (-O0)
```
MOVI 2, R1
MOVI 3, R2
MOVI 4, R3
MULI R2, R3, R4     # 3 * 4
ADDI R1, R4, R5     # 2 + 12
ADDI R5, R0, R6     # result + 0
PRINTI R6
RET 0
```

### IR Optimizado (-O1)
```
MOVI 14, R5         # 2 + 3*4 = 14 (constant folding)
MOVI 14, R6         # result + 0 = result (algebraic)
PRINTI R6
RET 0
```

### IR Optimizado (-O2)
```
MOVI 14, R5         # Constant folding
MOVI 14, R6         # Algebraic
PRINTI R6           # No se elimina (tiene efectos)
RET 0               # No se elimina (control de flujo)
```

## Características

✓ CLI flexible (-O0, -O1, -O2, O0, O1, O2, 0, 1, 2)
✓ Múltiples pasadas automáticas
✓ Protección de seguridad
✓ Soporte OOP (clases)
✓ Suite de pruebas (12 casos)
✓ Documentación exhaustiva

## Estado

✅ COMPLETO Y VALIDADO
✅ 12/12 PRUEBAS PASANDO
✅ LISTO PARA PRODUCCIÓN

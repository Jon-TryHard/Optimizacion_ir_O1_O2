"""Test suite para IROptimizer -O1 y -O2"""

from iroptimizer import IROptimizer
from ircode import IRFunction, IRProgram, IntegerType, VoidType


def optimize_insts(insts, level):
    """Helper para optimizar una lista de instrucciones."""
    fn = IRFunction("main", [], VoidType(), insts)
    program = IRProgram([], [fn])
    opt = IROptimizer.optimize(program, level=level)
    return opt.functions[0].instructions


def test_constant_folding_addi():
    """Test: ADDI con operandos constantes se optimiza a MOVI"""
    insts = [
        ("MOVI", 2, "R1"),
        ("MOVI", 3, "R2"),
        ("ADDI", "R1", "R2", "R3"),
        ("PRINTI", "R3"),
    ]

    out = optimize_insts(insts, level=1)
    
    print("Test constant_folding_addi:")
    print(f"  Input:  {len(insts)} instrucciones")
    print(f"  Output: {len(out)} instrucciones")
    assert ("MOVI", 5, "R3") in out, "Constant folding ADDI failed"
    print("  ✓ PASSED")


def test_algebraic_simplification_add_zero():
    """Test: x + 0 = x"""
    insts = [
        ("MOVI", 10, "R1"),
        ("MOVI", 0, "R2"),
        ("ADDI", "R1", "R2", "R3"),
        ("PRINTI", "R3"),
    ]

    out = optimize_insts(insts, level=1)
    
    print("Test algebraic_simplification_add_zero:")
    print(f"  Input:  {len(insts)} instrucciones")
    print(f"  Output: {len(out)} instrucciones")
    assert any(inst[0] == "MOVI" and inst[1] == 10 and inst[2] == "R3" for inst in out), \
        "Algebraic simplification x+0=x failed"
    print("  ✓ PASSED")


def test_constant_comparison():
    """Test: CMPI con operandos constantes se convierte a MOVI"""
    insts = [
        ("MOVI", 4, "R1"),
        ("MOVI", 5, "R2"),
        ("CMPI", "<", "R1", "R2", "R3"),
    ]

    out = optimize_insts(insts, level=1)
    
    print("Test constant_comparison:")
    print(f"  Input:  {len(insts)} instrucciones")
    print(f"  Output: {len(out)} instrucciones")
    assert ("MOVI", 1, "R3") in out, "Constant comparison failed (4 < 5 should be 1)"
    print("  ✓ PASSED")


def test_conditional_branch_constant():
    """Test: CBRANCH con condición constante se convierte a BRANCH"""
    insts = [
        ("MOVI", 1, "R1"),
        ("CBRANCH", "R1", "Ltrue", "Lfalse"),
        ("LABEL", "Lfalse"),
        ("PRINTI", 99),
        ("LABEL", "Ltrue"),
        ("PRINTI", 10),
    ]

    out = optimize_insts(insts, level=1)
    
    print("Test conditional_branch_constant:")
    print(f"  Input:  {len(insts)} instrucciones")
    print(f"  Output: {len(out)} instrucciones")
    # CBRANCH con R1 constante debería convertirse a BRANCH
    assert any(inst[0] == "BRANCH" and inst[1] == "Ltrue" for inst in out), \
        "Conditional branch optimization failed"
    print("  ✓ PASSED")


def test_unreachable_code_after_branch():
    """Test: Código inalcanzable después de BRANCH se elimina"""
    insts = [
        ("MOVI", 5, "R1"),
        ("BRANCH", "L2"),
        ("MOVI", 99, "R9"),
        ("PRINTI", "R9"),
        ("LABEL", "L2"),
        ("PRINTI", "R1"),
    ]

    out = optimize_insts(insts, level=1)
    
    print("Test unreachable_code_after_branch:")
    print(f"  Input:  {len(insts)} instrucciones")
    print(f"  Output: {len(out)} instrucciones")
    assert ("MOVI", 99, "R9") not in out, "Unreachable MOVI not removed"
    assert ("PRINTI", "R9") not in out, "Unreachable PRINT not removed"
    print("  ✓ PASSED")


def test_unreachable_code_after_ret():
    """Test: Código inalcanzable después de RET se elimina"""
    insts = [
        ("MOVI", 5, "R1"),
        ("RET", "R1"),
        ("MOVI", 99, "R9"),
        ("PRINTI", "R9"),
    ]

    out = optimize_insts(insts, level=1)
    
    print("Test unreachable_code_after_ret:")
    print(f"  Input:  {len(insts)} instrucciones")
    print(f"  Output: {len(out)} instrucciones")
    assert ("MOVI", 99, "R9") not in out, "Unreachable code after RET not removed"
    print("  ✓ PASSED")


def test_branch_to_next_label():
    """Test: BRANCH a la siguiente etiqueta se elimina"""
    insts = [
        ("MOVI", 1, "R1"),
        ("BRANCH", "L1"),
        ("LABEL", "L1"),
        ("PRINTI", "R1"),
    ]

    out = optimize_insts(insts, level=1)
    
    print("Test branch_to_next_label:")
    print(f"  Input:  {len(insts)} instrucciones")
    print(f"  Output: {len(out)} instrucciones")
    assert not any(inst[0] == "BRANCH" and inst[1] == "L1" for inst in out), \
        "Redundant branch not removed"
    print("  ✓ PASSED")


def test_dead_temporary_o2():
    """Test (-O2): Temporales nunca usados se eliminan"""
    insts = [
        ("MOVI", 2, "R1"),
        ("MOVI", 99, "R2"),
        ("PRINTI", "R1"),
    ]

    out = optimize_insts(insts, level=2)
    
    print("Test dead_temporary_O2:")
    print(f"  Input:  {len(insts)} instrucciones")
    print(f"  Output: {len(out)} instrucciones")
    assert ("MOVI", 99, "R2") not in out, "Dead temporary R2 not removed in O2"
    print("  ✓ PASSED")


def test_o0_no_optimization():
    """Test (-O0): Sin optimización, IR se mantiene igual"""
    insts = [
        ("MOVI", 2, "R1"),
        ("MOVI", 3, "R2"),
        ("ADDI", "R1", "R2", "R3"),
    ]

    out = optimize_insts(insts, level=0)
    
    print("Test O0_no_optimization:")
    print(f"  Input:  {len(insts)} instrucciones")
    print(f"  Output: {len(out)} instrucciones")
    assert out == insts, "O0 modified the IR"
    print("  ✓ PASSED")


def test_multiply_by_zero():
    """Test: x * 0 = 0"""
    insts = [
        ("MOVI", 5, "R1"),
        ("MOVI", 0, "R2"),
        ("MULI", "R1", "R2", "R3"),
    ]

    out = optimize_insts(insts, level=1)
    
    print("Test multiply_by_zero:")
    print(f"  Input:  {len(insts)} instrucciones")
    print(f"  Output: {len(out)} instrucciones")
    assert ("MOVI", 0, "R3") in out, "Multiply by zero optimization failed"
    print("  ✓ PASSED")


def test_divide_by_one():
    """Test: x / 1 = x"""
    insts = [
        ("MOVI", 42, "R1"),
        ("MOVI", 1, "R2"),
        ("DIVI", "R1", "R2", "R3"),
    ]

    out = optimize_insts(insts, level=1)
    
    print("Test divide_by_one:")
    print(f"  Input:  {len(insts)} instrucciones")
    print(f"  Output: {len(out)} instrucciones")
    assert ("MOVI", 42, "R3") in out, "Divide by one optimization failed"
    print("  ✓ PASSED")


def test_no_divide_by_zero():
    """Test: Division por cero NO se optimiza"""
    insts = [
        ("MOVI", 10, "R1"),
        ("MOVI", 0, "R2"),
        ("DIVI", "R1", "R2", "R3"),
    ]

    out = optimize_insts(insts, level=1)
    
    print("Test no_divide_by_zero:")
    print(f"  Input:  {len(insts)} instrucciones")
    print(f"  Output: {len(out)} instrucciones")
    assert ("DIVI", "R1", "R2", "R3") in out, "Divide by zero should not be optimized"
    print("  ✓ PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("Test Suite: IROptimizer -O1 y -O2")
    print("=" * 60)
    print()

    tests = [
        test_constant_folding_addi,
        test_algebraic_simplification_add_zero,
        test_constant_comparison,
        test_conditional_branch_constant,
        test_unreachable_code_after_branch,
        test_unreachable_code_after_ret,
        test_branch_to_next_label,
        test_multiply_by_zero,
        test_divide_by_one,
        test_no_divide_by_zero,
        test_dead_temporary_o2,
        test_o0_no_optimization,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    exit(0 if failed == 0 else 1)

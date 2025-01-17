import pytest
from pytest import raises
from decimal import Decimal

from calculator import Calculator
from calculator.exceptions import *
from calculator.types import Operator, Operation


_ = Calculator()
D = Decimal


def test_add():
    assert _.add(10, 1) == 11
    assert _.add(2.3, 12.35000) == 14.65
    assert _.add(0.1, 0.3) == 0.4
    assert _.add(10, 3.2) == 13.2
    assert _.add(2.99, 1) == 3.99
    assert _.add(-10, -2) == -12
    assert _.add(-10.2, -2) == -12.2
    assert _.add(-10.2, -2.83) == -13.03

def test_subtract():
    assert _.subtract(10, 1) == 9
    assert _.subtract(10, 0) == 10
    assert _.subtract(0, 10) == -10
    assert _.subtract(5, 10) == -5
    assert _.subtract(-10, -5) == -5
    assert _.subtract(10, -5) == 15
    assert _.subtract(-10, 0) == -10
    assert _.subtract(1_000_000_000, 999_999_999) == 1
    assert _.subtract(10.5, 2.3) == 8.2
    assert _.subtract(1.0000001, 1.0000000) == 0.0000001
    assert _.subtract(_.add(0.1, _.add(0.1, 0.1)), 0.3) == 0  # (0.1 + 0.1 + 0.1) - 0.3 == 0

def test_multiply():
    assert _.multiply(10, 1) == 10
    assert _.multiply(10, 0) == 0
    assert _.multiply(5, 4) == 20
    assert _.multiply(5, -4) == -20
    assert _.multiply(-5, -4) == 20
    assert _.multiply(7, 1) == 7
    assert _.multiply(1_000_000, 1_000) == 1_000_000_000
    assert _.multiply(2.5, 4.0) == 10.0
    assert _.multiply(0.1, 0.2) == 0.02
    assert _.multiply(1_000_000, 0.000001) == 1.0

def test_divide():
    assert _.divide(10, 2) == 5
    assert _.divide(10, 1) == 10
    assert _.divide(5, 2) == 2.5
    assert _.divide(10, -2) == -5
    assert _.divide(-10, -2) == 5
    assert _.divide(0, 10) == 0
    assert _.divide(1, 1_000_000) == 0.000001
    assert _.divide(1_000_000_000, 1_000) == 1_000_000
    assert _.divide(5.5, 2.0) == 2.75
    assert _.divide(1, 0.000001) == 1_000_000
    assert _.divide(1, 7) == 0.1428571429
    with raises(ZeroDivisionError): _.divide(1, 0)

def test_execute_operations():
    op1 = Operation(Operator.ADD, 1, 3)  # (4 - (1 + 3))
    op2 = Operation(Operator.SUB, 4, op1)
    assert _._execute_operations([op2, op1]) == D(0)

def test_calculate_invalid_input():
    with raises(UnknownSimbol): _.calculate("abc")
    with raises(NotInfixOperator): _.calculate("5 +")
    with raises(NotInfixOperator): _.calculate("++5")

def test_calculate_basic():
    assert _.calculate("1 + 1") == 2
    assert _.calculate("10 - 2") == 8
    assert _.calculate("4 * 5") == 20
    assert _.calculate("20 / 4") == 5

def test_calculate_mixed():
    assert _.calculate("2 + 3 * 4") == 14
    assert _.calculate("(2 + 3) * 4") == 20

def test_calculate_nested_parentheses():
    assert _.calculate("((2 + 3) * 2) + 1") == 11
    assert _.calculate("((4 - 2) + (3 * 2)) * 2") == 16

def test_calculate_decimal():
    assert _.calculate("5.5 + 2.2", return_decimal=True) == D('7.7')
    assert _.calculate("10.5 * 2", return_decimal=True) == D('21.0')
    assert _.calculate("10 / (3 + 3 * 9)", return_decimal=True) == D('10') / D('30')

def test_calculate_difficult_decimal():
    difficult_expression_1 = "10 + 2 - 3 * 4 / 5 + 6 - 7 * 8 / 9"
    difficult_expression_2 = "1 + 2 - 3 + 4 - 5 + 6 - 7 + 8 - 9 + (10 * (20 / (30 - (40 + (50 * 60)))))"
    assert _.calculate(difficult_expression_1, return_decimal=True) == D('9.377777777777777777777777778')
    assert _.calculate(difficult_expression_2, return_decimal=True) == D('-3.066445182724252491694352159')

def test_calculate_zero():
    assert _.calculate("0 * 100") == 0
    assert _.calculate("0 / 1") == 0

def test_calculate_large():
    assert _.calculate("1000000 * 1000000") == 1000000000000
    assert _.calculate("999999 + 1") == 1000000

def test_calculate_negative():
    assert _.calculate("-5 + 10") == 5
    assert _.calculate("-5 * -5") == 25
    assert _.calculate("-10 / 2") == -5

def test_calculate_with_formatting():
    assert _.calculate("  5  +  10   ") == 15
    assert _.calculate("3 * 2") == 6

def test_caclulate_complex():
    assert _.calculate("(5 + (3 * (2 + 1))) / 2") == 7

def test_calculate_zero_division():
    with raises(ZeroDivisionError): _.calculate("1 / 0")

def test_calculate_difficult():
    assert _.calculate("1000000000 * 2 + 300000000 - 500000000 / 2") == 2000000000 + 300000000 - 250000000
    assert _.calculate("(((10 + 20) * (30 / 2)) - (5 * 5)) + (3 * (2 + 1))") == (((10 + 20) * (30 / 2)) - (5 * 5)) + (3 * (2 + 1))
    assert _.calculate("2 + (3 * (4 + (5 * (6 - (7 + 8)))))") == 2 + (3 * (4 + (5 * (6 - (7 + 8)))))
    assert _.calculate("1.0000001 + 2.0000002 - 3.0000003") == 0
    assert _.calculate("1 / 0.0000001") == 10000000.0
    assert _.calculate("(1.5 + 2) * (3 - 4.5) / 2") == (1.5 + 2) * (3 - 4.5) / 2
    assert _.calculate("-1 + 43 * (4 - 5 * (-(3 - 4 * 10 - (4 + 1) * 3 * 9)))") == -36809
    assert _.calculate("1 + (1+1) - 1") == 2
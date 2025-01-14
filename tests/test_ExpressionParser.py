import pytest
from pytest import raises

from calculator import ExpressionParser, Operation
from calculator.enums import Operator
from calculator.exceptions import *
from calculator.types import *
from decimal import Decimal


_ = ExpressionParser
D = Decimal


def test_count_levels():
    assert _._count_levels("()") == 1
    assert _._count_levels("()()()") == 1
    assert _._count_levels("") == 0
    assert _._count_levels("23 + 4.2") == 0
    assert _._count_levels("(2 + ( 23 * (434 / (lol))))") == 4

def test_count_levels_invalid_parentheses():
    with raises(InvalidParentheses): _._count_levels("((())")
    with raises(InvalidParentheses): _._count_levels("))((")
    with raises(InvalidParentheses): _._count_levels("()()()()(")

def test_count_operators():
    assert _._count_operators("123 + 3 + 5") == 2
    assert _._count_operators("1+1+1+1+1") == 4

def test_count_operators_not_infix():
    with raises(NotInfixOperator): _._count_operators("123 + 3 + 5 +")
    with raises(NotInfixOperator): _._count_operators("- 123 + 3 + 5")
    with raises(NotInfixOperator): _._count_operators("123 + 3 + 5 + 4 +")
    with raises(NotInfixOperator): _._count_operators("123 + 3 + + 5 + 4")

def test_count_operands():
    assert _._count_operands("32141.321 2 2.0 0.3 .3123") == 5
    assert _._count_operands("1 2 3 4 5 6") == 6

def test_count_operands_invalid_operands():
    with raises(InvalidOperand): _._count_operands("1 2 3 .")
    with raises(InvalidOperand): _._count_operands("1..")
    with raises(InvalidOperand): _._count_operands(" .")
    with raises(InvalidOperand): _._count_operands("1 2 3 .3.3.")

def test_count_operators_and_operands__invalid_operators_count():
    with raises(InvalidOperatorsCount): _._count_operators_and_operands("1 - 2 - 3 + 4 + 5 6")


def test_convert_expression():
    expression = ['(', D(21), '+', D(334), '-', '(', D(1), '/', D(5), ')', ')']
    assert _._convert_expression("21 + 334 - (1 / 5)") == expression
    assert _._convert_expression("1 + 1") == ['(', D(1), '+', D(1), ')']

def test_parse():
    assert_correct_parsing("2 + 3 - (1 / 5)", 3, 4.8)
    assert_correct_parsing("(2 + (3 + (4 + (6 + 8 / 1))))", 5, 23)

    assert_correct_parsing("1 + 1", 1, 2)
    assert_correct_parsing("10 - 5", 1, 5)
    assert_correct_parsing("2 * 3", 1, 6)
    assert_correct_parsing("8 / 4", 1, 2)

    # Mixed operations with precedence
    assert_correct_parsing("2 + 3 * 4", 2, 14)  # 3 * 4 first, then 2 + 12
    assert_correct_parsing("(2 + 3) * 4", 2, 20)  # Parentheses first

    # Nested parentheses
    assert_correct_parsing("(1 + (2 * 3))", 2, 7)
    assert_correct_parsing("((1 + 2) * (3 + 4))", 3, 21)
    assert_correct_parsing("((2 + 3) - (1 / (5 + 5)))", 4, 4.9)

def test_parse_negative():
    assert_correct_parsing("2 + 3 / 1", 2, 5) # TODO: add here minuses

def assert_correct_parsing(expression: MathExpression, operations_count: int, result: Number):
    operations = _.parse(expression)
    assert len(operations) == operations_count
    assert operations[0].execute() == D(str(result))

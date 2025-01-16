import pytest
from pytest import raises
from decimal import Decimal

from calculator import OldExpressionParser
from calculator.types import *
from calculator.exceptions import *


_ = OldExpressionParser
D = Decimal
P = Parenthesis
Op = Operator

r = _.raw_convert


def assert_correct_parsing(expression: MathExpression, operations_count: int, result: Number):
    operations = _.parse(expression)
    assert len(operations) == operations_count
    assert operations[0].execute() == D(str(result))


def test_is_operand():
    assert _._is_operand(Operation(Op.ADD, D(1), D(1))) == True
    assert _._is_operand(Decimal(1)) == True

def test_count_operators():
    assert _._count_operators(r("1 - 1")) == 1
    assert _._count_operators(r("1")) == 0

def test_count_operators_not_infix():
    with raises(NotInfixOperator): _._count_operators(r("123 + 3 + 5 +"))
    with raises(NotInfixOperator): _._count_operators(r("- 123 + 3 + 5"))
    with raises(NotInfixOperator): _._count_operators(r("123 + 3 + 5 + 4 +"))
    with raises(NotInfixOperator): _._count_operators(r("123 + 3 + + 5 + 4"))

def test_count_operands():
    assert _._count_operands(r("32141.321 2 2.0 0.3 .3123")) == 5
    assert _._count_operands(r("1 2 3 4 5 6")) == 6

def test_count_operators_and_operands__invalid_operators_count():
    with raises(InvalidOperatorsCount): _._validate_operators_and_operands(r("1 - 2 - 3 + 4 + 5 6"))

def test_convert_expression():
    I = D(1)
    expression = ['(', D(21), '+', D(334), '-', '(', D(1), '/', D(5), ')', ')']
    assert _._convert_expression("21 + 334 - (1 / 5)") == expression
    assert _._convert_expression("1 + 1") == ['(', D(1), '+', D(1), ')']
    assert _._convert_expression("1+1+-1/-1") == ['(', I, '+', I, '+', -I, '/', -I, ')']

def test_parse():
    assert_correct_parsing("2 + 3 - (1 / 5)", 3, 4.8)
    assert_correct_parsing("(2 + (3 + (4 + (6 + 8 / 1))))", 5, 23)

    assert_correct_parsing("1 + 1", 1, 2)
    assert_correct_parsing("10 - 5", 1, 5)
    assert_correct_parsing("2 * 3", 1, 6)
    assert_correct_parsing("8 / 4", 1, 2)

    assert_correct_parsing("2 + 3 * 4", 2, 14)  # 3 * 4 first, then 2 + 12
    assert_correct_parsing("(2 + 3) * 4", 2, 20)  # In parentheses first

    assert_correct_parsing("(1 + (2 * 3))", 2, 7)
    assert_correct_parsing("((1 + 2) * (3 + 4))", 3, 21)
    assert_correct_parsing("((2 + 3) - (1 / (5 + 5)))", 4, 4.9)

def test_merge_minuses():
    expression_1 = [P.OPENING, D(1), Op.DIV, Op.SUB, D(1), P.CLOSING]
    expression_2 = [P.OPENING, Op.SUB, D(1), P.CLOSING]
    assert _._merge_minuses(expression_1) == ['(', D(1), '/', D(-1), ')']
    assert _._merge_minuses(expression_2) == ['(', D(-1), ')']

def test_parse_negative():
    assert_correct_parsing("2 + -3 / -1", 2, 5)

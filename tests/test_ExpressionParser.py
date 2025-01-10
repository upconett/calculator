import pytest
from pytest import raises

from calculator import ExpressionParser
from calculator.exceptions import *


_ = ExpressionParser


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

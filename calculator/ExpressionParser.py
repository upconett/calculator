from typing import *
from string import digits

from calculator import Operation
from calculator.types import *
from calculator.enums import *
from calculator.exceptions import *


DIGITS = digits
PARENTHESES = ['(', ')']
OPERATORS = ['+', '-', '*', '/']
POINT = '.'


def validate(expression: MathExpression):
    _check_invalid_simbols(expression)
    levels_number = _count_levels(expression)
    operators, operands = _count_operators_and_operands(expression)


def parse(expression: MathExpression) -> List[Operation]:
    ...

def _count_levels(expression: MathExpression) -> int:
    return _LevelsOf(expression).count()


class _LevelsOf:
    def __init__(self, expression: MathExpression):
        self.expression = expression
        self.max_level = self.level = 0

    def count(self) -> int:
        for char in self.expression:
            if _is_parentheses(char):
                self._update_level(char)
        self._check_if_closed()
        return self.max_level

    def _update_level(self, char: str):
        self._change_level(char)
        self._check_if_level_not_negative()
        self._update_max_level()

    def _change_level(self, parentheses: str) -> int:
        match parentheses:
            case '(': self.level += 1
            case ')': self.level -= 1

    def _check_if_level_not_negative(self):
        if self.level < 0:
            raise InvalidParentheses("Not opened")

    def _check_if_closed(self):
        if self.level != 0:
            raise InvalidParentheses("Not closed")

    def _update_max_level(self):
        self.max_level = max(self.level, self.max_level)


def _count_operators(expression: MathExpression) -> int:
    operators = 0
    for i in range(len(expression)):
        char = expression[i]
        if _is_operator(char):
            for j in range(i+1, len(expression)):
                if j == len(expression): break
                right_char = expression[j]
                if _is_part_of_operand(right_char):
                    break
                if _is_operator(right_char):
                    raise NotInfixOperator(right_char)
            else:
                raise NotInfixOperator("right side")
            for k in range(i-1, -1, -1):
                left_char = expression[k]
                if _is_part_of_operand(left_char):
                    break
                if _is_operator(left_char):
                    raise NotInfixOperator(i, k, left_char)
            else:
                raise NotInfixOperator("left side")
            operators += 1
    return operators

def _count_operands(expression: MathExpression) -> int:
    operands = 0
    current_operand = ''
    for char in expression:
        if _is_part_of_operand(char):
            current_operand += char
        elif current_operand:
            try:
                float(current_operand)
                operands += 1
            except Exception:
                raise InvalidOperand(current_operand)
            current_operand = ''
    try:
        float(current_operand)
        operands += 1
    except Exception as ex:
        raise InvalidOperand(current_operand)
    return operands

def _count_operators_and_operands(expression: MathExpression) -> Tuple[int, int]:
    operators = _count_operators(expression)
    operands = _count_operands(expression)
    if operands != (operators + 1):
        raise InvalidOperatorsCount
    return (operators, operands)

def _check_invalid_simbols(expression: MathExpression) -> None:
    for char in expression:
        if _is_invalid(char):
            raise InvalidSimbol(char)

def _is_parentheses(char: str) -> bool:
    return char in PARENTHESES

def _is_part_of_operand(char: str) -> bool:
    return char in (DIGITS + POINT)

def _is_operator(char: str) -> bool:
    return char in OPERATORS

def _is_whitespace(char: str) -> bool:
    return char == ' '

def _is_invalid(char: str) -> bool:
    return not any((
        _is_parentheses(char),
        _is_part_of_operand(char),
        _is_operator(char),
        _is_whitespace(char),
    ))

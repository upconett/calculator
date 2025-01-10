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
    for simbol in expression:
        if _is_parentheses(simbol):
            ...
        elif simbol == POINT:
            ...
        else:
            raise InvalidInput

def parse(expression: MathExpression) -> List[Operation]:
    ...

def _count_levels(expression: MathExpression) -> int:
    max_level = level = 0
    for simbol in expression:
        if _is_parentheses(simbol):
            if simbol == '(':
                level += 1
            else:
                level -= 1
            if level < 0:
                raise InvalidParentheses
            max_level = max(level, max_level)
    if level != 0:
        raise InvalidParentheses

    return max_level

def _count_operators(expression: MathExpression) -> int:
    operators = 0
    for i in range(len(expression)):
        simbol = expression[i]
        if _is_operator(simbol):
            for j in range(i+1, len(expression)):
                if j == len(expression): break
                right_simbol = expression[j]
                if _is_part_of_operand(right_simbol):
                    break
                if _is_operator(right_simbol):
                    raise NotInfixOperator(right_simbol)
            else:
                raise NotInfixOperator("right side")
            for k in range(i-1, -1, -1):
                left_simbol = expression[k]
                if _is_part_of_operand(left_simbol):
                    break
                if _is_operator(left_simbol):
                    raise NotInfixOperator(i, k, left_simbol)
            else:
                raise NotInfixOperator("left side")
            operators += 1
    return operators

def _count_operands(expression: MathExpression) -> int:
    operands = 0
    current_operand = ''
    for simbol in expression:
        if _is_part_of_operand(simbol):
            current_operand += simbol
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

def _is_parentheses(simbol: str) -> bool:
    return simbol in PARENTHESES

def _is_part_of_operand(simbol: str) -> bool:
    return simbol in (DIGITS + POINT)

def _is_operator(simbol: str) -> bool:
    return simbol in OPERATORS

def _is_whitespace(simbol: str) -> bool:
    return simbol == ' '

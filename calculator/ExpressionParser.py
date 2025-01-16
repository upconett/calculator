from typing import *
from string import digits

from calculator.types import *
from calculator.exceptions import *


DIGITS = digits
PARENTHESES = ['(', ')']
OPERATORS = ['+', '-', '*', '/']
POINT = '.'


def parse(expression: MathExpression) -> List[ExpressionMember]:
    expression = _clean_expression(expression)
    _check_unknown_simbols(expression)
    members = _parse_expression(expression)
    members = _merge_minuses(members)
    return members

def raw_parse(expression: MathExpression) -> List[ExpressionMember]:
    return _parse_expression(expression)


def _clean_expression(expression: MathExpression) -> MathExpression:
    return expression.replace(' ', '')

def _check_unknown_simbols(expression: MathExpression):
    for char in expression:
        if _is_invalid(char):
            raise UnknownSimbol(char)

def _parse_expression(expression: MathExpression) -> List[ExpressionMember]:
    members = []
    i = 0
    while i < len(expression):
        char = expression[i]
        if _is_parenthesis(char):
            _add_parenthesis(members, char)
        if _is_operator(char):
            _add_operator(members, char)
        if _is_part_of_operand(char):
            i = _add_operand(members, expression, i)
        i += 1
    members = _add_outer_parenthesis(members)
    return members

def _add_parenthesis(members: List[ExpressionMember], char: str) -> None:
    members.append(Parenthesis.determine(char))

def _add_operator(members: List[ExpressionMember], char: str) -> None:
    members.append(Operator.determine(char))

def _add_operand(members: List[ExpressionMember], expression: MathExpression, start_index: int) -> int:
    operand, continue_index, = _read_operand(expression, start_index)
    members.append(operand)
    return continue_index

def _read_operand(expression: MathExpression, start_index: int) -> Tuple[Decimal, int]:
    if not _is_part_of_operand(expression[start_index]):
        raise IsNotOperand(expression[start_index])
    str_operand = ""
    i = start_index
    while _operand_not_ended(expression, i):
        str_operand += expression[i]
        i += 1
    return (Decimal(str_operand), i-1)

def _operand_not_ended(expression: MathExpression, index: int) -> bool:
    return (
        index < len(expression) 
        and _is_part_of_operand(expression[index])
    )

def _add_outer_parenthesis(members: List[ExpressionMember]) -> List[ExpressionMember]:
    new_members = [Parenthesis.OPENING] + members
    new_members = new_members + [Parenthesis.CLOSING]
    return new_members

def _merge_minuses(members: List[ExpressionMember]) -> List[ExpressionMember]:
    merged_members = members.copy()
    i = 0
    while i < len(merged_members)-2:
        _try_to_merge(merged_members, i)
        _try_to_add_zero(merged_members, i)
        i += 1
    return merged_members

def _try_to_merge(members: List[ExpressionMember], index: int):
    if (
        _pattern__operator_minus_decimal(members, index)
        or _pattern__parenthesis_minus_decimal(members, index)
    ):
        _merge_minus_after_index(index, members)

def _try_to_add_zero(members: List[ExpressionMember], index: int):
    if (
        _pattern__parenthesis_minus_parenthesis(members, index)
    ):
        members.insert(index+1, Decimal(0))

def _pattern__parenthesis_minus_parenthesis(members: List[ExpressionMember], on_index: int) -> bool:
    first_member = members[on_index]
    second_member = members[on_index+1]
    third_member = members[on_index+2]
    return (
        first_member == Parenthesis.OPENING
        and second_member == '-'
        and third_member == Parenthesis.OPENING
    )


def _merge_minus_after_index(index: int, members: List[ExpressionMember]):
        members[index+2] = (-members[index+2])
        members.pop(index+1)

def _pattern__operator_minus_decimal(members: List[ExpressionMember], on_index: int) -> bool:
    return _pattern__something_minus_decimal(members, Operator, on_index)

def _pattern__parenthesis_minus_decimal(members: List[ExpressionMember], on_index: int) -> bool:
    return _pattern__something_minus_decimal(members, Parenthesis, on_index)

def _pattern__something_minus_decimal(members: List[ExpressionMember], thing: Type, on_index: int) -> bool:
    first_member = members[on_index]
    second_member = members[on_index+1]
    third_member = members[on_index+2]
    return (
        isinstance(first_member, thing)
        and second_member == '-'
        and isinstance(third_member, Decimal)
    )

def _is_parenthesis(char: str) -> bool:
    return char in PARENTHESES

def _is_part_of_operand(char: str) -> bool:
    return char in (DIGITS + POINT)

def _is_operator(char: str) -> bool:
    return char in OPERATORS

def _is_whitespace(char: str) -> bool:
    return char == ' '

def _is_invalid(char: str) -> bool:
    return not any((
        _is_parenthesis(char),
        _is_part_of_operand(char),
        _is_operator(char),
        _is_whitespace(char),
    ))

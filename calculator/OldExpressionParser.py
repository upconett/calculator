from typing import *
from string import digits

from calculator.types.Operation import Operation
from calculator.types.aliases import *
from calculator.types.enums import *
from calculator.exceptions import *



DIGITS = digits
PARENTHESES = ['(', ')']
OPERATORS = ['+', '-', '*', '/']
POINT = '.'


def parse(expression: MathExpression) -> List[Operation]:
    list_of_members = _convert_expression(expression)

    operations = []
    while len(list_of_members) > 1:
        _clean_parenthesis(list_of_members)
        for i in range(len(list_of_members)):
            try:
                x = _get_next_operand(list_of_members, i)
                op = _get_next_operator(list_of_members, i+1)
                y = _get_next_operand(list_of_members, i+2)
                next_simbol = list_of_members[i+3]
                if (
                    _is_weak_operator(op)
                    and _is_strong_operator(next_simbol)
                ):
                    op = _get_next_operator(list_of_members, i+3)
                    z = _get_next_operand(list_of_members, i+4)
                    operation = Operation(op, y, z)
                    _replace_with_operation(list_of_members, i+2, operation)
                else:
                    operation = Operation(op, x, y)
                    _replace_with_operation(list_of_members, i, operation)
                operations.append(operation)
                break
            except (IsNotOperand, IsNotOperator):
                while len(list_of_members) > i+1 and not list_of_members[i+1] == Parenthesis.OPENING: # skip to next openning parenthesis
                    i += 1
            except IndexError:
                break
    operations.reverse()
    return operations

def raw_convert(expression: MathExpression) -> List[ExpressionMember]:
    return _parse_expression(expression)


def _clean_expression(expression: MathExpression) -> CleanedExpression:
    return expression.replace(' ', '')

def _clean_parenthesis(expression: List[ExpressionMember]):
    for i in range(len(expression)-2):
        if (
            expression[i] == Parenthesis.OPENING
            and _is_operand(expression[i+1])
            and expression[i+2] == Parenthesis.CLOSING
        ):
            expression.pop(i+2); expression.pop(i) # removing parentheses

def _replace_with_operation(exp: List[ExpressionMember], index: int, operation: Operation):
    for _ in range(3):
        exp.pop(index)
    exp.insert(index, operation)

def _is_strong_operator(op: Any) -> bool:
    return isinstance(op, Operator) and (op in ['*', '/'])

def _is_weak_operator(op: Any) -> bool:
    return isinstance(op, Operator) and (op in ['+', '-'])

def _get_next_operand(expression: List[ExpressionMember], index: int) -> Operand:
    simbol = expression[index]
    if not _is_operand(simbol):
        raise IsNotOperand(simbol)
    return simbol

def _get_next_operator(expression: List[ExpressionMember], index: int) -> Operator:
    simbol = expression[index]
    if not isinstance(simbol, Operator):
        raise IsNotOperator(simbol)
    return simbol

def _convert_expression(expression: MathExpression) -> List[ExpressionMember]:
    expression = _clean_expression(expression)
    _check_invalid_simbols(expression)
    converted = _parse_expression(expression)
    _merge_minuses(converted)
    _validate_levels(converted)
    _validate_operators_and_operands(converted)
    return converted

def _parse_expression(expression: CleanedExpression) -> List[ExpressionMember]:
    converted = [Parenthesis.OPENING]
    i = 0
    while i < len(expression):
        char = expression[i]
        if _is_parenthesis(char):
            converted.append(Parenthesis.determine(char))
        if _is_operator(char):
            converted.append(Operator.determine(char))
        if _is_part_of_operand(char):
            operand, i = _read_operand(expression, i)
            converted.append(operand)
            continue
        i += 1
    converted.append(Parenthesis.CLOSING)
    return converted

def _merge_minuses(expression: List[ExpressionMember]) -> List[ExpressionMember]:
    i = 0
    while i < (len(expression)-2):
        if (
            _is_operator_minus_decimal(expression, i)
            or _is_parenthesis_minus_decimal(expression, i)
        ):
            expression[i+2] = (Decimal(0) - expression[i+2])
            expression.pop(i+1)
        i += 1
    return expression

    
def _is_operator_minus_decimal(expression: List[ExpressionMember], offset_index: int) -> bool:
    i = offset_index
    first_member = expression[i]
    second_member = expression[i+1]
    third_member = expression[i+2]
    return (
        isinstance(first_member, Operator)
        and second_member == '-'
        and isinstance(third_member, Decimal)
    )

def _is_parenthesis_minus_decimal(expression: List[ExpressionMember], offset_index: int) -> bool:
    i = offset_index
    first_member = expression[i]
    second_member = expression[i+1]
    third_member = expression[i+2]
    return (
        isinstance(first_member, Parenthesis)
        and second_member == '-'
        and isinstance(third_member, Decimal)
    )

def _read_operand(expression: MathExpression, start_index: int) -> Tuple[Decimal, int]:
    str_operand = ""
    if not _is_part_of_operand(expression[start_index]):
        raise IsNotOperand
    i = start_index
    while i < len(expression) and _is_part_of_operand(expression[i]):
        str_operand += expression[i]
        i += 1
    return (Decimal(str_operand), i)

def _add_operand(operands: List[List[Decimal]], operand: Decimal, level: int):
    try:
        operands[level].append(operand)
    except IndexError:
        while len(operands)-1 < level:
            operands.append([])
        _add_operand(operands, operand, level)

def _add_operator(operators: List[List[Operator]], char: str, level: int):
    try:
        operators[level].append(Operator.determine(char))
    except IndexError:
        while len(operators)-1 < level:
            operators.append([])
        _add_operator(operators, char, level)

def _validate_levels(expression: List[ExpressionMember]) -> int:
    _LevelsOf(expression).validate()

class _LevelsOf:
    def __init__(self, expression: List[ExpressionMember]):
        self.expression = expression
        self.max_level = self.level = 0

    def validate(self) -> None:
        for member in self.expression:
            if isinstance(member, Parenthesis):
                self._update_level(member)
        self._check_if_closed()

    def _update_level(self, parenthesis: Parenthesis):
        self._change_level(parenthesis)
        self._check_if_level_not_negative()
        self._update_max_level()

    def _change_level(self, parenthesis: Parenthesis):
        match parenthesis:
            case Parenthesis.OPENING: self.level += 1
            case Parenthesis.CLOSING: self.level -= 1

    def _check_if_level_not_negative(self):
        if self.level < 0:
            raise InvalidParentheses("Not opened")

    def _check_if_closed(self):
        if self.level != 0:
            raise InvalidParentheses("Not closed")

    def _update_max_level(self):
        self.max_level = max(self.level, self.max_level)


def _count_operators(expression: List[ExpressionMember]) -> int:
    operators = 0
    i = 1
    while i < (len(expression)-1):
        member = expression[i]
        if isinstance(member, Operator):
            previous = expression[i-1]
            next = expression[i+1]
            if isinstance(previous, Operator) or previous == Parenthesis.OPENING:
                raise NotInfixOperator("left side")
            if isinstance(next, Operator) or next == Parenthesis.CLOSING:
                raise NotInfixOperator("right side")
            operators += 1
        i += 1
    return operators

def _count_operands(expression: List[ExpressionMember]) -> int:
    return sum(_is_operand(x) for x in expression)

def _validate_operators_and_operands(expression: List[ExpressionMember]) -> Tuple[int, int]:
    operators = _count_operators(expression)
    operands = _count_operands(expression)
    if operands != (operators + 1):
        raise InvalidOperatorsCount
    return (operators, operands)

def _check_invalid_simbols(expression: MathExpression) -> None:
    for char in expression:
        if _is_invalid(char):
            raise UnknownSimbol(char)

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

def _is_operand(member: ExpressionMember) -> bool:
    return isinstance(member, Union[Decimal, Operation])

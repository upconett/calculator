from typing import *
from string import digits

from calculator.Operation import Operation
from calculator.types import *
from calculator.enums import *
from calculator.exceptions import *


DIGITS = digits
PARENTHESES = ['(', ')']
OPERATORS = ['+', '-', '*', '/']
POINT = '.'


def parse(expression: MathExpression) -> List[Operation]:
    """
    Algorithm as follows
    You edit the expression string all the time you find valid "minimal expression"
    You try to read "minimal expression" and if it is not "minimal" - handle exception
    WHEN READING:
        1. REWRITE _read_operand() to work with _0, _1, _2,... (these are operations, which were parsed earlier)
    - - START - -
    If you read:
    SUCCESFULLY
        1. append operations list with new Operation
        2. check if there is only one operand, like "(2)" then just remove parentheses and move to - - START - -
        2. replace the whole expression string (including parentheses) with "_{op_index}"
        3. increment op_index
    ON FAILURE (exception)
        1. Skip to the next openning bracket '('
        2. Try again
    FINALLY
        1. reverse the list operations (so that outer operation is of index 0)
        2. return operations
    """
    list_of_members = _convert_expression(expression)

    operations = []
    while len(list_of_members) > 1:
        _clean_parenthesis(list_of_members)
        for i in range(len(list_of_members)):
            print(list_of_members)
            try:
                x = _get_next_operand(list_of_members, i)
                op = _get_next_operator(list_of_members, i+1)
                y = _get_next_operand(list_of_members, i+2)
                next_simbol = list_of_members[i+3]
                if (
                    _is_weak_operator(op)
                    and _is_strong_operator(next_simbol)
                    and isinstance(list_of_members[i+4], Decimal)
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


def _clean_expression(expression: MathExpression) -> MathExpression:
    return expression.replace(' ', '')

def _clean_parenthesis(exp: List[ExpressionMember]):
    i = 0
    while i < len(exp)-2:
        try:
            # print("try clean", end=" ")
            if (
                exp[i] == Parenthesis.OPENING
                and _is_operand(exp[i+1])
                and exp[i+2] == Parenthesis.CLOSING
            ):
                # print("cleaned")
                exp.pop(i+2); exp.pop(i) # removing parentheses
            i += 1
        except IndexError:
            raise IndexError(f"{i}, {len(exp)-2}")


def _replace_with_operation(exp: List[ExpressionMember], index: int, operation: Operation):
    for _ in range(3):
        exp.pop(index)
    exp.insert(index, operation)

def _is_strong_operator(op: Any) -> bool:
    return isinstance(op, Operator) and (op in ['*', '/'])

def _is_weak_operator(op: Any) -> bool:
    return isinstance(op, Operator) and (op in ['+', '-'])

def _is_next_operator(exp: List[ExpressionMember], index: int) -> bool:
    return isinstance(exp[index], Operator)

def _get_next_operand(exp: List[ExpressionMember], index: int) -> Decimal:
    simbol = exp[index]
    if not _is_operand(simbol):
        raise IsNotOperand(simbol)
    return simbol

def _get_next_operator(exp: List[ExpressionMember], index: int) -> Operator:
    simbol = exp[index]
    if not isinstance(simbol, Operator):
        raise IsNotOperator(simbol)
    return simbol

def _convert_expression(expression: MathExpression) -> List[ExpressionMember]:
    expression = _clean_expression(expression)
    _check_invalid_simbols(expression)
    converted = _convert_cleaned_expression(expression)
    _validate_levels(converted)
    _validate_operators_and_operands(converted)
    return converted


def _convert_cleaned_expression(expression: CleanedExpression) -> ConvertedExpression:
    converted = [Parenthesis.OPENING]
    counter = 0
    i = 0
    while i < len(expression) and counter < 200:
        counter += 1
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
    _merge_minuses(converted)
    return converted

def _merge_minuses(expression: ConvertedExpression) -> ConvertedExpression:
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

    
def _is_operator_minus_decimal(expression: ConvertedExpression, offset_index: int) -> bool:
    i = offset_index
    first_member = expression[i]
    second_member = expression[i+1]
    third_member = expression[i+2]
    print(first_member, second_member, third_member)
    return (
        isinstance(first_member, Operator)
        and second_member == '-'
        and isinstance(third_member, Decimal)
    )

def _is_parenthesis_minus_decimal(expression: ConvertedExpression, offset_index: int) -> bool:
    i = offset_index
    first_member = expression[i]
    second_member = expression[i+1]
    third_member = expression[i+2]
    print(first_member, second_member, third_member)
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

def _read_operator(expression: MathExpression, start_index: int) -> Tuple[Operator, int]:
    return (Operator.determine(expression[start_index]), start_index+1)

def _get_operands(expression: MathExpression) -> List[List[Number]]:
    level = 0
    operands = []
    for i in range(len(expression)):
        char = expression[i]
        if _is_parenthesis(char):
            level += 1 if char == '(' else -1
        if _is_part_of_operand(char):
            operand, i = _read_operand(expression, i)
            _add_operand(operands, operand, level)
    return operands

def _add_operand(operands: List[List[Decimal]], operand: Decimal, level: int):
    try:
        operands[level].append(operand)
    except IndexError:
        while len(operands)-1 < level:
            operands.append([])
        _add_operand(operands, operand, level)


def _get_operators(expression: MathExpression) -> List[List[Operator]]:
    level = 0
    operators = []
    for char in expression:
        if _is_parenthesis(char):
            level += 1 if char == '(' else -1
        if _is_operator(char):
            _add_operator(operators, char, level)
    return operators

def _add_operator(operators: List[List[Operator]], char: str, level: int):
    try:
        operators[level].append(Operator.determine(char))
    except IndexError:
        while len(operators)-1 < level:
            operators.append([])
        _add_operator(operators, char, level)
    

# region validation

def _validate_levels(expression: ConvertedExpression) -> int:
    _LevelsOf(expression).validate()

class _LevelsOf:
    def __init__(self, expression: ConvertedExpression):
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


def _count_operators(expression: ConvertedExpression) -> int:
    operators = 0
    i = 1
    while i < (len(expression)-1):
        member = expression[i]
        if isinstance(member, Operator):
            previous = expression[i-1]
            next = expression[i+1]
            print(previous, member, next)
            if isinstance(previous, Operator) or previous == Parenthesis.OPENING:
                raise NotInfixOperator("left side")
            if isinstance(next, Operator) or next == Parenthesis.CLOSING:
                raise NotInfixOperator("right side")
            operators += 1
        i += 1
    return operators

def _raw_convert(expression: MathExpression) -> ConvertedExpression:
    converted = [Parenthesis.OPENING]
    counter = 0
    i = 0
    while i < len(expression) and counter < 200:
        counter += 1
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


def _count_operands(expression: ConvertedExpression) -> int:
    return sum(_is_operand(x) for x in expression)

def _try_add_operand(current_operand: str, operands: int) -> int:
    try:
        float(current_operand)
        return operands + 1
    except Exception:
        raise InvalidOperand(current_operand)

def _validate_operators_and_operands(expression: ConvertedExpression) -> Tuple[int, int]:
    operators = _count_operators(expression)
    operands = _count_operands(expression)
    if operands != (operators + 1):
        raise InvalidOperatorsCount
    return (operators, operands)

def _check_invalid_simbols(expression: MathExpression) -> None:
    for char in expression:
        if _is_invalid(char):
            raise InvalidSimbol(char)

# endregion

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

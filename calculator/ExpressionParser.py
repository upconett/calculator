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

ExpressionMember: TypeAlias = Union[Operator, Decimal, Parenthesis]



def validate(expression: MathExpression) -> None:
    expression = _clean_expression(expression)
    _check_invalid_simbols(expression)
    levels_number = _count_levels(expression)
    operators, operands = _count_operators_and_operands(expression)


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
    expression = _clean_expression(expression)
    operations = []
    exp = [] # expression that is not string but list of Operands, Operators and Parentheses
    exp = _convert_expression(expression)
    while len(exp) > 1:
        _clean_parenthesis(exp)
        for i in range(len(exp)):
            print(exp)
            try:
                x = _get_next_operand(exp, i)
                op = _get_next_operator(exp, i+1)
                y = _get_next_operand(exp, i+2)
                next_simbol = exp[i+3]
                if (
                    _is_weak_operator(op)
                    and _is_strong_operator(next_simbol)
                    and isinstance(exp[i+4], Decimal)
                ):
                    op = _get_next_operator(exp, i+3)
                    z = _get_next_operand(exp, i+4)
                    operation = Operation(op, y, z)
                    _replace_with_operation(exp, i+2, operation)
                else:
                    operation = Operation(op, x, y)
                    _replace_with_operation(exp, i, operation)
                operations.append(operation)
                i -= 1 # go back 1 unit to use freshly made operation as a new operand
            except (IsNotOperand, IsNotOperator):
                while len(exp) > i+1 and not exp[i+1] == Parenthesis.OPENING: # skip to next openning parenthesis
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
                and (isinstance(exp[i+1], Union[Operation, Decimal]))
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
    if not isinstance(simbol, Union[Decimal, Operation]):
        raise IsNotOperand(simbol)
    return simbol

def _get_next_operator(exp: List[ExpressionMember], index: int) -> Operator:
    simbol = exp[index]
    if not isinstance(simbol, Operator):
        raise IsNotOperator(simbol)
    return simbol

def _convert_expression(expression: MathExpression) -> List[ExpressionMember]:
    expression = expression.replace(' ', '')
    converted = [Parenthesis.OPENING]
    i = 0
    counter = 0
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

def _count_levels(expression: MathExpression) -> int:
    return _LevelsOf(expression).count()

class _LevelsOf:
    def __init__(self, expression: MathExpression):
        self.expression = expression
        self.max_level = self.level = 0

    def count(self) -> int:
        for char in self.expression:
            if _is_parenthesis(char):
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

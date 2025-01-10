from typing import *
from enum import Enum
from dataclasses import dataclass
from decimal import Decimal

from inline_calculator.exceptions import *


Number: TypeAlias = Union[int, float, Decimal]
StrResult: TypeAlias = str
MathExpression: TypeAlias = str


class Operator(Enum):
    """ Enum representing arithmetical operators. """
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'


@dataclass
class Operation:
    op: Operator
    x: Union[Decimal, "Operation"]
    y: Union[Decimal, "Operation"]

    def execute(self) -> Decimal:
        self._execute_inner()
        x, y = self.x, self.y
        match self.op:
            case Operator.ADD: return x + y
            case Operator.SUB: return x - y
            case Operator.MUL: return x * y
            case Operator.DIV: return x / y
    
    def _execute_inner(self):
        """
        Execute inner operations
        if arguments are such.
        """
        self.x = self._execute_if_is_operation(self.x)
        self.y = self._execute_if_is_operation(self.y)

    def _execute_if_is_operation(self, arg: Union[Decimal, "Operation"]) -> Decimal:
        if isinstance(arg, Operation):
            return arg.execute()
        return arg


class Calculator:
    def add(self, x: Number, y: Number) -> Number:
        return self._operate(Operator.ADD, x, y)

    def subtract(self, x: Number, y: Number) -> Number:
        return self._operate(Operator.SUB, x, y)

    def multiply(self, x: Number, y: Number) -> Number:
        return self._operate(Operator.MUL, x, y)

    def divide(self, x: Number, y: Number) -> Number:
        return self._operate(Operator.DIV, x, y)

    def calculate(self, expression: MathExpression) -> Number:
        self._validate_expression(expression)
        operations = self._parse_expression(expression)
        result = self._execute_operations(operations)
        return self._decimal_to_number(result)

    def _validate_expression(self, expression: MathExpression) -> None:
        ...

    def _parse_expression(self, expression: MathExpression) -> List[Operation]:
        ...

    def _execute_operations(self, operations: List[Operation]) -> Decimal:
        return self._execute_recursively(operations)

    def _execute_recursively(self, operations: List[Operation]) -> Decimal:
        try:
            # Retrieving only first (outer) operation to start recursive execution.
            first_operation = self._get_first_operation(operations)
            return first_operation.execute()
        except NoOperations:
            return Decimal(0)

    def _get_first_operation(self, operations: List[Operation]) -> Operation:
        if len(operations) >= 1:
            return operations[0]
        raise NoOperations

    def _operate(self, op: Operator, x: Number, y: Number) -> StrResult:
        x, y = self._ensure_decimal(x, y)
        result = Operation(op, x, y).execute()
        return self._decimal_to_number(result)

    def _ensure_decimal(self, x: Number, y: Number) -> Tuple[Decimal, Decimal]:
        x = self._number_to_decimal(x)
        y = self._number_to_decimal(y)
        return x, y

    def _number_to_decimal(self, number: Number) -> Decimal:
        return Decimal(str(number))

    def _decimal_to_number(self, decimal: Decimal) -> Number:
        number = round(float(decimal), 10)
        if round(number) == number:
            number = int(number)
        return number
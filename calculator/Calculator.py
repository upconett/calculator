from typing import *
from decimal import Decimal

from calculator.types import *
from calculator.exceptions import *
from calculator import ExpressionParser, ExpressionAnalyzer


class Calculator:

    def add(self, x: Number, y: Number, return_decimal: bool = False) -> Number:
        return self._operate(Operator.ADD, x, y, return_decimal)

    def subtract(self, x: Number, y: Number, return_decimal: bool = False) -> Number:
        return self._operate(Operator.SUB, x, y, return_decimal)

    def multiply(self, x: Number, y: Number, return_decimal: bool = False) -> Number:
        return self._operate(Operator.MUL, x, y, return_decimal)

    def divide(self, x: Number, y: Number, return_decimal: bool = False) -> Number:
        return self._operate(Operator.DIV, x, y, return_decimal)


    def calculate(self, expression: MathExpression, return_decimal: bool = False) -> Number:
        expression_members = ExpressionParser.parse(expression)
        analyzed_expression = ExpressionAnalyzer.analyze(expression_members)
        result = analyzed_expression.outer_operation.execute()
        if not return_decimal:
            result = self._decimal_to_number(result)
        return result


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

    def _operate(self, op: Operator, x: Number, y: Number, return_decimal: bool) -> Number | Decimal:
        x, y = self._ensure_decimal(x, y)
        result = Operation(op, x, y).execute()
        if not return_decimal:
            result = self._decimal_to_number(result)
        return result

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

from dataclasses import dataclass

from calculator.types import *
from calculator.enums import *


@dataclass
class Operation:
    op: Operator
    x: Operand
    y: Operand
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

    def _execute_if_is_operation(self, arg: Operand) -> Decimal:
        if isinstance(arg, Operation):
            return arg.execute()
        return arg

    def __repr__(self) -> str:
        x = float(self.x) if isinstance(self.x, Decimal) else self.x
        y = float(self.y) if isinstance(self.y, Decimal) else self.y
        return f"Op({self.op.value}, {x}, {y})"

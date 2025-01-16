from typing import *
from decimal import Decimal

if TYPE_CHECKING:
    from calculator.types.Operation import Operation
    from calculator.types.enums import Operator, Parenthesis


Number: TypeAlias = Union[int, float, Decimal]
Operand: TypeAlias = Union[Decimal, "Operation"]
MathExpression: TypeAlias = str
CleanedExpression: TypeAlias = str
ExpressionMember: TypeAlias = Union["Operator", "Operand", "Parenthesis"]

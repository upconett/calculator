from typing import *
from dataclasses import dataclass

from calculator.types.aliases import ExpressionMember
from calculator.types.Operation import Operation


@dataclass
class AnalyzedExpression:
    members: List[ExpressionMember]
    parenthesis_depth: int
    operators_count: int
    primary_operands_count: int
    outer_operation: Operation

from typing import *

from calculator.types import *
from calculator.exceptions import *


def analyze(expression_members: List[ExpressionMember]) -> AnalyzedExpression:
    return AnalyzedExpression(
        members=expression_members,
        parenthesis_depth=_get_parenthesis_depth(expression_members),
        operators_count=_count_operators(expression_members),
        primary_operands_count=_count_primary_operands(expression_members),
        outer_operation=_simplify_and_return_outer_operation(expression_members)
    )

def _get_parenthesis_depth(members: List[ExpressionMember]) -> int:
    return _ParenthesesIn(members).count_depth()

def _count_operators(members: List[ExpressionMember]) -> int:
    return _OperatorsIn(members).count()

def _count_primary_operands(members: List[ExpressionMember]) -> int:
    return _OperandsIn(members).count()

def _simplify_and_return_outer_operation(members: List[ExpressionMember]) -> Operation:
    return _SimplifierOf(members).simplify().get_outer_operation()
    

class _ParenthesesIn:
    def __init__(self, members: List[ExpressionMember]):
        self.members = members
        self.max_depth = self.depth = 0

    def count_depth(self) -> int:
        for member in self.members:
            if isinstance(member, Parenthesis):
                self._update_depth(member)
        self._check_if_closed()

    def _update_depth(self, parenthesis: Parenthesis):
        self._change_depth(parenthesis)
        self._check_if_depth_not_negative()
        self._update_max_depth()

    def _change_depth(self, parenthesis: Parenthesis):
        match parenthesis:
            case Parenthesis.OPENING: self.depth += 1
            case Parenthesis.CLOSING: self.depth -= 1

    def _check_if_depth_not_negative(self):
        if self.depth < 0:
            raise InvalidParentheses("Not opened")

    def _check_if_closed(self):
        if self.depth != 0:
            raise InvalidParentheses("Not closed")

    def _update_max_depth(self):
        self.max_depth = max(self.depth, self.max_depth)


class _OperatorsIn:
    def __init__(self, members: List[ExpressionMember]):
        self.members = members
        self.operators = 0

    def count(self) -> int:
        for i in range(1, len(self.members)-1):
            member = self.members[i]
            if isinstance(member, Operator):
                self._check_members_around(i)
                self.operators += 1
        return self.operators

    def _check_members_around(self, index: int):
        self._check_previous_member(index)
        self._check_next_member(index)

    def _check_previous_member(self, index: int):
        if self._violates_infix(index-1, Parenthesis.OPENING):
            raise NotInfixOperator(self.members[index], index)

    def _check_next_member(self, index: int):
        if self._violates_infix(index+1, Parenthesis.CLOSING):
            raise NotInfixOperator(self.members[index], index)

    def _violates_infix(self, index: int, parenthesis: Parenthesis) -> bool:
        member = self.members[index]
        return (
            isinstance(member, Operator)
            or member == parenthesis
        )


class _OperandsIn:
    def __init__(self, members: List[ExpressionMember]):
        self.members = members
        self.operands = 0

    def count(self) -> int:
        return sum(
            _is_operand(member)
            for member in self.members
        )


class _SimplifierOf:
    def __init__(self, members: List[ExpressionMember]):
        self.members = members
        self.operations = []
    
    def simplify(self) -> "_SimplifierOf":
        while len(self.members) > 1:
            self._clean_parentheses()
            for i in range(len(self.members)):
                try:
                    x = self._get_if_operand(i)
                    op = self._get_if_operator(i+1)
                    y = self._get_if_operand(i+2)
                    next_simbol = self.members[i+3]
                    if (
                        _is_weak_operator(op)
                        and _is_strong_operator(next_simbol)
                    ):
                        op = self._get_if_operator(i+3)
                        z = self._get_if_operand(i+4)
                        operation = Operation(op, y, z)
                        self._replace_with_operation(i+2, operation)
                    else:
                        operation = Operation(op, x, y)
                        self._replace_with_operation(i, operation)
                    self.operations.append(operation)
                    break
                except (IsNotOperand, IsNotOperator):
                    while len(self.members) > i+1 and not self.members[i+1] == Parenthesis.OPENING: # skip to next openning parenthesis
                        i += 1
                except IndexError:
                    break
        self.operations.reverse()
        return self
    
    def get_outer_operation(self) -> Operation:
        return self.operations[0]

    def _get_if_operand(self, index: int) -> Operand:
        member = self.members[index]
        if not _is_operand(member):
            raise IsNotOperand(member)
        return member

    def _get_if_operator(self, index: int) -> Operator:
        member = self.members[index]
        if not isinstance(member, Operator):
            raise IsNotOperator(member)
        return member

    def _clean_parentheses(self):
        for i in range(1, len(self.members)-1):
            if self._is_operand_enclosed_in_parentheses(i):
                self._remove_parentheses_around(i)

    def _is_operand_enclosed_in_parentheses(self, index: int) -> bool:
        return (
            self.members[index-1] == Parenthesis.OPENING
            and _is_operand(self.members[index])
            and self.members[index+1] == Parenthesis.CLOSING
        )
    
    def _remove_parentheses_around(self, index: int):
        self.members.pop(index+1)
        self.members.pop(index-1)

    def _replace_with_operation(self, index: int, operation: Operation):
        for _ in range(3):
            self.members.pop(index)
        self.members.insert(index, operation)

def _is_operand(member: ExpressionMember) -> bool:
    return isinstance(member, Union[Decimal, Operation])

def _is_strong_operator(op: ExpressionMember) -> bool:
    return isinstance(op, Operator) and (op in ['*', '/'])

def _is_weak_operator(op: ExpressionMember) -> bool:
    return isinstance(op, Operator) and (op in ['+', '-'])

from enum import Enum

from calculator.exceptions import (
    IsNotOperator,
    IsNotParenthesis,
)


class Operator(Enum):
    """ Enum representing arithmetical operators. """
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'

    @staticmethod
    def determine(char: str) -> "Operator":
        match char:
            case '+': return Operator.ADD
            case '-': return Operator.SUB
            case '*': return Operator.MUL
            case '/': return Operator.DIV
            case _: raise IsNotOperator(char)

    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return super().__eq__(value)
        elif isinstance(value, str):
            return value == self.value
        else:
            return False

    def __repr__(self):
        return f"{self.value}"


class Parenthesis(Enum):
    OPENING = '('
    CLOSING = ')'

    @staticmethod
    def determine(char: str) -> "Parenthesis":
        match char:
            case '(': return Parenthesis.OPENING
            case ')': return Parenthesis.CLOSING
            case _: raise IsNotParenthesis(char)

    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return super().__eq__(value)
        elif isinstance(value, str):
            return value == self.value
        else:
            return False

    def __repr__(self):
        return f"{self.value}"

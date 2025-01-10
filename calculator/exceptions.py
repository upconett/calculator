class InvalidInput(BaseException): pass
class InvalidParentheses(InvalidInput): pass
class InvalidOperand(InvalidInput): pass
class NotInfixOperator(InvalidInput): pass
class InvalidOperatorsCount(InvalidInput): pass

class NoOperations(BaseException):
    pass

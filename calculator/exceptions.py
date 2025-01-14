class InvalidInput(BaseException): pass
class InvalidParentheses(InvalidInput): pass
class InvalidOperand(InvalidInput): pass
class NotInfixOperator(InvalidInput): pass
class InvalidOperatorsCount(InvalidInput): pass
class InvalidSimbol(InvalidInput): pass

class NoOperations(BaseException):
    pass

class IsNotOperator(BaseException): pass
class IsNotOperand(BaseException): pass
class IsNotParenthesis(BaseException): pass

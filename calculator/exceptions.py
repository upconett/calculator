class ParsingError(BaseException): pass
class AnalysingError(BaseException): pass

class UnknownSimbol(ParsingError): pass

class NoOperations(AnalysingError): pass
class InvalidParentheses(AnalysingError): pass
class InvalidOperand(AnalysingError): pass
class NotInfixOperator(AnalysingError): pass
class InvalidOperatorsCount(AnalysingError): pass

class IsNotOperator(BaseException): pass
class IsNotOperand(BaseException): pass
class IsNotParenthesis(BaseException): pass

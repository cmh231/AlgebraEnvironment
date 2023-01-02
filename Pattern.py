from Expression import Expression
from PropertyInheritance import PropertyInheritance
import typing

class Pattern:
    def __init__(self,
                 propertyInheritance: PropertyInheritance,
                 index: typing.Union[int, None],
                 expression: typing.Union[Expression, None],
                 childPatterns: list['Pattern'],
                 checkLabels: bool = False
                 ):
        if ~((index is None) | (expression is None)):
            raise TypeError("One of " + str(index) + " or " + str(expression) + " should be None.")
        if expression:
            if ~propertyInheritance.inheritsProperties([expression.getPropertyInheritance()], False):
                raise TypeError("Expression " + str(expression) +
                                " does not inherit from " + str(propertyInheritance) + ".")
        self._propertyInheritance = propertyInheritance
        self._index = index
        self._expression = expression
        self._childPatterns = childPatterns
        self._checkLabels = checkLabels

    def getPropertyInheritance(self) -> PropertyInheritance:
        return self._propertyInheritance

    def getIndex(self) -> typing.Union[int, None]:
        return self._index

    def setIndex(self):
        raise NotImplementedError

    def getExpression(self) -> typing.Union[Expression, None]:
        return self._expression

    # def setExpression(self, expression: typing.Union[Expression, None], recursive: bool = True):
    #     self._expression = expression
    #     if expression is not None:
    #         if ~expression.checkPatternPropertiesQuick(self, self._checkLabels):
    #             raise TypeError("Expression " + str(expression) + " does not match provided pattern: "
    #                             + str(self) + ".")
    #
    #         if ~expression.patternCollisionCheck(self, self._checkLabels):
    #             raise TypeError("Expression " + str(expression) + " does not match provided pattern: "
    #                             + str(self) + ".")
    #
    #         self.setIndexWithoutUniqueness(self._index, expression)
    #
    #         self._index = None

    def getChildPatterns(self) -> list['Pattern']:
        return self._childPatterns

    def getIndexList(self) -> list[int]:
        return ([] if self._index is None else [self._index]) + \
               sum((pattern.getIndexList() for pattern in self._childPatterns), [])

    def getCheckLabels(self) -> bool:
        return self._checkLabels

    def getIndexUniqueness(self) -> bool:
        return len(self.getIndexList()) == len(set(self.getIndexList()))

    # def setIndexWithUniqueness(self, index: int, expression: Expression) -> typing.Union['Pattern', None]:
    #     if self._index == index:
    #         self.setExpression(expression)
    #         return self
    #
    #     for pattern in self._childPatterns:
    #         attemptResult = pattern.setIndexWithUniqueness(index, expression)
    #         if attemptResult:
    #             return attemptResult
    #
    #     return None
    #
    # def setIndexWithoutUniqueness(self, index: int, expression: typing.Union[Expression, None]) -> list['Pattern']:
    #     if self._index == index:
    #         self.setExpression(expression, False)
    #         return [self]
    #
    #     return sum((pattern.setIndexWithoutUniqueness(index, expression) for pattern in self._childPatterns), [])

    def expressionFromReplacements(self, indexReplacements: list[Expression]) -> Expression:
        if self._index is None and self._expression is None:
            raise ValueError("Neither an expression nor a variable index was provided by " + str(self) + ".")

        targetExpression: Expression = \
            self._expression if self._expression is not None \
            else indexReplacements[self._index]

        name: str = targetExpression.getName()
        propertyInheritance: PropertyInheritance = targetExpression.getPropertyInheritance()
        expressions: list[Expression] = targetExpression.getExpressions()
        for index in range(len(self._childPatterns)):
            childExpression = self._childPatterns[index].expressionFromReplacements(indexReplacements)
            expressions[index] = childExpression

        return Expression(name, propertyInheritance, expressions)

    def _getPatternsOfIndicesRaw(self) -> list[tuple[int, 'Pattern']]:
        return sum((childPattern._getPatternsOfIndicesRaw() for childPattern in self._childPatterns),
                   [] if self._index is None else [(self._index, self)])

    def indicesHaveConsistentPatterns(self) -> bool:
        rawPatternList = self._getPatternsOfIndicesRaw()
        indices = self.getIndexList()

        return len(set(rawPatternList)) == len(indices)

    def getPatternsOfIndices(self) -> tuple[list[typing.Union['Pattern', None]], bool]:
        rawPatternList: list[tuple[int, 'Pattern']] = self._getPatternsOfIndicesRaw()
        indices = set(self.getIndexList())

        if len(set(rawPatternList)) != len(indices):
            return ([], False)

        maxIndex: int = 0
        for patternEntry in set(rawPatternList):
            maxIndex = patternEntry[0] if patternEntry[0] > maxIndex else maxIndex

        patternList: list[typing.Union['Pattern', None]] = [None]*maxIndex
        for patternEntry in set(rawPatternList):
            patternList[patternEntry[0]] = patternEntry[1]

        return (patternList, True)

    def __str__(self) -> str:
        return "[" + str(self._propertyInheritance) + str(self._index) + "]" + \
               "(" + ", ".join(str(pattern) for pattern in self._childPatterns) + ")"
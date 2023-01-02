from Rule import Rule
from PropertyInheritance import PropertyInheritance
from Pattern import Pattern
import typing
from multipledispatch import dispatch

class Expression:
    def __init__(self, name: str, propertyInheritance: PropertyInheritance, expressions: list['Expression']):
        self._name = name
        self._propertyInheritance = propertyInheritance
        self._expressions = expressions

    def getName(self):
        return self._name

    def getPropertyInheritance(self):
        return self._propertyInheritance

    def getExpressions(self):
        return self._expressions

    def __str__(self) -> str:
        return self._name + "(" + ", ".join(str(expression) for expression in self._expressions) + ")"

    def applyRule(self, rule: Rule) -> typing.Union['Expression', None]:
        inputPattern = rule.getInputPattern()
        outputPattern = rule.getOutputPattern()
        checkLabels = inputPattern.getCheckLabels()

        if ~self.checkPatternPropertiesQuick(inputPattern, checkLabels):
            return self

        indexReplacements = self.getExpressionsFromPattern(inputPattern, checkLabels)
        if ~indexReplacements[1]:
            return self

        maxIndex: int = 0
        for replacementTuple in indexReplacements[0]:
            maxIndex = replacementTuple[0] if replacementTuple[0] > maxIndex else maxIndex

        replacementList: list[typing.Union[Expression, None]] = [None]*maxIndex
        for replacementTuple in indexReplacements[0]:
            index = replacementTuple[0]
            replacement = replacementTuple[1]
            replacementList[index] = replacement

        return outputPattern.expressionFromReplacements(replacementList)

    def getExpressionsFromPattern(self, pattern: Pattern, checkLabels: bool = False) -> tuple[list[tuple[int, 'Expression']], bool]:
        if ~self.checkSelfWithPatternProperties(pattern, checkLabels):
            raise ValueError("Self-check failed for expression " + str(self) + ". Use checkPatternQuick or " +
                             "checkPatternFull to prevent this issue in future.")

        expressionsRecord: list[tuple[int, 'Expression']] = []
        noConflicts: bool = True

        currentIndex = pattern.getIndex()
        if pattern.getExpression() is not None:
            return ([], True) # Must be true if basic structure was checked successfully, which we assume.

        if currentIndex is not None:
            expressionsRecord.append((currentIndex, self))

        childPatterns: list[Pattern] = pattern.getChildPatterns()
        for index in range(len(childPatterns)):
            newExpressions = self._expressions[index].getExpressionsFromPattern(childPatterns[index], checkLabels)
            expressionsRecord = expressionsRecord + newExpressions[0]
            noConflicts = newExpressions[1]

        return (expressionsRecord, self.patternCollisionCheck(pattern, expressionsRecord) & noConflicts)

    # I'm not confident with multiple dispatch given the 'self'. If there's a bug, later, this would be a good place to
    # check. This first can also be optimised to return False from the first collision found.
    @dispatch('Expression', Pattern, bool)
    def patternCollisionCheck(self, pattern: Pattern, checkLabels: bool = False) -> bool:
        ruleList = self.getExpressionsFromPattern(pattern, checkLabels)
        return len(set(ruleList)) == len(set(pattern.getIndexList()))

    @dispatch('Expression', Pattern, list[tuple[int, 'Expression']])
    def patternCollisionCheck(self, pattern: Pattern, ruleList: list[tuple[int, 'Expression']]) -> bool:
        return len(set(ruleList)) == len(set(pattern.getIndexList()))

    def checkSelfWithPatternProperties(self, pattern: Pattern, checkLabels: bool = False) -> bool:
        expression: typing.Union[Expression, None] = pattern.getExpression()
        if expression is not None:
            if expression != self:
                return False
        if ~self._propertyInheritance.inheritsProperties([pattern.getPropertyInheritance()], False):
            return False

        childPatterns = pattern.getChildPatterns()
        if (len(self._expressions) < len(childPatterns)) | \
           ((len(self._expressions) > len(childPatterns)) & checkLabels):
            return False

        return True

    def checkPatternPropertiesQuick(self, pattern: Pattern, checkLabels: bool = False) -> bool:
        if ~self.checkSelfWithPatternProperties(pattern, checkLabels):
            return False

        childPatterns = pattern.getChildPatterns()
        for index in range(len(childPatterns)):
            if ~self._expressions[index].checkPatternPropertiesQuick(childPatterns[index], checkLabels):
                return False

        return True

    def checkLocalPatternProperties(self,
                                    pattern: Pattern,
                                    checkLabels: bool = False
                                    ) -> 'Expression.PatternCheckResult':
        propertyInheritance: PropertyInheritance = pattern.getPropertyInheritance()
        index: typing.Union[int, None] = pattern.getIndex()
        expression: tuple['Expression', 'Expression'] = (pattern.getExpression(), self)
        valid: bool = self._propertyInheritance.inheritsProperties([pattern.getPropertyInheritance()], False)
        childPatternChecks: list['Expression.PatternCheckResult'] = []

        childPatterns: list[Pattern] = pattern.getChildPatterns()
        if (len(self._expressions) < len(childPatterns)) | \
           ((len(self._expressions) > len(childPatterns)) & checkLabels):
            valid = False
            return Expression.PatternCheckResult(propertyInheritance, index, expression, valid, childPatternChecks)

        for index in range(len(childPatterns)):
            childPatternChecks.append(self._expressions[index].checkLocalPatternProperties(childPatterns[index], checkLabels))

        return Expression.PatternCheckResult(propertyInheritance, index, expression, valid, childPatternChecks)

    class PatternCheckResult:
        def __init__(self,
                     propertyInheritance: PropertyInheritance,
                     index: typing.Union[int, None],
                     expression: tuple[typing.Union['Expression', None], 'Expression'],
                     valid: bool,
                     childPatternChecks: list['Expression.PatternCheckResult']
                     ):
            self._propertyInheritance = propertyInheritance
            self._index = index
            self._expression = expression
            self._valid = valid
            self._childPatternChecks = childPatternChecks

        def __str__(self) -> str:
            return "[" + str(self._propertyInheritance) + str(self._index) + "]" + \
                   "{" + ", ".join(str(pattern) for pattern in self._childPatternChecks) + "}"
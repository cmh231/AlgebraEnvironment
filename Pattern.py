from Expression import Expression
from PropertyInheritance import PropertyInheritance
import typing
from typing import List
from typing import Tuple

class Pattern:
    """Class to store and handle patterns for pattern-matching."""
    def __init__(self,
                 name: typing.Union[str, None],
                 propertyInheritance: PropertyInheritance,
                 index: typing.Union[int, None],
                 expression: typing.Union[Expression, None],
                 childPatterns: List['Pattern'],
                 checkLabels: bool = False
                 ):
        """
        Create a pattern with the given properties.

        Notes:
            One of expression and index must be equal to None - there's no need to name the variable if it's already
            been explicitly given.
            If an expression is given, propertyInheritance must match for it.
            Indices must be greater than or equal to 0.

        :param name: [Optional] Name of the expression to be found by the pattern.
        :param propertyInheritance: PropertyInheritance to check for in the expression.
        :param index: [Optional] Index used to identify interesting parts of the pattern.
        :param expression: [Optional] An explicit expression to check for.
        :param childPatterns: List of the patterns expected in the argument of the expression.
        :param checkLabels: Whether to constrain additional arguments in the expression after those specified by the
                            pattern.
        """

        # One of expression and index must be equal to None - there's no need to name the variable if it's already
        # been explicitly given.
        if not((index is None) | (expression is None)):
            raise TypeError("One of " + str(index) + " or " + str(expression) + " should be None.")

        # Check if the expression provided matches its stated properties.
        if expression:
            if not propertyInheritance.inheritsProperties([expression.getPropertyInheritance()], False):
                raise TypeError("Expression " + str(expression) +
                                " does not inherit from " + str(propertyInheritance) + ".")

        # Indices can't be less than 0.
        if index < 0:
            raise ValueError("Index cannot be less than 0.")

        self._name: typing.Union[str, None] = name
        self._propertyInheritance: PropertyInheritance = propertyInheritance
        self._index: int = index
        self._expression: Expression = expression
        self._childPatterns: List[Pattern] = childPatterns
        self._checkLabels: bool = checkLabels

    def getName(self) -> typing.Union[str, None]:
        return self._name

    def getPropertyInheritance(self) -> PropertyInheritance:
        return self._propertyInheritance

    def getIndex(self) -> typing.Union[int, None]:
        return self._index

    def getExpression(self) -> typing.Union[Expression, None]:
        return self._expression

    def getChildPatterns(self) -> List['Pattern']:
        return self._childPatterns

    def getIndexList(self) -> List[int]:
        """Return a list of all indices appearing in the pattern."""
        return ([] if self._index is None else [self._index]) + \
            sum((pattern.getIndexList() for pattern in self._childPatterns), [])

    def getCheckLabels(self) -> bool:
        return self._checkLabels

    def getIndexUniqueness(self) -> bool:
        return len(self.getIndexList()) == len(set(self.getIndexList()))

    def _getPatternsOfIndicesRaw(self) -> List[Tuple[int, 'Pattern']]:
        return sum((childPattern._getPatternsOfIndicesRaw() for childPattern in self._childPatterns),
                   [] if self._index is None else [(self._index, self)])

    def indicesHaveConsistentPatterns(self) -> bool:
        rawPatternList = self._getPatternsOfIndicesRaw()
        indices = self.getIndexList()

        return len(set(rawPatternList)) == len(indices)

    def getPatternsOfIndices(self) -> Tuple[List[typing.Union['Pattern', None]], bool]:
        rawPatternList: List[Tuple[int, 'Pattern']] = self._getPatternsOfIndicesRaw()
        indices = set(self.getIndexList())

        if len(set(rawPatternList)) != len(indices):
            return ([], False)

        maxIndex: int = 0
        for patternEntry in set(rawPatternList):
            maxIndex = patternEntry[0] if patternEntry[0] > maxIndex else maxIndex

        patternList: List[typing.Union['Pattern', None]] = [None]*maxIndex
        for patternEntry in set(rawPatternList):
            patternList[patternEntry[0]] = patternEntry[1]

        return (patternList, True)

    def expressionFromReplacements(self, indexReplacements: List[Expression]) -> Expression:
        """
        Build an expression from a pattern using a list of variables and their indices.

        Expressions are loaded either from being explicitly given in the pattern, or from the list of indexReplacements.
        Arguments to each expression are supplied by either the pattern, or their original values. Arguments supplied by
        the pattern will overwrite existing arguments where provided, but further details will be untouched. The indices
        supplied are assumed to be sufficient to create the whole expression.

        :param indexReplacements: A list of expressions to replace indices with - accessed by index.
        :return: The new expression constructed from the replacements.
        """

        # We need either an expression or a variable, at least!
        if self._index is None and self._expression is None:
            raise ValueError("Neither an expression nor a variable index was provided by " + str(self) + ".")

        # Either get an expression from the pattern's expression, or from an index.
        targetExpression: Expression = \
            self._expression if self._expression is not None \
            else indexReplacements[self._index]

        # Extract the information needed to create a new expression.
        name: str = targetExpression.getName()
        propertyInheritance: PropertyInheritance = targetExpression.getPropertyInheritance()
        expressions: List[Expression] = targetExpression.getExpressions()
        for index in range(len(self._childPatterns)):
            childExpression = self._childPatterns[index].expressionFromReplacements(indexReplacements)
            expressions[index] = childExpression

        # TODO: consider copying over details of any remaining expressions.
        return Expression(name, propertyInheritance, expressions)

    def getExpressionsFromPattern(self, expression: Expression) -> Tuple[List[Tuple[int, Expression]], bool]:
        """
        Get all expressions corresponding to an index in the pattern, and check whether any collisions occur.

        Note: The expression provided is assumed to match under checkPatternProperties as a minimum, and an error will
              be thrown if this is not the case.

        :param expression: The expression against which to match this pattern.
        :return: A tuple of the form ([(Index1, Expression1), (Index2, Expression2), ...], noConflicts).
                 A list of indices and their corresponding expressions are returned, with noConflicts recording whether
                 any two variables share the same type.
        """

        # The list we return is guaranteed to be a list of all expressions corresponding to an index. Neither providing
        # an incomplete list, nor missing out necessary indices, would be meaningful, and so an error is thrown. These
        # local checks should be carried out in advance.
        if not self.checkExpressionWithPatternProperties(expression):
            raise ValueError("Self-check failed for expression " + str(expression) + ". Use checkPatternProperties or " +
                             "checkLocalPatternProperties to prevent this issue in future.")

        # Initialise the relevant details for a pattern without any indices to return no list and no conflicts.
        expressionsRecord: List[Tuple[int, Expression]] = []
        noConflicts: bool = True

        # If we reach an explicit expression, this must correspond successfully with the pattern for initial checks to
        # have returned true.
        currentIndex = self.getIndex()
        if self.getExpression() is not None:
            return ([], True)

        # If we are at an index currently, add ourselves to the list.
        if currentIndex is not None:
            expressionsRecord.append((currentIndex, expression))

        # Loop through the remaining expressions to check, and combine their results.
        childPatterns: List[Pattern] = self.getChildPatterns()
        for index in range(len(childPatterns)):
            newExpressions = expression.getExpressions()[index].getExpressionsFromPattern(childPatterns[index])
            expressionsRecord = expressionsRecord + newExpressions[0]
            noConflicts = newExpressions[1]

        # Check whether combining the index records of ourselves and our children causes any conflicts, whilst noting
        # any existing conflicts.
        return (expressionsRecord, self.patternCollisionCheck(expressionsRecord) & noConflicts)

    def patternCollisionCheck(self, expressionsRecord: List[Tuple[int, Expression]]) -> bool:
        """
        Check whether or not any indices have conflicting expressions as entries.

        Note, the expression from which this expression record was generated is assumed to have passed
        checkPatternProperties.

        :param expressionsRecord: The record of which expressions were found for which indices.
        :return: Whether any indices have conflicting entries associated with them.
        """

        # Every index must have at least one associated expression if the pattern was valid prior to collision checking.
        # Once duplicates are removed, there should exist exactly one expression for each index, and hence the length of
        # both lists should be equal. If there are any repeats of indices, but not of expressions for those indices, the
        # length of set(pattern.getIndexList()) will remain, but the length of set(expressionsRecord) will increase.
        return len(set(expressionsRecord)) == len(set(self.getIndexList()))

    def checkExpressionWithPatternProperties(self, expression: Expression) -> bool:
        """
        Check local properties of the provided expression against this pattern.

        This will pick up differences in names, properties, and the length of arguments throughout the remaining
        expression and property tree. It will not, however, check for conflicts.

        :param expression: The expression at the same level as the current pattern being checked.
        :return: Whether there are any local conflicts between the expression and pattern.
        """
        checkLabels = self.getCheckLabels()

        patternExpression: typing.Union[Expression, None] = self.getExpression()
        if patternExpression is not None:
            if patternExpression != expression:
                return False

        patternName = self.getName()
        if patternName is not None and patternName != expression.getName():
            return False

        if not expression.getPropertyInheritance().inheritsProperties([self.getPropertyInheritance()], False):
            return False

        childPatterns = self.getChildPatterns()
        if (len(expression.getExpressions()) < len(childPatterns)) | \
           ((len(expression.getExpressions()) > len(childPatterns)) & checkLabels):
            return False

        return True

    def checkLocalPatternProperties(self, expression: Expression,
                                    ) -> 'Pattern.PatternCheckResult':
        """
        Debug on which comparisons a check between this pattern and a given expression failed locally.

        This function provides a less efficient and direct alternative to checkPatternProperties, designed to be used
        when a pattern fails to match an expression whose matching is expected.

        :param expression: The expression this pattern is checked against.
        :return: PatternCheckResult instance containing the local results of the check.
        """

        # Prepare variables needed to create the new PatternCheckResult
        pattern: 'Pattern' = self
        checkLabels: bool = pattern.getCheckLabels()
        valid: bool = pattern.checkExpressionWithPatternProperties(expression)
        childPatternChecks: List['Pattern.PatternCheckResult'] = []

        # Check whether the number of arguments in the expression is compatible with the number in the pattern. If not,
        # continued checks would have no meaning, and so the debug is truncated here.
        childPatterns: List['Pattern'] = pattern.getChildPatterns()
        if (len(expression.getExpressions()) < len(childPatterns)) | \
           ((len(expression.getExpressions()) > len(childPatterns)) & checkLabels):
            return Pattern.PatternCheckResult(pattern, False, expression, childPatternChecks)

        # Compare expressions to child patterns, and store the results in a childPatternCheck.
        for index in range(len(childPatterns)):
            childPatternChecks.append(
                childPatterns[index].checkLocalPatternProperties(expression.getExpressions()[index])
            )

        # Construct the current layer of the PatternCheckResult and return it.
        return Pattern.PatternCheckResult(pattern, valid, expression, childPatternChecks)

    def checkPatternProperties(self, expression: Expression) -> bool:
        """
        Perform a basic check as to whether the structure of this pattern matches a given expression.

        This will pick up differences in names, properties, and the length of arguments, but will not pick up on
        collisions where two expressions with the same index are found to differ.

        :param expression: The expression this pattern is checked against.
        :return: Whether the check was successful.
        """

        # If this level isn't compatible, the structure as a whole is incompatible, and no further computation is
        # needed.
        if not self.checkExpressionWithPatternProperties(expression):
            return False

        # If a single child is incompatible, so too is the structure as a whole, and, again, no further computation is
        # needed.
        childPatterns = self.getChildPatterns()
        for index in range(len(childPatterns)):
            if not childPatterns[index].checkPatternProperties(expression.getExpressions()[index]):
                return False

        # If the entire structure has been successfully checked, then the check has succeeded.
        return True

    class PatternCheckResult:
        """A helper class to see where pattern checks locally failed."""

        def __init__(self,
                     pattern: 'Pattern',
                     valid: bool,
                     foundExpression: Expression,
                     childPatternChecks: List['Pattern.PatternCheckResult']):
            """
            Create new PatternCheckResult based on a pattern and comparisons with that pattern.

            :param pattern: The pattern PatternCheckResult was based upon.
            :param valid: Whether the comparison was valid.
            :param foundExpression: The expression pattern was checked against.
            :param childPatternChecks: Any children which were checked.
            """

            self._pattern: Pattern = pattern
            self._valid: bool = valid
            self._foundExpression: Expression = foundExpression
            self._childPatternChecks: List['Pattern.PatternCheckResult'] = childPatternChecks

        def __str__(self) -> str:
            # Follows the format [NameIndex]([Argument1Index1](...), [Argument2Index2](...)...)
            return "[" + str(self._pattern.getName()) + str(self._pattern.getIndex()) + "]" + \
                   "(" + ", ".join(str(patternCheck) for patternCheck in self._childPatternChecks) + ")"

    def __str__(self) -> str:
        return "[" + str(self._name) + str(self._index) + "]" + \
               "(" + ", ".join(str(pattern) for pattern in self._childPatterns) + ")"
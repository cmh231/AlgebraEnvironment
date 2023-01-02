from Rule import Rule
from PropertyInheritance import PropertyInheritance
from Pattern import Pattern
import typing

class Expression:
    """Expressions with defined properties, potentially referring to other expressions as arguments."""

    def __init__(self, name: str, propertyInheritance: PropertyInheritance, expressions: list['Expression']):
        """
        Create an instance of Expression with a given name, properties, and inheritance.

        :param name: Name of the expression. This may be checked against patterns.
        :param propertyInheritance: Properties of the expression. This will be checked against patterns.
        :param expressions: List of expressions to be used as arguments of labels.
                            These may be checked against patterns.
        """

        self._name = name
        self._propertyInheritance = propertyInheritance
        self._expressions = expressions

    def getName(self):
        """Get the name of this expression."""
        return self._name

    def getPropertyInheritance(self):
        """Get the property of this expression. If multiple properties are relevant, this may be anonymous."""
        return self._propertyInheritance

    def getExpressions(self):
        """Get the list of expressions acting as arguments for this property"""
        return self._expressions

    def applyRule(self, rule: Rule) -> typing.Union['Expression', None]:
        """
        Check if a rule can be applied to an expression, and apply it, if it can be, returning a new expression.

        Pattern matching is applied between the expression and the inputPattern of the rule. If this is not a success,
        the original expression is returned. If this is a success, a new expression is created by replacing the indices
        of the outputPattern with those found through pattern matching with the inputPattern.

        :param rule: The rule to apply to this expression.
        :return: If the rule applies to this expression, the expression resulting from applying the rule.
                 Otherwise, the original expression is returned.
        """

        # Getting the two relevant patterns.
        inputPattern: Pattern = rule.getInputPattern()
        outputPattern: Pattern = rule.getOutputPattern()

        # Perform the basic pattern-matching check.
        if ~self.checkPatternProperties(inputPattern):
            return self

        # Get the list of replacements, and act on the result of the collision check.
        indexReplacements = self.getExpressionsFromPattern(inputPattern)
        if ~indexReplacements[1]:
            return self

        # We're going to need a list. Find how long it will be so we can pre-initialise it. In general, the indices
        # might not be as simple as ranging from 1 to N, so we need to account for this.
        maxIndex: int = 0
        for replacementTuple in indexReplacements[0]:
            maxIndex = replacementTuple[0] if replacementTuple[0] > maxIndex else maxIndex

        # Initialise an empty array, then proceed to fill it.
        replacementList: list[typing.Union[Expression, None]] = [None]*maxIndex
        for replacementTuple in indexReplacements[0]:
            index = replacementTuple[0]
            replacement = replacementTuple[1]
            replacementList[index] = replacement

        return outputPattern.expressionFromReplacements(replacementList)

    def getExpressionsFromPattern(self, pattern: Pattern) -> tuple[list[tuple[int, 'Expression']], bool]:
        """
        Get all expressions corresponding to an index in the pattern, and check whether any collisions occur.

        Note: The pattern provided is assumed to pass checkPatternProperties as a minimum, and an error will be thrown
              if this is not the case.

        :param pattern: The pattern to check against.
        :return: A tuple of the form ([(Index1, Expression1), (Index2, Expression2), ...], noConflicts).
                 A list of indices and their corresponding expressions are returned, with noConflicts recording whether
                 any two variables share the same type.
        """

        # The list we return is guaranteed to be a list of all expressions corresponding to an index. Neither providing
        # an incomplete list, nor missing out necessary indices, would be meaningful, and so an error is thrown. These
        # local checks should be carried out in advance.
        if ~self.checkSelfWithPatternProperties(pattern):
            raise ValueError("Self-check failed for expression " + str(self) + ". Use checkPatternProperties or " +
                             "checkLocalPatternProperties to prevent this issue in future.")

        # Initialise the relevant details for a pattern without any indices to return no list and no conflicts.
        expressionsRecord: list[tuple[int, 'Expression']] = []
        noConflicts: bool = True

        # If we reach an explicit expression, this must correspond successfully with the pattern for initial checks to
        # have returned true.
        currentIndex = pattern.getIndex()
        if pattern.getExpression() is not None:
            return ([], True)

        # If we are at an index currently, add ourselves to the list.
        if currentIndex is not None:
            expressionsRecord.append((currentIndex, self))

        # Loop through the remaining expressions to check, and combine their results.
        childPatterns: list[Pattern] = pattern.getChildPatterns()
        for index in range(len(childPatterns)):
            newExpressions = self._expressions[index].getExpressionsFromPattern(childPatterns[index])
            expressionsRecord = expressionsRecord + newExpressions[0]
            noConflicts = newExpressions[1]

        # Check whether combining the index records of ourselves and our children causes any conflicts, whilst noting
        # any existing conflicts.
        return (expressionsRecord, Expression.patternCollisionCheck(pattern, expressionsRecord) & noConflicts)

    @staticmethod
    def patternCollisionCheck(pattern: Pattern, expressionsRecord: list[tuple[int, 'Expression']]) -> bool:
        """
        Check whether or not any indices have conflicting expressions as entries.

        :param pattern: The pattern from which the expressionsRecord was generated. Must pass checkPatternProperties.
        :param expressionsRecord: The record of which expressions were found for which indices.
        :return: Whether any indices have conflicting entries associated with them.
        """

        # Every index must have at least one associated expression if the pattern was valid prior to collision checking.
        # Once duplicates are removed, there should exist exactly one expression for each index, and hence the length of
        # both lists should be equal. If there are any repeats of indices, but not of expressions for those indices, the
        # length of set(pattern.getIndexList()) will remain, but the length of set(expressionsRecord) will increase.
        return len(set(expressionsRecord)) == len(set(pattern.getIndexList()))

    def checkSelfWithPatternProperties(self, pattern: Pattern) -> bool:
        """
        Check local properties of the provided pattern against the current expression.

        This will pick up differences in names, properties, and the length of arguments.

        :param pattern: The pattern at the same level as the current expression being checked.
        :return: Whether there are any local conflicts between the current expression and the pattern.
        """
        checkLabels = pattern.getCheckLabels()

        expression: typing.Union[Expression, None] = pattern.getExpression()
        if expression is not None:
            if expression != self:
                return False

        patternName = pattern.getName()
        if patternName is not None and patternName != self._name:
            return False

        if ~self._propertyInheritance.inheritsProperties([pattern.getPropertyInheritance()], False):
            return False

        childPatterns = pattern.getChildPatterns()
        if (len(self._expressions) < len(childPatterns)) | \
           ((len(self._expressions) > len(childPatterns)) & checkLabels):
            return False

        return True

    def checkPatternProperties(self, pattern: Pattern) -> bool:
        """
        Perform a basic check as to whether the structure of a given pattern matches that of an expression.

        This will pick up differences in names, properties, and the length of arguments, but will not pick up on
        collisions where two expressions with the same index are found to differ.

        :param pattern: The pattern this expression is checked against.
        :return: Whether the check was successful.
        """

        # If this level isn't compatible, the structure as a whole is incompatible, and no further computation is
        # needed.
        if ~self.checkSelfWithPatternProperties(pattern):
            return False

        # If a single child is incompatible, so too is the structure as a whole, and, again, no further computation is
        # needed.
        childPatterns = pattern.getChildPatterns()
        for index in range(len(childPatterns)):
            if ~self._expressions[index].checkPatternProperties(childPatterns[index]):
                return False

        # If the entire structure has been successfully checked, then the check has succeeded.
        return True

    def checkLocalPatternProperties(self,
                                    pattern: Pattern,
                                    ) -> 'Expression.PatternCheckResult':
        """
        Debug on which comparisons a check between this expression and a given pattern failed locally.

        This function provides a less efficient and direct alternative to checkPatternProperties, designed to be used
        when a pattern fails to match an expression whose matching is expected.

        :param pattern: The pattern this expression is checked against.
        :return: PatternCheckResult instance containing the local results of the check.
        """

        # Prepare variables needed to create the new PatternCheckResult
        expression: 'Expression' = self
        checkLabels: bool = pattern.getCheckLabels()
        valid: bool = self.checkSelfWithPatternProperties(pattern)
        childPatternChecks: list['Expression.PatternCheckResult'] = []

        # Check whether the number of arguments in the expression is compatible with the number in the pattern. If not,
        # continued checks would have no meaning, and so the debug is truncated here.
        childPatterns: list[Pattern] = pattern.getChildPatterns()
        if (len(self._expressions) < len(childPatterns)) | \
           ((len(self._expressions) > len(childPatterns)) & checkLabels):
            return Expression.PatternCheckResult(pattern, False, expression, childPatternChecks)

        # Compare expressions to child patterns, and store the results in a childPatternCheck.
        for index in range(len(childPatterns)):
            childPatternChecks.append(
                self._expressions[index].checkLocalPatternProperties(childPatterns[index])
            )

        # Construct the current layer of the PatternCheckResult and return it.
        return Expression.PatternCheckResult(pattern, valid, expression, childPatternChecks)

    class PatternCheckResult:
        """A helper class to see where pattern checks locally failed."""

        def __init__(self,
                     pattern: Pattern,
                     valid: bool,
                     foundExpression: 'Expression',
                     childPatternChecks: list['Expression.PatternCheckResult']):
            """
            Create new PatternCheckResult based on a pattern and comparisons with that pattern.

            :param pattern: The pattern PatternCheckResult was based upon.
            :param valid: Whether the comparison was valid.
            :param foundExpression: The expression pattern was checked against.
            :param childPatternChecks: Any children which were checked.
            """

            self._pattern: Pattern = pattern
            self._valid: bool = valid
            self._foundExpression: 'Expression' = foundExpression
            self._childPatternChecks: list['Expression.PatternCheckResult'] = childPatternChecks

        def __str__(self) -> str:
            # Follows the format [NameIndex]([Argument1Index1](...), [Argument2Index2](...)...)
            return "[" + str(self._pattern.getName()) + str(self._pattern.getIndex()) + "]" + \
                   "(" + ", ".join(str(patternCheck) for patternCheck in self._childPatternChecks) + ")"

    def __str__(self) -> str:
        # Follows the format Name(Argument1, Argument2, ...)
        return self._name + "(" + ", ".join(str(expression) for expression in self._expressions) + ")"
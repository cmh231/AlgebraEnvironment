from Pattern import Pattern
from Expression import Expression
import typing
from typing import List
from typing import Tuple

class Rule:
    """Class describing a rule to be applied to an expression."""

    def __init__(self, name: str, inputPattern: Pattern, outputPattern: Pattern):
        """
        Create a new Rule with a specified name, alongside input and output patterns.

        Note: Some basic checks will be applied on whether a given output pattern can be made from the information
        provided by the input pattern, but this will not catch all edge-cases.

        :param name: Rule name. Primarily for identification and conversion to strings..
        :param inputPattern: Pattern which to be matched to the Expression. Variables in the pattern which are important
                             should be assigned indices. These can be used to retrieve particular variables, later, or
                             to enforce certain variables remaining the same.
        :param outputPattern: Pattern returned by the rule. The variables retrieved from pattern matching with the input
                              pattern will be fed into the output pattern. As such any index appearing in the output
                              pattern must have a corresponding index in the input pattern.
        """
        self._name = name
        self._inputPattern = inputPattern
        self._outputPattern = outputPattern
        if ~self.checkValidRule():
            raise ValueError("Arguments of the output pattern specified by the input did not inherit the properties " +
                             "required by the output pattern.")

    def getName(self) -> str:
        """Return the name of the rule."""
        return self._name

    def getInputPattern(self) -> Pattern:
        """Return the input pattern of the rule."""
        return self._inputPattern

    def getOutputPattern(self) -> Pattern:
        """Return the output pattern of the rule."""
        return self._outputPattern

    def checkValidRule(self) -> bool:
        """
        Apply basic checks to determine whether the rule may be valid. Forms a necessary, but not sufficient, condition.

        Specifically, this check tests whether

        :return: Whether the rule passed the check.
        """

        # Extract all patterns given
        inputPatternsStruct: Tuple[List[Pattern], bool] = self._inputPattern.getPatternsOfIndices()
        outputPatternsStruct: Tuple[List[Pattern], bool] = self._inputPattern.getPatternsOfIndices()

        if ~inputPatternsStruct[1] | ~outputPatternsStruct[1]:
            return False

        inputPatterns: List[Pattern] = inputPatternsStruct[0]
        outputPatterns: List[Pattern] = outputPatternsStruct[0]

        if len(outputPatterns) > len(inputPatterns):
            return False

        #TODO: Account for a deeper comparison of two patterns than simply checking their properties. For now, it's
        #      just on the user to avoid this.
        for index in range(len(outputPatterns)):
            inputPattern = inputPatterns[index]
            if inputPattern is None:
                return False
            outputPattern = outputPatterns[index]
            if ~inputPattern.getPropertyInheritance().inheritsProperties(
                    [outputPattern.getPropertyInheritance()],
                    False
            ):
                return False

        return True

    def applyRule(self, expression: Expression) -> typing.Union[Expression, None]:
        """
        Check if a rule can be applied to an expression, and apply it, if it can be, return the new expression.

        Pattern matching is applied between the expression and the inputPattern of the rule. If this is not a success,
        the original expression is returned. If this is a success, a new expression is created by replacing the indices
        of the outputPattern with those found through pattern matching with the inputPattern.

        :param expression: The expression to which to apply this rule.
        :return: If this rule applies to the expression, return the expression resulting from applying the rule.
                 Otherwise, the original expression is returned.
        """

        # Getting the two relevant patterns.
        inputPattern: Pattern = self.getInputPattern()
        outputPattern: Pattern = self.getOutputPattern()

        # Perform the basic pattern-matching check.
        if ~inputPattern.checkPatternProperties(expression):
            return expression

        # Get the list of replacements, and act on the result of the collision check.
        indexReplacements = inputPattern.getExpressionsFromPattern(expression)
        if ~indexReplacements[1]:
            return expression

        # We're going to need a list. Find how long it will be so we can pre-initialise it. In general, the indices
        # might not be as simple as ranging from 1 to N, so we need to account for this.
        maxIndex: int = 0
        for replacementTuple in indexReplacements[0]:
            maxIndex = replacementTuple[0] if replacementTuple[0] > maxIndex else maxIndex

        # Initialise an empty array, then proceed to fill it.
        replacementList: List[typing.Union[Expression, None]] = [None]*maxIndex
        for replacementTuple in indexReplacements[0]:
            index = replacementTuple[0]
            replacement = replacementTuple[1]
            replacementList[index] = replacement

        return outputPattern.expressionFromReplacements(replacementList)

    def __str__(self) -> str:
        """"""
        return self._name + ":(" + str(self._inputPattern.getName()) + "->" + str(self._outputPattern.getName()) + ")"
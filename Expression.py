from PropertyInheritance import PropertyInheritance
from typing import List

class Expression:
    """Expressions with defined properties, potentially referring to other expressions as arguments."""

    def __init__(self, name: str, propertyInheritance: PropertyInheritance, expressions: List['Expression']):
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

    def __str__(self) -> str:
        # Follows the format Name(Argument1, Argument2, ...)
        return self._name + "(" + ", ".join(str(expression) for expression in self._expressions) + ")"
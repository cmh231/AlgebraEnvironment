from typing import List

class PropertyInheritance:
    """
    Contain details about other properties inherited by a given property.

    Equality of instances of this class should be decided based on whether the full names of two objects are found to
    be equal. This enforces the best practice of ensuring that properties with the same inheritance should be given
    distinct names, and allows for different instances of the same property to be directly compared.

    Static Variables:
    printHash = False - Whether conversion to a string be appended with the hash of the property's inheritance.
    """

    printHash = False

    def __init__(self, name: str, inheritedProperties: List['PropertyInheritance']):
        """
        Create a property with a given name and inheriting a list of other properties.

        :param name: Name of the property.
        :param inheritedProperties: List of the properties from which this property directly inherits.
        """

        self._name: str = name
        self._inheritedProperties: List['PropertyInheritance'] = inheritedProperties
        self._fullName = ""
        self._fullName: str = self.getFullName()
        self._propertyHash: int = hash(self._fullName)

    def getPropertyInheritance(self):
        """Get list of properties from which this property directly inherits."""

        return self._inheritedProperties

    def getFullName(self) -> str:
        """Get the full name of the property, containing its complete inheritance tree."""

        # Since the class is read-only, once the name has been found, return the stored value.
        if self._fullName:
            return self._fullName

        # Find the full name recursively.
        return self._name + \
            "(" + \
            ", ".join(inheritedProperty.getFullName() for inheritedProperty in self._inheritedProperties) + \
            ")"

    def getPropertyHash(self) -> int:
        """Get the hash of the property tree."""

        return self._propertyHash

    def inheritsPropertiesList(self,
                               properties: List['PropertyInheritance'],
                               deepCheck: bool = True
                               ) -> List['PropertyInheritance']:
        """
        Take a list of properties and return a list of all from those from that list which this inherits.

        :param properties: List of properties to check for.
        :param deepCheck: Whether to continue checking deeper into the inheritance tree once inheritance has been found.
                          Should always be False if none of the properties provided inherit from one another.
        :return: List of properties from the input list which this inherits.
        """

        # If no properties can be found which match, whatever the value of deepCheck, iterate the search to a new level.
        if not self._propertyHash in (currentProperty.getPropertyHash() for currentProperty in properties):
            return sum((inheritedProperty.inheritsPropertiesList(properties, deepCheck)
                        for inheritedProperty in self._inheritedProperties), [])

        # If we have found a property, and deepCheck is False, we need recurse no further.
        if not deepCheck:
            return [self]

        # If deepCheck is True and this property is one of our targets, continue to iterate, and return this object,
        return [self] + sum((inheritedProperty.inheritsPropertiesList(properties, deepCheck)
                             for inheritedProperty in self._inheritedProperties), [])

    def inheritsProperties(self, properties: List['PropertyInheritance'], deepCheck: bool = True) -> bool:
        """
        Take a list of properties and return True if they are all found.

        :param properties: List of properties to check for.
        :param deepCheck: Whether to continue checking deeper into the inheritance tree once inheritance has been found.
                          Should always be False if none of the properties provided inherit from one another.
        :return: Whether all properties from the provided list were found.
        """

        return properties == self.inheritsPropertiesList(properties, deepCheck)

    def __str__(self) -> str:
        # Return our name, appending the hash based on the value of printHash.
        return self._name + (str(self._propertyHash) if PropertyInheritance.printHash else "")

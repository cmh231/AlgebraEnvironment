class PropertyInheritance:
    printHash = False

    def __init__(self, name: str, inheritedProperties: list['PropertyInheritance']):
        self._name = name
        self._inheritedProperties = inheritedProperties
        self._fullName = self.getFullName()
        self._propertyHash = hash(self._fullName)

    def getPropertyInheritance(self):
        return self._inheritedProperties

    def getFullName(self) -> str:
        if self._name:
            return self._name
        return self._name + \
            "(" + \
            ", ".join(inheritedProperty.getFullName() for inheritedProperty in self._inheritedProperties) + \
            ")"

    def getPropertyHash(self) -> int:
        return self._propertyHash

    def inheritedPropertyList(self,
                              properties: list['PropertyInheritance'],
                              deepCheck: bool = True
                              ) -> list['PropertyInheritance']:
        if ~self._propertyHash in (currentProperty.getPropertyHash() for currentProperty in properties):
            return sum((inheritedProperty.inheritedPropertyList(properties, deepCheck)
                        for inheritedProperty in self._inheritedProperties), [])
        if ~deepCheck:
            return [self]
        return [self] + sum((inheritedProperty.inheritedPropertyList(properties, deepCheck)
                             for inheritedProperty in self._inheritedProperties), [])

    def inheritsProperties(self, properties: list['PropertyInheritance'], deepCheck: bool = True) -> bool:
        return properties == self.inheritedPropertyList(properties, deepCheck)

    def __str__(self) -> str:
        return self._name + (str(self._propertyHash) if PropertyInheritance.printHash else "")

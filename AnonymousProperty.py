from PropertyInheritance import PropertyInheritance

class AnonymousProperty(PropertyInheritance):
    def __init__(self, inheritedProperties: list['PropertyInheritance']):
        super().__init__("λ", inheritedProperties)
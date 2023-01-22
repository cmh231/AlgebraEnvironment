from PropertyInheritance import PropertyInheritance
from typing import List

class AnonymousProperty(PropertyInheritance):
    """Anonymous property used if one object inherits multiple unrelated properties."""

    def __init__(self, inheritedProperties: List['PropertyInheritance']):
        # A fixed name can be used since anonymous properties are, by definition defined only by those they contain.
        super().__init__("λ", inheritedProperties)
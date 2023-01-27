"""
Provide tools for converting trees of singly-inherited properties to PropertyInheritanceObjects en masse.

Whilst not all properties necessarily need obey single-inheritance, we can at least construct a set of properties which
do, and which are typically useful for addressing problems in second-quantisation, involving a 1D chain of sites. As
such, these can be represented as a tree datastructure, and are visually shown below.

When updating trees to be used by these tools, it is suggested to ensure that each property have a unique name. This is
in general only necessary to provide unambiguous keys for an output dictionary, and is not required by the property tree
format. Where multiple properties might have the same name, it is suggested to disambiguate by adding a prefix to the
name to specify a distinguishing part of its inheritance. Even if one intends only to use the tree output, it is
recommended this be adhered to in general, and included with the definition of any such trees, in future.

For example, if the property 'Stable' is to be defined, it might inherit either from a 'Building' property (referring to
the type of building), or a 'DynamicObject' property (referring to whether a system of movable objects is stable). In
this case, it would be suggested to add these in the form
    ("Object", [
        ("Building", [
            ("StableBuilding", [])
        ])
        ("DynamicObject", [
            ("StableDynamicObject", [])
        ])
    ])
"""

from PropertyInheritance import PropertyInheritance
import typing
from typing import Dict
from typing import List
from typing import Tuple

# TemplateTree = Tuple[str, List[TemplateTree]]

class PropertyTree:
    def __init__(self, currentProperty: PropertyInheritance, descendants: List['PropertyTree']):
        self._currentProperty = currentProperty
        self._descendants = descendants

    def __str__(self) -> str:
        return str(self._currentProperty.getName()) + "->" + \
               "[" + ", ".join(str(descendant) for descendant in self._descendants) + "]"

class PropertyInheritanceGenerator:
    @staticmethod
    def generatePropertyTreeFromTemplate(template,# -> TemplateTree
                                         parentPropertyInheritance: typing.Union[PropertyInheritance, None] = None
                                         ) -> PropertyTree:
        currentPropertyTemplate: str = template[0]
        inheritingProperties = template[1]
        currentProperty = PropertyInheritance(currentPropertyTemplate,
                                              [] if parentPropertyInheritance is None else [parentPropertyInheritance]
                                              )
        branches = [PropertyInheritanceGenerator.generatePropertyTreeFromTemplate(inheritingProperty, currentProperty)
                    for inheritingProperty in inheritingProperties]
        return PropertyTree(currentProperty, branches)

    @staticmethod
    def generatePropertyDictionaryAndKeysFromTemplate(template,# -> TemplateTree
                                                      parentPropertyInheritance: typing.Union[PropertyInheritance,
                                                                                              None
                                                                                              ] = None
                                                      ) -> Tuple[List[str], Dict[str, PropertyInheritance]]:
        currentPropertyTemplate: str = template[0]
        inheritingProperties = template[1]
        currentProperty = PropertyInheritance(currentPropertyTemplate,
                                              [] if parentPropertyInheritance is None else [parentPropertyInheritance]
                                              )
        currentDictionary: Dict[str, PropertyInheritance] = {currentPropertyTemplate: currentProperty}
        currentKeys: List[str] = [currentPropertyTemplate]
        for inheritingProperty in inheritingProperties:
            inheritingData: Tuple[List[str], Dict[str, PropertyInheritance]] = \
                PropertyInheritanceGenerator.generatePropertyDictionaryAndKeysFromTemplate(inheritingProperty,
                                                                                           currentProperty)
            inheritingKeys: List[str] = inheritingData[0]
            inheritingDictionary: Dict[str, PropertyInheritance] = inheritingData[1]
            currentKeys += inheritingKeys
            if len(currentKeys) != len(set(currentKeys)):
                raise IndexError("Two or more properties provided had the same name.")
            currentDictionary = {**currentDictionary, **inheritingDictionary}

        return (currentKeys, currentDictionary)

    @staticmethod
    def generatePropertyDictionaryFromTemplate(template,
                                               parentPropertyInheritance: typing.Union[PropertyInheritance,
                                                                                       None
                                                                                       ] = None
                                               ) -> Dict[str, PropertyInheritance]:
        return PropertyInheritanceGenerator.generatePropertyDictionaryAndKeysFromTemplate(
            template,
            parentPropertyInheritance
        )[1]
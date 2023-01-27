"""
A template for building PropertyInheritance objects.

Whilst not all properties necessarily need obey single-inheritance, we can at least construct a set of properties which
do, and which are typically useful for addressing problems in second-quantisation, involving a 1D chain of sites. As
such, these can be represented as a tree datastructure, and are visually shown below.

When updating this list, it is suggested to ensure that each property have a unique name. This isn't in general only
necessary to provide unambiguous keys for an output dictionary, and is not required by the property tree format.
Where multiple properties might have the same name, it is suggested to disambiguate by adding a prefix to the name to
specify a distinguishing part of its inheritance. Even if one intends only to use the tree output, it is recommended
this be adhered to in general, for reasons of future-proofing.

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

from SinglyInheritedPropertyInheritanceGeneration import PropertyInheritanceGenerator

_secondQuantisedTemplateTree = \
    ("GeneralFunction", [
        ("LabelledConstant", [
            ("LinearOperator", [
                ("HermitianOperator", [
                    ("PauliX", []),
                    ("PauliY", []),
                    ("PauliZ", []),
                    ("SpinX", []),
                    ("SpinY", []),
                    ("SpinZ", []),
                    ("NumberOperator", [])
                ]),
                ("AntiHermitianOperator", []),
                ("FermionicOperator", []),
                ("BosonicOperator", [
                    ("HardCoreOperator", [])
                ]),
                ("CreationOperator", []),
                ("AnnihilationOperator", []),
                ("SpinStateOperator", []),
                ("DiagonalOperator", [
                    ("ScalarOperator", [
                        ("IdentityOperator", [])
                    ])
                ]),
                ("SelfInverseOperator", [])
            ]),
            ("Number", [
                ("RealNumber", [
                    ("RationalNumber", [
                        ("Integer", [
                            ("ModuloInteger", [])
                        ])
                    ])
                ]),
                ("ImaginaryNumber", [])
            ]),
            ("Set", [
                ("List", [
                    ("IntegerList", [
                        ("ConsecutiveIntegerList", [
                            ("ZeroStartingList", [])
                        ])
                    ])
                ])
            ])
        ]),
        ("Function", [
            ("LargeOperator", [
                ("LargeAddition", []),
                ("LargeMultiplication", [])
            ]),
            ("BinaryOperator", [
                ("BinaryAddition", []),
                ("BinaryMultiplication", []),
                ("ListUnion", []),
                ("ListIntersection", []),
                ("ListSubtraction", [])
            ]),
            ("UnaryOperator", [
                ("AntiLinearOperator", [
                    ("HermitianConjugate", [])
                ]),
                ("ReverseList", [])
            ]),
            ("AssociativeOperator", [])
        ])
    ])

secondQuantisedPropertyTree = PropertyInheritanceGenerator.generatePropertyTreeFromTemplate(
    _secondQuantisedTemplateTree
)
secondQuantisedPropertyDictionary = PropertyInheritanceGenerator.generatePropertyDictionaryFromTemplate(
    _secondQuantisedTemplateTree
)
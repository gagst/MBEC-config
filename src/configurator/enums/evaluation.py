from enum import StrEnum


class SlotComponentEval(StrEnum):
    CORRECT_VALUE = "cmpt correct value"
    """Correct value is provided for the given component slot."""

    INCORRECT_VALUE = "cmpt incorrect value"
    """Incorrect value is provided for the given component slot."""

    VECTOR_VALUE_NO_MATCH = "cmpt vector value no match"
    """Cannot find the vector corresponding to the given component slot value."""

    NO_MATCH_SLOT = "cmpt no match slot"
    """Slot of the component cannot be matched with equipment (due to no component-equipment matching, or equipment does not have such slot)."""

    VECTOR_SHOULD_BE_STR = "shouldbe_{}"
    """Temporary string to indicate what value of the vector should be provided."""


class SlotEquipmentEval(StrEnum):
    CORRECT_VALUE = "eqpt correct value"
    """Correct value is provided for the given equipment slot."""

    INCORRECT_VALUE = "eqpt incorrect value"
    """Incorrect value is provided for the given equipment slot."""

    VECTOR_VALUE_NO_MATCH = "eqpt vector value no match"
    """Cannot find the vector corresponding to the given equipment slot value."""

    NO_MATCH_SLOT = "eqpt no match slot"
    """Slot of the equipment cannot be matched with component (due to no equipment-component matching, or component does not have such slot)."""


class EquipmentEval(StrEnum):
    FULLY_CORRECT = "eqpt correct"
    """Equipment is represented by some component. All slots of the equipment are correctly represented."""

    MATCH = "eqpt match"
    """Equipment is represented by some component."""

    NO_MATCH = "eqpt no match"
    """Equipment is not represented by any component."""


class ComponentEval(StrEnum):
    FULLY_CORRECT = "cmpt correct"
    """Component is matched with some equipment. All slots of the component are correct."""

    MATCH = "cmpt match"
    """Component is matched with some equipment."""

    NO_MATCH = "cmpt no match"
    """Component is not matched with any equipment."""


# Ignored slots: "name", "originalName", "isExternal", "hasInitialCapacity", "hasSelfDischarge"
class EvaluationNonVectorSlot(StrEnum):
    HAS_MAX_GENERATION = "hasMaxGeneration"
    HAS_MAX_CONSUMPTION = "hasMaxConsumption"
    HAS_MAX_CAPACITY = "hasMaxCapacity"
    HAS_EFFICIENCY = "hasEfficiency"
    HAS_FLEXIBLE_PERIOD_START = "hasFlexiblePeriodStart"
    HAS_FLEXIBLE_PERIOD_END = "hasFlexiblePeriodEnd"
    HAS_ENERGY_REQUIREMENT = "hasEnergyRequirement"


class EvaluationVectorSlot(StrEnum):
    HAS_GENERATION_VECTOR = "hasGenerationVector"
    HAS_CONSUMPTION_VECTOR = "hasConsumptionVector"

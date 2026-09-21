from enum import StrEnum


class ComponentTypeString(StrEnum):
    FIXED_GENERATION = "fixed generation"
    FIXED_CONSUMPTION = "fixed consumption"
    FLEXIBLE_GENERATION = "flexible generation"
    FLEXIBLE_CONSUMPTION = "flexible consumption"
    TIME_FLEXIBLE_CONSUMPTION = "time flexible consumption"
    STORAGE = "storage"
    INTERCONNECTOR = "interconnector"

from typing import Literal

from ..constants import scenario_fields


class Infrastructure:
    def __init__(self, name: str, infrastructure_type: Literal["e", "h"]):
        self._name = name
        if infrastructure_type not in ["e", "h"]:
            raise NotImplementedError(f"Infrastructure type {infrastructure_type} is not defined!")
        else:
            self._infrastructure_type = infrastructure_type

        self._is_control_adjusted = False
        self._max_control_generation_kw = 0
        self._max_control_consumption_kw = 0

        self._max_fixed_generation_kw = 0
        self._max_fixed_consumption_kw = 0

    def __eq__(self, other):
        if not isinstance(other, Infrastructure):
            return NotImplemented
        return (self.name, self.infrastructure_type) == (other.name, other.infrastructure_type)

    def __hash__(self):
        return hash((self.name, self.infrastructure_type))

    def __str__(self):
        return f"{self.name} ({self.infrastructure_type})"

    def __repr__(self):
        return f"Infrastructure(name='{self.name}', infrastructure_type={self.infrastructure_type})"

    @property
    def name(self):
        return self._name

    @property
    def infrastructure_type(self):
        return self._infrastructure_type

    @property
    def max_control_generation_kw(self):
        if self._is_control_adjusted:
            return self._max_control_generation_kw
        else:
            raise Exception(
                f"Infrastructure {self.name}: "
                f"increase_max_control_* or increase_max_fixed_* were not called, thus cannot return max_control_generation_kw "
            )

    @property
    def max_control_consumption_kw(self):
        if self._is_control_adjusted:
            return self._max_control_consumption_kw
        else:
            raise Exception(
                f"Infrastructure {self.name}: "
                f"increase_max_control_* or increase_max_fixed_* were not called, thus cannot return max_control_consumption_kw "
            )

    @property
    def max_fixed_generation_kw(self):
        if self._is_control_adjusted:
            return self._max_fixed_generation_kw
        else:
            raise Exception(
                f"Infrastructure {self.name}: "
                f"increase_max_control_* or increase_max_fixed_* were not called, thus cannot return max_fixed_generation_kw "
            )

    @property
    def max_fixed_consumption_kw(self):
        if self._is_control_adjusted:
            return self._max_fixed_consumption_kw
        else:
            raise Exception(
                f"Infrastructure {self.name}: "
                f"increase_max_control_* or increase_max_fixed_* were not called, thus cannot return max_fixed_consumption_kw "
            )

    @property
    def required_control_generation_kw(self):
        if self._is_control_adjusted:
            if self.max_fixed_consumption_kw > self.max_control_generation_kw:
                return self.max_fixed_consumption_kw - self.max_control_generation_kw
            else:
                return 0
        else:
            raise Exception(
                f"Infrastructure {self.name}: "
                f"increase_max_control_* or increase_max_fixed_* were not called, thus cannot return required_control_generation_kw "
            )

    @property
    def required_control_consumption_kw(self):
        if self._is_control_adjusted:
            if self.max_fixed_generation_kw > self.max_control_consumption_kw:
                return self.max_fixed_generation_kw - self.max_control_consumption_kw
            else:
                return 0
        else:
            raise Exception(
                f"Infrastructure {self.name}: "
                f"increase_max_control_* or increase_max_fixed_* were not called, thus cannot return required_control_consumption_kw "
            )

    def increase_max_control_generation(self, by_kw: float):
        self._is_control_adjusted = True
        self._max_control_generation_kw += by_kw

    def increase_max_control_consumption(self, by_kw: float):
        self._is_control_adjusted = True
        self._max_control_consumption_kw += by_kw

    def increase_max_fixed_generation(self, by_kw: float):
        self._is_control_adjusted = True
        self._max_fixed_generation_kw += by_kw

    def increase_max_fixed_consumption(self, by_kw: float):
        self._is_control_adjusted = True
        self._max_fixed_consumption_kw += by_kw

    def to_dict(self) -> dict:
        return {scenario_fields.NAME: self.name, scenario_fields.INFRASTRUCTURE_TYPE: self.infrastructure_type}

    @classmethod
    def from_dict(cls, data: dict) -> "Infrastructure":
        name = data.get(scenario_fields.NAME)
        infrastructure_type = data.get(scenario_fields.INFRASTRUCTURE_TYPE)
        if name is None or infrastructure_type is None:
            raise ValueError("Both 'name' and 'infrastructure_type' must be provided in the dictionary.")
        return cls(name=name, infrastructure_type=infrastructure_type)

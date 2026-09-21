from pathlib import Path
from typing import Optional, Union

import yaml

from ..constants.file_names import FileNames
from ..constants import scenario_fields
from .equipment.equipment import Equipment
from .infrastructure import Infrastructure


class Scenario:
    def __init__(self):
        self._equipment = []
        self._infrastructures = set()
        self._names = set()

    @classmethod
    def from_dict(cls, data: dict):
        instance = cls()

        infrastructures = [
            Infrastructure.from_dict(infra_dict) for infra_dict in data.get(scenario_fields.INFRASTRUCTURES, [])
        ]
        for i in infrastructures:
            instance.add(i)

        equipment = [
            Equipment.from_dict(equip_dict, infrastructures=infrastructures)
            for equip_dict in data.get(scenario_fields.EQUIPMENT, [])
        ]
        for e in equipment:
            instance.add(e)

        return instance

    @classmethod
    def from_yaml(cls, dir_path: Path) -> "Scenario":
        path = dir_path / FileNames.SCENARIO
        with open(path, "r", encoding="utf-8") as f:
            scenario_data = yaml.safe_load(f)
        scenario = cls.from_dict(scenario_data)
        return scenario

    def add(self, smth: Union[Infrastructure, Equipment], exist_ok=False):
        if isinstance(smth, Infrastructure):
            if exist_ok or smth.name not in self._names:
                self._infrastructures.add(smth)
                self._names.add(smth.name)
            else:
                raise ValueError(f"There is already an infrastructure or equipment named {smth.name} in the scenario.")
        elif isinstance(smth, Equipment):
            if exist_ok or smth.name not in self._names:
                for i in smth.infrastructures:
                    if i not in self._infrastructures:
                        raise ValueError(
                            f"The infrastructure {i.name} is not added to the scenario. Please add it before adding the equipment that is connected to it."
                        )
                self._equipment.append(smth)
                self._names.add(smth.name)
            else:
                raise ValueError(f"There is already an infrastructure or equipment named {smth.name} in the scenario.")
        else:
            raise TypeError(f"The type {type(smth)} is not supported in scenario.")

    @property
    def equipment(self) -> list[Equipment]:
        return sorted(self._equipment, key=lambda x: x.name)

    @property
    def infrastructures(self) -> list[Infrastructure]:
        return sorted(self._infrastructures, key=lambda x: x.name)

    @property
    def e_infrastructures(self) -> list[Infrastructure]:
        return sorted([v for v in self._infrastructures if v.infrastructure_type == "e"], key=lambda x: x.name)

    @property
    def h_infrastructures(self) -> list[Infrastructure]:
        return sorted([v for v in self._infrastructures if v.infrastructure_type == "h"], key=lambda x: x.name)

    @property
    def buildings(self) -> list[str]:
        names = set()
        for equipment in self._equipment:
            if equipment.building is not None:
                names.add(equipment.building)
        return sorted(names)

    def get_equipment(self, name: str) -> Optional[Equipment]:
        for equipment in self._equipment:
            if equipment.name == name:
                return equipment
        return None

    def get_infrastructure(self, name: str) -> Optional[Infrastructure]:
        for i in self._infrastructures:
            if i.name == name:
                return i
        return None

    def get_building_equipment(self, building_name: Optional[str]) -> list[Equipment]:
        result = []
        for equipment in self._equipment:
            if equipment.building == building_name:
                result.append(equipment)
        return sorted(result, key=lambda x: x.name)

    def get_building_infrastructures(
        self,
        building_name: Optional[str],
        infrastructure_type: Optional[str],
    ) -> list[Infrastructure]:
        result = set()
        for equipment in self.get_building_equipment(building_name):
            infrastructures = equipment.infrastructures
            for i in infrastructures:
                if infrastructure_type is not None and i.infrastructure_type == infrastructure_type:
                    result.add(i)
        return sorted(result, key=lambda x: x.name)

    def get_infrastructure_equipment(self, infrastructure: Union[str, Infrastructure]) -> list[Equipment]:
        if isinstance(infrastructure, Infrastructure):
            infrastructure_name = infrastructure.name
        elif isinstance(infrastructure, str):
            infrastructure_name = infrastructure
        else:
            raise TypeError(f"The type {type(infrastructure)} is not supported in get_infrastructure_equipment.")

        result = []
        for equipment in self._equipment:
            if infrastructure_name in equipment.infrastructure_names:
                result.append(equipment)
        return sorted(result, key=lambda x: x.name)

    def get_infrastructure_buildings(self, infrastructure: Union[str, Infrastructure]) -> list[str]:
        if isinstance(infrastructure, Infrastructure):
            infrastructure = infrastructure.name
        elif isinstance(infrastructure, str):
            infrastructure = infrastructure
        else:
            raise TypeError(f"The type {type(infrastructure)} is not supported in get_infrastructure_buildings.")

        result = set()
        for equipment in self._equipment:
            if infrastructure in equipment.infrastructure_names and equipment.building is not None:
                result.add(equipment.building)
        return sorted(result)

    def to_dict(self) -> dict:
        self.validate()
        return {
            scenario_fields.INFRASTRUCTURES: [v.to_dict() for v in self.infrastructures],
            scenario_fields.EQUIPMENT: [e.to_dict() for e in self.equipment],
        }

    def to_yaml(self, dir_path: Path) -> None:
        path = dir_path / FileNames.SCENARIO
        with path.open("w", encoding="utf-8") as fh:
            yaml.dump(self.to_dict(), fh, default_flow_style=False, sort_keys=True)

    def validate(self):
        """
        Raises Exception if any infrastructure has no equipment connected.
        """
        for i in self._infrastructures:
            if len(self.get_infrastructure_equipment(i.name)) == 0:
                raise Exception(f"Infrastructure {i.name} has no equipment connected.")

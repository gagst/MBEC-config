import abc
from dataclasses import dataclass, field
from typing import Optional, Union

from ...constants import scenario_fields
from ...enums.evaluation import EvaluationNonVectorSlot
from ...entities import brick_lite, s4bldg_lite
from ...utils.config import ConfigLoader
from ...utils.random import RandomTool
from ..equipment.equipment import META_DICT, META_SIMILAR, Equipment
from ..infrastructure import Infrastructure
from ..kees_lite import Component, FixedConsumptionComponent


@dataclass
class Consumption(Equipment, abc.ABC):
    max_consumption: float = field(
        init=False,
        metadata={
            META_DICT: scenario_fields.MAX_CONSUMPTION_KW,
            META_SIMILAR: EvaluationNonVectorSlot.HAS_MAX_CONSUMPTION,
        },
    )

    @classmethod
    def create_random(
        cls,
        config_loader: ConfigLoader,
        name: str,
        infrastructures: list[Infrastructure],
        building: Optional[str] = None,
        *args,
        **kwargs,
    ) -> "Consumption":
        config = config_loader.get_section(cls.__name__)
        if len(infrastructures) != 1:
            raise ValueError(f"Consumption {name} must be connected to one infrastructure.")
        consumption = cls.create(name=name, infrastructures=infrastructures, building=building)
        consumption.is_controllable = False
        consumption.is_external = False
        max_cons = RandomTool.select_uniform(config["cons_at_least_kw"], config["cons_at_most_kw"], 2)
        consumption.max_consumption = max_cons
        consumption.infrastructures[0].increase_max_fixed_consumption(max_cons)
        return consumption

    @property
    def text_description_type(self) -> Optional[str]:
        return None

    @property
    def text_description_parameters(self) -> Optional[str]:
        return None


@dataclass
class ElectricalConsumption(Consumption):
    def add_s4bldg_description(
        self,
        id_str: str,
        semantic_description: s4bldg_lite.SemanticDescription,
        building_space: Optional[s4bldg_lite.BuildingSpace],
    ):
        space_id = building_space.id if building_space is not None else None
        semantic_description.electricAppliances.append(s4bldg_lite.ElectricAppliance(id=id_str, isContainedIn=space_id))

    def add_brick_description(
        self,
        id_str: str,
        semantic_description: brick_lite.SemanticDescription,
        building: Optional[brick_lite.Building],
        loops: Optional[list[brick_lite.Loop]],
        systems: Optional[list[brick_lite.System]],
    ):
        building_id = building.id if building is not None else None
        equipment = brick_lite.BuildingElectricalMeter(id=id_str, hasLocation=building_id)
        if loops is not None:
            for loop in loops:
                loop.hasPart.append(equipment.id)
        if systems is not None:
            for system in systems:
                system.hasPart.append(equipment.id)
        semantic_description.equipment.append(equipment)

    @property
    def reference_component_representation(self) -> list[Union[Component, list[Component]]]:
        return [
            FixedConsumptionComponent(
                name=self.name,
                hasConsumptionVector=self.e_infrastructures[0].name,
                isExternal=self.is_external,
            )
        ]


@dataclass
class HeatingConsumption(Consumption):
    def add_s4bldg_description(
        self,
        id_str: str,
        semantic_description: s4bldg_lite.SemanticDescription,
        building_space: Optional[s4bldg_lite.BuildingSpace],
    ):
        space_id = building_space.id if building_space is not None else None
        semantic_description.spaceHeaters.append(s4bldg_lite.SpaceHeater(id=id_str, isContainedIn=space_id))

    def add_brick_description(
        self,
        id_str: str,
        semantic_description: brick_lite.SemanticDescription,
        building: Optional[brick_lite.Building],
        loops: Optional[list[brick_lite.Loop]],
        systems: Optional[list[brick_lite.System]],
    ):
        building_id = building.id if building is not None else None
        equipment = brick_lite.BuildingHotWaterMeter(id=id_str, hasLocation=building_id)
        if loops is not None:
            for loop in loops:
                loop.hasPart.append(equipment.id)
        if systems is not None:
            for system in systems:
                system.hasPart.append(equipment.id)
        semantic_description.equipment.append(equipment)

    @property
    def reference_component_representation(self) -> list[Union[Component, list[Component]]]:
        return [
            FixedConsumptionComponent(
                name=self.name,
                hasConsumptionVector=self.h_infrastructures[0].name,
                isExternal=self.is_external,
            )
        ]

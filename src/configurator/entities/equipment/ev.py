from dataclasses import dataclass, field
from typing import Optional, Union

from ..s4bldg_lite import PropertyValue
from ...constants import scenario_fields
from ...enums.evaluation import EvaluationNonVectorSlot
from ...entities import brick_lite, s4bldg_lite
from ...utils.config import ConfigLoader
from ...utils.random import RandomTool
from ..brick_lite import PropValue
from ..infrastructure import Infrastructure
from ..kees_lite import Component, FlexibleConsumptionComponent, TimeFlexibleConsumptionComponent
from .equipment import META_DICT, META_SIMILAR, Equipment


@dataclass
class EV(Equipment):
    energy_requirement: float = field(
        init=False,
        metadata={
            META_DICT: scenario_fields.ENERGY_REQUIREMENT_KWH,
            META_SIMILAR: EvaluationNonVectorSlot.HAS_ENERGY_REQUIREMENT,
        },
    )
    max_consumption: float = field(
        init=False,
        metadata={
            META_DICT: scenario_fields.MAX_CONSUMPTION_KW,
            META_SIMILAR: EvaluationNonVectorSlot.HAS_MAX_CONSUMPTION,
        },
    )
    time_from: str = field(
        init=False,
        metadata={META_DICT: scenario_fields.TIME_FROM, META_SIMILAR: EvaluationNonVectorSlot.HAS_FLEXIBLE_PERIOD_START},
    )
    time_till: str = field(
        init=False,
        metadata={META_DICT: scenario_fields.TIME_TILL, META_SIMILAR: EvaluationNonVectorSlot.HAS_FLEXIBLE_PERIOD_END},
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
    ) -> "EV":
        config = config_loader.get_section(cls.__name__)
        if len(infrastructures) != 1:
            raise ValueError(f"EV {name} must be connected to one infrastructure.")
        ev = cls.create(name=name, infrastructures=infrastructures, building=building)
        ev.is_controllable = True
        ev.is_external = False
        required = RandomTool.select_uniform(
            config["required_cons_at_least_kwh"], config["required_cons_at_most_kwh"], 2
        )
        ev.energy_requirement = required
        max_cons = RandomTool.select_uniform(config["cons_at_least_kw"], config["cons_at_most_kw"], 2)
        ev.max_consumption = max_cons
        ev.time_from = config["time_from"]
        ev.time_till = config["time_till"]
        ev.infrastructures[0].increase_max_control_consumption(max_cons)
        return ev

    def add_s4bldg_description(
        self,
        id_str: str,
        semantic_description: s4bldg_lite.SemanticDescription,
        building_space: Optional[s4bldg_lite.BuildingSpace],
    ):
        # Note that currently it is represented similarly to electrical consumption
        space_id = building_space.id if building_space is not None else None
        max_power = PropertyValue(hasValue=self.max_consumption, isMeasuredIn="KW")

        semantic_description.electricAppliances.append(
            s4bldg_lite.ElectricAppliance(
                id=id_str,
                isContainedIn=space_id,
                maximumApparentPower=max_power,
            )
        )

    def add_brick_description(
        self,
        id_str: str,
        semantic_description: brick_lite.SemanticDescription,
        building: Optional[brick_lite.Building],
        loops: Optional[list[brick_lite.Loop]],
        systems: Optional[list[brick_lite.System]],
    ):
        building_id = building.id if building is not None else None
        max_cons = PropValue(value=self.max_consumption, hasUnit="KW")
        direction = PropValue(value="unidirectional", hasUnit=None)
        equipment = brick_lite.ElectricVehicleChargingStation(
            id=id_str,
            ratedPowerInput=max_cons,
            electricVehicleChargerDirectionality=direction,
            hasLocation=building_id,
        )
        if loops is not None:
            for loop in loops:
                loop.hasPart.append(equipment.id)
        if systems is not None:
            for system in systems:
                system.hasPart.append(equipment.id)
        semantic_description.equipment.append(equipment)

    @property
    def text_description_type(self) -> str:
        return "electric vehicle"

    @property
    def text_description_parameters(self) -> Optional[str]:
        building = self.building
        if building is None:
            return (
                f"Electric vehicle requires {self.energy_requirement} kWh"
                f" of energy to be charged every day from {self.time_from} "
                f"to {self.time_till}. The maximum allowed power for electric vehicle charging "
                f"is {self.max_consumption} kWh."
            )
        else:
            return (
                f'Electric vehicle in the building "{building}" requires {self.energy_requirement} kWh'
                f' of energy to be charged every day from {self.time_from} '
                f'to {self.time_till}. The maximum allowed power for electric vehicle charging '
                f'in {building} is {self.max_consumption} kW.'
            )

    @property
    def reference_component_representation(self) -> list[Union[Component, list[Component]]]:
        return [
            TimeFlexibleConsumptionComponent(
                name=self.name,
                hasConsumptionVector=self.e_infrastructures[0].name,
                hasMaxConsumption=self.max_consumption,
                hasEnergyRequirement=self.energy_requirement,
                hasFlexiblePeriodStart=self.time_from,
                hasFlexiblePeriodEnd=self.time_till,
                isExternal=self.is_external,
            ),
            FlexibleConsumptionComponent(
                name=self.name,
                hasConsumptionVector=self.e_infrastructures[0].name,
                hasMaxConsumption=self.max_consumption,
                isExternal=self.is_external,
            ),
        ]

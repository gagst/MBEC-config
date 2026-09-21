import abc
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
from ..kees_lite import Component, StorageComponent
from .equipment import META_DICT, META_SIMILAR, Equipment


@dataclass
class Storage(Equipment, abc.ABC):
    max_generation: float = field(
        init=False,
        metadata={META_DICT: scenario_fields.MAX_GENERATION_KW, META_SIMILAR: EvaluationNonVectorSlot.HAS_MAX_GENERATION},
    )
    max_consumption: float = field(
        init=False,
        metadata={
            META_DICT: scenario_fields.MAX_CONSUMPTION_KW,
            META_SIMILAR: EvaluationNonVectorSlot.HAS_MAX_CONSUMPTION,
        },
    )
    max_capacity: float = field(
        init=False,
        metadata={META_DICT: scenario_fields.MAX_CAPACITY_KWH, META_SIMILAR: EvaluationNonVectorSlot.HAS_MAX_CAPACITY},
    )
    efficiency: float = field(
        init=False, metadata={META_DICT: scenario_fields.EFFICIENCY, META_SIMILAR: EvaluationNonVectorSlot.HAS_EFFICIENCY}
    )
    self_discharge: float = field(init=False, metadata={META_DICT: scenario_fields.SELF_DISCHARGE})

    @classmethod
    def create_random(
        cls,
        config_loader: ConfigLoader,
        name: str,
        infrastructures: list[Infrastructure],
        building: Optional[str] = None,
        *args,
        **kwargs,
    ) -> "Storage":
        config = config_loader.get_section(cls.__name__)
        if len(infrastructures) != 1:
            raise ValueError(f"Storage {name} must be connected to one infrastructure.")
        storage = cls.create(name=name, infrastructures=infrastructures, building=building)
        storage.is_controllable = True
        storage.is_external = RandomTool.is_event_triggered(config["external_prob"])
        c_rate = RandomTool.select_uniform(config["c_rate_at_least"], config["c_rate_at_most"], 2)
        max_capacity = RandomTool.select_uniform(config["capacity_at_least_kwh"], config["capacity_at_most_kwh"], 2)
        storage.max_capacity = max_capacity
        max_rate = round(c_rate * max_capacity, 2)
        storage.max_generation = max_rate
        storage.max_consumption = max_rate
        efficiency = RandomTool.select_uniform(config["efficiency_at_least"], config["efficiency_at_most"], 2)
        storage.efficiency = efficiency
        self_discharge = RandomTool.select_uniform(
            config["self_discharge_at_least"], config["self_discharge_at_most"], 2
        )
        storage.self_discharge = self_discharge
        storage.infrastructures[0].increase_max_control_generation(max_rate)
        storage.infrastructures[0].increase_max_control_consumption(max_rate)
        return storage


class ElectricalStorage(Storage):
    def add_s4bldg_description(
        self,
        id_str: str,
        semantic_description: s4bldg_lite.SemanticDescription,
        building_space: Optional[s4bldg_lite.BuildingSpace],
    ):
        space_id = building_space.id if building_space is not None else None

        max_gen = PropertyValue(hasValue=self.max_generation, isMeasuredIn="KW")

        max_cons = PropertyValue(hasValue=self.max_consumption, isMeasuredIn="KW")
        max_cons_slot_options = {"nominalPowerConsumption": max_cons, "nominalEnergyConsumption": max_cons}
        max_cons_slot = RandomTool.select_key_value(max_cons_slot_options)

        semantic_description.electricFlowStorageDevices.append(
            s4bldg_lite.ElectricFlowStorageDevice(
                id=id_str, isContainedIn=space_id, storageType="BATTERY", apparentPowerMax=max_gen, **max_cons_slot
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
        max_gen = PropValue(value=self.max_generation, hasUnit="KW")
        max_cons = PropValue(value=self.max_consumption, hasUnit="KW")
        efficiency = PropValue(value=self.efficiency)
        equipment = brick_lite.Battery(
            id=id_str,
            ratedPowerOutput=max_gen,
            ratedPowerInput=max_cons,
            conversionEfficiency=efficiency,
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
        return "an electrical energy storage system"

    @property
    def text_description_parameters(self) -> Optional[str]:
        # NOTE: self discharge is not considered!
        building = self.building
        if building is None:
            first_sentence = f"The electrical energy storage system has a maximum capacity of {self.max_capacity} kWh."

        else:
            first_sentence = f'The electrical energy storage system installed in the building "{building}" has a maximum capacity of {self.max_capacity} kWh.'

        description = first_sentence + (
            f" The storage system's maximum charging power is "
            f"{self.max_consumption} kW,"
            f" and its discharging power is {self.max_generation} kW. "
            f"The storage system's charging"
            f" and discharging efficiencies are {self.efficiency}."
        )
        return description

    @property
    def reference_component_representation(self) -> list[Union[Component, list[Component]]]:
        return [
            StorageComponent(
                name=self.name,
                hasGenerationVector=self.e_infrastructures[0].name,
                hasConsumptionVector=self.e_infrastructures[0].name,
                hasMaxGeneration=self.max_generation,
                hasMaxConsumption=self.max_consumption,
                hasEfficiency=self.efficiency,
                hasMaxCapacity=self.max_capacity,
                isExternal=self.is_external,
                hasSelfDischarge=self.self_discharge
            )
        ]

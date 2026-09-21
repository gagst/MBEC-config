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
from ..kees_lite import Component, FlexibleConsumptionComponent, FlexibleGenerationComponent, InterconnectorComponent
from .equipment import META_DICT, META_SIMILAR, Equipment


@dataclass
class HeatPump(Equipment):
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
    cop: float = field(
        init=False, metadata={META_DICT: scenario_fields.COP, META_SIMILAR: EvaluationNonVectorSlot.HAS_EFFICIENCY}
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
    ) -> "HeatPump":
        config = config_loader.get_section(cls.__name__)
        if len(infrastructures) != 2:
            raise ValueError(f"Heat pump {name} must be connected to two infrastructures.")
        hp = cls.create(name=name, infrastructures=infrastructures, building=building)
        hp.is_controllable = True
        hp.is_external = RandomTool.is_event_triggered(config["external_prob"])
        max_gen = RandomTool.select_uniform(config["gen_at_least_kw"], config["gen_at_most_kw"], 2)
        hp.max_generation = max_gen
        cop = RandomTool.select_uniform(config["cop_at_least"], config["cop_at_most"], 2)
        hp.cop = cop
        max_cons = round(max_gen / cop, 2)
        hp.max_consumption = max_cons

        has_e_infrastructure = False
        has_h_infrastructure = False
        for infrastructure in hp.infrastructures:
            if infrastructure.infrastructure_type == "e":
                infrastructure.increase_max_control_consumption(max_cons)
                has_e_infrastructure = True
            elif infrastructure.infrastructure_type == "h":
                infrastructure.increase_max_control_generation(max_gen)
                has_h_infrastructure = True
        if not (has_h_infrastructure and has_e_infrastructure):
            raise ValueError(f"Heat pump {name} should be connected to both e and h infrastructures.")
        return hp

    def add_s4bldg_description(
        self,
        id_str: str,
        semantic_description: s4bldg_lite.SemanticDescription,
        building_space: Optional[s4bldg_lite.BuildingSpace],
    ):
        space_id = building_space.id if building_space is not None else None

        max_gen = PropertyValue(hasValue=self.max_generation, isMeasuredIn="KW")
        max_gen_slot_options = {
            "outputCapacity": max_gen,
            "nominalHeatingCapacity": max_gen,
            "nominalCapacity": max_gen,
        }
        max_gen_slot = RandomTool.select_key_value(max_gen_slot_options)

        max_cons = PropertyValue(hasValue=self.max_consumption, isMeasuredIn="KW")
        max_cons_slot_options = {
            "nominalPowerConsumption": max_cons,
            "nominalEnergyConsumption": max_cons,
            "apparentPowerMax": max_cons,
        }
        max_cons_slot = RandomTool.select_key_value(max_cons_slot_options)

        semantic_description.energyConversionDevices.append(
            s4bldg_lite.EnergyConversionDevice(id=id_str, isContainedIn=space_id, **max_gen_slot, **max_cons_slot)
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
        cop = PropValue(value=self.cop)
        equipment = brick_lite.PackagedHeatPump(
            id=id_str,
            ratedPowerOutput=max_gen,
            ratedPowerInput=max_cons,
            conversionEfficiency=cop,
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
        return "a heat pump"

    @property
    def text_description_parameters(self) -> str:
        building = self.building
        heat_pump_string = "The heat pump" if building is None else f'The heat pump installed in the building "{building}"'
        return (
            f"{heat_pump_string} has a coefficient of performance of {self.cop}."
            f" {heat_pump_string} has a maximum electrical consumption of {self.max_consumption} kW,"
            f" and its maximum heat generation is {self.max_generation} kW."
        )

    @property
    def reference_component_representation(self) -> list[Union[Component, list[Component]]]:
        return [
            InterconnectorComponent(
                name=self.name,
                hasGenerationVector=self.h_infrastructures[0].name,
                hasConsumptionVector=self.e_infrastructures[0].name,
                hasMaxGeneration=self.max_generation,
                hasMaxConsumption=self.max_consumption,
                hasEfficiency=self.cop,
                isExternal=self.is_external,
            ),
            [
                FlexibleGenerationComponent(
                    name=self.name,
                    hasGenerationVector=self.h_infrastructures[0].name,
                    hasMaxGeneration=self.max_generation,
                    isExternal=self.is_external,
                ),
                FlexibleConsumptionComponent(
                    name=self.name,
                    hasConsumptionVector=self.e_infrastructures[0].name,
                    hasMaxConsumption=self.max_consumption,
                    isExternal=self.is_external,
                ),
            ],
        ]

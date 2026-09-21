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
from ..kees_lite import Component, FlexibleConsumptionComponent, FlexibleGenerationComponent, InterconnectorComponent
from .equipment import META_DICT, META_SIMILAR, Equipment


@dataclass
class Grid(Equipment, abc.ABC):
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

    @classmethod
    def create_random(
        cls,
        config_loader: ConfigLoader,
        name: str,
        infrastructures: list[Infrastructure],
        building: Optional[str] = None,
        gen_at_least_kw: Optional[float] = None,
        cons_at_least_kw: Optional[float] = None,
        *args,
        **kwargs,
    ) -> "Grid":
        config = config_loader.get_section(cls.__name__)
        if len(infrastructures) != 1:
            raise ValueError(f"Grid {name} must be connected to one infrastructure")

        grid = cls.create(name=name, infrastructures=infrastructures, building=building)
        grid.is_controllable = True
        grid.is_external = True

        cons_ratio = config["consumption_ratio"]

        gen_at_least_kw = gen_at_least_kw if gen_at_least_kw is not None else config["gen_at_least_kw"]
        configured_cons_at_least_kw = config["gen_at_least_kw"] * cons_ratio
        required_cons_at_least_kw = cons_at_least_kw if cons_at_least_kw is not None else 0
        max_gen = RandomTool.select_uniform(gen_at_least_kw, config["gen_at_most_kw"], 2)
        grid.max_generation = max_gen
        if required_cons_at_least_kw > 0 or RandomTool.is_event_triggered(config["allow_consumption_prob"]):
            cons_lower_bound = max(required_cons_at_least_kw, configured_cons_at_least_kw)
            cons_upper_bound = max(config["gen_at_most_kw"] * cons_ratio, cons_lower_bound)
            max_cons = RandomTool.select_uniform(cons_lower_bound, cons_upper_bound, 2)
        else:
            max_cons = 0
        grid.max_consumption = max_cons
        grid.infrastructures[0].increase_max_control_generation(max_gen)
        grid.infrastructures[0].increase_max_control_consumption(max_cons)
        return grid

    def add_s4bldg_description(
        self,
        id_str: str,
        semantic_description: s4bldg_lite.SemanticDescription,
        building_space: Optional[s4bldg_lite.BuildingSpace],
    ):
        space_id = building_space.id if building_space is not None else None

        max_gen = PropertyValue(hasValue=self.max_generation, isMeasuredIn="KW")
        max_cons = PropertyValue(hasValue=self.max_consumption, isMeasuredIn="KW")

        if self.max_generation > 0:
            semantic_description.flowMeters.append(
                s4bldg_lite.FlowMeter(id=id_str, isContainedIn=space_id, apparentPowerMax=max_gen)
            )
        if self.max_consumption > 0:
            semantic_description.flowMeters.append(
                s4bldg_lite.FlowMeter(id=id_str, isContainedIn=space_id, apparentPowerMax=max_cons)
            )


@dataclass
class ElectricalGrid(Grid):
    # Note: Transformer is not a good choice - can't differentiate between import and export max allowed power,
    # since one transformer is used for both export and import.

    def add_brick_description(
        self,
        id_str: str,
        semantic_description: brick_lite.SemanticDescription,
        building: Optional[brick_lite.Building],
        loops: Optional[list[brick_lite.Loop]],
        systems: Optional[list[brick_lite.System]],
    ):
        building_id = building.id if building is not None else None
        max_gen = self.max_generation
        max_cons = self.max_consumption
        if max_gen > 0:
            max_gen_val = PropValue(value=max_gen, hasUnit="KW")
            equipment = brick_lite.ElectricalMeter(id=id_str, ratedPowerInput=max_gen_val, hasLocation=building_id)
            if loops is not None:
                for loop in loops:
                    loop.hasPart.append(equipment.id)
            if systems is not None:
                for system in systems:
                    system.hasPart.append(equipment.id)
            semantic_description.equipment.append(equipment)
        if max_cons > 0:
            max_cons_val = PropValue(value=max_cons, hasUnit="KW")
            equipment = brick_lite.ElectricalMeter(id=id_str, ratedPowerOutput=max_cons_val, hasLocation=building_id)
            if loops is not None:
                for loop in loops:
                    loop.hasPart.append(equipment.id)
            if systems is not None:
                for system in systems:
                    system.hasPart.append(equipment.id)
            semantic_description.equipment.append(equipment)

    @property
    def text_description_type(self) -> Optional[str]:
        return "a national electric grid"

    @property
    def text_description_parameters(self) -> Optional[str]:
        max_cons = self.max_consumption
        max_gen = self.max_generation
        if max_cons > 0 and max_gen > 0:
            return (
                f"The national electric grid connection allows for importing {max_gen} kW"
                f" and exporting {max_cons} kW of electricity."
            )
        elif max_gen > 0:
            return f"The national electric grid connection allows for importing {max_gen} kW of electricity."
        else:
            raise NotImplementedError(
                f"Can't generate text description for equipment {self.name} with zero maximum generation!"
            )

    @property
    def reference_component_representation(self) -> list[Union[Component, list[Component]]]:
        max_cons = self.max_consumption
        max_gen = self.max_generation
        flexible_components_pair = []
        if max_gen > 0:
            flexible_components_pair.append(
                FlexibleGenerationComponent(
                    name=self.name,
                    hasMaxGeneration=self.max_generation,
                    hasGenerationVector=self.e_infrastructures[0].name,
                    isExternal=self.is_external,
                )
            )
        if max_cons > 0:
            flexible_components_pair.append(
                FlexibleConsumptionComponent(
                    name=self.name,
                    hasMaxConsumption=self.max_consumption,
                    hasConsumptionVector=self.e_infrastructures[0].name,
                    isExternal=self.is_external,
                )
            )
        interconnector_pair = []
        if max_gen > 0:
            interconnector_pair.append(
                InterconnectorComponent(
                    name=self.name,
                    hasMaxGeneration=self.max_generation,
                    hasGenerationVector=self.e_infrastructures[0].name,
                    isExternal=self.is_external,
                )
            )
        if max_cons > 0:
            interconnector_pair.append(
                InterconnectorComponent(
                    name=self.name,
                    hasMaxConsumption=self.max_consumption,
                    hasConsumptionVector=self.e_infrastructures[0].name,
                    isExternal=self.is_external,
                )
            )

        return [flexible_components_pair, interconnector_pair]


@dataclass
class HeatingGrid(Grid):
    def add_brick_description(
        self,
        id_str: str,
        semantic_description: brick_lite.SemanticDescription,
        building: Optional[brick_lite.Building],
        loops: Optional[list[brick_lite.Loop]],
        systems: Optional[list[brick_lite.System]],
    ):
        building_id = building.id if building is not None else None
        max_gen = self.max_generation
        max_cons = self.max_consumption
        if max_gen > 0:
            max_gen = PropValue(value=max_gen, hasUnit="KW")
            equipment = brick_lite.HotWaterMeter(id=id_str, ratedPowerInput=max_gen, hasLocation=building_id)
            if loops is not None:
                for loop in loops:
                    loop.hasPart.append(equipment.id)
            if systems is not None:
                for system in systems:
                    system.hasPart.append(equipment.id)
            semantic_description.equipment.append(equipment)
        if max_cons > 0:
            max_cons = PropValue(value=max_cons, hasUnit="KW")
            equipment = brick_lite.HotWaterMeter(id=id_str, ratedPowerOutput=max_cons, hasLocation=building_id)
            if loops is not None:
                for loop in loops:
                    loop.hasPart.append(equipment.id)
            if systems is not None:
                for system in systems:
                    system.hasPart.append(equipment.id)
            semantic_description.equipment.append(equipment)

    @property
    def text_description_type(self) -> Optional[str]:
        return "district heating"

    @property
    def text_description_parameters(self) -> Optional[str]:
        max_cons = self.max_consumption
        max_gen = self.max_generation
        if max_cons > 0 and max_gen > 0:
            return f"The district heating connection allows for importing {max_gen} kW and exporting {max_cons} kW of heat."
        elif max_gen > 0:
            return f"The district heating connection allows for importing {max_gen} kW of heat."
        else:
            raise NotImplementedError(
                f"Can't generate text description for equipment {self.name} with zero maximum generation!"
            )

    @property
    def reference_component_representation(self) -> list[Union[Component, list[Component]]]:
        max_cons = self.max_consumption
        max_gen = self.max_generation
        flexible_components_pair = []
        if max_gen > 0:
            flexible_components_pair.append(
                FlexibleGenerationComponent(
                    name=self.name,
                    hasMaxGeneration=self.max_generation,
                    hasGenerationVector=self.h_infrastructures[0].name,
                    isExternal=self.is_external,
                )
            )
        if max_cons > 0:
            flexible_components_pair.append(
                FlexibleConsumptionComponent(
                    name=self.name,
                    hasMaxConsumption=self.max_consumption,
                    hasConsumptionVector=self.h_infrastructures[0].name,
                    isExternal=self.is_external,
                )
            )
        interconnector_pair = []
        if max_gen > 0:
            interconnector_pair.append(
                InterconnectorComponent(
                    name=self.name,
                    hasMaxGeneration=self.max_generation,
                    hasGenerationVector=self.h_infrastructures[0].name,
                    isExternal=self.is_external,
                )
            )
        if max_cons > 0:
            interconnector_pair.append(
                InterconnectorComponent(
                    name=self.name,
                    hasMaxConsumption=self.max_consumption,
                    hasConsumptionVector=self.h_infrastructures[0].name,
                    isExternal=self.is_external,
                )
            )

        return [flexible_components_pair, interconnector_pair]

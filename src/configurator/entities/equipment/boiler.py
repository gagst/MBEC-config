from dataclasses import dataclass, field
from typing import Optional, Union

from ..s4bldg_lite import PropertyValue
from ...constants import scenario_fields
from ...enums.evaluation import EvaluationNonVectorSlot
from ...entities import brick_lite, s4bldg_lite
from ...utils.config import ConfigLoader
from ...utils.random import RandomTool
from ..brick_lite import PropValue
from ..equipment.equipment import Equipment, META_SIMILAR, META_DICT
from ..infrastructure import Infrastructure
from ..kees_lite import Component, FlexibleGenerationComponent, InterconnectorComponent


@dataclass
class Boiler(Equipment):
    max_generation: float = field(
        init=False,
        metadata={
            META_DICT: scenario_fields.MAX_GENERATION_KW,
            META_SIMILAR: EvaluationNonVectorSlot.HAS_MAX_GENERATION,
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
    ) -> "Boiler":
        config = config_loader.get_section(cls.__name__)
        if len(infrastructures) != 1:
            raise ValueError(f"Boiler {name} must be connected to one infrastructure.")
        boiler = cls.create(name=name, infrastructures=infrastructures, building=building)
        boiler.is_controllable = True
        boiler.is_external = RandomTool.is_event_triggered(config["external_prob"])
        max_gen = RandomTool.select_uniform(config["gen_at_least_kw"], config["gen_at_most_kw"], 2)
        boiler.max_generation = max_gen
        boiler.infrastructures[0].increase_max_control_generation(max_gen)
        return boiler

    def add_s4bldg_description(
        self,
        id_str: str,
        semantic_description: s4bldg_lite.SemanticDescription,
        building_space: Optional[s4bldg_lite.BuildingSpace],
    ):
        space_id = building_space.id if building_space is not None else None
        max_gen = PropertyValue(hasValue=self.max_generation, isMeasuredIn="KW")
        slot_options = {"outputCapacity": max_gen, "nominalHeatingCapacity": max_gen, "nominalCapacity": max_gen}
        slot = RandomTool.select_key_value(slot_options)
        semantic_description.boilers.append(s4bldg_lite.Boiler(id=id_str, isContainedIn=space_id, **slot))

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
        equipment = brick_lite.Boiler(id=id_str, ratedPowerOutput=max_gen, hasLocation=building_id)
        if loops is not None:
            for loop in loops:
                loop.hasPart.append(equipment.id)
        if systems is not None:
            for system in systems:
                system.hasPart.append(equipment.id)
        semantic_description.equipment.append(equipment)

    @property
    def text_description_type(self) -> str:
        return "a boiler"

    @property
    def text_description_parameters(self) -> str:
        building = self.building
        if building is None:
            return f"The boiler's max generation is {self.max_generation} kW."
        else:
            return f'The maximum generation of the boiler installed in the building "{building}" is {self.max_generation} kW.'

    @property
    def reference_component_representation(self) -> list[Union[Component, list[Component]]]:
        return [
            FlexibleGenerationComponent(
                name=self.name,
                hasMaxGeneration=self.max_generation,
                hasGenerationVector=self.h_infrastructures[0].name,
                isExternal=self.is_external,
            ),
            InterconnectorComponent(
                name=self.name,
                hasMaxGeneration=self.max_generation,
                hasGenerationVector=self.h_infrastructures[0].name,
                isExternal=self.is_external,
            ),
        ]

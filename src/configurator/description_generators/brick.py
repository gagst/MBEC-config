from pathlib import Path

from linkml_runtime.dumpers import RDFLibDumper
from linkml_runtime.utils.schemaview import SchemaView

from ..constants.file_names import FileNames
from ..constants.paths import BRICK_SCHEMA_PATH
from ..entities.brick_lite import (
    Building,
    HotWaterLoop,
    HotWaterSystem,
    SemanticDescription,
    ElectricalSystem,
)
from ..entities.scenario import Scenario
from ..utils.rdf import clean_brick_rdf, to_brick_id


def generate_brick_description(scenario_dir_path: Path, anonymize_ids: bool):
    if anonymize_ids:
        brick_description_path = scenario_dir_path / FileNames.BRICK_DESCRIPTION_ANON
    else:
        brick_description_path = scenario_dir_path / FileNames.BRICK_DESCRIPTION
    scenario = Scenario.from_yaml(scenario_dir_path)

    semantic_description = SemanticDescription()

    semantic_buildings = {
        name: Building(id=to_brick_id(name, no_type_description=False, type_description="building"))
        for name in scenario.buildings
    }
    semantic_description.buildings = list(semantic_buildings.values())

    semantic_loops = dict()
    semantic_systems = dict()
    for vector in scenario.infrastructures:
        connected_equipment = scenario.get_infrastructure_equipment(vector)
        if len(connected_equipment) >= 0:
            if vector.infrastructure_type == "e":
                semantic_systems[vector.name] = ElectricalSystem(
                    id=to_brick_id(vector.name, no_type_description=False, type_description="system")
                )
            if vector.infrastructure_type == "h":
                semantic_loops[vector.name] = HotWaterLoop(
                    id=to_brick_id(vector.name, no_type_description=False, type_description="loop")
                )
                semantic_systems[vector.name] = HotWaterSystem(
                    id=to_brick_id(vector.name, no_type_description=False, type_description="system")
                )

    semantic_description.loops = list(semantic_loops.values())
    semantic_description.systems = list(semantic_systems.values())

    for equipment in scenario.equipment:
        building_name = equipment.building
        if building_name is not None:
            building = semantic_buildings[building_name]
        else:
            building = None
        loops = [semantic_loops[vector] for vector in equipment.infrastructure_names if vector in semantic_loops]
        systems = [semantic_systems[vector] for vector in equipment.infrastructure_names if vector in semantic_systems]
        id_str = to_brick_id(
            equipment.name, no_type_description=anonymize_ids, type_description=equipment.text_description_type
        )
        equipment.add_brick_description(
            id_str=id_str,
            semantic_description=semantic_description,
            building=building,
            loops=loops,
            systems=systems,
        )

    schemaview = SchemaView(BRICK_SCHEMA_PATH)
    RDFLibDumper().dump(element=semantic_description, schemaview=schemaview, to_file=brick_description_path)

    clean_brick_rdf(brick_description_path)

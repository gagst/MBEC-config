from pathlib import Path

from linkml_runtime.dumpers import RDFLibDumper
from linkml_runtime.utils.schemaview import SchemaView

from ..constants.file_names import FileNames
from ..constants.paths import S4BLDG_SCHEMA_PATH
from ..entities.s4bldg_lite import Building, BuildingSpace, SemanticDescription
from ..entities.scenario import Scenario
from ..utils.rdf import clean_s4bldg_rdf, to_s4bldg_id


def generate_s4bldg_description(scenario_dir_path: Path, anonymize_ids: bool):
    if anonymize_ids:
        s4bldg_description_path = scenario_dir_path / FileNames.S4BLDG_DESCRIPTION_ANON
    else:
        s4bldg_description_path = scenario_dir_path / FileNames.S4BLDG_DESCRIPTION
    scenario = Scenario.from_yaml(scenario_dir_path)

    semantic_description = SemanticDescription()

    semantic_buildings = {
        name: Building(id=to_s4bldg_id(name, no_type_description=False, type_description="building"))
        for name in scenario.buildings
    }
    semantic_description.buildings = list(semantic_buildings.values())

    semantic_building_spaces = {
        b_name: BuildingSpace(
            id=to_s4bldg_id(b_name, no_type_description=False, type_description="space"),
            isSpaceOf=semantic_buildings[b_name].id,
        )
        for b_name in semantic_buildings.keys()
    }
    semantic_description.buildingSpaces = list(semantic_building_spaces.values())

    for equipment in scenario.equipment:
        building_name = equipment.building
        if building_name is not None:
            building_space = semantic_building_spaces[building_name]
        else:
            building_space = None
        id_str = to_s4bldg_id(
            equipment.name, no_type_description=anonymize_ids, type_description=equipment.text_description_type
        )
        equipment.add_s4bldg_description(
            id_str=id_str, semantic_description=semantic_description, building_space=building_space
        )

    schemaview = SchemaView(S4BLDG_SCHEMA_PATH)
    RDFLibDumper().dump(element=semantic_description, schemaview=schemaview, to_file=s4bldg_description_path)

    clean_s4bldg_rdf(s4bldg_description_path)

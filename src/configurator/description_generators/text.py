from pathlib import Path

import inflect

from ..constants.file_names import FileNames
from ..entities.equipment import HeatPump
from ..entities.scenario import Scenario
from ..utils.text import TextDescription, enumeration


def generate_text_description(scenario_dir_path: Path):
    p = inflect.engine()
    text = TextDescription()
    text_description_path = scenario_dir_path / FileNames.TEXT_DESCRIPTION
    scenario = Scenario.from_yaml(scenario_dir_path)

    buildings = scenario.buildings
    n_buildings = len(buildings)
    n_buildings_str = str(n_buildings) + " " + p.plural_noun("building", n_buildings)
    text.add_sentence(f"The community of the buildings contains {n_buildings_str}.")
    text.add_sentence(
        "Each building has its own meter measuring electrical consumption and another meter measuring heating consumption."
    )

    # ELECTRICITY
    for vector in scenario.e_infrastructures:
        vector_equipment = scenario.get_infrastructure_equipment(vector)
        connected_buildings = [f'"{b}"' for b in scenario.get_infrastructure_buildings(vector)]
        equipment_types = [
            equipment.text_description_type
            for equipment in vector_equipment
            if equipment.text_description_type is not None
        ]
        equipment_types_with_buildings = [
            equipment.text_description_type_with_building
            for equipment in vector_equipment
            if equipment.text_description_type_with_building is not None
        ]
        equipment_descriptions = [
            equipment.text_description_parameters
            for equipment in vector_equipment
            if equipment.text_description_parameters is not None
        ]
        if len(connected_buildings) > 1:
            if len(equipment_types_with_buildings) > 1:
                text.add_sentence(
                    f"Buildings {enumeration(connected_buildings)} share the same electrical connection (same wiring) "
                    f"to several assets: {enumeration(equipment_types_with_buildings)}."
                )
            elif len(equipment_types_with_buildings) == 1:
                text.add_sentence(
                    f"Buildings {enumeration(connected_buildings)} have an electrical connection to "
                    f"{equipment_types_with_buildings[0]}."
                )
            else:
                raise ValueError(f"There is no equipment in vector {vector} in scenario {scenario_dir_path}.")
        elif len(connected_buildings) == 1:
            if len(equipment_types) > 1:
                text.add_sentence(
                    f"Building {connected_buildings[0]} shares the same electrical connection (same wiring) "
                    f"to several assets: {enumeration(equipment_types)}."
                )
            elif len(equipment_types) == 1:
                text.add_sentence(
                    f"Building {connected_buildings[0]} has an electrical connection to {equipment_types[0]}."
                )
            else:
                raise ValueError(
                    f"There is no equipment in building {connected_buildings[0]} in vector {vector} "
                    f"in scenario {scenario_dir_path}."
                )
        # Note: vectors without connected buildings mean that there is no equipment connected to these vectors.
        text.add_sentences(equipment_descriptions)

    # HEATING
    for vector in scenario.h_infrastructures:
        vector_equipment = scenario.get_infrastructure_equipment(vector)
        connected_buildings = [f'"{b}"' for b in scenario.get_infrastructure_buildings(vector)]
        equipment_types = [
            equipment.text_description_type
            for equipment in vector_equipment
            if equipment.text_description_type is not None
        ]
        equipment_types_with_buildings = [
            equipment.text_description_type_with_building
            for equipment in vector_equipment
            if equipment.text_description_type_with_building is not None
        ]
        equipment_descriptions = [
            equipment.text_description_parameters
            for equipment in vector_equipment
            if equipment.text_description_parameters is not None and not isinstance(equipment, HeatPump)
        ]
        if len(connected_buildings) > 1:
            if len(equipment_types_with_buildings) > 1:
                text.add_sentence(
                    f"Buildings {enumeration(connected_buildings)} share the same connection (same hot water system) "
                    f"to several assets: {enumeration(equipment_types_with_buildings)}."
                )
            elif len(equipment_types_with_buildings) == 1:
                text.add_sentence(
                    f"Buildings {enumeration(connected_buildings)} have a connection "
                    f"to {equipment_types_with_buildings[0]}."
                )
            else:
                raise ValueError(f"There is no equipment in vector {vector} in scenario {scenario_dir_path}.")
        elif len(connected_buildings) == 1:
            if len(equipment_types) > 1:
                text.add_sentence(
                    f"Building {connected_buildings[0]} shares the same connection (same hot water system) "
                    f"to several assets: {enumeration(equipment_types)}."
                )
            elif len(equipment_types) == 1:
                text.add_sentence(f"Building {connected_buildings[0]} has a connection to {equipment_types[0]}.")
            else:
                raise ValueError(
                    f"There is no equipment in building {connected_buildings[0]} in vector {vector} "
                    f"in scenario {scenario_dir_path}."
                )
        # Note: vectors without connected buildings mean that there is no equipment connected to these vectors.
        text.add_sentences(equipment_descriptions)
    text_description_path.write_text(text.get_text())

from .entities.equipment import (
    PV,
    Boiler,
    ElectricalConsumption,
    ElectricalGrid,
    ElectricalStorage,
    HeatingConsumption,
    HeatingGrid,
    HeatPump,
)
from .entities.infrastructure import Infrastructure
from .entities.scenario import Scenario
from .enums.config_section import ConfigSections
from .utils.config import ConfigLoader
from .utils.names import NameGenerator
from .utils.random import RandomTool


def generate_scenario(config_loader: ConfigLoader):
    scenario_config = config_loader.get_section(ConfigSections.SCENARIO_GENERATOR)

    RandomTool.set_seed(scenario_config["seed"])

    scenario = Scenario()
    name_gen = NameGenerator()

    # Generate buildings
    n_buildings = RandomTool.select_positive_int(scenario_config["max_n_buildings"])
    default_e_infra = Infrastructure(name_gen.get_infrastructure_name(), "e")
    default_h_infra = Infrastructure(name_gen.get_infrastructure_name(), "h")
    shared_e_infra = [default_e_infra]
    for i in range(n_buildings):
        building_id = name_gen.get_building_name()

        # Determine electrical infrastructure
        if RandomTool.is_event_triggered(scenario_config["custom_electricity_infra_prob"]):
            e_infra = Infrastructure(name_gen.get_infrastructure_name(), "e")
        else:
            if RandomTool.is_event_triggered(scenario_config["create_new_shared_electricity_infra_prob"]):
                e_infra = Infrastructure(name_gen.get_infrastructure_name(), "e")
                shared_e_infra.append(e_infra)
            else:
                e_infra = RandomTool.select_element(shared_e_infra)
        scenario.add(e_infra, exist_ok=True)

        # Determine heating infrastructure
        if RandomTool.is_event_triggered(scenario_config["custom_heating_infra_prob"]):
            h_infra = Infrastructure(name_gen.get_infrastructure_name(), "h")
        else:
            h_infra = default_h_infra
        scenario.add(h_infra, exist_ok=True)

        # Add consumption profiles
        scenario.add(
            ElectricalConsumption.create_random(
                name=name_gen.get_equipment_name(),
                infrastructures=[e_infra],
                config_loader=config_loader,
                building=building_id,
            )
        )
        scenario.add(
            HeatingConsumption.create_random(
                name=name_gen.get_equipment_name(),
                infrastructures=[h_infra],
                config_loader=config_loader,
                building=building_id,
            )
        )

        # Add Electrical Storage
        if RandomTool.is_event_triggered(scenario_config["storage_prob"]):
            scenario.add(
                ElectricalStorage.create_random(
                    name=name_gen.get_equipment_name(),
                    infrastructures=[e_infra],
                    config_loader=config_loader,
                    building=building_id,
                )
            )

        # Add PV
        if RandomTool.is_event_triggered(scenario_config["pv_prob"]):
            scenario.add(
                PV.create_random(
                    name=name_gen.get_equipment_name(),
                    infrastructures=[e_infra],
                    config_loader=config_loader,
                    building=building_id,
                )
            )

        # Add boiler
        if RandomTool.is_event_triggered(scenario_config["boiler_prob"]):
            scenario.add(
                Boiler.create_random(
                    name=name_gen.get_equipment_name(),
                    infrastructures=[h_infra],
                    config_loader=config_loader,
                    building=building_id,
                )
            )

        # Add heat pump
        if RandomTool.is_event_triggered(scenario_config["heat_pump_prob"]):
            scenario.add(
                HeatPump.create_random(
                    name=name_gen.get_equipment_name(),
                    infrastructures=[e_infra, h_infra],
                    config_loader=config_loader,
                    building=building_id,
                )
            )

    # Make sure energy infrastructures are realistic
    for infrastructure in scenario.infrastructures:
        if len(scenario.get_infrastructure_equipment(infrastructure.name)) > 0:
            # Add electrical grid connection
            if infrastructure.infrastructure_type == "e":
                scenario.add(
                    ElectricalGrid.create_random(
                        name=name_gen.get_equipment_name(),
                        infrastructures=[infrastructure],
                        config_loader=config_loader,
                        gen_at_least_kw=infrastructure.required_control_generation_kw,
                        cons_at_least_kw=infrastructure.required_control_consumption_kw,
                    )
                )
            # Add heating grid connection
            if infrastructure.infrastructure_type == "h":
                if infrastructure.required_control_generation_kw > 0 or RandomTool.is_event_triggered(
                    scenario_config["heat_grid_prob"]
                ):
                    scenario.add(
                        HeatingGrid.create_random(
                            name=name_gen.get_equipment_name(),
                            infrastructures=[infrastructure],
                            config_loader=config_loader,
                            gen_at_least_kw=infrastructure.required_control_generation_kw,
                        )
                    )
    return scenario

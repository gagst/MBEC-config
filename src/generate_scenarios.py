import argparse
from pathlib import Path

from configurator.utils.config import ConfigLoader
from configurator.description_generators.brick import generate_brick_description
from configurator.description_generators.s4bldg import generate_s4bldg_description
from configurator.description_generators.text import generate_text_description
from configurator.graph_configurators.reference import GraphConfigurator
from configurator.scenario_generator import generate_scenario
from configurator.utils.experiments import scenario_output_path


def main():
    parser = argparse.ArgumentParser(description="Generate multiple scenarios based on a configuration file.")
    parser.add_argument("-c", "--config", type=str, help="Path to the configuration file.", required=True)
    parser.add_argument("-n", "--n_scenarios", type=int, help="Number of scenarios to generate.", required=True)
    parser.add_argument("-o", "--output", type=str, help="Path to the output directory.", required=False)
    parser.add_argument(
        "-e",
        "--experiment",
        type=str,
        help=(
            "Experiment name used to derive standard paths: "
            "output/<experiment>_scenarios, logs/<experiment>, and evaluation/<experiment>."
        ),
        required=False,
    )

    args = parser.parse_args()

    # Ensure the configuration file exists
    config_path = Path(args.config)
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Create a ConfigLoader instance
    config_loader = ConfigLoader(str(config_path))

    output_dir = scenario_output_path(config_path=config_path, output=args.output, experiment=args.experiment)
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(args.n_scenarios):
        scenario_name = f"scenario_{i}"
        scenario_dir = output_dir / scenario_name
        scenario_dir.mkdir(parents=True, exist_ok=True)

        scenario = generate_scenario(config_loader)
        scenario.to_yaml(scenario_dir)

        generate_text_description(scenario_dir)
        generate_s4bldg_description(scenario_dir, anonymize_ids=False)
        generate_s4bldg_description(scenario_dir, anonymize_ids=True)
        generate_brick_description(scenario_dir, anonymize_ids=False)
        generate_brick_description(scenario_dir, anonymize_ids=True)
        GraphConfigurator(scenario_dir_path=scenario_dir).configure_graph()


if __name__ == "__main__":
    main()

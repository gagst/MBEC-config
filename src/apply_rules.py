import argparse
import logging
from pathlib import Path

from configurator.utils.config import ConfigLoader
from configurator.graph_configurators import brick_rules, s4bldg_rules
from configurator.utils.experiments import log_path, scenario_input_paths
from configurator.utils.logging import setup_logging


def main():
    parser = argparse.ArgumentParser(
        description="Configure graph using SPARQL rules and corresponding semantic descriptions."
    )
    parser.add_argument("-c", "--config", type=str, help="Path to the configuration file.", required=True)
    parser.add_argument("-i", "--input", type=str, help="Path to the input directory with scenarios.", required=False)
    parser.add_argument(
        "-l", "--log", type=str, help="Path to where the file with log is going to be saved.", required=False
    )
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

    scenarios_dirs = scenario_input_paths(input_path=args.input, experiment=args.experiment)

    for scenarios_dir in scenarios_dirs:
        log_file = log_path(
            experiment=args.experiment,
            command_name="rules",
            input_path=str(scenarios_dir),
            log=args.log,
        )
        setup_logging(level_file=logging.DEBUG, level_stdout=logging.INFO, log_file=log_file)

        for scenario_dir_path in scenarios_dir.iterdir():
            if scenario_dir_path.is_dir():
                s4bldg_rules.GraphConfigurator(
                    scenario_dir_path=scenario_dir_path, config_loader=config_loader
                ).configure_graph()
                brick_rules.GraphConfigurator(
                    scenario_dir_path=scenario_dir_path, config_loader=config_loader
                ).configure_graph()


if __name__ == "__main__":
    main()

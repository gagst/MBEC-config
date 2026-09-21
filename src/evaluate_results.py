import argparse
import logging
from pathlib import Path

from configurator.utils.config import ConfigLoader
from configurator.enums.config_section import ConfigSections
from configurator.utils.experiments import log_path, evaluation_path, scenario_input_paths
from configurator.graph_evaluator import GraphEvaluator
from configurator.utils.logging import setup_logging


def main():
    parser = argparse.ArgumentParser(description="Evaluate the results of different graph generation methods.")
    parser.add_argument("-c", "--config", type=str, help="Path to the configuration file.", required=True)
    parser.add_argument("-i", "--input", type=str, help="Path to the input directory with scenarios.", required=False)
    parser.add_argument("-o", "--output", type=str, help="Path to where the file with results is going to be saved.", required=False)
    parser.add_argument("-l", "--log", type=str, help="Path to where the file with log is going to be saved.", required=False)
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
    config_loader.get_section(ConfigSections.EVALUATOR)

    scenarios_dirs = scenario_input_paths(input_path=args.input, experiment=args.experiment)

    if args.output is not None and len(scenarios_dirs) > 1:
        raise ValueError("--output can only be used with a single --input scenario set")

    for scenarios_dir in scenarios_dirs:
        log_file = log_path(
            experiment=args.experiment,
            command_name="evaluation",
            input_path=str(scenarios_dir),
            log=args.log,
        )
        setup_logging(level_file=logging.DEBUG, level_stdout=logging.INFO, log_file=log_file)

        output_path = evaluation_path(scenarios_dir=scenarios_dir, output=args.output, experiment=args.experiment)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        GraphEvaluator(scenario_dirs=scenarios_dir, output_path=output_path).evaluate()


if __name__ == "__main__":
    main()

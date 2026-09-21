import argparse
import logging
from pathlib import Path

from tqdm import tqdm

from configurator.utils.config import ConfigLoader
from configurator.enums.config_section import ConfigSections
from configurator.graph_configurators.llm import LLMGraphConfigurator
from configurator.utils.experiments import scenario_input_paths, log_path
from configurator.utils.logging import setup_logging


def main():
    parser = argparse.ArgumentParser(description="Configure graph using LLMs and text descriptions.")
    parser.add_argument("-c", "--config", type=str, help="Path to the configuration file.", required=True)
    parser.add_argument("-i", "--input", type=str, help="Path to the input directory with scenarios.", required=False)
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
    config_section = config_loader.get_section(ConfigSections.LLM_GRAPH_CONFIGURATOR)

    scenarios_dirs = scenario_input_paths(input_path=args.input, experiment=args.experiment)

    scenario_dirs_list = [d for scenarios_dir in scenarios_dirs for d in scenarios_dir.iterdir() if d.is_dir()]
    configurators_list = config_section["configurators"]
    total = len(scenario_dirs_list) * len(configurators_list)
    with tqdm(total=total, desc="Asking all", unit="configurator") as pbar:
        for scenarios_dir in scenarios_dirs:
            log_file = log_path(
                experiment=args.experiment,
                command_name="llm",
                input_path=str(scenarios_dir),
                config_path=config_path,
                log=args.log,
            )
            setup_logging(level_file=logging.DEBUG, level_stdout=logging.INFO, log_file=log_file)

            for scenario_dir_path in scenarios_dir.iterdir():
                if scenario_dir_path.is_dir():
                    for config in configurators_list:
                        LLMGraphConfigurator.configure_graph(scenario_dir_path=scenario_dir_path, config=config)
                        pbar.update(1)


if __name__ == "__main__":
    main()

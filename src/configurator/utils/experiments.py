from pathlib import Path

from configurator.constants.paths import EVALUATION_RESULTS_DIR_PATH, LOGS_DIR_PATH, OUTPUT_DIR_PATH


def experiment_scenarios_root(experiment: str) -> Path:
    return OUTPUT_DIR_PATH / f"{experiment}_scenarios"


def scenario_output_path(config_path: Path, output: str | None, experiment: str | None) -> Path:
    if output is not None:
        return Path(output)
    if experiment is not None:
        return experiment_scenarios_root(experiment) / config_path.stem
    raise ValueError("one of --output or --experiment is required")


def scenario_input_paths(input_path: str | None, experiment: str | None) -> list[Path]:
    if input_path is not None:
        scenarios_dir = Path(input_path)
        if not scenarios_dir.exists():
            raise FileNotFoundError(f"Scenarios directory not found: {scenarios_dir}")
        return [scenarios_dir]

    if experiment is None:
        raise ValueError("one of --input or --experiment is required")

    root = experiment_scenarios_root(experiment)
    if not root.exists():
        raise FileNotFoundError(f"Experiment scenarios directory not found: {root}")

    paths = sorted(item for item in root.iterdir() if item.is_dir())
    if len(paths) == 0:
        raise FileNotFoundError(f"No scenario set directories found in: {root}")
    return paths


def log_path(
    log: str | None,
    experiment: str | None,
    command_name: str,
    input_path: str | None = None,
    config_path: Path | None = None,
) -> Path | None:
    if log is not None:
        return Path(log)

    if experiment is None:
        return None

    log_dir = LOGS_DIR_PATH / experiment / command_name
    if input_path is not None and config_path is not None:
        return log_dir / f"{config_path.stem}_{Path(input_path).name}.log"
    if input_path is not None:
        return log_dir / f"{Path(input_path).name}.log"
    if config_path is not None:
        return log_dir / f"{config_path.stem}.log"
    raise Exception("input_path or config_path is required")


def evaluation_path(scenarios_dir: Path, output: str | None, experiment: str | None) -> Path:
    if output is not None:
        return Path(output)
    if experiment is not None:
        return EVALUATION_RESULTS_DIR_PATH / experiment / f"{scenarios_dir.name}.csv"
    raise ValueError("one of --output or --experiment is required")

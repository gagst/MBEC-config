from pathlib import Path

PROJECT_ROOT_PATH = Path(__file__).resolve().parents[3]

BRICK_TTL_PATH = PROJECT_ROOT_PATH / "ontologies/brick_lite.owl.ttl"
S4BLDG_TTL_PATH = PROJECT_ROOT_PATH / "ontologies/s4bldg_lite.owl.ttl"

OUTPUT_DIR_PATH = PROJECT_ROOT_PATH / "output"
LOGS_DIR_PATH = PROJECT_ROOT_PATH / "logs"
EVALUATION_RESULTS_DIR_PATH = PROJECT_ROOT_PATH / "evaluation"

S4BLDG_SCHEMA_PATH = PROJECT_ROOT_PATH / "linkml_schemas/s4bldg_lite.yaml"
BRICK_SCHEMA_PATH = PROJECT_ROOT_PATH / "linkml_schemas/brick_lite.yaml"
TEMPLATES_DIR_PATH = PROJECT_ROOT_PATH / "src/configurator/templates"

import yaml

from ..enums.config_section import ConfigSections


class ConfigLoader:
    def __init__(self, config_file_path):
        self._config_file_path = config_file_path
        self._config = self._load_config()

    def _load_config(self):
        try:
            with open(self._config_file_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self._config_file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration file: {e}")

    def get_section(self, section_name: ConfigSections | str):
        return self._config.get(section_name, {})

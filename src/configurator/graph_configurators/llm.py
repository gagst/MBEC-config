import abc
import json
import logging
import re
from pathlib import Path
from textwrap import fill

from jinja2 import Environment, FileSystemLoader
from ollama import chat
from pydantic import TypeAdapter
from pydantic_core import from_json

from ..constants.file_names import FileNames
from ..constants.paths import TEMPLATES_DIR_PATH
from ..entities.kees_lite import (
    Component,
    EnergyVector,
    FixedConsumptionComponent,
    FixedGenerationComponent,
    FlexibleConsumptionComponent,
    FlexibleGenerationComponent,
    Graph,
    InterconnectorComponent,
    StorageComponent,
    TimeFlexibleConsumptionComponent,
)
from ..entities.scenario import Scenario
from ..enums.component_name import ComponentTypeString
from ..utils.graph import GraphUtils

logger = logging.getLogger(__name__)


IGNORED_COMPONENT_CLASSES = [ComponentTypeString.TIME_FLEXIBLE_CONSUMPTION]
IGNORED_SLOTS = ["isExternal", "originalName"]


class LLMGraphConfigurator(abc.ABC):
    _component_classes = {
        ComponentTypeString.FIXED_GENERATION: FixedGenerationComponent,
        ComponentTypeString.FIXED_CONSUMPTION: FixedConsumptionComponent,
        ComponentTypeString.FLEXIBLE_GENERATION: FlexibleGenerationComponent,
        ComponentTypeString.FLEXIBLE_CONSUMPTION: FlexibleConsumptionComponent,
        ComponentTypeString.TIME_FLEXIBLE_CONSUMPTION: TimeFlexibleConsumptionComponent,
        ComponentTypeString.STORAGE: StorageComponent,
        ComponentTypeString.INTERCONNECTOR: InterconnectorComponent,
    }

    _environment = Environment(loader=FileSystemLoader(TEMPLATES_DIR_PATH))

    def _log(self, level: int, message: str):
        logger.log(
            level,
            f"[Scenario: {self._scenario_dir_path.name} "
            f"| Input: {self._input_source} "
            f"| Model: {self._model} "
            f"| Think: {self._model_think} "
            f"| Examples: {self._prompt_with_examples}] "
            f"{message}",
        )

    @classmethod
    def configure_graph(cls, scenario_dir_path: Path, config: dict):
        if config["type"] == "ollama":
            graph_configurator = OllamaGraphConfigurator
        else:
            raise NotImplementedError(f"Configurator type not supported: {config['type']}")
        instance = graph_configurator(scenario_dir_path=scenario_dir_path, config=config)
        instance.create_graph()

    def __init__(self, scenario_dir_path: Path, config: dict):
        self._scenario_dir_path = scenario_dir_path
        self._config = config
        self._scenario = Scenario.from_yaml(scenario_dir_path)
        self._model = config["model"]
        self._model_think = config["think"]
        self._input_source = config["input_source"]
        self._prompt_with_examples = config["prompt_with_examples"]
        self._seed = config["seed"]
        self._temperature = config["temperature"]
        self._output_path = scenario_dir_path / FileNames.llm_graph(
            input_source=self._input_source,
            model_name=self._model,
            model_think=self._model_think,
            prompt_with_examples=self._prompt_with_examples,
        )
        if self.input_source_is_text:
            input_source_path = self._scenario_dir_path / FileNames.TEXT_DESCRIPTION
        else:
            input_source_path = self._scenario_dir_path / FileNames.semantic_description(self._input_source)
        self._input_content = input_source_path.read_text()

    @abc.abstractmethod
    def _get_response_content(self, prompt: str) -> str:
        raise NotImplementedError()

    @property
    def input_source_is_text(self) -> bool:
        return self._input_source == "text"

    @property
    def input_source_content(self) -> str:
        return self._input_content

    @property
    def prompt_with_examples(self) -> bool:
        return self._prompt_with_examples

    def create_graph(self):
        # Vectors
        self._log(logging.INFO, "Start configuring vectors")
        prompt = self._environment.get_template("prompt.j2").render(for_vector=True, configurator=self)
        reply = self._get_response_content(prompt)
        vector_names = self._parse_vector_names(reply)
        vectors = {name: EnergyVector(name=name) for name in vector_names}

        # Components
        components = dict()
        for component_type, component_class in LLMGraphConfigurator._component_classes.items():
            if component_type not in IGNORED_COMPONENT_CLASSES:
                self._log(logging.INFO, f"Start configuring {component_type}")
                component_slots = self._get_component_slots(component_class)
                prompt = self._environment.get_template("prompt.j2").render(
                    for_component=True,
                    configurator=self,
                    component_type=str(component_type),
                    component_slots=component_slots,
                    vector_names=[f'"{name}"' for name in vectors.keys()],
                    component_type_enum=ComponentTypeString,
                )
                reply = self._get_response_content(prompt)
                components[component_type] = self._parse_components(reply, component_class=component_class)

        graph = Graph(
            energyVectors=list(vectors.values()),
            fixedGenerations=components.get(ComponentTypeString.FIXED_GENERATION, []),
            fixedConsumptions=components.get(ComponentTypeString.FIXED_CONSUMPTION, []),
            flexibleGenerations=components.get(ComponentTypeString.FLEXIBLE_GENERATION, []),
            flexibleConsumptions=components.get(ComponentTypeString.FLEXIBLE_CONSUMPTION, []),
            timeFlexibleConsumptions=components.get(ComponentTypeString.TIME_FLEXIBLE_CONSUMPTION, []),
            interconnectors=components.get(ComponentTypeString.INTERCONNECTOR, []),
            storages=components.get(ComponentTypeString.STORAGE, []),
        )
        GraphUtils.save_graph(graph=graph, output_path=self._output_path)

    def _get_component_slots(self, component_class):
        result = {}
        for f_name, f_info in component_class.model_fields.items():
            if f_name not in IGNORED_SLOTS:
                if f_info.description is not None:
                    result[f_name] = f_info.description
                else:
                    raise NotImplementedError(f"Field {f_name} in {component_class} does not have a description.")
        return result

    def _clean_json_array(self, text: str):
        if "Answer:" in text:
            text = text.split("Answer:")[1]
        text = text.replace("\n", "").replace("\r", "")
        text = re.sub(r"^```json\s*|```$", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)
        square_brackets_match = re.search(r"\[.*\]", text, re.DOTALL)
        if square_brackets_match:
            return square_brackets_match.group(0), True

        curly_braces_match = re.search(r"\{.*\}", text, re.DOTALL)
        if curly_braces_match:
            return curly_braces_match.group(0), False

        raise ValueError("No valid JSON content found in the input text.")

    def _parse_vector_names(self, reply: str) -> list[str]:
        result = []
        try:
            cleaned_json, _ = self._clean_json_array(reply)
            parsed_json = json.loads(cleaned_json)
            if isinstance(parsed_json, list):
                result = [str(element) for element in parsed_json]
            elif isinstance(parsed_json, str):
                result = [parsed_json]
            else:
                raise ValueError(f"Parsed content is neither a list nor a string: {reply}")
        except (json.JSONDecodeError, ValueError) as e:
            self._log(logging.ERROR, f"Error parsing vectors from reply: {e}")
        self._log(logging.DEBUG, f"Parsed vectors: {result}")
        return result

    def _parse_components(self, reply: str, component_class: type[Component]):
        result = []
        try:
            clean_json, is_array = self._clean_json_array(reply)
            if is_array:
                ta = TypeAdapter(list[component_class])
                components = ta.validate_json(clean_json, experimental_allow_partial=True)
                result = components
            else:
                component = component_class.model_validate(from_json(clean_json, allow_partial=True))
                result = [component]
        except (json.JSONDecodeError, ValueError) as e:
            self._log(logging.ERROR, f"Error parsing components from reply: {e}")
        self._log(logging.DEBUG, f"Parsed components: {result}")
        return result


class OllamaGraphConfigurator(LLMGraphConfigurator):
    def _get_response_content(self, prompt: str):
        response = chat(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            think=self._model_think,
            format="json",
            options={
                "seed": self._seed,
                "temperature": self._temperature,
            },
        )
        content = response.message.content
        self._log(
            logging.DEBUG,
            "\n".join(
                [
                    f"prompt: {fill(prompt, width=80)}",
                    f"content: {content}",
                    f"thinking: {response.message.thinking}",
                    f"done: {response.done}",
                    f"done_reason: {response.done_reason}",
                    f"total_duration: {response.total_duration}",
                    f"load_duration: {response.load_duration}",
                    f"prompt_eval_duration: {response.prompt_eval_duration}",
                    f"eval_duration: {response.eval_duration}",
                    f"prompt_eval_count: {response.prompt_eval_count}",
                    f"eval_count: {response.eval_count}",
                ]
            ),
        )
        return content

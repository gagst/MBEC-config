from abc import ABC

from ..enums.ontology import Ontology
from ..utils.names import make_path_friendly, graph_file_name


class FileNames(ABC):
    @staticmethod
    def semantic_description(ontology: str) -> str:
        return f"{ontology}_description.ttl"

    @staticmethod
    def llm_graph(input_source: str, model_name: str, model_think: bool, prompt_with_examples: bool) -> str:
        model = make_path_friendly(model_name)
        think = "_think" if model_think else ""
        examples = "_with_examples" if prompt_with_examples else ""
        method = f"{input_source}_{model}{think}{examples}"
        return graph_file_name(method=method)

    @staticmethod
    def rule_graph(ontology: Ontology) -> str:
        method = f"{ontology}_rules"
        return graph_file_name(method=method)

    BRICK_DESCRIPTION = semantic_description(Ontology.BRICK.full_name(anon=False))
    BRICK_DESCRIPTION_ANON = semantic_description(Ontology.BRICK.full_name(anon=True))
    S4BLDG_DESCRIPTION = semantic_description(Ontology.S4BLDG.full_name(anon=False))
    S4BLDG_DESCRIPTION_ANON = semantic_description(Ontology.S4BLDG.full_name(anon=True))
    TEXT_DESCRIPTION = "text_description.txt"
    SCENARIO = "scenario.yaml"

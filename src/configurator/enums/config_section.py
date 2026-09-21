from enum import StrEnum


class ConfigSections(StrEnum):
    SCENARIO_GENERATOR = "ScenarioGenerator"
    BRICK_RULES_GRAPH_CONFIGURATOR = "BrickRuleGraphConfigurator"
    S4BLDG_RULES_GRAPH_CONFIGURATOR = "S4BLDGRuleGraphConfigurator"
    LLM_GRAPH_CONFIGURATOR = "LLMGraphConfigurator"
    EVALUATOR = "Evaluator"

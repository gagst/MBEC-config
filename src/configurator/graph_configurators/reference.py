from pathlib import Path

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
from ..utils.graph import GraphUtils


class GraphConfigurator:
    def __init__(self, scenario_dir_path: Path):
        self._scenario_dir_path = scenario_dir_path
        self._result_path = scenario_dir_path / "reference_graph.yaml"

        self._scenario = Scenario.from_yaml(scenario_dir_path)

        self._vectors = {i.name: EnergyVector(name=i.name) for i in self._scenario.infrastructures}

    def configure_graph(self):
        result = Graph()

        for equipment in self._scenario.equipment:
            reference = equipment.reference_component_representation[0]
            if isinstance(reference, Component):
                reference = [reference]
            for component in reference:
                if isinstance(component, FixedGenerationComponent):
                    result.fixedGenerations.append(component)
                elif isinstance(component, FixedConsumptionComponent):
                    result.fixedConsumptions.append(component)
                elif isinstance(component, FlexibleGenerationComponent):
                    result.flexibleGenerations.append(component)
                elif isinstance(component, FlexibleConsumptionComponent):
                    result.flexibleConsumptions.append(component)
                elif isinstance(component, TimeFlexibleConsumptionComponent):
                    result.timeFlexibleConsumptions.append(component)
                elif isinstance(component, InterconnectorComponent):
                    result.interconnectors.append(component)
                elif isinstance(component, StorageComponent):
                    result.storages.append(component)
        result.energyVectors.extend(list(self._vectors.values()))

        GraphUtils.save_graph(graph=result, output_path=self._result_path)

import logging
from collections import defaultdict
from dataclasses import fields
from pathlib import Path
from typing import Optional

from linkml_runtime.dumpers import YAMLDumper
from linkml_runtime.loaders import YAMLLoader

from ..entities import kees_lite
from ..entities.equipment.equipment import META_SIMILAR, Equipment
from ..entities.infrastructure import Infrastructure
from ..entities.kees_lite import Component, EnergyVector, Graph
from .names import are_strings_similar, get_name_candidates, get_string_similarity
from .random import RandomTool

logger = logging.getLogger(__name__)


class GraphUtils:
    def _log(self, level: int, message: str):
        logger.log(level, f"[Graph: {self._graph_path}] {message}")

    def __init__(self, graph_path: Path, graph: Optional[Graph] = None):
        self._graph_path = graph_path
        if graph is None:
            with open(graph_path, "r", encoding="utf-8") as f:
                graph = YAMLLoader().load(source=f, target_class=Graph)
        self._graph: Graph = graph
        self._components = [
            *graph.fixedGenerations,
            *graph.fixedConsumptions,
            *graph.flexibleGenerations,
            *graph.flexibleConsumptions,
            *graph.timeFlexibleConsumptions,
            *graph.interconnectors,
            *graph.storages,
        ]
        self._correct_names()

    @classmethod
    def save_graph(cls, graph: Graph, output_path: Path):
        graph_utils = cls(graph=graph, graph_path=output_path)
        YAMLDumper().dump(element=graph_utils._graph, to_file=str(output_path))

    @property
    def components(self) -> list[Component]:
        return self._components

    @property
    def vectors(self) -> list[EnergyVector]:
        return self._graph.energyVectors

    @property
    def vector_names(self) -> list[str]:
        return [vector.name for vector in self.vectors]

    @property
    def graph(self) -> Graph:
        return self._graph

    def get_vector(self, name: str) -> kees_lite.EnergyVector:
        for vector in self._graph.energyVectors:
            if vector.name == name:
                return vector
        raise LookupError(f"EnergyVector with name '{name}' not found")

    def get_component(self, name: str) -> Component:
        for component in self._components:
            if component.name == name:
                return component
        raise LookupError(f"Component with name '{name}' not found")

    def get_similar_vectors(self, infrastructure: Infrastructure, buildings: list[str]) -> dict[str, int]:
        """
        Returns dictionary where keys are energy vector names and values are similarity metric.
        """
        possible_vector_names = get_name_candidates(infrastructure, buildings=buildings)

        similar_vectors = defaultdict(int)
        for vector in self.vectors:
            for candidate in possible_vector_names:
                vector_search_name = vector.originalName if vector.originalName is not None else vector.name
                if are_strings_similar(vector_search_name, candidate):
                    similar_vectors[vector.name] += get_string_similarity(vector_search_name, candidate)
        self._log(logging.DEBUG, f"{infrastructure} similar vectors: {dict(similar_vectors)}")
        return similar_vectors

    def get_similar_components(self, equipment: Equipment) -> dict[str, int]:
        """
        Returns dictionary where keys are component names and values are similarity metric.
        """
        possible_component_names = get_name_candidates(equipment)

        similar_components = defaultdict(int)
        for component in self.components:
            # Find components with similar names
            name_similarity = 0
            component_search_name = component.originalName if component.originalName is not None else component.name
            for candidate in possible_component_names:
                if are_strings_similar(component_search_name, candidate):
                    name_similarity += 1
            name_similarity = 1 if name_similarity > 0 else 0  # range: 0 or 1
            similar_components[component.name] += name_similarity

            # Find components with applicable class:
            class_similarity = 0
            if component.__class__.__name__ in equipment.reference_component_classes_flat:
                class_similarity = 1
            similar_components[component.name] += class_similarity  # range: 0 or 1

            # Find components with similar slot values
            field_similarity = 0
            n_similar_fields = 0  # number of equipment fields with "similar" metadata
            for equipment_field in fields(equipment):
                component_slot = equipment_field.metadata.get(META_SIMILAR, None)
                if component_slot is not None:
                    n_similar_fields += 1
                    equipment_value = getattr(equipment, equipment_field.name, None)
                    component_value = getattr(component, component_slot, None)
                    if equipment_value is not None and component_value == equipment_value:
                        field_similarity += 1
            field_similarity = field_similarity / n_similar_fields if n_similar_fields > 0 else 0  # range: 0 to 1
            similar_components[component.name] += field_similarity

            if similar_components[component.name] > 3:
                raise Exception(
                    "The similarity score cannot be greater than 3, check the uniqueness of component names."
                )
        self._log(logging.DEBUG, f"{equipment} similar components: {dict(similar_components)}")
        return similar_components

    def _correct_names(self):
        is_graph_changed = False
        unique_vector_names = set()
        for v in self._graph.energyVectors:
            if v.name is None:
                v.name = f"vector__{RandomTool.get_random_string(2)}"
                is_graph_changed = True
            elif v.name in unique_vector_names:
                v.originalName = v.name
                v.name = f"{v.name}__{RandomTool.get_random_string(2)}"
                is_graph_changed = True
            unique_vector_names.add(v.name)
        unique_component_names = set()
        for c in self.components:
            if c.name is None:
                c.name = f"component__{RandomTool.get_random_string(2)}"
                is_graph_changed = True
            elif c.name in unique_component_names:
                c.originalName = c.name
                c.name = f"{c.name}__{RandomTool.get_random_string(2)}"
                is_graph_changed = True
            unique_component_names.add(c.name)
        if is_graph_changed:
            YAMLDumper().dump(element=self._graph, to_file=str(self._graph_path))

import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional

import pandas as pd

from .constants.thresholds import STRING_SIMILARITY_THRESHOLD
from .entities.equipment.equipment import Equipment
from .entities.kees_lite import Component
from .entities.scenario import Scenario
from .enums.evaluation import (
    ComponentEval,
    EquipmentEval,
    EvaluationNonVectorSlot,
    EvaluationVectorSlot,
    SlotComponentEval,
    SlotEquipmentEval,
)
from .utils.graph import GraphUtils
from .utils.random import RandomTool

logger = logging.getLogger(__name__)

ALL_EVALUATION_SLOTS = {*[m.value for m in EvaluationNonVectorSlot], *[m.value for m in EvaluationVectorSlot]}
EvaluationResult = SlotComponentEval | SlotEquipmentEval | EquipmentEval | ComponentEval | str


class GraphEvaluator:
    def __init__(self, scenario_dirs: Path, output_path: Path):
        self._scenario_dirs = scenario_dirs
        self._output_path = output_path
        self._results = []

    def evaluate(self):
        for item in self._scenario_dirs.iterdir():
            if item.is_dir():
                self._evaluate_scenario(item)
        pd.concat(self._results).to_csv(self._output_path)

    def _evaluate_scenario(self, scenario_dir_path: Path):
        scenario = Scenario.from_yaml(scenario_dir_path)
        for item in scenario_dir_path.iterdir():
            match = re.match(r"(.*)_graph\.yaml$", item.name)
            if item.is_file() and match:
                configurator_name = match.group(1)
                results = ConfiguratorEvaluator(graph_path=item, scenario=scenario).evaluate()
                results = pd.DataFrame(results)
                results["configurator"] = configurator_name
                results["scenario"] = scenario_dir_path.name
                self._results.append(results)


class ConfiguratorEvaluator:
    def _log(self, level: int, message: str, infrastructure=None, equipment=None):
        if infrastructure is not None:
            prefix = f"[Graph: {self._graph_path} | Infrastructure: {infrastructure}]"
        elif equipment is not None:
            prefix = f"[Graph: {self._graph_path} | Equipment: {equipment}]"
        else:
            prefix = f"[Graph: {self._graph_path}]"
        logger.log(level, f"{prefix} {message}")

    def __init__(self, graph_path: Path, scenario: Scenario):
        self._graph_path = graph_path
        self._graph_utils = GraphUtils(graph_path=graph_path)
        self._scenario = scenario
        self._results = EvaluationResults()

        # {infrastructure.name: {vector.name: similarity_int}}
        self._infrastructures_to_similar_vectors = {
            i.name: self._graph_utils.get_similar_vectors(
                infrastructure=i, buildings=self._scenario.get_infrastructure_buildings(i)
            )
            for i in self._scenario.infrastructures
        }

    def evaluate(self):
        # Evaluate all equipment
        mapping_c_to_e: dict[str, Equipment] = dict()  # {component.name: equipment}

        # Start with the equipment with the highly similar components found
        equipment_to_similar_components: list[
            tuple[Equipment, int, dict[str, int]]
        ] = []  # [(equipment, max_similarity, {component.name: similarity_int}), (), ...]
        for equipment in self._scenario.equipment:
            similar_components = self._graph_utils.get_similar_components(equipment)  # {component.name: similarity_int}
            if len(similar_components) != 0:
                max_similarity = max(similar_components.values())
            else:
                max_similarity = 0
            equipment_to_similar_components.append((equipment, max_similarity, similar_components))

        # Sort in descending order of max similarity
        equipment_to_similar_components = sorted(equipment_to_similar_components, key=lambda x: x[1], reverse=True)

        for equipment, _, similar_components in equipment_to_similar_components:
            similar_components = {
                name: similarity
                for name, similarity in similar_components.items()
                if similarity > 0 and name not in mapping_c_to_e
            }  # {component.name: similarity_int}

            # Calculate max similarity again, because after filtering, the maximum values can change
            if len(similar_components) != 0:
                max_similarity = max(similar_components.values())
                components = [
                    self._graph_utils.get_component(c_name)
                    for c_name, similarity in similar_components.items()
                    if similarity == max_similarity
                ]
                self._log(
                    level=logging.DEBUG,
                    equipment=equipment,
                    message=f"components' max similarity={max_similarity}: {[c.name for c in components]}",
                )
                evaluated_components = self._evaluate_equipment(equipment=equipment, components=components)
                if len(evaluated_components) != 0:
                    self._log(
                        level=logging.DEBUG, equipment=equipment, message=f"mapped components: {evaluated_components}"
                    )
                    for component in evaluated_components:
                        mapping_c_to_e[component.name] = equipment
                else:
                    self._add_equipment_no_mapping_evaluation(equipment)
            else:
                self._add_equipment_no_mapping_evaluation(equipment)

        # Evaluate components for which no mapping was found
        for component in self._graph_utils.components:
            if component.name not in mapping_c_to_e:
                self._add_component_no_mapping_evaluation(component)

        # Find vector mapping
        mapping_v_to_i: dict[str, str] = dict()  # {vector.name: infrastructure.name}

        # Start with the infrastructures with highly similar vectors found
        infrastructures_to_similar_vectors: list[
            tuple[str, int, dict[str, int]]
        ] = []  # [(infrastructure_name, max_similarity, {vector.name: similarity_int}), (), ...]
        for infrastructure_name, similar_vectors in self._infrastructures_to_similar_vectors.items():
            if len(similar_vectors) != 0:
                max_similarity = max(similar_vectors.values())
            else:
                max_similarity = 0
            infrastructures_to_similar_vectors.append((infrastructure_name, max_similarity, similar_vectors))
        # Sort in descending order of max similarity
        infrastructures_to_similar_vectors = sorted(
            infrastructures_to_similar_vectors, key=lambda x: x[1], reverse=True
        )

        for infrastructure_name, _, similar_vectors in infrastructures_to_similar_vectors:
            similar_vectors = {
                name: similarity
                for name, similarity in similar_vectors.items()
                if similarity >= STRING_SIMILARITY_THRESHOLD and name not in mapping_v_to_i
            }  # Use similarity threshold because the similarity score was not discretized for vectors before

            # Calculate max similarity again, because after filtering, the maximum values can change
            if len(similar_vectors) != 0:
                max_similarity = max(similar_vectors.values())
                vectors = [
                    self._graph_utils.get_vector(v_name)
                    for v_name, similarity in similar_vectors.items()
                    if similarity == max_similarity
                ]
                if len(vectors) == 1:
                    evaluated_vector = vectors[0]
                    self._log(
                        level=logging.DEBUG,
                        infrastructure=infrastructure_name,
                        message=f"mapped vector: {evaluated_vector.name}",
                    )
                elif len(vectors) > 1:
                    evaluated_vector = RandomTool.select_element(vectors)
                    self._log(
                        level=logging.DEBUG,
                        infrastructure=infrastructure_name,
                        message=f"mapped vector (random): {evaluated_vector.name}",
                    )
                else:
                    self._log(level=logging.DEBUG, infrastructure=infrastructure_name, message="no vector mapped")
                    continue
                mapping_v_to_i[evaluated_vector.name] = infrastructure_name

        # Update vector slot evaluation
        self._update_vector_component_slot_evaluation(mapping_v_to_i)
        self._results.add_equipment_match_results()
        self._results.add_component_match_results()

        self._log(level=logging.INFO, message=f"Graph: {self._graph_path} is evaluated")
        return self._results.to_dict()

    def _evaluate_equipment(
        self,
        equipment: Equipment,
        components: list[Component],
    ) -> list[Component]:
        components = components.copy()
        results = []
        reference_is_matched = False
        for reference in equipment.reference_component_representation:
            if reference_is_matched:
                break
            if isinstance(reference, list):
                if len(reference) != len(components):
                    self._log(
                        level=logging.WARNING,
                        equipment=equipment,
                        message=f"There are {len(reference)} reference components expected, however {len(components)} "
                        f"components are given for evaluation.",
                    )
                # Have a match only if all reference components are represented by components
                matched_components = []
                available_components = components.copy()
                for ref_component in reference:
                    component_match = None

                    # Find match along available components
                    for component in available_components:
                        if ref_component.__class__.__name__ == component.__class__.__name__:
                            component_match = component
                            break  # component match is found, move to the next component in this reference component list

                    # If not match for the reference component can be found - move to the next reference implementation
                    if component_match is None:
                        matched_components = []
                        break

                    matched_components.append(component_match)
                    available_components.remove(component_match)

                if len(matched_components) > 0:
                    results.extend(matched_components)
                    reference_is_matched = True
            else:
                if len(components) != 1:
                    self._log(
                        level=logging.WARNING,
                        equipment=equipment,
                        message=f"There is only one reference component expected, "
                        f"however {len(components)} components are given for evaluation.",
                    )
                for component in components:
                    if reference.__class__.__name__ == component.__class__.__name__:
                        results.append(component)
                        reference_is_matched = True
                        break

        # No-mapping handled by self._add_equipment_no_mapping_evaluation.
        if len(results) == 0:
            return []

        # Evaluate the selected components
        evaluated_reference_slots = defaultdict(list)
        for component in results:
            for component_slot in component.model_fields_set:
                if component_slot in equipment.reference_component_slots:
                    eval_result = self._add_component_field_evaluation(
                        equipment=equipment,
                        component=component,
                        slot_name=component_slot,
                        reference_value=equipment.reference_component_slots[component_slot],
                    )
                    evaluated_reference_slots[component_slot].append(eval_result)
                else:
                    self._add_component_slot_no_mapping_evaluation(
                        component=component,
                        slot_name=component_slot,
                    )
        # Evaluate equipment slots
        for reference_slot in equipment.reference_component_slots:
            if reference_slot not in evaluated_reference_slots:
                self._add_equipment_slot_no_mapping_evaluation(
                    equipment=equipment,
                    slot_name=reference_slot,
                )
            else:
                self._add_equipment_slot_evaluation(
                    component_results=evaluated_reference_slots[reference_slot],
                    equipment=equipment,
                    slot_name=reference_slot,
                )
        return results

    def _add_component_field_evaluation(
        self,
        equipment: Equipment,
        component: Component,
        slot_name: str,
        reference_value: Optional,
    ):
        component_value = getattr(component, slot_name)
        if slot_name in EvaluationVectorSlot:
            if component_value is None:
                result = SlotComponentEval.VECTOR_VALUE_NO_MATCH
            else:
                # Reference value - infrastructure name
                if component_value in self._graph_utils.vector_names:
                    # Update vector similarities, only if this vector was properly created in the graph by configurator
                    self._infrastructures_to_similar_vectors[reference_value][component_value] += 1
                    self._log(
                        level=logging.DEBUG,
                        message=f"Energy vector {component_value} may represent infrastructure {reference_value}. "
                        f"Increase similarity score by 1",
                    )
                result = SlotComponentEval.VECTOR_SHOULD_BE_STR.format(reference_value)
        elif slot_name in EvaluationNonVectorSlot:
            if reference_value == component_value:
                result = SlotComponentEval.CORRECT_VALUE
            else:
                result = SlotComponentEval.INCORRECT_VALUE
        else:
            return None  # slot should be ignored
        self._results.add(
            result=result,
            equipment_name=equipment.name,
            equipment_class=equipment.class_name,
            component_name=component.name,
            component_class=component.__class__.__name__,
            slot=slot_name,
        )
        return result

    def _add_component_slot_no_mapping_evaluation(
        self,
        component: Component,
        slot_name: str,
    ):
        self._results.add(
            result=SlotComponentEval.NO_MATCH_SLOT,
            component_name=component.name,
            component_class=component.__class__.__name__,
            slot=slot_name,
        )

    def _add_equipment_slot_no_mapping_evaluation(
        self,
        equipment: Equipment,
        slot_name: str,
    ):
        self._results.add(
            result=SlotEquipmentEval.NO_MATCH_SLOT,
            equipment_name=equipment.name,
            equipment_class=equipment.class_name,
            slot=slot_name,
        )

    def _add_component_no_mapping_evaluation(self, component: Component):
        self._results.add(
            result=ComponentEval.NO_MATCH,
            component_name=component.name,
            component_class=component.__class__.__name__,
        )
        for slot in component.model_fields_set:
            self._results.add(
                result=SlotComponentEval.NO_MATCH_SLOT,
                slot=slot,
                component_class=component.__class__.__name__,
                component_name=component.name,
            )

    def _add_equipment_no_mapping_evaluation(self, equipment: Equipment):
        self._results.add(
            result=EquipmentEval.NO_MATCH,
            equipment_name=equipment.name,
            equipment_class=equipment.class_name,
        )
        for slot in equipment.reference_component_slots:
            self._results.add(
                result=SlotEquipmentEval.NO_MATCH_SLOT,
                slot=slot,
                equipment_name=equipment.name,
                equipment_class=equipment.class_name,
            )

    def _evaluate_component_vector_result(
        self,
        mapping_v_to_i: dict[str, str],
        result: str,
        component_name: str | None,
        slot_name: str | None,
    ) -> SlotComponentEval:
        reference_infrastructure_name = result.split(SlotComponentEval.VECTOR_SHOULD_BE_STR.format(""))[1]

        if component_name is None or slot_name is None:
            return SlotComponentEval.VECTOR_VALUE_NO_MATCH

        # Search for the mapping between infrastructure and vector
        reference_vector_name = None
        for vector_name, infrastructure_name in mapping_v_to_i.items():
            if infrastructure_name == reference_infrastructure_name:
                reference_vector_name = vector_name

        if reference_vector_name is not None:
            # If mapping is found
            component = self._graph_utils.get_component(component_name)
            slot_value = getattr(component, slot_name)
            if reference_vector_name == slot_value:
                output = SlotComponentEval.CORRECT_VALUE
            else:
                output = SlotComponentEval.VECTOR_VALUE_NO_MATCH
        else:
            # If mapping not found
            output = SlotComponentEval.VECTOR_VALUE_NO_MATCH
        return output

    def _update_vector_component_slot_evaluation(self, mapping_v_to_i: dict[str, str]):
        positions = []

        for i, result, component_name, slot_name in self._results.get_vector_component_slot_evaluations():
            positions.append(i)
            self._results.set_result(
                index=i,
                result=self._evaluate_component_vector_result(
                    mapping_v_to_i=mapping_v_to_i,
                    result=result,
                    component_name=component_name,
                    slot_name=slot_name,
                ),
            )
        self._results.add_equipment_vector_results(positions)

    def _add_equipment_slot_evaluation(self, equipment: Equipment, slot_name: str, component_results: list[str]):
        component_results = set(component_results)
        if len(component_results) > 1:
            raise Exception(f"Different results are assigned to the same slot and equipment: {component_results}")
        # Check first if it contains vector should be:
        vector_should_be = False
        for result in component_results:
            if result is not None and SlotComponentEval.VECTOR_SHOULD_BE_STR.format("") in result:
                vector_should_be = True

        if vector_should_be:
            return  # Vector slots are resolved later after vector mapping is computed.

        if SlotComponentEval.CORRECT_VALUE in component_results:
            result = SlotEquipmentEval.CORRECT_VALUE
        elif SlotComponentEval.VECTOR_VALUE_NO_MATCH in component_results:
            result = SlotEquipmentEval.VECTOR_VALUE_NO_MATCH
        elif SlotComponentEval.INCORRECT_VALUE in component_results:
            result = SlotEquipmentEval.INCORRECT_VALUE
        else:
            return
        self._results.add(
            result=result, equipment_name=equipment.name, equipment_class=equipment.class_name, slot=slot_name
        )


class EvaluationResults:
    def __init__(self):
        self._equipment_names: list[str | None] = []
        self._equipment_classes: list[str | None] = []
        self._component_names: list[str | None] = []
        self._component_classes: list[str | None] = []
        self._slots: list[str | None] = []
        self._results: list[EvaluationResult] = []

    def add(
        self,
        result: EvaluationResult,
        equipment_name: Optional[str] = None,
        equipment_class: Optional[str] = None,
        component_name: Optional[str] = None,
        component_class: Optional[str] = None,
        slot: Optional[str] = None,
    ):
        if slot is not None and slot not in ALL_EVALUATION_SLOTS:
            return  #  skip slots that are not part of the evaluation
        self._equipment_names.append(equipment_name)
        self._equipment_classes.append(equipment_class)
        self._component_names.append(component_name)
        self._component_classes.append(component_class)
        self._slots.append(slot)
        self._results.append(result)

    def set_result(self, index: int, result: EvaluationResult):
        self._results[index] = result

    def get_vector_component_slot_evaluations(self) -> list[tuple[int, str, str | None, str | None]]:
        temp_string = SlotComponentEval.VECTOR_SHOULD_BE_STR.format("")
        return [
            (index, result, self._component_names[index], self._slots[index])
            for index, result in enumerate(self._results)
            if temp_string in result
        ]

    def add_equipment_match_results(self):
        # Search for rows that already have an equipment match result
        equipment_with_result: set[tuple[str | None, str | None]] = set() # set((equipment.name, equipment.__class__.__name__))
        for i, result in enumerate(self._results):
            if isinstance(result, EquipmentEval):
                equipment_with_result.add((self._equipment_names[i], self._equipment_classes[i]))

        # Iterate over all results
        equipment_results: dict[tuple[str | None, str | None], EquipmentEval] = {}
        for i, result in enumerate(self._results):
            # Skip if the result is not a slot evaluation of a component slot
            if not isinstance(result, SlotEquipmentEval):
                continue

            key = (self._equipment_names[i], self._equipment_classes[i])

            # Skip if the component already has already component evaluation results
            if key in equipment_with_result:
                continue

            if key not in equipment_results:
                equipment_results[key] = EquipmentEval.FULLY_CORRECT
            if result != SlotEquipmentEval.CORRECT_VALUE:
                equipment_results[key] = EquipmentEval.MATCH

        for (equipment_name, equipment_class), equipment_result in equipment_results.items():
            self.add(
                result=equipment_result,
                equipment_name=equipment_name,
                equipment_class=equipment_class,
            )

    def add_component_match_results(self):
        # Search for rows that already have a component match result
        components_with_result: set[tuple[str | None, str | None]] = set()  # set((component.name, component.__class__.__name__))
        for i, result in enumerate(self._results):
            if isinstance(result, ComponentEval):
                components_with_result.add((self._component_names[i], self._component_classes[i]))

        # Iterate over all results
        component_results: dict[tuple[str | None, str | None], ComponentEval] = {}
        for i, result in enumerate(self._results):
            # Skip if the result is not a slot evaluation of a component slot
            if not isinstance(result, SlotComponentEval):
                continue

            key = (self._component_names[i], self._component_classes[i])

            # Skip if the component already has already component evaluation results
            if key in components_with_result:
                continue

            if key not in component_results:
                component_results[key] = ComponentEval.FULLY_CORRECT
            if result != SlotComponentEval.CORRECT_VALUE:
                component_results[key] = ComponentEval.MATCH

        for (component_name, component_class), component_result in component_results.items():
            self.add(
                result=component_result,
                component_name=component_name,
                component_class=component_class,
            )

    def add_equipment_vector_results(self, positions: list[int]):
        # {(equipment.name, equipment.class_name, slot): SlotEquipmentEval}
        equipment_results: dict[tuple[str | None, str | None, str | None], SlotEquipmentEval] = {}
        for i in positions:
            key = (self._equipment_names[i], self._equipment_classes[i], self._slots[i])
            if key not in equipment_results:
                equipment_results[key] = SlotEquipmentEval.VECTOR_VALUE_NO_MATCH
            if self._results[i] == SlotComponentEval.CORRECT_VALUE:
                equipment_results[key] = SlotEquipmentEval.CORRECT_VALUE

        for (equipment_name, equipment_class, slot), equipment_result in equipment_results.items():
            self.add(
                result=equipment_result,
                equipment_name=equipment_name,
                equipment_class=equipment_class,
                slot=slot,
            )

    def to_dict(self):
        if self._contains_temp_results():
            raise Exception("Evaluation results contain temporary values that should be removed before saving to dict.")
        return {
            "equipment": self._equipment_names,
            "equipment_class": self._equipment_classes,
            "component": self._component_names,
            "component_class": self._component_classes,
            "slot": self._slots,
            "result": self._results,
        }

    def _contains_temp_results(self):
        component_temp_string = SlotComponentEval.VECTOR_SHOULD_BE_STR.format("")
        for result in self._results:
            if component_temp_string in result:
                return True
        return False

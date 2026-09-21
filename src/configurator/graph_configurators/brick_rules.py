import logging
from pathlib import Path

import rdflib
from rdflib.namespace import split_uri

from ..constants.file_names import FileNames
from ..constants.paths import BRICK_TTL_PATH
from ..entities.kees_lite import (
    EnergyVector,
    FixedConsumptionComponent,
    FixedGenerationComponent,
    FlexibleGenerationComponent,
    Graph,
    InterconnectorComponent,
    StorageComponent,
)
from ..enums.ontology import Ontology
from ..utils.config import ConfigLoader, ConfigSections
from ..utils.graph import GraphUtils
from ..utils.rdf import transform_to_kw, ResourceDescription

logger = logging.getLogger(__name__)


class GraphConfigurator:
    def _log(self, level: int, message: str):
        logger.log(level, f"[Scenario: {self._scenario_dir_path.name} | Brick Rules] {message}")

    def __init__(self, scenario_dir_path: Path, config_loader: ConfigLoader):
        self._scenario_dir_path = scenario_dir_path
        self._result_path = scenario_dir_path / FileNames.rule_graph(Ontology.BRICK)
        self._config = config_loader.get_section(ConfigSections.BRICK_RULES_GRAPH_CONFIGURATOR)

        # Use anon version, so it is easier to match names (in anon version names of equipment are taken from Scenario without changes)
        rdf_description_path = (scenario_dir_path / FileNames.BRICK_DESCRIPTION_ANON).resolve().as_uri()
        rdf_graph = rdflib.Graph()
        rdf_graph.parse(rdf_description_path, format="turtle")
        rdf_graph.parse(BRICK_TTL_PATH, format="turtle")
        self._rdf_graph = rdf_graph

        self._e_vectors: dict[str, EnergyVector] = {}
        """Resource name -> `EnergyVector`"""

        self._h_vectors: dict[str, EnergyVector] = {}
        """Resource name -> `EnergyVector`"""

        self._processed_equipment: list[str] = []
        """Resource names of processed `brick:Electrical_System` individuals"""

        self._processed_loops: list[str] = []
        """Resource names of processed `brick:Hot_Water_Loop` individuals`"""

        self._processed_systems: list[str] = []
        """Resource names of processed `brick:Hot_Water_System` individuals`"""

    def configure_graph(self):
        result = Graph()

        self._log(logging.INFO, "Use class brick:Electrical_System as candidate for electrical energy vector.")
        e_systems = self._get_e_systems()
        self._e_vectors = {name: EnergyVector(name=name) for name in e_systems}
        self._processed_systems.extend(e_systems)
        result.energyVectors.extend(self._e_vectors.values())

        self._log(logging.INFO, "Use class brick:Hot_Water_Loop as candidate for heating energy vector.")
        h_loops = self._get_h_loops()
        self._h_vectors = {name: EnergyVector(name=name) for name in h_loops}
        self._processed_loops.extend(h_loops)
        result.energyVectors.extend(self._h_vectors.values())

        self._add_boilers(result)
        self._add_e_consumption_meters(result)
        self._add_h_consumption_meters(result)
        self._add_heatpumps(result)
        self._add_pvs(result)
        self._add_batteries(result)

        GraphUtils.save_graph(graph=result, output_path=self._result_path)

        # Log ignored instances:
        # Loops
        all_loops = self._get_loops()
        ignored_loops = set(all_loops) - set(self._processed_loops)
        for loop in ignored_loops:
            description = all_loops[loop]
            self._log(logging.INFO, f"Ignored loop: {description.full_uri} of class {description.type_uri}.")
        # Systems
        all_systems = self._get_systems()
        ignored_systems = set(all_systems) - set(self._processed_systems)
        for system in ignored_systems:
            description = all_systems[system]
            self._log(logging.INFO, f"Ignored system: {description.full_uri} of class {description.type_uri}.")
        # Equipment
        all_equipment = self._get_equipment()
        ignored_equipment = set(all_equipment) - set(self._processed_equipment)
        for equipment in ignored_equipment:
            description = all_equipment[equipment]
            self._log(logging.INFO, f"Ignored equipment: {description.full_uri} of class {description.type_uri}.")

    def _get_e_systems(self) -> list[str]:
        """ "
        Returns list with resource names of individuals of `brick:Electrical_System` class and its subclasses.
        """
        q = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?type
        WHERE {
            ?x rdf:type ?type .
            ?type rdfs:subClassOf* brick:Electrical_System .
        }"""
        query_results = self._rdf_graph.query(q)
        return [split_uri(row.x)[-1] for row in query_results]

    def _get_h_systems(self) -> list[str]:
        """ "
        Returns list with resource names of individuals of `brick:Hot_Water_System` class and its subclasses.
        """
        q = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?type
        WHERE {
            ?x rdf:type ?type .
            ?type rdfs:subClassOf* brick:Hot_Water_System .
        }"""
        query_results = self._rdf_graph.query(q)
        return [split_uri(row.x)[-1] for row in query_results]

    def _get_h_loops(self) -> list[str]:
        """ "
        Returns list with resource names of individuals of `brick:Hot_Water_Loop` class and its subclasses.
        """
        q = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?type
        WHERE {
            ?x rdf:type ?type .
            ?type rdfs:subClassOf* brick:Hot_Water_Loop .
        }"""
        query_results = self._rdf_graph.query(q)
        return [split_uri(row.x)[-1] for row in query_results]

    def _get_connected_e_system(self, equipment_uri: rdflib.term.URIRef) -> list[str]:
        """ "
        Returns list with resource names of individuals of `brick:Electrical_System` and its subclasses
         connected to equipment with provided URI.
        """
        q = f"""
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x
        WHERE {{
            ?x rdf:type/rdfs:subClassOf* brick:Electrical_System .
            ?x brick:hasPart <{equipment_uri}> .
        }}
        """
        query_results = self._rdf_graph.query(q)
        return [split_uri(row.x)[-1] for row in query_results]

    def _get_connected_h_system(self, equipment_uri: rdflib.term.URIRef) -> list[str]:
        """ "
        Returns list with resource names of individuals of `brick:Hot_Water_System` class and its subclasses
         connected to equipment with provided URI.
        """
        q = f"""
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x
        WHERE {{
            ?x rdf:type/rdfs:subClassOf* brick:Hot_Water_System .
            ?x brick:hasPart <{equipment_uri}> .
        }}
        """
        query_results = self._rdf_graph.query(q)
        return [split_uri(row.x)[-1] for row in query_results]

    def _get_connected_h_loop(self, equipment_uri: rdflib.term.URIRef) -> list[str]:
        """ "
        Returns list with resource names of individuals of `brick:Hot_Water_Loop` class and its subclasses
        connected to equipment with provided URI.
        """
        q = f"""
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x
        WHERE {{
            ?x rdf:type/rdfs:subClassOf* brick:Hot_Water_Loop .
            ?x brick:hasPart <{equipment_uri}> .
        }}
        """
        query_results = self._rdf_graph.query(q)
        return [split_uri(row.x)[-1] for row in query_results]

    def _get_connected_e_vector(self, equipment_uri: rdflib.term.URIRef) -> EnergyVector:
        vectors = self._get_connected_e_system(equipment_uri)
        if len(vectors) != 1:
            raise Exception(f"Equipment {equipment_uri} has none or multiple electrical vector candidates: {vectors}!")
        return self._e_vectors[vectors[0]]

    def _get_connected_h_vector(self, equipment_uri: rdflib.term.URIRef) -> EnergyVector:
        vectors = self._get_connected_h_loop(equipment_uri)
        if len(vectors) != 1:
            raise Exception(f"Equipment {equipment_uri} has none or multiple heating vector candidates: {vectors}!")
        return self._h_vectors[vectors[0]]

    def _get_equipment(self) -> dict[str, ResourceDescription]:
        """ "
        Returns dictionary with individuals of `brick:Equipment` and its subclasses
         where keys are resource names and values are `ResourceDescriptions` containing full resource URI and URI of its type.
        """
        q = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?type
        WHERE {
            ?x rdf:type ?type .
            ?type rdfs:subClassOf* brick:Equipment .
        }"""
        query_results = self._rdf_graph.query(q)
        return {split_uri(row.x)[-1]: ResourceDescription(full_uri=row.x, type_uri=row.type) for row in query_results}

    def _get_loops(self) -> dict[str, ResourceDescription]:
        """ "
        Returns dictionary with individuals of `brick:Loop` and its subclasses
         where keys are resource names and values are `ResourceDescriptions` containing full resource URI and URI of its type.
        """
        q = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?type
        WHERE {
            ?x rdf:type ?type .
            ?type rdfs:subClassOf* brick:Loop .
        }"""
        query_results = self._rdf_graph.query(q)
        return {split_uri(row.x)[-1]: ResourceDescription(full_uri=row.x, type_uri=row.type) for row in query_results}

    def _get_systems(self) -> dict[str, ResourceDescription]:
        """ "
        Returns dictionary with individuals of `brick:System` and its subclasses
         where keys are resource names and values are `ResourceDescriptions` containing full resource URI and URI of its type.
        """
        q = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?type
        WHERE {
            ?x rdf:type ?type .
            ?type rdfs:subClassOf* brick:System .
        }"""
        query_results = self._rdf_graph.query(q)
        return {split_uri(row.x)[-1]: ResourceDescription(full_uri=row.x, type_uri=row.type) for row in query_results}

    def _add_boilers(self, kees_graph: Graph) -> None:
        q = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?x ?pVal ?pUnit
        WHERE {
            ?x rdf:type/rdfs:subClassOf* brick:Boiler .

            OPTIONAL {
                ?x brick:ratedPowerOutput ?power .
                ?power brick:value ?pVal .
                ?power brick:hasUnit ?pUnit .
            }
        }"""
        query_results = self._rdf_graph.query(q)
        for row in query_results:
            name = split_uri(row.x)[-1]
            max_generation = transform_to_kw(value=row.pVal, unit_uri=row.pUnit)
            vector = self._get_connected_h_vector(row.x)
            component = FlexibleGenerationComponent(
                name=name,
                hasMaxGeneration=max_generation,
                hasGenerationVector=vector.name,
                isExternal=False,
            )
            kees_graph.flexibleGenerations.append(component)
            self._processed_equipment.append(name)

    def _add_e_consumption_meters(self, kees_graph: Graph) -> None:
        q = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x
        WHERE {
            ?x rdf:type/rdfs:subClassOf* brick:Electrical_Meter .
        }"""
        query_results = self._rdf_graph.query(q)
        for row in query_results:
            name = split_uri(row.x)[-1]
            vector = self._get_connected_e_vector(row.x)
            component = FixedConsumptionComponent(
                name=name,
                hasConsumptionVector=vector.name,
                isExternal=False,
            )
            kees_graph.fixedConsumptions.append(component)
            self._processed_equipment.append(name)

    def _add_h_consumption_meters(self, kees_graph: Graph) -> None:
        q = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x
        WHERE {
            ?x rdf:type/rdfs:subClassOf* brick:Hot_Water_Meter .
        }"""
        query_results = self._rdf_graph.query(q)
        for row in query_results:
            name = split_uri(row.x)[-1]
            vector = self._get_connected_h_vector(row.x)
            component = FixedConsumptionComponent(
                name=name,
                hasConsumptionVector=vector.name,
                isExternal=False,
            )
            kees_graph.fixedConsumptions.append(component)
            self._processed_equipment.append(name)

    def _add_heatpumps(self, kees_graph: Graph) -> None:
        q = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?genVal ?genUnit ?consValue ?consUnit ?effVal
        WHERE {
            ?x rdf:type/rdfs:subClassOf* brick:Packaged_Heat_Pump .

            OPTIONAL {
                ?x brick:ratedPowerOutput ?gen .
                ?gen brick:value ?genVal .
                ?gen brick:hasUnit ?genUnit .
            }
            
            OPTIONAL {
                ?x brick:ratedPowerInput ?cons .
                ?cons brick:value ?consValue .
                ?cons brick:hasUnit ?consUnit .
            }
            
            OPTIONAL {
                ?x brick:conversionEfficiency ?eff .
                ?eff brick:value ?effVal .
            }
        }"""
        query_results = self._rdf_graph.query(q)
        for row in query_results:
            name = split_uri(row.x)[-1]
            max_generation = transform_to_kw(value=row.genVal, unit_uri=row.genUnit)
            max_consumption = transform_to_kw(value=row.consValue, unit_uri=row.consUnit)
            efficiency = float(row.effVal) if row.effVal is not None else None
            h_vector = self._get_connected_h_vector(row.x)
            e_vector = self._get_connected_e_vector(row.x)
            component = InterconnectorComponent(
                name=name,
                hasGenerationVector=h_vector.name,
                hasConsumptionVector=e_vector.name,
                hasMaxGeneration=max_generation,
                hasMaxConsumption=max_consumption,
                hasEfficiency=efficiency,
                isExternal=False,
            )
            kees_graph.interconnectors.append(component)
            self._processed_equipment.append(name)

    def _add_pvs(self, kees_graph: Graph) -> None:
        q = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x
        WHERE {
            ?x rdf:type/rdfs:subClassOf* brick:PV_Panel .
        }"""
        query_results = self._rdf_graph.query(q)
        for row in query_results:
            name = split_uri(row.x)[-1]
            vector = self._get_connected_e_vector(row.x)
            component = FixedGenerationComponent(
                name=name,
                hasGenerationVector=vector.name,
                isExternal=False,
            )
            kees_graph.fixedGenerations.append(component)
            self._processed_equipment.append(name)

    def _add_batteries(self, kees_graph: Graph) -> None:
        q = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?genVal ?genUnit ?consVal ?consUnit ?effVal
        WHERE {
            ?x rdf:type/rdfs:subClassOf* brick:Battery .

            OPTIONAL {
                ?x brick:ratedPowerOutput ?gen .
                ?gen brick:value ?genVal .
                ?gen brick:hasUnit ?genUnit .
            }

            OPTIONAL {
                ?x brick:ratedPowerInput ?cons .
                ?cons brick:value ?consVal .
                ?cons brick:hasUnit ?consUnit .
            }

            OPTIONAL {
                ?x brick:conversionEfficiency ?eff .
                ?eff brick:value ?effVal .
            }
        }"""
        query_results = self._rdf_graph.query(q)
        for row in query_results:
            name = split_uri(row.x)[-1]
            max_generation = transform_to_kw(value=row.genVal, unit_uri=row.genUnit)
            max_consumption = transform_to_kw(value=row.consVal, unit_uri=row.consUnit)
            efficiency = float(row.effVal) if row.effVal is not None else None
            e_vector = self._get_connected_e_vector(row.x)
            component = StorageComponent(
                name=name,
                hasGenerationVector=e_vector.name,
                hasConsumptionVector=e_vector.name,
                hasMaxGeneration=max_generation,
                hasMaxConsumption=max_consumption,
                hasEfficiency=efficiency,
                isExternal=False,
            )
            kees_graph.storages.append(component)
            self._processed_equipment.append(name)

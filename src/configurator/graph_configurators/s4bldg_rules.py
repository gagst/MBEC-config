import logging
from pathlib import Path
from typing import Optional

import rdflib
from rdflib.namespace import split_uri

from ..constants.file_names import FileNames
from ..constants.paths import S4BLDG_TTL_PATH
from ..entities.kees_lite import (
    EnergyVector,
    FixedConsumptionComponent,
    FixedGenerationComponent,
    FlexibleGenerationComponent,
    Graph,
    InterconnectorComponent,
    StorageComponent,
)
from ..enums.config_section import ConfigSections
from ..enums.ontology import Ontology
from ..utils.config import ConfigLoader
from ..utils.graph import GraphUtils
from ..utils.rdf import transform_to_kw, ResourceDescription

logger = logging.getLogger(__name__)


class GraphConfigurator:
    def _log(self, level: int, message: str):
        logger.log(level, f"[Scenario: {self._scenario_dir_path.name}] | S4BLDG Rules] {message}")

    def __init__(self, scenario_dir_path: Path, config_loader: ConfigLoader):
        self._scenario_dir_path = scenario_dir_path
        self._result_path = scenario_dir_path / FileNames.rule_graph(Ontology.S4BLDG)
        self._config = config_loader.get_section(ConfigSections.S4BLDG_RULES_GRAPH_CONFIGURATOR)

        # Use anon version, so it is easier to match names (in anon version names of equipment are taken from Scenario without changes)
        rdf_description_path = (scenario_dir_path / FileNames.S4BLDG_DESCRIPTION_ANON).resolve().as_uri()
        rdf_graph = rdflib.Graph()
        rdf_graph.parse(rdf_description_path, format="turtle")
        rdf_graph.parse(S4BLDG_TTL_PATH, format="turtle")
        self._rdf_graph = rdf_graph

        self._e_default_vec = EnergyVector(name="electrical")
        self._e_default_vec_is_used = False
        self._h_default_vec = EnergyVector(name="heating")
        self._h_default_vec_is_used = False

        self._e_vectors: dict[str, EnergyVector] = {}
        """Resource name -> `EnergyVector`"""

        self._h_vectors: dict[str, EnergyVector] = {}
        """Resource name -> `EnergyVector`"""

        self._processed_devices: list[str] = []
        """Resource names of processed `s4bldg:Device` individuals"""

        self._processed_buildings: list[str] = []
        """Resource names of processed `s4bldg:Building` individuals"""

    def configure_graph(self):
        result = Graph()

        self._log(logging.INFO, "Assume each building has an electrical and heating vector.")

        self._add_boilers(result)
        self._add_electric_appliances(result)
        self._add_space_heaters(result)
        self._add_energy_conversion_devices(result)
        self._add_solar_devices(result)
        self._add_storage_devices(result)

        # Add vectors:
        if self._e_default_vec_is_used:
            result.energyVectors.append(self._e_default_vec)
        if self._h_default_vec_is_used:
            result.energyVectors.append(self._h_default_vec)
        result.energyVectors.extend(self._e_vectors.values())
        result.energyVectors.extend(self._h_vectors.values())

        GraphUtils.save_graph(graph=result, output_path=self._result_path)

        # Log ignored instances
        # Buildings
        all_buildings = self._get_buildings()
        ignored_buildings = set(all_buildings) - set(self._processed_buildings)
        for building in ignored_buildings:
            description = all_buildings[building]
            self._log(logging.INFO, f"Ignored building: {description.full_uri} of class {description.type_uri}.")
        # Devices
        all_devices = self._get_devices()
        ignored_devices = set(all_devices) - set(self._processed_devices)
        for device in ignored_devices:
            description = all_devices[device]
            self._log(logging.INFO, f"Ignored device: {description.full_uri} of class {description.type_uri}.")

    def _get_e_vector(self, building_uri: Optional[rdflib.term.URIRef]) -> EnergyVector:
        if building_uri is None:
            self._e_default_vec_is_used = True
            return self._e_default_vec
        name = split_uri(building_uri)[-1]
        if name not in self._e_vectors:
            self._e_vectors[name] = EnergyVector(name=f"{name}_electrical")
        self._processed_buildings.append(name)
        return self._e_vectors[name]

    def _get_h_vector(self, building_uri: Optional[rdflib.term.URIRef]) -> EnergyVector:
        if building_uri is None:
            self._h_default_vec_is_used = True
            return self._h_default_vec
        name = split_uri(building_uri)[-1]
        if name not in self._h_vectors:
            self._h_vectors[name] = EnergyVector(name=f"{name}_heating")
        self._processed_buildings.append(name)
        return self._h_vectors[name]

    def _get_buildings(self) -> dict[str, ResourceDescription]:
        """ "
        Returns dictionary with individuals of  `s4bldg:Building` and its subclasses
         where keys are resource names and values are `ResourceDescriptions` containing full resource URI and URI of its type.
        """
        q = """
        PREFIX s4bldg: <https://saref.etsi.org/saref4bldg/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?type
        WHERE {
            ?x rdf:type ?type .
            ?type rdfs:subClassOf* s4bldg:Building .
        }"""
        query_results = self._rdf_graph.query(q)
        return {split_uri(row.x)[-1]: ResourceDescription(full_uri=row.x, type_uri=row.type) for row in query_results}

    def _get_devices(self) -> dict[str, ResourceDescription]:
        """ "
        Returns dictionary with individuals of `saref:Device` and its subclasses
         where keys are resource names and values are `ResourceDescriptions` containing full resource URI and URI of its type.
        """
        q = """
        PREFIX s4bldg: <https://saref.etsi.org/saref4bldg/>
        PREFIX saref: <https://saref.etsi.org/core/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?type
        WHERE {
            ?x rdf:type ?type .
            ?type rdfs:subClassOf* saref:Device .
        }"""
        query_results = self._rdf_graph.query(q)
        return {split_uri(row.x)[-1]: ResourceDescription(full_uri=row.x, type_uri=row.type) for row in query_results}

    def _add_boilers(self, kees_graph: Graph) -> None:
        q = """
        PREFIX s4bldg: <https://saref.etsi.org/saref4bldg/>
        PREFIX saref: <https://saref.etsi.org/core/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?b ?pVal ?pUnit
        WHERE {
            ?x rdf:type/rdfs:subClassOf* s4bldg:Boiler .

            OPTIONAL {
                ?x s4bldg:isContainedIn ?space .
                ?space rdf:type/rdfs:subClassOf* s4bldg:BuildingSpace .
                ?space s4bldg:isSpaceOf ?b .
            }

            OPTIONAL {
                ?x s4bldg:outputCapacity ?power .
                ?power saref:hasValue ?pVal .
                ?power saref:isMeasuredIn ?pUnit .
            }

            OPTIONAL {
                ?x s4bldg:nominalHeatingCapacity ?power .
                ?power saref:hasValue ?pVal .
                ?power saref:isMeasuredIn ?pUnit .
            }

            OPTIONAL {
                ?x s4bldg:nominalCapacity ?power .
                ?power saref:hasValue ?pVal .
                ?power saref:isMeasuredIn ?pUnit .
            }
        }"""
        query_results = self._rdf_graph.query(q)
        for row in query_results:
            name = split_uri(row.x)[-1]
            max_generation = transform_to_kw(value=row.pVal, unit_uri=row.pUnit)
            vector = self._get_h_vector(row.b)
            component = FlexibleGenerationComponent(
                name=name,
                hasMaxGeneration=max_generation,
                hasGenerationVector=vector.name,
                isExternal=False,
            )
            kees_graph.flexibleGenerations.append(component)
            self._processed_devices.append(name)

    def _add_electric_appliances(self, kees_graph: Graph) -> None:
        q = """
        PREFIX s4bldg: <https://saref.etsi.org/saref4bldg/>
        PREFIX saref: <https://saref.etsi.org/core/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?b
        WHERE {
            ?x rdf:type/rdfs:subClassOf* s4bldg:ElectricAppliance .
            
            OPTIONAL {
                ?x s4bldg:isContainedIn ?space .
                ?space rdf:type/rdfs:subClassOf* s4bldg:BuildingSpace .
                ?space s4bldg:isSpaceOf ?b .
            }
        }"""
        query_results = self._rdf_graph.query(q)
        for row in query_results:
            name = split_uri(row.x)[-1]
            vector = self._get_e_vector(row.b)
            component = FixedConsumptionComponent(
                name=name,
                hasConsumptionVector=vector.name,
                isExternal=False,
            )
            kees_graph.fixedConsumptions.append(component)
            self._processed_devices.append(name)

    def _add_space_heaters(self, kees_graph: Graph) -> None:
        q = """
        PREFIX s4bldg: <https://saref.etsi.org/saref4bldg/>
        PREFIX saref: <https://saref.etsi.org/core/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?b
        WHERE {
            ?x rdf:type/rdfs:subClassOf* s4bldg:SpaceHeater .

            OPTIONAL {
                ?x s4bldg:isContainedIn ?space .
                ?space rdf:type/rdfs:subClassOf* s4bldg:BuildingSpace .
                ?space s4bldg:isSpaceOf ?b .
            }
        }"""
        query_results = self._rdf_graph.query(q)
        for row in query_results:
            name = split_uri(row.x)[-1]
            vector = self._get_h_vector(row.b)
            component = FixedConsumptionComponent(
                name=name,
                hasConsumptionVector=vector.name,
                isExternal=False,
            )
            kees_graph.fixedConsumptions.append(component)
            self._processed_devices.append(name)

    def _add_energy_conversion_devices(self, kees_graph: Graph) -> None:
        q = """
        PREFIX s4bldg: <https://saref.etsi.org/saref4bldg/>
        PREFIX saref: <https://saref.etsi.org/core/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?b ?genVal ?genUnit ?consVal ?consUnit
        WHERE {
            ?x rdf:type/rdfs:subClassOf* s4bldg:EnergyConversionDevice .

            OPTIONAL {
                ?x s4bldg:isContainedIn ?space .
                ?space rdf:type/rdfs:subClassOf* s4bldg:BuildingSpace .
                ?space s4bldg:isSpaceOf ?b .
            }

            OPTIONAL {
                ?x s4bldg:outputCapacity ?gen .
                ?gen saref:hasValue ?genVal .
                ?gen saref:isMeasuredIn ?genUnit .
            }

            OPTIONAL {
                ?x s4bldg:nominalHeatingCapacity ?gen .
                ?gen saref:hasValue ?genVal .
                ?gen saref:isMeasuredIn ?genUnit .
            }

            OPTIONAL {
                ?x s4bldg:nominalCapacity ?gen .
                ?gen saref:hasValue ?genVal .
                ?gen saref:isMeasuredIn ?genUnit .
            }
            
            OPTIONAL {
                ?x s4bldg:nominalPowerConsumption ?cons .
                ?cons saref:hasValue ?consVal .
                ?cons saref:isMeasuredIn ?consUnit .
            }

            OPTIONAL {
                ?x s4bldg:nominalEnergyConsumption ?cons .
                ?cons saref:hasValue ?consVal .
                ?cons saref:isMeasuredIn ?consUnit .
            }

            OPTIONAL {
                ?x s4bldg:apparentPowerMax ?cons .
                ?cons saref:hasValue ?consVal .
                ?cons saref:isMeasuredIn ?consUnit .
            }
        }"""
        query_results = self._rdf_graph.query(q)
        for row in query_results:
            name = split_uri(row.x)[-1]
            max_generation = transform_to_kw(value=row.genVal, unit_uri=row.genUnit)
            max_consumption = transform_to_kw(value=row.consVal, unit_uri=row.consUnit)
            h_vector = self._get_h_vector(row.b)
            e_vector = self._get_e_vector(row.b)
            component = InterconnectorComponent(
                name=name,
                hasGenerationVector=h_vector.name,
                hasConsumptionVector=e_vector.name,
                hasMaxGeneration=max_generation,
                hasMaxConsumption=max_consumption,
                isExternal=False,
            )
            kees_graph.interconnectors.append(component)
            self._processed_devices.append(name)

    def _add_solar_devices(self, kees_graph: Graph) -> None:
        q = """
        PREFIX s4bldg: <https://saref.etsi.org/saref4bldg/>
        PREFIX saref: <https://saref.etsi.org/core/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?b
        WHERE {
            ?x rdf:type/rdfs:subClassOf* s4bldg:SolarDevice .

            OPTIONAL {
                ?x s4bldg:isContainedIn ?space .
                ?space rdf:type/rdfs:subClassOf* s4bldg:BuildingSpace .
                ?space s4bldg:isSpaceOf ?b .
            }
        }"""
        query_results = self._rdf_graph.query(q)
        for row in query_results:
            name = split_uri(row.x)[-1]
            vector = self._get_e_vector(row.b)
            component = FixedGenerationComponent(
                name=name,
                hasGenerationVector=vector.name,
                isExternal=False,
            )
            kees_graph.fixedGenerations.append(component)
            self._processed_devices.append(name)

    def _add_storage_devices(self, kees_graph: Graph) -> None:
        q = """
        PREFIX s4bldg: <https://saref.etsi.org/saref4bldg/>
        PREFIX saref: <https://saref.etsi.org/core/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?x ?b ?genVal ?genUnit ?consVal ?consUnit
        WHERE {
            ?x rdf:type/rdfs:subClassOf* s4bldg:ElectricFlowStorageDevice .

            OPTIONAL {
                ?x s4bldg:isContainedIn ?space .
                ?space rdf:type/rdfs:subClassOf* s4bldg:BuildingSpace .
                ?space s4bldg:isSpaceOf ?b .
            }

            OPTIONAL {
                ?x s4bldg:apparentPowerMax ?gen .
                ?gen saref:hasValue ?genVal .
                ?gen saref:isMeasuredIn ?genUnit .
            }

            OPTIONAL {
                ?x s4bldg:nominalPowerConsumption ?cons .
                ?cons saref:hasValue ?consVal .
                ?cons saref:isMeasuredIn ?consUnit .
            }

            OPTIONAL {
                ?x s4bldg:nominalEnergyConsumption ?cons .
                ?cons saref:hasValue ?consVal .
                ?cons saref:isMeasuredIn ?consUnit .
            }    
        }"""
        query_results = self._rdf_graph.query(q)
        for row in query_results:
            name = split_uri(row.x)[-1]
            max_generation = transform_to_kw(value=row.genVal, unit_uri=row.genUnit)
            max_consumption = transform_to_kw(value=row.consVal, unit_uri=row.consUnit)
            e_vector = self._get_e_vector(row.b)
            component = StorageComponent(
                name=name,
                hasGenerationVector=e_vector.name,
                hasConsumptionVector=e_vector.name,
                hasMaxGeneration=max_generation,
                hasMaxConsumption=max_consumption,
                isExternal=False,
            )
            kees_graph.storages.append(component)
            self._processed_devices.append(name)

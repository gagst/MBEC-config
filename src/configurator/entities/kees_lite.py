from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )

    @model_serializer(mode='wrap', when_used='unless-none')
    def treat_empty_lists_as_none(
            self, handler: SerializerFunctionWrapHandler,
            info: SerializationInfo) -> dict[str, Any]:
        if info.exclude_none:
            _instance = self.model_copy()
            for field, field_info in type(_instance).model_fields.items():
                if getattr(_instance, field) == [] and not(
                        field_info.is_required()):
                    setattr(_instance, field, None)
        else:
            _instance = self
        return handler(_instance, info)



class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'kees_lite',
     'id': 'https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/kees_lite.owl.ttl',
     'imports': ['linkml:types'],
     'name': 'KEES_lite',
     'prefixes': {'kees_lite': {'prefix_prefix': 'kees_lite',
                                'prefix_reference': 'https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/kees_lite.owl.ttl/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'C:\\Users\\gagin01\\Projects\\multi-vector-optimization-configurator\\linkml_schemas\\kees_lite.yaml'} )


class Graph(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/kees_lite.owl.ttl',
         'tree_root': True})

    energyVectors: Optional[list[EnergyVector]] = Field(default=[], json_schema_extra = { "linkml_meta": {'domain_of': ['Graph']} })
    fixedGenerations: Optional[list[FixedGenerationComponent]] = Field(default=[], json_schema_extra = { "linkml_meta": {'domain_of': ['Graph']} })
    fixedConsumptions: Optional[list[FixedConsumptionComponent]] = Field(default=[], json_schema_extra = { "linkml_meta": {'domain_of': ['Graph']} })
    flexibleGenerations: Optional[list[FlexibleGenerationComponent]] = Field(default=[], json_schema_extra = { "linkml_meta": {'domain_of': ['Graph']} })
    flexibleConsumptions: Optional[list[FlexibleConsumptionComponent]] = Field(default=[], json_schema_extra = { "linkml_meta": {'domain_of': ['Graph']} })
    timeFlexibleConsumptions: Optional[list[TimeFlexibleConsumptionComponent]] = Field(default=[], json_schema_extra = { "linkml_meta": {'domain_of': ['Graph']} })
    interconnectors: Optional[list[InterconnectorComponent]] = Field(default=[], json_schema_extra = { "linkml_meta": {'domain_of': ['Graph']} })
    storages: Optional[list[StorageComponent]] = Field(default=[], json_schema_extra = { "linkml_meta": {'domain_of': ['Graph']} })


class EnergyVector(ConfiguredBaseModel):
    """
    Energy vector represents the infrastructure of the building that can be used to transfer energy between different components. The components can generate and consume energy to and from connected energy vectors.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/kees_lite.owl.ttl',
         'slot_usage': {'name': {'identifier': True, 'name': 'name', 'required': True}}})

    name: str = Field(default=..., description="""string with short unique human-readable name of the component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    originalName: Optional[str] = Field(default=None, description="""string with the name assigned by configurator (should be ignored in most cases).""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })


class Component(ConfiguredBaseModel):
    """
    A component is a representation of one or multiple physical assets. They are connected to at least one energy vector and can consume energy from a vector or generate energy to a vector.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/kees_lite.owl.ttl'})

    name: Optional[str] = Field(default=None, description="""string with short unique human-readable name of the component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    originalName: Optional[str] = Field(default=None, description="""string with the name assigned by configurator (should be ignored in most cases).""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    isExternal: Optional[bool] = Field(default=None, description="""boolean that indicates if the component is considered external or not.""", json_schema_extra = { "linkml_meta": {'domain': 'Component', 'domain_of': ['Component']} })


class FixedConsumptionComponent(Component):
    """
    A component that consumes energy from an energy vector and is not controllable. For example, an energy demand when there is no demand side management is implemented.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/kees_lite.owl.ttl'})

    hasConsumptionVector: Optional[str] = Field(default=None, description="""connected energy vector from which the component consumes energy.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FixedConsumptionComponent',
                       'FlexibleConsumptionComponent',
                       'TimeFlexibleConsumptionComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    name: Optional[str] = Field(default=None, description="""string with short unique human-readable name of the component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    originalName: Optional[str] = Field(default=None, description="""string with the name assigned by configurator (should be ignored in most cases).""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    isExternal: Optional[bool] = Field(default=None, description="""boolean that indicates if the component is considered external or not.""", json_schema_extra = { "linkml_meta": {'domain': 'Component', 'domain_of': ['Component']} })


class FixedGenerationComponent(Component):
    """
    A component that generates energy to one connected energy vector and is not controllable.  For example, a PV might have a forecast for the next 24 hours.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/kees_lite.owl.ttl'})

    hasGenerationVector: Optional[str] = Field(default=None, description="""connected energy vector to which the component generates energy.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FixedGenerationComponent',
                       'FlexibleGenerationComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    name: Optional[str] = Field(default=None, description="""string with short unique human-readable name of the component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    originalName: Optional[str] = Field(default=None, description="""string with the name assigned by configurator (should be ignored in most cases).""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    isExternal: Optional[bool] = Field(default=None, description="""boolean that indicates if the component is considered external or not.""", json_schema_extra = { "linkml_meta": {'domain': 'Component', 'domain_of': ['Component']} })


class FlexibleConsumptionComponent(Component):
    """
    A controllable component that consumes energy from one connected energy vector.  Its consumption can be controlled within a given bound.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/kees_lite.owl.ttl'})

    hasConsumptionVector: Optional[str] = Field(default=None, description="""connected energy vector from which the component consumes energy.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FixedConsumptionComponent',
                       'FlexibleConsumptionComponent',
                       'TimeFlexibleConsumptionComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    hasMaxConsumption: Optional[float] = Field(default=None, description="""number indicating maximum energy consumption from the connected energy vector in kW.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FlexibleConsumptionComponent',
                       'TimeFlexibleConsumptionComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    name: Optional[str] = Field(default=None, description="""string with short unique human-readable name of the component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    originalName: Optional[str] = Field(default=None, description="""string with the name assigned by configurator (should be ignored in most cases).""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    isExternal: Optional[bool] = Field(default=None, description="""boolean that indicates if the component is considered external or not.""", json_schema_extra = { "linkml_meta": {'domain': 'Component', 'domain_of': ['Component']} })


class TimeFlexibleConsumptionComponent(Component):
    """
    Time-flexible consumption component consumes energy only between given time frame.  Washing machines or other flexible appliances are examples of assets that can be represented by the component.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/kees_lite.owl.ttl'})

    hasConsumptionVector: Optional[str] = Field(default=None, description="""connected energy vector from which the component consumes energy.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FixedConsumptionComponent',
                       'FlexibleConsumptionComponent',
                       'TimeFlexibleConsumptionComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    hasMaxConsumption: Optional[float] = Field(default=None, description="""number indicating maximum energy consumption from the connected energy vector in kW.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FlexibleConsumptionComponent',
                       'TimeFlexibleConsumptionComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    hasEnergyRequirement: Optional[float] = Field(default=None, description="""number indicating how much energy should be consumed by the component in given flexibility period in kWh.""", json_schema_extra = { "linkml_meta": {'domain': 'TimeFlexibleConsumptionComponent',
         'domain_of': ['TimeFlexibleConsumptionComponent']} })
    hasFlexiblePeriodStart: Optional[str] = Field(default=None, description="""time of the day from which the component can consume energy.""", json_schema_extra = { "linkml_meta": {'domain': 'TimeFlexibleConsumptionComponent',
         'domain_of': ['TimeFlexibleConsumptionComponent']} })
    hasFlexiblePeriodEnd: Optional[str] = Field(default=None, description="""time of the day until which the component can consume energy.""", json_schema_extra = { "linkml_meta": {'domain': 'TimeFlexibleConsumptionComponent',
         'domain_of': ['TimeFlexibleConsumptionComponent']} })
    name: Optional[str] = Field(default=None, description="""string with short unique human-readable name of the component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    originalName: Optional[str] = Field(default=None, description="""string with the name assigned by configurator (should be ignored in most cases).""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    isExternal: Optional[bool] = Field(default=None, description="""boolean that indicates if the component is considered external or not.""", json_schema_extra = { "linkml_meta": {'domain': 'Component', 'domain_of': ['Component']} })


class FlexibleGenerationComponent(Component):
    """
    A component that generates energy to one connected energy vector.  Its generation can be controlled within a given bound
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/kees_lite.owl.ttl'})

    hasGenerationVector: Optional[str] = Field(default=None, description="""connected energy vector to which the component generates energy.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FixedGenerationComponent',
                       'FlexibleGenerationComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    hasMaxGeneration: Optional[float] = Field(default=None, description="""number indicating maximum energy generation in the connected energy vector in kW.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FlexibleGenerationComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    name: Optional[str] = Field(default=None, description="""string with short unique human-readable name of the component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    originalName: Optional[str] = Field(default=None, description="""string with the name assigned by configurator (should be ignored in most cases).""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    isExternal: Optional[bool] = Field(default=None, description="""boolean that indicates if the component is considered external or not.""", json_schema_extra = { "linkml_meta": {'domain': 'Component', 'domain_of': ['Component']} })


class InterconnectorComponent(Component):
    """
    A controllable component that consumes energy from one energy vector, transforms it with given efficiency, and generates the energy to another connected energy vector. For instance, heat pump or electrical transformer.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/kees_lite.owl.ttl'})

    hasGenerationVector: Optional[str] = Field(default=None, description="""connected energy vector to which the component generates energy.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FixedGenerationComponent',
                       'FlexibleGenerationComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    hasConsumptionVector: Optional[str] = Field(default=None, description="""connected energy vector from which the component consumes energy.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FixedConsumptionComponent',
                       'FlexibleConsumptionComponent',
                       'TimeFlexibleConsumptionComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    hasMaxGeneration: Optional[float] = Field(default=None, description="""number indicating maximum energy generation in the connected energy vector in kW.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FlexibleGenerationComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    hasMaxConsumption: Optional[float] = Field(default=None, description="""number indicating maximum energy consumption from the connected energy vector in kW.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FlexibleConsumptionComponent',
                       'TimeFlexibleConsumptionComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    hasEfficiency: Optional[float] = Field(default=None, description="""number indicating the efficiency of the energy conversion.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['InterconnectorComponent', 'StorageComponent']} })
    name: Optional[str] = Field(default=None, description="""string with short unique human-readable name of the component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    originalName: Optional[str] = Field(default=None, description="""string with the name assigned by configurator (should be ignored in most cases).""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    isExternal: Optional[bool] = Field(default=None, description="""boolean that indicates if the component is considered external or not.""", json_schema_extra = { "linkml_meta": {'domain': 'Component', 'domain_of': ['Component']} })


class StorageComponent(Component):
    """
    A component that can store energy and can consume and generate from/to an energy vector, e.g. a battery storage system.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/kees_lite.owl.ttl'})

    hasGenerationVector: Optional[str] = Field(default=None, description="""connected energy vector to which the component generates energy.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FixedGenerationComponent',
                       'FlexibleGenerationComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    hasConsumptionVector: Optional[str] = Field(default=None, description="""connected energy vector from which the component consumes energy.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FixedConsumptionComponent',
                       'FlexibleConsumptionComponent',
                       'TimeFlexibleConsumptionComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    hasMaxGeneration: Optional[float] = Field(default=None, description="""number indicating maximum energy generation in the connected energy vector in kW.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FlexibleGenerationComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    hasMaxConsumption: Optional[float] = Field(default=None, description="""number indicating maximum energy consumption from the connected energy vector in kW.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['FlexibleConsumptionComponent',
                       'TimeFlexibleConsumptionComponent',
                       'InterconnectorComponent',
                       'StorageComponent']} })
    hasEfficiency: Optional[float] = Field(default=None, description="""number indicating the efficiency of the energy conversion.""", json_schema_extra = { "linkml_meta": {'domain': 'Component',
         'domain_of': ['InterconnectorComponent', 'StorageComponent']} })
    hasInitialCapacity: Optional[float] = Field(default=None, description="""number indicating initial capacity of the storage, before first timestep in kWh.""", json_schema_extra = { "linkml_meta": {'domain': 'StorageComponent', 'domain_of': ['StorageComponent']} })
    hasMaxCapacity: Optional[float] = Field(default=None, description="""number indicating maximum capacity of the storage in kWh.""", json_schema_extra = { "linkml_meta": {'domain': 'StorageComponent', 'domain_of': ['StorageComponent']} })
    hasSelfDischarge: Optional[float] = Field(default=None, description="""number indicating the fraction of charge lost at each time step.""", json_schema_extra = { "linkml_meta": {'domain': 'StorageComponent', 'domain_of': ['StorageComponent']} })
    name: Optional[str] = Field(default=None, description="""string with short unique human-readable name of the component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    originalName: Optional[str] = Field(default=None, description="""string with the name assigned by configurator (should be ignored in most cases).""", json_schema_extra = { "linkml_meta": {'domain_of': ['EnergyVector', 'Component']} })
    isExternal: Optional[bool] = Field(default=None, description="""boolean that indicates if the component is considered external or not.""", json_schema_extra = { "linkml_meta": {'domain': 'Component', 'domain_of': ['Component']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Graph.model_rebuild()
EnergyVector.model_rebuild()
Component.model_rebuild()
FixedConsumptionComponent.model_rebuild()
FixedGenerationComponent.model_rebuild()
FlexibleConsumptionComponent.model_rebuild()
TimeFlexibleConsumptionComponent.model_rebuild()
FlexibleGenerationComponent.model_rebuild()
InterconnectorComponent.model_rebuild()
StorageComponent.model_rebuild()

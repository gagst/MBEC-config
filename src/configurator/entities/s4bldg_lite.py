# Auto generated from s4bldg_lite.yaml by pythongen.py version: 0.0.1
# Generation date: 2026-07-13T15:36:52
# Schema: s4bldg_lite
#
# id: https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/s4bldg_lite.owl.ttl
# description:
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import re
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union
)

from jsonasobj2 import (
    JsonObj,
    as_dict
)
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions
)
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import (
    camelcase,
    sfx,
    underscore
)
from linkml_runtime.utils.metamodelcore import (
    bnode,
    empty_dict,
    empty_list
)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str
)
from rdflib import (
    Namespace,
    URIRef
)

from linkml_runtime.linkml_model.types import Float, String

metamodel_version = "1.7.0"
version = None

# Namespaces
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
S4BLDG = CurieNamespace('s4bldg', 'https://saref.etsi.org/saref4bldg/')
S4BLDG_LITE = CurieNamespace('s4bldg_lite', 'https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/s4bldg_lite.owl.ttl/')
SAREF = CurieNamespace('saref', 'https://saref.etsi.org/core/')
UNIT = CurieNamespace('unit', 'https://qudt.org/vocab/unit/')
DEFAULT_ = S4BLDG


# Types

# Class references
class BuildingId(extended_str):
    pass


class BuildingSpaceId(extended_str):
    pass


class DeviceId(extended_str):
    pass


class BoilerId(DeviceId):
    pass


class SpaceHeaterId(DeviceId):
    pass


class ElectricApplianceId(DeviceId):
    pass


class FlowMeterId(DeviceId):
    pass


class SolarDeviceId(DeviceId):
    pass


class ElectricFlowStorageDeviceId(DeviceId):
    pass


class EnergyConversionDeviceId(DeviceId):
    pass


class TransformerId(DeviceId):
    pass


@dataclass(repr=False)
class SemanticDescription(YAMLRoot):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = S4BLDG_LITE["SemanticDescription"]
    class_class_curie: ClassVar[str] = "s4bldg_lite:SemanticDescription"
    class_name: ClassVar[str] = "SemanticDescription"
    class_model_uri: ClassVar[URIRef] = S4BLDG.SemanticDescription

    buildings: Optional[Union[list[Union[str, BuildingId]], dict[Union[str, BuildingId], Union[dict, "Building"]]]] = empty_dict()
    buildingSpaces: Optional[Union[dict[Union[str, BuildingSpaceId], Union[dict, "BuildingSpace"]], list[Union[dict, "BuildingSpace"]]]] = empty_dict()
    boilers: Optional[Union[dict[Union[str, BoilerId], Union[dict, "Boiler"]], list[Union[dict, "Boiler"]]]] = empty_dict()
    spaceHeaters: Optional[Union[dict[Union[str, SpaceHeaterId], Union[dict, "SpaceHeater"]], list[Union[dict, "SpaceHeater"]]]] = empty_dict()
    electricAppliances: Optional[Union[dict[Union[str, ElectricApplianceId], Union[dict, "ElectricAppliance"]], list[Union[dict, "ElectricAppliance"]]]] = empty_dict()
    flowMeters: Optional[Union[dict[Union[str, FlowMeterId], Union[dict, "FlowMeter"]], list[Union[dict, "FlowMeter"]]]] = empty_dict()
    solarDevices: Optional[Union[dict[Union[str, SolarDeviceId], Union[dict, "SolarDevice"]], list[Union[dict, "SolarDevice"]]]] = empty_dict()
    electricFlowStorageDevices: Optional[Union[dict[Union[str, ElectricFlowStorageDeviceId], Union[dict, "ElectricFlowStorageDevice"]], list[Union[dict, "ElectricFlowStorageDevice"]]]] = empty_dict()
    energyConversionDevices: Optional[Union[dict[Union[str, EnergyConversionDeviceId], Union[dict, "EnergyConversionDevice"]], list[Union[dict, "EnergyConversionDevice"]]]] = empty_dict()
    transformers: Optional[Union[dict[Union[str, TransformerId], Union[dict, "Transformer"]], list[Union[dict, "Transformer"]]]] = empty_dict()

    def __post_init__(self, *_: str, **kwargs: Any):
        self._normalize_inlined_as_list(slot_name="buildings", slot_type=Building, key_name="id", keyed=True)

        self._normalize_inlined_as_list(slot_name="buildingSpaces", slot_type=BuildingSpace, key_name="id", keyed=True)

        self._normalize_inlined_as_list(slot_name="boilers", slot_type=Boiler, key_name="id", keyed=True)

        self._normalize_inlined_as_list(slot_name="spaceHeaters", slot_type=SpaceHeater, key_name="id", keyed=True)

        self._normalize_inlined_as_list(slot_name="electricAppliances", slot_type=ElectricAppliance, key_name="id", keyed=True)

        self._normalize_inlined_as_list(slot_name="flowMeters", slot_type=FlowMeter, key_name="id", keyed=True)

        self._normalize_inlined_as_list(slot_name="solarDevices", slot_type=SolarDevice, key_name="id", keyed=True)

        self._normalize_inlined_as_list(slot_name="electricFlowStorageDevices", slot_type=ElectricFlowStorageDevice, key_name="id", keyed=True)

        self._normalize_inlined_as_list(slot_name="energyConversionDevices", slot_type=EnergyConversionDevice, key_name="id", keyed=True)

        self._normalize_inlined_as_list(slot_name="transformers", slot_type=Transformer, key_name="id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Building(YAMLRoot):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = S4BLDG["Building"]
    class_class_curie: ClassVar[str] = "s4bldg:Building"
    class_name: ClassVar[str] = "Building"
    class_model_uri: ClassVar[URIRef] = S4BLDG.Building

    id: Union[str, BuildingId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, BuildingId):
            self.id = BuildingId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BuildingSpace(YAMLRoot):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = S4BLDG["BuildingSpace"]
    class_class_curie: ClassVar[str] = "s4bldg:BuildingSpace"
    class_name: ClassVar[str] = "BuildingSpace"
    class_model_uri: ClassVar[URIRef] = S4BLDG.BuildingSpace

    id: Union[str, BuildingSpaceId] = None
    isSpaceOf: Optional[Union[str, BuildingId]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, BuildingSpaceId):
            self.id = BuildingSpaceId(self.id)

        if self.isSpaceOf is not None and not isinstance(self.isSpaceOf, BuildingId):
            self.isSpaceOf = BuildingId(self.isSpaceOf)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Device(YAMLRoot):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SAREF["Device"]
    class_class_curie: ClassVar[str] = "saref:Device"
    class_name: ClassVar[str] = "Device"
    class_model_uri: ClassVar[URIRef] = S4BLDG.Device

    id: Union[str, DeviceId] = None
    isContainedIn: Optional[Union[str, BuildingSpaceId]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, DeviceId):
            self.id = DeviceId(self.id)

        if self.isContainedIn is not None and not isinstance(self.isContainedIn, BuildingSpaceId):
            self.isContainedIn = BuildingSpaceId(self.isContainedIn)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Boiler(Device):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = S4BLDG["Boiler"]
    class_class_curie: ClassVar[str] = "s4bldg:Boiler"
    class_name: ClassVar[str] = "Boiler"
    class_model_uri: ClassVar[URIRef] = S4BLDG.Boiler

    id: Union[str, BoilerId] = None
    outputCapacity: Optional[Union[dict, "PropertyValue"]] = None
    nominalHeatingCapacity: Optional[Union[dict, "PropertyValue"]] = None
    nominalCapacity: Optional[Union[dict, "PropertyValue"]] = None
    nominalEnergyConsumption: Optional[Union[dict, "PropertyValue"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, BoilerId):
            self.id = BoilerId(self.id)

        if self.outputCapacity is not None and not isinstance(self.outputCapacity, PropertyValue):
            self.outputCapacity = PropertyValue(**as_dict(self.outputCapacity))

        if self.nominalHeatingCapacity is not None and not isinstance(self.nominalHeatingCapacity, PropertyValue):
            self.nominalHeatingCapacity = PropertyValue(**as_dict(self.nominalHeatingCapacity))

        if self.nominalCapacity is not None and not isinstance(self.nominalCapacity, PropertyValue):
            self.nominalCapacity = PropertyValue(**as_dict(self.nominalCapacity))

        if self.nominalEnergyConsumption is not None and not isinstance(self.nominalEnergyConsumption, PropertyValue):
            self.nominalEnergyConsumption = PropertyValue(**as_dict(self.nominalEnergyConsumption))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class SpaceHeater(Device):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = S4BLDG["SpaceHeater"]
    class_class_curie: ClassVar[str] = "s4bldg:SpaceHeater"
    class_name: ClassVar[str] = "SpaceHeater"
    class_model_uri: ClassVar[URIRef] = S4BLDG.SpaceHeater

    id: Union[str, SpaceHeaterId] = None
    outputCapacity: Optional[Union[dict, "PropertyValue"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, SpaceHeaterId):
            self.id = SpaceHeaterId(self.id)

        if self.outputCapacity is not None and not isinstance(self.outputCapacity, PropertyValue):
            self.outputCapacity = PropertyValue(**as_dict(self.outputCapacity))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ElectricAppliance(Device):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = S4BLDG["ElectricAppliance"]
    class_class_curie: ClassVar[str] = "s4bldg:ElectricAppliance"
    class_name: ClassVar[str] = "ElectricAppliance"
    class_model_uri: ClassVar[URIRef] = S4BLDG.ElectricAppliance

    id: Union[str, ElectricApplianceId] = None
    nominalCapacity: Optional[Union[dict, "PropertyValue"]] = None
    nominalPowerConsumption: Optional[Union[dict, "PropertyValue"]] = None
    nominalEnergyConsumption: Optional[Union[dict, "PropertyValue"]] = None
    apparentPowerMax: Optional[Union[dict, "PropertyValue"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ElectricApplianceId):
            self.id = ElectricApplianceId(self.id)

        if self.nominalCapacity is not None and not isinstance(self.nominalCapacity, PropertyValue):
            self.nominalCapacity = PropertyValue(**as_dict(self.nominalCapacity))

        if self.nominalPowerConsumption is not None and not isinstance(self.nominalPowerConsumption, PropertyValue):
            self.nominalPowerConsumption = PropertyValue(**as_dict(self.nominalPowerConsumption))

        if self.nominalEnergyConsumption is not None and not isinstance(self.nominalEnergyConsumption, PropertyValue):
            self.nominalEnergyConsumption = PropertyValue(**as_dict(self.nominalEnergyConsumption))

        if self.apparentPowerMax is not None and not isinstance(self.apparentPowerMax, PropertyValue):
            self.apparentPowerMax = PropertyValue(**as_dict(self.apparentPowerMax))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class FlowMeter(Device):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = S4BLDG["FlowMeter"]
    class_class_curie: ClassVar[str] = "s4bldg:FlowMeter"
    class_name: ClassVar[str] = "FlowMeter"
    class_model_uri: ClassVar[URIRef] = S4BLDG.FlowMeter

    id: Union[str, FlowMeterId] = None
    outputCapacity: Optional[Union[dict, "PropertyValue"]] = None
    nominalHeatingCapacity: Optional[Union[dict, "PropertyValue"]] = None
    nominalCapacity: Optional[Union[dict, "PropertyValue"]] = None
    nominalPowerConsumption: Optional[Union[dict, "PropertyValue"]] = None
    nominalEnergyConsumption: Optional[Union[dict, "PropertyValue"]] = None
    apparentPowerMax: Optional[Union[dict, "PropertyValue"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, FlowMeterId):
            self.id = FlowMeterId(self.id)

        if self.outputCapacity is not None and not isinstance(self.outputCapacity, PropertyValue):
            self.outputCapacity = PropertyValue(**as_dict(self.outputCapacity))

        if self.nominalHeatingCapacity is not None and not isinstance(self.nominalHeatingCapacity, PropertyValue):
            self.nominalHeatingCapacity = PropertyValue(**as_dict(self.nominalHeatingCapacity))

        if self.nominalCapacity is not None and not isinstance(self.nominalCapacity, PropertyValue):
            self.nominalCapacity = PropertyValue(**as_dict(self.nominalCapacity))

        if self.nominalPowerConsumption is not None and not isinstance(self.nominalPowerConsumption, PropertyValue):
            self.nominalPowerConsumption = PropertyValue(**as_dict(self.nominalPowerConsumption))

        if self.nominalEnergyConsumption is not None and not isinstance(self.nominalEnergyConsumption, PropertyValue):
            self.nominalEnergyConsumption = PropertyValue(**as_dict(self.nominalEnergyConsumption))

        if self.apparentPowerMax is not None and not isinstance(self.apparentPowerMax, PropertyValue):
            self.apparentPowerMax = PropertyValue(**as_dict(self.apparentPowerMax))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class SolarDevice(Device):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = S4BLDG["SolarDevice"]
    class_class_curie: ClassVar[str] = "s4bldg:SolarDevice"
    class_name: ClassVar[str] = "SolarDevice"
    class_model_uri: ClassVar[URIRef] = S4BLDG.SolarDevice

    id: Union[str, SolarDeviceId] = None
    nominalCapacity: Optional[Union[dict, "PropertyValue"]] = None
    apparentPowerMax: Optional[Union[dict, "PropertyValue"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, SolarDeviceId):
            self.id = SolarDeviceId(self.id)

        if self.nominalCapacity is not None and not isinstance(self.nominalCapacity, PropertyValue):
            self.nominalCapacity = PropertyValue(**as_dict(self.nominalCapacity))

        if self.apparentPowerMax is not None and not isinstance(self.apparentPowerMax, PropertyValue):
            self.apparentPowerMax = PropertyValue(**as_dict(self.apparentPowerMax))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ElectricFlowStorageDevice(Device):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = S4BLDG["ElectricFlowStorageDevice"]
    class_class_curie: ClassVar[str] = "s4bldg:ElectricFlowStorageDevice"
    class_name: ClassVar[str] = "ElectricFlowStorageDevice"
    class_model_uri: ClassVar[URIRef] = S4BLDG.ElectricFlowStorageDevice

    id: Union[str, ElectricFlowStorageDeviceId] = None
    nominalCapacity: Optional[Union[dict, "PropertyValue"]] = None
    nominalPowerConsumption: Optional[Union[dict, "PropertyValue"]] = None
    nominalEnergyConsumption: Optional[Union[dict, "PropertyValue"]] = None
    apparentPowerMax: Optional[Union[dict, "PropertyValue"]] = None
    storageType: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ElectricFlowStorageDeviceId):
            self.id = ElectricFlowStorageDeviceId(self.id)

        if self.nominalCapacity is not None and not isinstance(self.nominalCapacity, PropertyValue):
            self.nominalCapacity = PropertyValue(**as_dict(self.nominalCapacity))

        if self.nominalPowerConsumption is not None and not isinstance(self.nominalPowerConsumption, PropertyValue):
            self.nominalPowerConsumption = PropertyValue(**as_dict(self.nominalPowerConsumption))

        if self.nominalEnergyConsumption is not None and not isinstance(self.nominalEnergyConsumption, PropertyValue):
            self.nominalEnergyConsumption = PropertyValue(**as_dict(self.nominalEnergyConsumption))

        if self.apparentPowerMax is not None and not isinstance(self.apparentPowerMax, PropertyValue):
            self.apparentPowerMax = PropertyValue(**as_dict(self.apparentPowerMax))

        if self.storageType is not None and not isinstance(self.storageType, str):
            self.storageType = str(self.storageType)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class EnergyConversionDevice(Device):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = S4BLDG["EnergyConversionDevice"]
    class_class_curie: ClassVar[str] = "s4bldg:EnergyConversionDevice"
    class_name: ClassVar[str] = "EnergyConversionDevice"
    class_model_uri: ClassVar[URIRef] = S4BLDG.EnergyConversionDevice

    id: Union[str, EnergyConversionDeviceId] = None
    outputCapacity: Optional[Union[dict, "PropertyValue"]] = None
    nominalHeatingCapacity: Optional[Union[dict, "PropertyValue"]] = None
    nominalCapacity: Optional[Union[dict, "PropertyValue"]] = None
    nominalPowerConsumption: Optional[Union[dict, "PropertyValue"]] = None
    nominalEnergyConsumption: Optional[Union[dict, "PropertyValue"]] = None
    apparentPowerMax: Optional[Union[dict, "PropertyValue"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, EnergyConversionDeviceId):
            self.id = EnergyConversionDeviceId(self.id)

        if self.outputCapacity is not None and not isinstance(self.outputCapacity, PropertyValue):
            self.outputCapacity = PropertyValue(**as_dict(self.outputCapacity))

        if self.nominalHeatingCapacity is not None and not isinstance(self.nominalHeatingCapacity, PropertyValue):
            self.nominalHeatingCapacity = PropertyValue(**as_dict(self.nominalHeatingCapacity))

        if self.nominalCapacity is not None and not isinstance(self.nominalCapacity, PropertyValue):
            self.nominalCapacity = PropertyValue(**as_dict(self.nominalCapacity))

        if self.nominalPowerConsumption is not None and not isinstance(self.nominalPowerConsumption, PropertyValue):
            self.nominalPowerConsumption = PropertyValue(**as_dict(self.nominalPowerConsumption))

        if self.nominalEnergyConsumption is not None and not isinstance(self.nominalEnergyConsumption, PropertyValue):
            self.nominalEnergyConsumption = PropertyValue(**as_dict(self.nominalEnergyConsumption))

        if self.apparentPowerMax is not None and not isinstance(self.apparentPowerMax, PropertyValue):
            self.apparentPowerMax = PropertyValue(**as_dict(self.apparentPowerMax))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Transformer(Device):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = S4BLDG["Transformer"]
    class_class_curie: ClassVar[str] = "s4bldg:Transformer"
    class_name: ClassVar[str] = "Transformer"
    class_model_uri: ClassVar[URIRef] = S4BLDG.Transformer

    id: Union[str, TransformerId] = None
    outputCapacity: Optional[Union[dict, "PropertyValue"]] = None
    nominalCapacity: Optional[Union[dict, "PropertyValue"]] = None
    apparentPowerMax: Optional[Union[dict, "PropertyValue"]] = None
    primaryApparentPower: Optional[Union[dict, "PropertyValue"]] = None
    secondaryApparentPower: Optional[Union[dict, "PropertyValue"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, TransformerId):
            self.id = TransformerId(self.id)

        if self.outputCapacity is not None and not isinstance(self.outputCapacity, PropertyValue):
            self.outputCapacity = PropertyValue(**as_dict(self.outputCapacity))

        if self.nominalCapacity is not None and not isinstance(self.nominalCapacity, PropertyValue):
            self.nominalCapacity = PropertyValue(**as_dict(self.nominalCapacity))

        if self.apparentPowerMax is not None and not isinstance(self.apparentPowerMax, PropertyValue):
            self.apparentPowerMax = PropertyValue(**as_dict(self.apparentPowerMax))

        if self.primaryApparentPower is not None and not isinstance(self.primaryApparentPower, PropertyValue):
            self.primaryApparentPower = PropertyValue(**as_dict(self.primaryApparentPower))

        if self.secondaryApparentPower is not None and not isinstance(self.secondaryApparentPower, PropertyValue):
            self.secondaryApparentPower = PropertyValue(**as_dict(self.secondaryApparentPower))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class PropertyValue(YAMLRoot):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = SAREF["PropertyValue"]
    class_class_curie: ClassVar[str] = "saref:PropertyValue"
    class_name: ClassVar[str] = "PropertyValue"
    class_model_uri: ClassVar[URIRef] = S4BLDG.PropertyValue

    hasValue: Optional[float] = None
    isMeasuredIn: Optional[Union[str, "Units"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.hasValue is not None and not isinstance(self.hasValue, float):
            self.hasValue = float(self.hasValue)

        if self.isMeasuredIn is not None and not isinstance(self.isMeasuredIn, Units):
            self.isMeasuredIn = Units(self.isMeasuredIn)

        super().__post_init__(**kwargs)


# Enumerations
class Units(EnumDefinitionImpl):

    KW = PermissibleValue(
        text="KW",
        meaning=UNIT["KiloW"])
    KWH = PermissibleValue(
        text="KWH",
        meaning=UNIT["KiloW-HR"])

    _defn = EnumDefinition(
        name="Units",
    )

# Slots
class slots:
    pass

slots.id = Slot(uri=S4BLDG.id, name="id", curie=S4BLDG.curie('id'),
                   model_uri=S4BLDG.id, domain=None, range=URIRef)

slots.isSpaceOf = Slot(uri=S4BLDG.isSpaceOf, name="isSpaceOf", curie=S4BLDG.curie('isSpaceOf'),
                   model_uri=S4BLDG.isSpaceOf, domain=BuildingSpace, range=Optional[Union[str, BuildingId]])

slots.isContainedIn = Slot(uri=S4BLDG.isContainedIn, name="isContainedIn", curie=S4BLDG.curie('isContainedIn'),
                   model_uri=S4BLDG.isContainedIn, domain=None, range=Optional[Union[str, BuildingSpaceId]])

slots.hasValue = Slot(uri=SAREF.hasValue, name="hasValue", curie=SAREF.curie('hasValue'),
                   model_uri=S4BLDG.hasValue, domain=None, range=Optional[float])

slots.isMeasuredIn = Slot(uri=SAREF.isMeasuredIn, name="isMeasuredIn", curie=SAREF.curie('isMeasuredIn'),
                   model_uri=S4BLDG.isMeasuredIn, domain=None, range=Optional[Union[str, "Units"]])

slots.outputCapacity = Slot(uri=S4BLDG.outputCapacity, name="outputCapacity", curie=S4BLDG.curie('outputCapacity'),
                   model_uri=S4BLDG.outputCapacity, domain=None, range=Optional[Union[dict, PropertyValue]])

slots.nominalHeatingCapacity = Slot(uri=S4BLDG.nominalHeatingCapacity, name="nominalHeatingCapacity", curie=S4BLDG.curie('nominalHeatingCapacity'),
                   model_uri=S4BLDG.nominalHeatingCapacity, domain=None, range=Optional[Union[dict, PropertyValue]])

slots.nominalCapacity = Slot(uri=S4BLDG.nominalCapacity, name="nominalCapacity", curie=S4BLDG.curie('nominalCapacity'),
                   model_uri=S4BLDG.nominalCapacity, domain=None, range=Optional[Union[dict, PropertyValue]])

slots.nominalPowerConsumption = Slot(uri=S4BLDG.nominalPowerConsumption, name="nominalPowerConsumption", curie=S4BLDG.curie('nominalPowerConsumption'),
                   model_uri=S4BLDG.nominalPowerConsumption, domain=None, range=Optional[Union[dict, PropertyValue]])

slots.nominalEnergyConsumption = Slot(uri=S4BLDG.nominalEnergyConsumption, name="nominalEnergyConsumption", curie=S4BLDG.curie('nominalEnergyConsumption'),
                   model_uri=S4BLDG.nominalEnergyConsumption, domain=None, range=Optional[Union[dict, PropertyValue]])

slots.apparentPowerMax = Slot(uri=S4BLDG.apparentPowerMax, name="apparentPowerMax", curie=S4BLDG.curie('apparentPowerMax'),
                   model_uri=S4BLDG.apparentPowerMax, domain=None, range=Optional[Union[dict, PropertyValue]])

slots.storageType = Slot(uri=S4BLDG.storageType, name="storageType", curie=S4BLDG.curie('storageType'),
                   model_uri=S4BLDG.storageType, domain=None, range=Optional[str])

slots.primaryApparentPower = Slot(uri=S4BLDG.primaryApparentPower, name="primaryApparentPower", curie=S4BLDG.curie('primaryApparentPower'),
                   model_uri=S4BLDG.primaryApparentPower, domain=None, range=Optional[Union[dict, PropertyValue]])

slots.secondaryApparentPower = Slot(uri=S4BLDG.secondaryApparentPower, name="secondaryApparentPower", curie=S4BLDG.curie('secondaryApparentPower'),
                   model_uri=S4BLDG.secondaryApparentPower, domain=None, range=Optional[Union[dict, PropertyValue]])

slots.semanticDescription__buildings = Slot(uri=S4BLDG.buildings, name="semanticDescription__buildings", curie=S4BLDG.curie('buildings'),
                   model_uri=S4BLDG.semanticDescription__buildings, domain=None, range=Optional[Union[list[Union[str, BuildingId]], dict[Union[str, BuildingId], Union[dict, Building]]]])

slots.semanticDescription__buildingSpaces = Slot(uri=S4BLDG.buildingSpaces, name="semanticDescription__buildingSpaces", curie=S4BLDG.curie('buildingSpaces'),
                   model_uri=S4BLDG.semanticDescription__buildingSpaces, domain=None, range=Optional[Union[dict[Union[str, BuildingSpaceId], Union[dict, BuildingSpace]], list[Union[dict, BuildingSpace]]]])

slots.semanticDescription__boilers = Slot(uri=S4BLDG.boilers, name="semanticDescription__boilers", curie=S4BLDG.curie('boilers'),
                   model_uri=S4BLDG.semanticDescription__boilers, domain=None, range=Optional[Union[dict[Union[str, BoilerId], Union[dict, Boiler]], list[Union[dict, Boiler]]]])

slots.semanticDescription__spaceHeaters = Slot(uri=S4BLDG.spaceHeaters, name="semanticDescription__spaceHeaters", curie=S4BLDG.curie('spaceHeaters'),
                   model_uri=S4BLDG.semanticDescription__spaceHeaters, domain=None, range=Optional[Union[dict[Union[str, SpaceHeaterId], Union[dict, SpaceHeater]], list[Union[dict, SpaceHeater]]]])

slots.semanticDescription__electricAppliances = Slot(uri=S4BLDG.electricAppliances, name="semanticDescription__electricAppliances", curie=S4BLDG.curie('electricAppliances'),
                   model_uri=S4BLDG.semanticDescription__electricAppliances, domain=None, range=Optional[Union[dict[Union[str, ElectricApplianceId], Union[dict, ElectricAppliance]], list[Union[dict, ElectricAppliance]]]])

slots.semanticDescription__flowMeters = Slot(uri=S4BLDG.flowMeters, name="semanticDescription__flowMeters", curie=S4BLDG.curie('flowMeters'),
                   model_uri=S4BLDG.semanticDescription__flowMeters, domain=None, range=Optional[Union[dict[Union[str, FlowMeterId], Union[dict, FlowMeter]], list[Union[dict, FlowMeter]]]])

slots.semanticDescription__solarDevices = Slot(uri=S4BLDG.solarDevices, name="semanticDescription__solarDevices", curie=S4BLDG.curie('solarDevices'),
                   model_uri=S4BLDG.semanticDescription__solarDevices, domain=None, range=Optional[Union[dict[Union[str, SolarDeviceId], Union[dict, SolarDevice]], list[Union[dict, SolarDevice]]]])

slots.semanticDescription__electricFlowStorageDevices = Slot(uri=S4BLDG.electricFlowStorageDevices, name="semanticDescription__electricFlowStorageDevices", curie=S4BLDG.curie('electricFlowStorageDevices'),
                   model_uri=S4BLDG.semanticDescription__electricFlowStorageDevices, domain=None, range=Optional[Union[dict[Union[str, ElectricFlowStorageDeviceId], Union[dict, ElectricFlowStorageDevice]], list[Union[dict, ElectricFlowStorageDevice]]]])

slots.semanticDescription__energyConversionDevices = Slot(uri=S4BLDG.energyConversionDevices, name="semanticDescription__energyConversionDevices", curie=S4BLDG.curie('energyConversionDevices'),
                   model_uri=S4BLDG.semanticDescription__energyConversionDevices, domain=None, range=Optional[Union[dict[Union[str, EnergyConversionDeviceId], Union[dict, EnergyConversionDevice]], list[Union[dict, EnergyConversionDevice]]]])

slots.semanticDescription__transformers = Slot(uri=S4BLDG.transformers, name="semanticDescription__transformers", curie=S4BLDG.curie('transformers'),
                   model_uri=S4BLDG.semanticDescription__transformers, domain=None, range=Optional[Union[dict[Union[str, TransformerId], Union[dict, Transformer]], list[Union[dict, Transformer]]]])


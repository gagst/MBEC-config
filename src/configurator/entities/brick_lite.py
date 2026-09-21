# Auto generated from brick_lite.yaml by pythongen.py version: 0.0.1
# Generation date: 2026-07-13T15:36:53
# Schema: brick_lite
#
# id: https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/brick_lite.owl.ttl
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
BRICK = CurieNamespace('brick', 'https://brickschema.org/schema/Brick#')
BRICK_LITE = CurieNamespace('brick_lite', 'https://raw.githubusercontent.com/gagst/MBEC-config/main/ontologies/brick_lite.owl.ttl/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
REC = CurieNamespace('rec', 'https://w3id.org/rec#')
UNIT = CurieNamespace('unit', 'https://qudt.org/vocab/unit/')
DEFAULT_ = BRICK


# Types

# Class references
class LoopId(extended_str):
    pass


class HotWaterLoopId(LoopId):
    pass


class SystemId(extended_str):
    pass


class DomesticHotWaterSystemId(SystemId):
    pass


class ElectricalSystemId(SystemId):
    pass


class EnergySystemId(ElectricalSystemId):
    pass


class EnergyGenerationSystemId(EnergySystemId):
    pass


class PVGenerationSystemId(EnergyGenerationSystemId):
    pass


class EnergyStorageSystemId(EnergySystemId):
    pass


class BatteryEnergyStorageSystemId(EnergyStorageSystemId):
    pass


class HotWaterSystemId(SystemId):
    pass


class EquipmentId(extended_str):
    pass


class BoilerId(EquipmentId):
    pass


class ElectricalEquipmentId(EquipmentId):
    pass


class TransformerId(EquipmentId):
    pass


class ElectricVehicleChargingStationId(EquipmentId):
    pass


class BatteryId(EquipmentId):
    pass


class PVPanelId(EquipmentId):
    pass


class PackagedHeatPumpId(EquipmentId):
    pass


class ElectricalMeterId(EquipmentId):
    pass


class HotWaterMeterId(EquipmentId):
    pass


class BuildingElectricalMeterId(ElectricalMeterId):
    pass


class BuildingHotWaterMeterId(HotWaterMeterId):
    pass


class BuildingId(extended_str):
    pass


@dataclass(repr=False)
class SemanticDescription(YAMLRoot):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK_LITE["SemanticDescription"]
    class_class_curie: ClassVar[str] = "brick_lite:SemanticDescription"
    class_name: ClassVar[str] = "SemanticDescription"
    class_model_uri: ClassVar[URIRef] = BRICK.SemanticDescription

    loops: Optional[Union[dict[Union[str, LoopId], Union[dict, "Loop"]], list[Union[dict, "Loop"]]]] = empty_dict()
    systems: Optional[Union[dict[Union[str, SystemId], Union[dict, "System"]], list[Union[dict, "System"]]]] = empty_dict()
    buildings: Optional[Union[list[Union[str, BuildingId]], dict[Union[str, BuildingId], Union[dict, "Building"]]]] = empty_dict()
    equipment: Optional[Union[dict[Union[str, EquipmentId], Union[dict, "Equipment"]], list[Union[dict, "Equipment"]]]] = empty_dict()

    def __post_init__(self, *_: str, **kwargs: Any):
        self._normalize_inlined_as_list(slot_name="loops", slot_type=Loop, key_name="id", keyed=True)

        self._normalize_inlined_as_list(slot_name="systems", slot_type=System, key_name="id", keyed=True)

        self._normalize_inlined_as_list(slot_name="buildings", slot_type=Building, key_name="id", keyed=True)

        self._normalize_inlined_as_list(slot_name="equipment", slot_type=Equipment, key_name="id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Loop(YAMLRoot):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Loop"]
    class_class_curie: ClassVar[str] = "brick:Loop"
    class_name: ClassVar[str] = "Loop"
    class_model_uri: ClassVar[URIRef] = BRICK.Loop

    id: Union[str, LoopId] = None
    hasPart: Optional[Union[dict[Union[str, EquipmentId], Union[dict, "Equipment"]], list[Union[dict, "Equipment"]]]] = empty_dict()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, LoopId):
            self.id = LoopId(self.id)

        self._normalize_inlined_as_list(slot_name="hasPart", slot_type=Equipment, key_name="id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HotWaterLoop(Loop):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Hot_Water_Loop"]
    class_class_curie: ClassVar[str] = "brick:Hot_Water_Loop"
    class_name: ClassVar[str] = "HotWaterLoop"
    class_model_uri: ClassVar[URIRef] = BRICK.HotWaterLoop

    id: Union[str, HotWaterLoopId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, HotWaterLoopId):
            self.id = HotWaterLoopId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class System(YAMLRoot):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["System"]
    class_class_curie: ClassVar[str] = "brick:System"
    class_name: ClassVar[str] = "System"
    class_model_uri: ClassVar[URIRef] = BRICK.System

    id: Union[str, SystemId] = None
    hasPart: Optional[Union[dict[Union[str, EquipmentId], Union[dict, "Equipment"]], list[Union[dict, "Equipment"]]]] = empty_dict()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, SystemId):
            self.id = SystemId(self.id)

        self._normalize_inlined_as_list(slot_name="hasPart", slot_type=Equipment, key_name="id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DomesticHotWaterSystem(System):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Domestic_Hot_Water_System"]
    class_class_curie: ClassVar[str] = "brick:Domestic_Hot_Water_System"
    class_name: ClassVar[str] = "DomesticHotWaterSystem"
    class_model_uri: ClassVar[URIRef] = BRICK.DomesticHotWaterSystem

    id: Union[str, DomesticHotWaterSystemId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, DomesticHotWaterSystemId):
            self.id = DomesticHotWaterSystemId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ElectricalSystem(System):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Electrical_System"]
    class_class_curie: ClassVar[str] = "brick:Electrical_System"
    class_name: ClassVar[str] = "ElectricalSystem"
    class_model_uri: ClassVar[URIRef] = BRICK.ElectricalSystem

    id: Union[str, ElectricalSystemId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ElectricalSystemId):
            self.id = ElectricalSystemId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class EnergySystem(ElectricalSystem):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Energy_System"]
    class_class_curie: ClassVar[str] = "brick:Energy_System"
    class_name: ClassVar[str] = "EnergySystem"
    class_model_uri: ClassVar[URIRef] = BRICK.EnergySystem

    id: Union[str, EnergySystemId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, EnergySystemId):
            self.id = EnergySystemId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class EnergyGenerationSystem(EnergySystem):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Energy_Generation_System"]
    class_class_curie: ClassVar[str] = "brick:Energy_Generation_System"
    class_name: ClassVar[str] = "EnergyGenerationSystem"
    class_model_uri: ClassVar[URIRef] = BRICK.EnergyGenerationSystem

    id: Union[str, EnergyGenerationSystemId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, EnergyGenerationSystemId):
            self.id = EnergyGenerationSystemId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class PVGenerationSystem(EnergyGenerationSystem):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["PV_Generation_System"]
    class_class_curie: ClassVar[str] = "brick:PV_Generation_System"
    class_name: ClassVar[str] = "PVGenerationSystem"
    class_model_uri: ClassVar[URIRef] = BRICK.PVGenerationSystem

    id: Union[str, PVGenerationSystemId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, PVGenerationSystemId):
            self.id = PVGenerationSystemId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class EnergyStorageSystem(EnergySystem):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Energy_Storage_System"]
    class_class_curie: ClassVar[str] = "brick:Energy_Storage_System"
    class_name: ClassVar[str] = "EnergyStorageSystem"
    class_model_uri: ClassVar[URIRef] = BRICK.EnergyStorageSystem

    id: Union[str, EnergyStorageSystemId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, EnergyStorageSystemId):
            self.id = EnergyStorageSystemId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BatteryEnergyStorageSystem(EnergyStorageSystem):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Battery_Energy_Storage_System"]
    class_class_curie: ClassVar[str] = "brick:Battery_Energy_Storage_System"
    class_name: ClassVar[str] = "BatteryEnergyStorageSystem"
    class_model_uri: ClassVar[URIRef] = BRICK.BatteryEnergyStorageSystem

    id: Union[str, BatteryEnergyStorageSystemId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, BatteryEnergyStorageSystemId):
            self.id = BatteryEnergyStorageSystemId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HotWaterSystem(System):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Hot_Water_System"]
    class_class_curie: ClassVar[str] = "brick:Hot_Water_System"
    class_name: ClassVar[str] = "HotWaterSystem"
    class_model_uri: ClassVar[URIRef] = BRICK.HotWaterSystem

    id: Union[str, HotWaterSystemId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, HotWaterSystemId):
            self.id = HotWaterSystemId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Equipment(YAMLRoot):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Equipment"]
    class_class_curie: ClassVar[str] = "brick:Equipment"
    class_name: ClassVar[str] = "Equipment"
    class_model_uri: ClassVar[URIRef] = BRICK.Equipment

    id: Union[str, EquipmentId] = None
    hasPart: Optional[Union[dict[Union[str, EquipmentId], Union[dict, "Equipment"]], list[Union[dict, "Equipment"]]]] = empty_dict()
    hasLocation: Optional[Union[str, BuildingId]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, EquipmentId):
            self.id = EquipmentId(self.id)

        self._normalize_inlined_as_list(slot_name="hasPart", slot_type=Equipment, key_name="id", keyed=True)

        if self.hasLocation is not None and not isinstance(self.hasLocation, BuildingId):
            self.hasLocation = BuildingId(self.hasLocation)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Boiler(Equipment):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Boiler"]
    class_class_curie: ClassVar[str] = "brick:Boiler"
    class_name: ClassVar[str] = "Boiler"
    class_model_uri: ClassVar[URIRef] = BRICK.Boiler

    id: Union[str, BoilerId] = None
    ratedPowerOutput: Optional[Union[dict, "PropValue"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, BoilerId):
            self.id = BoilerId(self.id)

        if self.ratedPowerOutput is not None and not isinstance(self.ratedPowerOutput, PropValue):
            self.ratedPowerOutput = PropValue(**as_dict(self.ratedPowerOutput))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ElectricalEquipment(Equipment):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Electrical_Equipment"]
    class_class_curie: ClassVar[str] = "brick:Electrical_Equipment"
    class_name: ClassVar[str] = "ElectricalEquipment"
    class_model_uri: ClassVar[URIRef] = BRICK.ElectricalEquipment

    id: Union[str, ElectricalEquipmentId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ElectricalEquipmentId):
            self.id = ElectricalEquipmentId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Transformer(Equipment):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Transformer"]
    class_class_curie: ClassVar[str] = "brick:Transformer"
    class_name: ClassVar[str] = "Transformer"
    class_model_uri: ClassVar[URIRef] = BRICK.Transformer

    id: Union[str, TransformerId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, TransformerId):
            self.id = TransformerId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ElectricVehicleChargingStation(Equipment):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Electric_Vehicle_Charging_Station"]
    class_class_curie: ClassVar[str] = "brick:Electric_Vehicle_Charging_Station"
    class_name: ClassVar[str] = "ElectricVehicleChargingStation"
    class_model_uri: ClassVar[URIRef] = BRICK.ElectricVehicleChargingStation

    id: Union[str, ElectricVehicleChargingStationId] = None
    electricVehicleChargerDirectionality: Optional[Union[dict, "PropValue"]] = None
    ratedPowerInput: Optional[Union[dict, "PropValue"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ElectricVehicleChargingStationId):
            self.id = ElectricVehicleChargingStationId(self.id)

        if self.electricVehicleChargerDirectionality is not None and not isinstance(self.electricVehicleChargerDirectionality, PropValue):
            self.electricVehicleChargerDirectionality = PropValue(**as_dict(self.electricVehicleChargerDirectionality))

        if self.ratedPowerInput is not None and not isinstance(self.ratedPowerInput, PropValue):
            self.ratedPowerInput = PropValue(**as_dict(self.ratedPowerInput))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Battery(Equipment):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Battery"]
    class_class_curie: ClassVar[str] = "brick:Battery"
    class_name: ClassVar[str] = "Battery"
    class_model_uri: ClassVar[URIRef] = BRICK.Battery

    id: Union[str, BatteryId] = None
    ratedPowerInput: Optional[Union[dict, "PropValue"]] = None
    ratedPowerOutput: Optional[Union[dict, "PropValue"]] = None
    conversionEfficiency: Optional[Union[dict, "PropValue"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, BatteryId):
            self.id = BatteryId(self.id)

        if self.ratedPowerInput is not None and not isinstance(self.ratedPowerInput, PropValue):
            self.ratedPowerInput = PropValue(**as_dict(self.ratedPowerInput))

        if self.ratedPowerOutput is not None and not isinstance(self.ratedPowerOutput, PropValue):
            self.ratedPowerOutput = PropValue(**as_dict(self.ratedPowerOutput))

        if self.conversionEfficiency is not None and not isinstance(self.conversionEfficiency, PropValue):
            self.conversionEfficiency = PropValue(**as_dict(self.conversionEfficiency))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class PVPanel(Equipment):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["PV_Panel"]
    class_class_curie: ClassVar[str] = "brick:PV_Panel"
    class_name: ClassVar[str] = "PVPanel"
    class_model_uri: ClassVar[URIRef] = BRICK.PVPanel

    id: Union[str, PVPanelId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, PVPanelId):
            self.id = PVPanelId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class PackagedHeatPump(Equipment):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Packaged_Heat_Pump"]
    class_class_curie: ClassVar[str] = "brick:Packaged_Heat_Pump"
    class_name: ClassVar[str] = "PackagedHeatPump"
    class_model_uri: ClassVar[URIRef] = BRICK.PackagedHeatPump

    id: Union[str, PackagedHeatPumpId] = None
    ratedPowerInput: Optional[Union[dict, "PropValue"]] = None
    ratedPowerOutput: Optional[Union[dict, "PropValue"]] = None
    conversionEfficiency: Optional[Union[dict, "PropValue"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, PackagedHeatPumpId):
            self.id = PackagedHeatPumpId(self.id)

        if self.ratedPowerInput is not None and not isinstance(self.ratedPowerInput, PropValue):
            self.ratedPowerInput = PropValue(**as_dict(self.ratedPowerInput))

        if self.ratedPowerOutput is not None and not isinstance(self.ratedPowerOutput, PropValue):
            self.ratedPowerOutput = PropValue(**as_dict(self.ratedPowerOutput))

        if self.conversionEfficiency is not None and not isinstance(self.conversionEfficiency, PropValue):
            self.conversionEfficiency = PropValue(**as_dict(self.conversionEfficiency))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ElectricalMeter(Equipment):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Electrical_Meter"]
    class_class_curie: ClassVar[str] = "brick:Electrical_Meter"
    class_name: ClassVar[str] = "ElectricalMeter"
    class_model_uri: ClassVar[URIRef] = BRICK.ElectricalMeter

    id: Union[str, ElectricalMeterId] = None
    ratedPowerInput: Optional[Union[dict, "PropValue"]] = None
    ratedPowerOutput: Optional[Union[dict, "PropValue"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ElectricalMeterId):
            self.id = ElectricalMeterId(self.id)

        if self.ratedPowerInput is not None and not isinstance(self.ratedPowerInput, PropValue):
            self.ratedPowerInput = PropValue(**as_dict(self.ratedPowerInput))

        if self.ratedPowerOutput is not None and not isinstance(self.ratedPowerOutput, PropValue):
            self.ratedPowerOutput = PropValue(**as_dict(self.ratedPowerOutput))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HotWaterMeter(Equipment):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Hot_Water_Meter"]
    class_class_curie: ClassVar[str] = "brick:Hot_Water_Meter"
    class_name: ClassVar[str] = "HotWaterMeter"
    class_model_uri: ClassVar[URIRef] = BRICK.HotWaterMeter

    id: Union[str, HotWaterMeterId] = None
    ratedPowerInput: Optional[Union[dict, "PropValue"]] = None
    ratedPowerOutput: Optional[Union[dict, "PropValue"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, HotWaterMeterId):
            self.id = HotWaterMeterId(self.id)

        if self.ratedPowerInput is not None and not isinstance(self.ratedPowerInput, PropValue):
            self.ratedPowerInput = PropValue(**as_dict(self.ratedPowerInput))

        if self.ratedPowerOutput is not None and not isinstance(self.ratedPowerOutput, PropValue):
            self.ratedPowerOutput = PropValue(**as_dict(self.ratedPowerOutput))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BuildingElectricalMeter(ElectricalMeter):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Building_Electrical_Meter"]
    class_class_curie: ClassVar[str] = "brick:Building_Electrical_Meter"
    class_name: ClassVar[str] = "BuildingElectricalMeter"
    class_model_uri: ClassVar[URIRef] = BRICK.BuildingElectricalMeter

    id: Union[str, BuildingElectricalMeterId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, BuildingElectricalMeterId):
            self.id = BuildingElectricalMeterId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BuildingHotWaterMeter(HotWaterMeter):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["Building_Hot_Water_Meter"]
    class_class_curie: ClassVar[str] = "brick:Building_Hot_Water_Meter"
    class_name: ClassVar[str] = "BuildingHotWaterMeter"
    class_model_uri: ClassVar[URIRef] = BRICK.BuildingHotWaterMeter

    id: Union[str, BuildingHotWaterMeterId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, BuildingHotWaterMeterId):
            self.id = BuildingHotWaterMeterId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Building(YAMLRoot):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = REC["Building"]
    class_class_curie: ClassVar[str] = "rec:Building"
    class_name: ClassVar[str] = "Building"
    class_model_uri: ClassVar[URIRef] = BRICK.Building

    id: Union[str, BuildingId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, BuildingId):
            self.id = BuildingId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class PropValue(YAMLRoot):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = BRICK["PropValue"]
    class_class_curie: ClassVar[str] = "brick:PropValue"
    class_name: ClassVar[str] = "PropValue"
    class_model_uri: ClassVar[URIRef] = BRICK.PropValue

    value: Optional[float] = None
    hasUnit: Optional[Union[str, "Units"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.value is not None and not isinstance(self.value, float):
            self.value = float(self.value)

        if self.hasUnit is not None and not isinstance(self.hasUnit, Units):
            self.hasUnit = Units(self.hasUnit)

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

slots.id = Slot(uri=BRICK.id, name="id", curie=BRICK.curie('id'),
                   model_uri=BRICK.id, domain=None, range=URIRef)

slots.value = Slot(uri=BRICK.value, name="value", curie=BRICK.curie('value'),
                   model_uri=BRICK.value, domain=None, range=Optional[float])

slots.hasUnit = Slot(uri=BRICK.hasUnit, name="hasUnit", curie=BRICK.curie('hasUnit'),
                   model_uri=BRICK.hasUnit, domain=None, range=Optional[Union[str, "Units"]])

slots.hasPart = Slot(uri=BRICK.hasPart, name="hasPart", curie=BRICK.curie('hasPart'),
                   model_uri=BRICK.hasPart, domain=None, range=Optional[Union[dict[Union[str, EquipmentId], Union[dict, Equipment]], list[Union[dict, Equipment]]]])

slots.hasLocation = Slot(uri=BRICK.hasLocation, name="hasLocation", curie=BRICK.curie('hasLocation'),
                   model_uri=BRICK.hasLocation, domain=None, range=Optional[Union[str, BuildingId]])

slots.ratedPowerOutput = Slot(uri=BRICK.ratedPowerOutput, name="ratedPowerOutput", curie=BRICK.curie('ratedPowerOutput'),
                   model_uri=BRICK.ratedPowerOutput, domain=None, range=Optional[Union[dict, PropValue]])

slots.ratedPowerInput = Slot(uri=BRICK.ratedPowerInput, name="ratedPowerInput", curie=BRICK.curie('ratedPowerInput'),
                   model_uri=BRICK.ratedPowerInput, domain=None, range=Optional[Union[dict, PropValue]])

slots.electricVehicleChargerDirectionality = Slot(uri=BRICK.electricVehicleChargerDirectionality, name="electricVehicleChargerDirectionality", curie=BRICK.curie('electricVehicleChargerDirectionality'),
                   model_uri=BRICK.electricVehicleChargerDirectionality, domain=None, range=Optional[Union[dict, PropValue]])

slots.conversionEfficiency = Slot(uri=BRICK.conversionEfficiency, name="conversionEfficiency", curie=BRICK.curie('conversionEfficiency'),
                   model_uri=BRICK.conversionEfficiency, domain=None, range=Optional[Union[dict, PropValue]])

slots.semanticDescription__loops = Slot(uri=BRICK.loops, name="semanticDescription__loops", curie=BRICK.curie('loops'),
                   model_uri=BRICK.semanticDescription__loops, domain=None, range=Optional[Union[dict[Union[str, LoopId], Union[dict, Loop]], list[Union[dict, Loop]]]])

slots.semanticDescription__systems = Slot(uri=BRICK.systems, name="semanticDescription__systems", curie=BRICK.curie('systems'),
                   model_uri=BRICK.semanticDescription__systems, domain=None, range=Optional[Union[dict[Union[str, SystemId], Union[dict, System]], list[Union[dict, System]]]])

slots.semanticDescription__buildings = Slot(uri=BRICK.buildings, name="semanticDescription__buildings", curie=BRICK.curie('buildings'),
                   model_uri=BRICK.semanticDescription__buildings, domain=None, range=Optional[Union[list[Union[str, BuildingId]], dict[Union[str, BuildingId], Union[dict, Building]]]])

slots.semanticDescription__equipment = Slot(uri=BRICK.equipment, name="semanticDescription__equipment", curie=BRICK.curie('equipment'),
                   model_uri=BRICK.semanticDescription__equipment, domain=None, range=Optional[Union[dict[Union[str, EquipmentId], Union[dict, Equipment]], list[Union[dict, Equipment]]]])


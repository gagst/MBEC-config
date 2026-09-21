import abc
import importlib
import logging
from dataclasses import dataclass, field, fields
from typing import Any, Optional, Union

from ...constants import scenario_fields
from ...entities import brick_lite, s4bldg_lite
from ...utils.config import ConfigLoader
from ..infrastructure import Infrastructure
from ..kees_lite import Component

logger = logging.getLogger(__name__)

META_DICT = "to_dict"
META_SIMILAR = "similar"


@dataclass(init=False)
class Equipment(abc.ABC):
    name: str = field(init=False, metadata={META_DICT: scenario_fields.NAME})
    infrastructures: list[Infrastructure] = field(init=False)
    infrastructure_names: list[str] = field(
        init=False, metadata={META_DICT: scenario_fields.CONNECTED_INFRASTRUCTURE_NAMES}
    )
    building: Optional[str] = field(init=False, metadata={META_DICT: scenario_fields.BUILDING})
    class_name: str = field(init=False, metadata={META_DICT: scenario_fields.CLASS_NAME})

    is_controllable: bool = field(init=False, metadata={META_DICT: scenario_fields.CONTROLLABLE})
    is_external: bool = field(init=False, metadata={META_DICT: scenario_fields.EXTERNAL})

    def __str__(self):
        return f"{self.name} ({self.class_name} connected to {self.infrastructure_names} located in {self.building})"

    @classmethod
    def create(cls, name: str, infrastructures: list[Infrastructure], building: Optional[str]) -> "Equipment":
        instance = cls.__new__(cls)
        instance.name = name
        instance.infrastructures = infrastructures
        instance.infrastructure_names = [i.name for i in infrastructures]
        instance.building = building
        instance.class_name = instance.__class__.__name__
        return instance

    @classmethod
    @abc.abstractmethod
    def create_random(
        cls,
        config_loader: ConfigLoader,
        name: str,
        infrastructures: list[Infrastructure],
        building: Optional[str],
        *_: Any,
        **__: Any,
    ) -> "Equipment":
        raise NotImplementedError()

    @abc.abstractmethod
    def add_s4bldg_description(
        self,
        id_str: str,
        semantic_description: s4bldg_lite.SemanticDescription,
        building_space: Optional[s4bldg_lite.BuildingSpace],
    ):
        raise NotImplementedError()

    @abc.abstractmethod
    def add_brick_description(
        self,
        id_str: str,
        semantic_description: brick_lite.SemanticDescription,
        building: Optional[brick_lite.Building],
        loops: Optional[list[brick_lite.Loop]],
        systems: Optional[list[brick_lite.System]],
    ):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def text_description_type(self) -> Optional[str]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def text_description_parameters(self) -> Optional[str]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def reference_component_representation(self) -> list[Union[Component, list[Component]]]:
        raise NotImplementedError()

    @property
    def reference_component_slots(self) -> dict:
        result = {}
        for reference in self.reference_component_representation:
            if isinstance(reference, list):
                for r in reference:
                    for slot_name in r.model_fields_set:
                        if slot_name not in result:
                            result[slot_name] = getattr(r, slot_name)
            else:
                for slot_name in reference.model_fields_set:
                    if slot_name not in result:
                        result[slot_name] = getattr(reference, slot_name)
        return result

    @property
    def reference_component_classes_flat(self) -> list[str]:
        results = set()
        for reference in self.reference_component_representation:
            if isinstance(reference, list):
                for r in reference:
                    results.add(r.__class__.__name__)
            else:
                results.add(reference.__class__.__name__)
        return list(results)

    @property
    def text_description_type_with_building(self) -> Optional[str]:
        connected_building = self.building
        text_description_type = self.text_description_type
        if connected_building is not None and text_description_type is not None:
            return f'{text_description_type} in building "{connected_building}"'
        else:
            return self.text_description_type

    @property
    def e_infrastructures(self) -> list[Infrastructure]:
        return list({i for i in self.infrastructures if i.infrastructure_type == "e"})

    @property
    def h_infrastructures(self) -> list[Infrastructure]:
        return list({i for i in self.infrastructures if i.infrastructure_type == "h"})

    def to_dict(self) -> dict:
        result = {}
        for f in fields(self):
            dict_name = f.metadata.get(META_DICT, None)
            if dict_name is not None:
                result[dict_name] = getattr(self, f.name)
        return result

    @classmethod
    def from_dict(cls, data: dict, infrastructures: list[Infrastructure]):
        class_name = data.get(scenario_fields.CLASS_NAME)
        equipment_module = importlib.import_module(__package__)  # from where to import components
        equipment_cls: type[Equipment] = getattr(equipment_module, class_name)
        instance = equipment_cls.__new__(equipment_cls)
        for f in fields(instance):
            dict_name = f.metadata.get(META_DICT, None)
            if dict_name is not None:
                if dict_name in data:
                    setattr(instance, f.name, data.get(dict_name))
                else:
                    raise AttributeError(
                        f"Field '{dict_name}' is missing in the dictionary for class {instance.__class__.__name__}."
                    )

        infrastructure_names_mapper = {i.name: i for i in infrastructures}
        instance.infrastructures = [infrastructure_names_mapper[name] for name in instance.infrastructure_names]
        return instance

import re
from typing import Optional

from rapidfuzz.distance import Levenshtein

from ..constants.thresholds import STRING_SIMILARITY_THRESHOLD
from ..entities.equipment.equipment import Equipment
from ..entities.infrastructure import Infrastructure
from ..utils.random import RandomTool
from ..utils.word_lists import ANIMALS, PLANTS, SCIENTISTS


def get_string_similarity(string1: str, string2: str) -> float:
    string1 = _clean_string_for_similarity(string1)
    string2 = _clean_string_for_similarity(string2)

    return Levenshtein.normalized_similarity(string1, string2)


def are_strings_similar(string1: str, string2: str) -> float:
    ratio = get_string_similarity(string1, string2)
    return ratio >= STRING_SIMILARITY_THRESHOLD


def _clean_string_for_similarity(string: str) -> str:
    # If there are leftovers from the RDF:
    if ":" in string:
        string = string.split(":")[1]
    # Remove non-alphanumeric symbols and convert to lowercase
    string = string.lower()
    string = re.sub(r"[^a-z0-9]", " ", string)
    # If name is multiple words divided by non-alphanumeric symbols (transformed to spaces) ignore the relative position
    string = "".join(sorted(string.split()))
    return string


def _extend_with_strings(string_list: list[str], extra: list[str]) -> list[str]:
    result = string_list.copy()
    for s in string_list:
        for e in extra:
            result.append(f"{s} {e}")
    return result


def _extend_with_abbreviations(string_list: list[str]) -> list[str]:
    abbreviations = {
        "EV": "electric vehicle",
        "PV": "photovoltaic",
    }
    result = string_list.copy()
    for candidate in string_list:
        for abbr, full in abbreviations.items():
            if abbr in candidate:
                result.append(candidate.replace(abbr, full))
    return result


def _get_combinations(strings: list[str]) -> list[str]:
    n = len(strings)
    result = []
    for i in range(n):
        for j in range(i + 1, n + 1):
            combo = strings[i:j]
            if combo:
                result.append(" ".join(combo))
    return result


def get_name_candidates(for_object: Equipment | Infrastructure, buildings: Optional[list[str]] = None) -> list[str]:
    # The spaces and order of words does not matter since they are ignored in similarity calculations

    candidates = [for_object.name]  # Note that name of the infrastructure is not available in the text descriptions

    if isinstance(for_object, Equipment):
        # It is ok to get all combinations, since every candidate carry new information
        if for_object.building is not None:
            candidates.append(for_object.building)
        if for_object.text_description_type is not None:
            candidates.append(for_object.text_description_type)
        candidates = _get_combinations(candidates)

    elif isinstance(for_object, Infrastructure):
        # Add information about connected buildings
        if buildings is not None:
            candidates.extend(buildings)

        # Use extend method to avoid combinations of similar terms, e.g. "heat" and "heating"
        if for_object.infrastructure_type == "e":
            candidates = _extend_with_strings(candidates, ["electricity", "electrical"])
        elif for_object.infrastructure_type == "h":
            candidates = _extend_with_strings(candidates, ["heating", "heat"])
        candidates.extend(["system", "loop"])

    candidates = _extend_with_abbreviations(candidates)
    return candidates


def make_path_friendly(string: str) -> str:
    string = string.strip()
    string = string.replace(" ", "-")
    string = string.replace(".", "-")
    string = string.replace(":", "-")
    return string


def graph_file_name(method: str) -> str:
    return f"{method}_graph.yaml"


class NameGenerator:
    def __init__(self):
        self._building_name_options = RandomTool.shuffle(SCIENTISTS)
        self._equipment_name_options = RandomTool.shuffle(ANIMALS)
        self._infrastructure_name_options = RandomTool.shuffle(PLANTS)

    def get_building_name(self) -> str:
        return self._building_name_options.pop()

    def get_equipment_name(self) -> str:
        return self._equipment_name_options.pop()

    def get_infrastructure_name(self) -> str:
        return self._infrastructure_name_options.pop()

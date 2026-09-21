import re
from dataclasses import dataclass
from typing import Optional

import rdflib

from .names import make_path_friendly


def remove_semantic_description(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    removing = False
    cleaned_lines = []

    pattern = re.compile(r"\[\]\s+a\s+\w+:SemanticDescription\s*;")
    for line in lines:
        if pattern.search(line):
            removing = True
        if removing:
            if line.strip().endswith("."):
                removing = False
            continue
        cleaned_lines.append(line)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)


def clean_s4bldg_rdf(path):
    remove_semantic_description(path)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    cleaned_content = "\n".join([line for line in content.splitlines() if line.strip()])

    with open(path, "w", encoding="utf-8") as f:
        f.write(cleaned_content)


def clean_brick_rdf(path):
    remove_semantic_description(path)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r"\[\s*a\s+\w+:PropValue\s*;?")
    cleaned_content = pattern.sub("[", content)

    cleaned_content = "\n".join([line for line in cleaned_content.splitlines() if line.strip()])

    with open(path, "w", encoding="utf-8") as f:
        f.write(cleaned_content)


def _to_rdf(prefix: str, name: str, type_description: Optional[str], no_type_description: bool) -> str:
    if not no_type_description and type_description is not None:
        name = f"{type_description} {name}"
    name = make_path_friendly(name)
    return f"{prefix}:{name}"


def to_s4bldg_id(name: str, no_type_description: bool, type_description: Optional[str]) -> str:
    return _to_rdf(
        prefix="s4bldg_lite", name=name, no_type_description=no_type_description, type_description=type_description
    )


def to_brick_id(name: str, no_type_description: bool, type_description: Optional[str]) -> str:
    return _to_rdf(
        prefix="brick_lite", name=name, no_type_description=no_type_description, type_description=type_description
    )


def transform_to_kw(value: rdflib.term.Literal | None, unit_uri: rdflib.term.URIRef | None) -> float | None:
    if value is None or unit_uri is None:
        return None
    if str(unit_uri) == "https://qudt.org/vocab/unit/KiloW":
        pass
    else:
        raise NotImplementedError(f"Unit {unit_uri} is not supported!")
    return float(value)


@dataclass
class ResourceDescription:
    """
    Helper dataclass to describe RDF resources and their full URI and URI for their type,
    """
    full_uri: rdflib.term.URIRef
    type_uri: rdflib.term.URIRef

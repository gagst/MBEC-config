from enum import StrEnum


class Ontology(StrEnum):
    S4BLDG = "s4bldg"
    BRICK = "brick"

    def full_name(self, anon: bool) -> str:
        if anon:
            return f"{self.value}_anon"
        else:
            return self.value

import string
from random import Random
from typing import Callable


class RandomTool:
    random = Random(1234)

    @staticmethod
    def set_seed(seed: int):
        RandomTool.random.seed(seed)

    @staticmethod
    def is_event_triggered(probability: float) -> bool:
        if not 0 <= probability <= 1:
            raise ValueError(f"Probability must be between 0 and 1, not {probability}")
        return RandomTool.random.random() < probability

    @staticmethod
    def select_key_value(all_slots: dict) -> dict:
        choice = RandomTool.random.choice(list(all_slots.keys()))
        return {choice: all_slots[choice]}

    @staticmethod
    def call(*args: Callable):
        choice = RandomTool.random.choice(args)
        choice()

    @staticmethod
    def select_element(options: list):
        return RandomTool.random.choice(options)

    @staticmethod
    def select_uniform(low: float, high: float, decimal_digits: int) -> float:
        return round(RandomTool.random.uniform(low, high), decimal_digits)

    @staticmethod
    def select_positive_int(high: int) -> int:
        return RandomTool.random.randint(1, high)

    @staticmethod
    def get_random_string(length: int) -> str:
        characters = string.ascii_letters + string.digits
        return "".join(RandomTool.random.choice(characters) for _ in range(length))

    @staticmethod
    def shuffle(what: list) -> list:
        result = what.copy()
        RandomTool.random.shuffle(result)  # shuffling in place
        return result

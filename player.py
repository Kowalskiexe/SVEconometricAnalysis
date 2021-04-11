from functools import cache, cached_property

from yaml.tokens import StreamStartToken


class Player:

    def __init__(self, energy: int, watering_cost: float, already_taken: int,
                 seed_capital: int, profession: str, season: str, day_of_season: int):
        self.energy: int = energy
        self.watering_cost: float = watering_cost
        self.already_taken: int = already_taken
        self.seed_capital: int = seed_capital
        self.profession: str = profession
        self.season: str = season
        self.day_of_season: int = day_of_season

    @cached_property
    def max_tiles(self) -> int:
        return int((self.energy / self.watering_cost) - self.already_taken)

    def __repr__(self):
        return f'Player:\n\tseed capital: {self.seed_capital}\tmax tiles: {self.max_tiles}'

from dataclasses import dataclass


@dataclass
class SimUnit:
    id: int
    player: int
    x: int
    y: int
    ms: int
    cc: int
    hp: int
    chop: int
    carry: list  # length 6

    @property
    def pos(self):
        return (self.x, self.y)

    @property
    def total(self):
        return sum(self.carry)

    @property
    def free(self):
        return self.cc - self.total


@dataclass
class SimPlant:
    type: str
    x: int
    y: int
    size: int
    health: int
    fruits: int
    cooldown: int

    @property
    def pos(self):
        return (self.x, self.y)


@dataclass
class GameState:
    width: int
    height: int
    walkable: set
    shacks: list
    inventories: list
    units: list
    plants: list
    scores: list
    turn: int
    next_id: int


def from_ascii(rows, talents=(1, 1, 1, 0)):
    width = len(rows[0])
    height = len(rows)
    walkable = set()
    shacks = [None, None]
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "0":
                shacks[0] = (x, y)
            elif ch == "1":
                shacks[1] = (x, y)
            else:
                walkable.add((x, y))
    units = []
    for p in (0, 1):
        sx, sy = shacks[p]
        units.append(SimUnit(p, p, sx, sy, talents[0], talents[1],
                             talents[2], talents[3], [0] * 6))
    return GameState(width=width, height=height, walkable=walkable, shacks=shacks,
                     inventories=[[0] * 6, [0] * 6], units=units, plants=[],
                     scores=[0, 0], turn=1, next_id=len(units))

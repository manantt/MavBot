from sc2.units import Units
from sc2.constants import *
from sc2.cache import property_cache_forever, property_cache_once_per_frame
from sc2.position import Point2, Point3
from sc2.units import Units

NEUTRAL = 0
ALLY = 1
ENEMY = 2

class BaseManager:
    def __init__(self, game):
        self.game = game
        self.bases = []
        self.init_bases()

    def init_bases(self):
        for b in self.game.expansion_locations:
            base = Base(game)
            base.position = b.position
            base.minerals = get_base_minerals(base)
            base.vespene = get_base_vespene(base)

    def get_base_minerals(self, base):
        return 0

    def get_base_vespene(self, base):
        return 0

    def get_bases(self, owner="all"):
        if owner in [NEUTRAL, ALLY, ENEMY]:
            return self.bases.filter(lambda base: base.owner == owner)
        return self.bases

class Base:
    def __init__(self, game):
        self.game = game
        self.position = None
        self.owner: int = None
        self.hidden: bool = False
        self.workers: Units = Units([], game)
        self.defenses: int = 0
        self.structures: int = 0
        self.minerals: int = None
        self.vespene: int = None

    def check_base(self):
        self.check_owner()
        if self.owner == 1:
            pass

    def init_owner(self):
        pass

    def is_ally(self):
        pass

    def is_enemy(self):
        pass

    def check_owner(self):
        pass

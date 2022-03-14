from sc2.units import Units
from sc2.constants import *
from sc2.cache import property_cache_forever, property_cache_once_per_frame
from sc2.position import Point2, Point3
from sc2.units import Units

import datetime

OWNER_NEUTRAL = 0
OWNER_ALLY = 1
OWNER_ENEMY = 2

RANGE_SAFE = 0
RANGE_WARNING = 1
RANGE_DANGER = 2
RANGE_PANIC = 3

WORKER_VALUE = 0
MINERAL_VALUE = 0
VESPENE_VALUE = 0


class BaseManager:
    def __init__(self, game):
        self.game = game
        self.bases = []
        self.enemy_main_spoted = False
        self.init_bases()

    def init_bases(self):
        #for b in self.game.expansion_locations_list:
        #    base = Base(game)
        #    base.position = b.position
        #    base.minerals = get_base_minerals(base)
        #    base.vespene = get_base_vespene(base)
        #    base.last_check = datetime.now()
        #    if b.position.distance_to(self.game.start_position < EXPANSION_GAP_THRESHOLD):
        #        base.owner = OWNER_ALLY
        #    elif b.position.distance_to(self.game.enemy_start_locations[0] < EXPANSION_GAP_THRESHOLD):
        #        base.owner = OWNER_ENEMY
        #    else:
        #        base.owner = OWNER_NEUTRAL
        #    self.bases.append(base)
        pass

    def update_bases(self):
        pass

    def debug_bases(self):
        pass

    def get_base_minerals(self, base):
        return 0

    def get_base_vespene(self, base):
        return 0

    def get_bases(self, owner="all"):
        if owner in [OWNER_NEUTRAL, OWNER_ALLY, OWNER_ENEMY]:
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
        self.hidden: bool = True
        self.last_check = None

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

    @property
    def value(self):
        # workers + resources + structures
        pass

    @property
    def danger(self):
        # near enemy bases + near enemy troops - base defenders
        pass

    @property
    def risk(self):
        # value/dangerousness
        pass

    @property
    def workers(self):
        pass

    @property
    def structures(self):
        pass

    @property
    def defenses(self):
        pass

    @property
    def resources(self):
        pass

    def is_safe_to_expand(self, worker):
        "true if there are no enemies between the worker and the base"
        pass


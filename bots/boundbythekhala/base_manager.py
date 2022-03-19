from sc2.units import Units
from sc2.constants import *
from sc2.cache import property_cache_forever, property_cache_once_per_frame
from sc2.position import Point2, Point3
from sc2.units import Units

from datetime import datetime
import math

RANGE_SAFE = 0
RANGE_WARNING = 1
RANGE_DANGER = 2
RANGE_PANIC = 3

WORKER_VALUE = 0
MINERAL_VALUE = 0
VESPENE_VALUE = 0

SPEED_MINING_DISTANCE = 2.22
HARVEST_RETURN_DISTANCE = 3.9

TOWNHALL_MAX_DISTANCE_TO_BASE = 5

class BaseManager:
    OWNER_NEUTRAL = 0
    OWNER_ALLY = 1
    OWNER_ENEMY = 2

    def __init__(self, game):
        self.game = game
        self.bases = []
        self.bussy_probes = []
        self.enemy_main_spoted = False
        self.inited = False

    async def init_bases(self):
        # inits the bases on first step
        for b in self.game.expansion_locations:
            base = Base(self.game)
            base.position = b.position
            base.last_check = datetime.now()
            if b.position.distance_to(self.game.start_location) < TOWNHALL_MAX_DISTANCE_TO_BASE:
                base.owner = self.OWNER_ALLY
            elif b.position.distance_to(self.game.enemy_start_locations[0]) < TOWNHALL_MAX_DISTANCE_TO_BASE:
                base.owner = self.OWNER_ENEMY
            else:
                base.owner = self.OWNER_NEUTRAL
            base.distance_to_enemy_main = base.position.distance_to(self.game.enemy_start_locations[0])
            self.bases.append(base)
        await self.init_first_workers()

    async def init_first_workers(self):
        # distributes the workers on first step
        base = self.get_bases(self.OWNER_ALLY)[0]
        local_minerals = [mineral for mineral in self.game.mineral_field if mineral.distance_to(base.position) <= 8]
        local_minerals.sort(key=lambda mineral: mineral.distance_to(base.position))
        local_minerals = Units(local_minerals, self)
        used_workers = []
        while self.game.workers.tags_not_in(used_workers):
            for mineral in local_minerals:
                if mineral.tag not in base.mineral_worker_tags:
                    base.mineral_worker_tags[mineral.tag] = []
                workers = self.game.workers.tags_not_in(used_workers)
                if workers:
                    worker = workers.closest_to(mineral)
                    used_workers.append(worker.tag)
                    base.mineral_worker_tags[mineral.tag].append(worker.tag)
                    worker.gather(mineral)
                else:
                    return

    async def update_bases(self):
        if not self.inited:
            await self.init_bases()
            self.inited = True
        else:
            self.check_enemy_main()
            for base in self.bases:
                base.update_base(self.enemy_main_spoted)
            self.distribute_workers()

    def debug_bases(self):
        pass

    def get_bases(self, owner="all"):
        if owner in [self.OWNER_NEUTRAL, self.OWNER_ALLY, self.OWNER_ENEMY]:
            return Units(self.bases, self.game).filter(lambda base: base.owner == owner)
        return self.bases

    def get_free_workers(self):
        gathering_workers = []
        for base in self.bases:
            for mineral_tag in base.mineral_worker_tags:
                for worker_tag in base.mineral_worker_tags[mineral_tag]:
                    gathering_workers.append(worker_tag)
            for gas_tag in base.vespene_worker_tags:
                for worker_tag in base.vespene_worker_tags[gas_tag]:
                    gathering_workers.append(worker_tag)
        return self.game.workers.tags_not_in(gathering_workers +  self.bussy_probes)

    def distribute_workers(self):
        # sends free workers to mine
        free_workers = self.get_free_workers()
        if free_workers:
            for worker in free_workers:
                base = self.get_next_mining_base()
                if base:
                    mineral_field = base.get_next_mining_field()
                    if mineral_field:
                        if self.game.structures(UnitTypeId.ASSIMILATOR).find_by_tag(mineral_field):
                            base.vespene_worker_tags[mineral_field].append(worker.tag)
                        else:
                            base.mineral_worker_tags[mineral_field].append(worker.tag)

    def get_next_mining_base(self):
        # returns the first not filled mining base
        for base in self.bases:
            if base.owner == self.OWNER_ALLY:
                for mineral_tag in base.mineral_worker_tags:
                    if len(base.mineral_worker_tags[mineral_tag]) < 2:
                        return base
                for assimilator_tag in base.vespene_worker_tags:
                    if len(base.vespene_worker_tags[assimilator_tag]) < 3:
                        return base
        return None

    def release_worker(self, worker):
        # allows a worker to do other stuff
        for base in self.bases:
            for mineral_tag in base.mineral_worker_tags:
                for worker_tag in base.mineral_worker_tags[mineral_tag]:
                    if worker.tag == worker_tag:
                        base.mineral_worker_tags[mineral_tag].remove(worker_tag)

    """
    TODO: move to strategy_manager
    def get_next_base_to_scout(self):
        closest = None
        for base in self.get_bases(self.OWNER_NEUTRAL):
            if not closest:
                closest = base
            elif base.last_check < closest.last_check:
                closest = base
            elif base.last_check == closest.last_check:
                if base.distance_to_enemy_main < closest.distance_to_enemy_main:
                    closest = base
        return closest.position"""

    def check_enemy_main(self):
        # we know there is an enemy townhall in his main even if not spoted
        if not self.enemy_main_spoted:
            enemy_th = self.game.enemy_structures.filter(lambda u: u.type_id in [UnitTypeId.COMMANDCENTER, UnitTypeId.COMMANDCENTERFLYING, UnitTypeId.ORBITALCOMMAND, UnitTypeId.PLANETARYFORTRESS, UnitTypeId.ORBITALCOMMANDFLYING, UnitTypeId.NEXUS, UnitTypeId.HATCHERY, UnitTypeId.LAIR, UnitTypeId.HIVE])
            if enemy_th:
                enemy_th = enemy_th.closer_than(5, self.game.enemy_start_locations[0])
                if enemy_th:
                    self.enemy_main_spoted = True

class Base:
    def __init__(self, game):
        self.game = game
        self.position = None
        self.owner = None
        self.hidden = False
        self.minerals = None
        self.vespene = None
        self.mineral_worker_tags = {} # links mineral fields to asigned workers tags
        self.vespene_worker_tags = {} # links assimilators to asigned workers tags
        self.last_check = None
        self.distance_to_enemy_main = 0

    def update_base(self, enemy_main_spoted):
        if self.position.distance_to(self.game.enemy_start_locations[0]) > 5 or enemy_main_spoted:
            self.owner = BaseManager.OWNER_NEUTRAL
        for n in self.game.townhalls.ready:
            if self.position.distance_to(n) < TOWNHALL_MAX_DISTANCE_TO_BASE:
                self.owner = BaseManager.OWNER_ALLY
        for s in self.game.enemy_structures():
            if self.position.distance_to(s) < 13:
                self.owner = BaseManager.OWNER_ENEMY
        # last check
        for unit in self.game.units:
            if unit.distance_to(self.position) < 5:
                self.last_check = datetime.now()

        self.update_mining_fields()
        if self.owner == BaseManager.OWNER_ALLY:
            self.speed_mining()
        

    def update_mining_fields(self):
        # Checks the minerals and gas amount and initialized the mining_fields array if not yet
        local_minerals = [mineral for mineral in self.game.mineral_field if mineral.distance_to(self.position) <= 8]
        local_minerals.sort(key=lambda mineral: mineral.distance_to(self.position))
        local_minerals = Units(local_minerals, self)
        total_minerals = 0
        for mineral in local_minerals:
            total_minerals += mineral.mineral_contents
            if mineral.tag not in self.mineral_worker_tags:
                self.mineral_worker_tags[mineral.tag] = []
        self.minerals = total_minerals
        # TODO lo mismo para el gas

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

    def distance_to(self, base):
        "ground distance between 2 bases"
        return 0

    def air_distance_to(self, base):
        "rect line distance between 2 bases"
        return 0

    ################### mining functions
    def speed_mining(self):
        for mineral_tag in list(self.mineral_worker_tags):
            mineral_field = self.game.mineral_field.find_by_tag(mineral_tag)
            if not mineral_field:
                del self.mineral_worker_tags[mineral_tag]
                continue
            for worker_tag in self.mineral_worker_tags[mineral_tag]:
                worker = self.game.workers.find_by_tag(worker_tag)
                if not worker or not worker.is_moving and not worker.is_collecting and not worker.is_idle:
                    continue
                nexus = self.game.structures(UnitTypeId.NEXUS).ready
                if not nexus:
                    continue
                nexus = nexus.closest_to(mineral_field)
                # todo check worker, mineral and nexus exists
                if not worker.is_carrying_resource:
                    if worker.distance_to(mineral_field) > SPEED_MINING_DISTANCE:
                        if not worker.is_moving:
                            worker.move(mineral_field.position.towards(worker.position, 0.5))
                    else:
                        worker.gather(mineral_field)
                else:
                    if worker.distance_to(nexus) > HARVEST_RETURN_DISTANCE and worker.distance_to(mineral_field) > SPEED_MINING_DISTANCE:
                        if not worker.is_moving:
                            worker.move(nexus.position.towards(worker.position, 3))
                    else:
                        worker(AbilityId.HARVEST_RETURN_PROBE)

        for gas_tag in list(self.vespene_worker_tags):
            assimilator = self.game.structures(UnitTypeId.ASSIMILATOR).find_by_tag(gas_tag)
            if not assimilator:
                del self.vespene_worker_tags[gas_tag]
                continue
            for worker_tag in self.vespene_worker_tags[gas_tag]:
                worker = self.game.workers.find_by_tag(worker_tag)
                if not worker or self.game.bot.unit_manager.worker_is_building(worker):
                    continue
                if worker.is_carrying_resource and not worker.order_target:
                    worker(AbilityId.HARVEST_RETURN_PROBE)
                elif not worker.is_carrying_resource and not worker.order_target == assimilator.tag:
                    worker.gather(assimilator)

    def get_next_mining_field(self):
        for gas_tag in self.vespene_worker_tags:
            if len(self.vespene_worker_tags[gas_tag]) < 3:
                return gas_tag
        min_workers_per_field = math.inf
        for mineral_tag in self.mineral_worker_tags:
            if len(self.mineral_worker_tags[mineral_tag]) < min_workers_per_field:
                min_workers_per_field = len(self.mineral_worker_tags[mineral_tag])
        if min_workers_per_field < 2:
            for mineral_tag in self.mineral_worker_tags:
                if len(self.mineral_worker_tags[mineral_tag]) <= min_workers_per_field:
                    return mineral_tag
        else:
            return None
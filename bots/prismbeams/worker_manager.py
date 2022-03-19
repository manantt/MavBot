from sc2.units import Units
from sc2.constants import *
from sc2.position import Point2, Point3
from sc2.data import Race
import math

SPEED_MINING_DISTANCE = 2.22
HARVEST_RETURN_DISTANCE = 3.9

class WorkerManager:
    def __init__(self, game):
        self.game = game
        self.workers_distributed = False
        self.mining_fields = {}
        self.gas_fields = {}
        self.proxy_worker = None
        self.first_pylon_worker = None
        self.gw_worker = None
        self.cc_worker = None

    async def manage_workers(self):
        if not self.workers_distributed:
            await self.distribute_workers_init()
        else:
            self.distribute_workers()
            self.speed_mining()
        await self.build_wall()
        await self.build_assimilators()
        await self.manage_proxy_worker()
        self.attack_other_workers()

    def attack_other_workers(self):
        for ew in self.game.enemy_units(set([UnitTypeId.PROBE, UnitTypeId.SCV, UnitTypeId.DRONE, UnitTypeId.MULE])):
            workers_attacking_ew = self.game.units(UnitTypeId.PROBE).filter(lambda w: w.is_attacking and w.order_target == ew.tag)
            if ew.distance_to(self.game.start_location) > 20 or self.game.units(UnitTypeId.VOIDRAY):
                for worker in workers_attacking_ew:
                    worker.move(self.game.start_location)
            else:
                if not workers_attacking_ew:
                    worker = self.game.select_build_worker(ew.position)
                    if worker:
                        worker.attack(ew)

    async def distribute_workers_init(self):
        nexus = self.game.townhalls.ready.first
        local_minerals = [mineral for mineral in self.game.mineral_field if mineral.distance_to(nexus) <= 8]
        local_minerals.sort(key=lambda mineral: mineral.distance_to(nexus))
        local_minerals = Units(local_minerals, self)
        used_workers = []
        
        while self.game.workers.tags_not_in(used_workers):
            for mineral in local_minerals:
                if mineral.tag not in self.mining_fields:
                    self.mining_fields[mineral.tag] = []
                workers = self.game.workers.tags_not_in(used_workers)
                if workers:
                    worker = workers.closest_to(mineral)
                    used_workers.append(worker.tag)
                    self.mining_fields[mineral.tag].append(worker.tag)
                    worker.gather(mineral)
                else:
                    self.workers_distributed = True
                    return

    def speed_mining(self):
        for mineral_tag in list(self.mining_fields):
            mineral_field = self.game.mineral_field.find_by_tag(mineral_tag)
            if not mineral_field:
                del self.mining_fields[mineral_tag]
                continue
            for worker_tag in self.mining_fields[mineral_tag]:
                worker = self.game.workers.find_by_tag(worker_tag)
                if not worker or (not worker.is_moving and not worker.is_collecting and not worker.is_idle):
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

        for gas_tag in list(self.gas_fields):
            assimilator = self.game.structures(UnitTypeId.ASSIMILATOR).find_by_tag(gas_tag)
            if not assimilator:
                del self.gas_fields[gas_tag]
                continue
            for worker_tag in self.gas_fields[gas_tag]:
                worker = self.game.workers.find_by_tag(worker_tag)
                if not worker or worker.is_attacking:
                    continue
                if not worker.is_carrying_resource and not worker.order_target == assimilator.tag:
                    worker.gather(assimilator)

    def get_free_workers(self):
        gathering_workers = []
        for mineral_tag in self.mining_fields:
            for worker_tag in self.mining_fields[mineral_tag]:
                gathering_workers.append(worker_tag)
        for gas_tag in self.gas_fields:
            for worker_tag in self.gas_fields[gas_tag]:
                gathering_workers.append(worker_tag)
        return self.game.workers.tags_not_in(gathering_workers)

    def distribute_workers(self):
        free_workers = self.get_free_workers().tags_not_in([self.cc_worker,self.gw_worker,self.proxy_worker,self.first_pylon_worker])
        if free_workers:
            for worker in free_workers:
                next_field = self.get_next_mining_field()
                if next_field:
                    self.mining_fields[next_field].append(worker.tag)
        # priorize gas
        for gas_tag in list(self.gas_fields):
            assimilator = self.game.structures.find_by_tag(gas_tag)
            if not assimilator:
                del self.gas_fields[gas_tag]
                return
            if assimilator.surplus_harvesters < 0:
                worker = self.game.select_build_worker(assimilator.position)
                if not worker:
                    return
                self.release_worker(worker.tag)
                self.gas_fields[gas_tag].append(worker.tag)
            elif assimilator.surplus_harvesters > 0:
                if self.gas_fields[gas_tag]:
                    del self.gas_fields[gas_tag][-1]

    def get_next_mining_field(self):
        min_workers_per_field = math.inf
        for mineral_tag in self.mining_fields:
            if len(self.mining_fields[mineral_tag]) < min_workers_per_field:
                min_workers_per_field = len(self.mining_fields[mineral_tag])
        for mineral_tag in self.mining_fields:
            if len(self.mining_fields[mineral_tag]) <= min_workers_per_field:
                return mineral_tag

    def release_worker(self, worker):
        for mineral_tag in self.mining_fields:
            for worker_tag in self.mining_fields[mineral_tag]:
                if worker == worker_tag:
                    self.mining_fields[mineral_tag].remove(worker_tag)
                    return
        for gas_tag in self.gas_fields:
            for worker_tag in self.gas_fields[gas_tag]:
                if worker == worker_tag:
                    self.gas_fields[gas_tag].remove(worker_tag)
                    return

    async def build_wall(self):
        # 1st pylon
        if not self.first_pylon_worker and not self.game.already_pending(UnitTypeId.PYLON) and not self.game.structures(UnitTypeId.PYLON):
            if self.game.minerals >= 55:
                nexus = self.game.structures(UnitTypeId.NEXUS)
                if nexus:
                    workers = self.game.workers.filter(lambda unit: not unit.is_carrying_minerals)
                    if workers:
                        self.first_pylon_worker = workers.closest_to(nexus.first).tag
                        self.release_worker(self.first_pylon_worker)
        if self.first_pylon_worker:
            worker = self.game.workers.find_by_tag(self.first_pylon_worker)
            if not worker:
                self.first_pylon_worker = None
                return
            if self.game.can_afford(UnitTypeId.PYLON): 
                worker.build(UnitTypeId.PYLON, self.game.main_base_ramp.protoss_wall_pylon)
            else:
                worker.move(self.game.main_base_ramp.protoss_wall_pylon)
        if self.game.structures(UnitTypeId.PYLON).amount:
            self.first_pylon_worker = None
        # gateway
        if self.gw_worker:
            if not self.game.structures(UnitTypeId.GATEWAY).amount and not self.game.already_pending(UnitTypeId.GATEWAY):
                worker = self.game.workers.find_by_tag(self.gw_worker)
                if not worker:
                    self.gw_worker = None
                    return
                if self.game.can_afford(UnitTypeId.GATEWAY) and self.game.structures(UnitTypeId.PYLON).ready.exists:
                    worker.build(UnitTypeId.GATEWAY, list(self.game.main_base_ramp.protoss_wall_buildings)[0])
                else:
                    worker.move(list(self.game.main_base_ramp.protoss_wall_buildings)[0])
        if self.game.structures(UnitTypeId.GATEWAY).amount:
            self.gw_worker = None
        # ciberneticscore
        if self.cc_worker:
            if not self.game.structures(UnitTypeId.CYBERNETICSCORE).amount and not self.game.already_pending(UnitTypeId.CYBERNETICSCORE):
                worker = self.game.workers.find_by_tag(self.cc_worker)
                if not worker:
                    self.cc_worker = None
                    return
                if self.game.can_afford(UnitTypeId.CYBERNETICSCORE) and self.game.structures(UnitTypeId.GATEWAY).ready.exists:
                    worker.build(UnitTypeId.CYBERNETICSCORE, list(self.game.main_base_ramp.protoss_wall_buildings)[1])
                else:
                    worker.move(list(self.game.main_base_ramp.protoss_wall_buildings)[1])
        if self.game.structures(UnitTypeId.CYBERNETICSCORE).amount:
            self.cc_worker = None

        if (self.game.already_pending(UnitTypeId.VOIDRAY) or self.game.units(UnitTypeId.VOIDRAY)) and self.game.structures(UnitTypeId.STARGATE) and self.game.can_afford(UnitTypeId.PYLON) and not self.game.already_pending(UnitTypeId.PYLON) and self.game.supply_left < 4:
            if not self.game.structures(UnitTypeId.PYLON).closer_than(5, self.game.start_location.towards(self.game.game_info.map_center, -3)):
                await self.game.build(UnitTypeId.PYLON, self.game.start_location.towards(self.game.game_info.map_center, -3))
            else:
                await self.game.build(UnitTypeId.PYLON, self.game.main_base_ramp.protoss_wall_warpin)

        if self.game.can_afford(UnitTypeId.SHIELDBATTERY) and not self.game.already_pending(UnitTypeId.SHIELDBATTERY) and not self.game.structures(UnitTypeId.SHIELDBATTERY).closer_than(20, self.game.start_location.towards(self.game.game_info.map_center, -3)) \
                and self.game.structures(UnitTypeId.PYLON).ready.closer_than(5, self.game.start_location.towards(self.game.game_info.map_center, -3)):
            await self.game.build(UnitTypeId.SHIELDBATTERY, self.game.bot.deff_position)

    async def build_assimilators(self):
        if self.game.can_afford(UnitTypeId.ASSIMILATOR) and self.game.structures(UnitTypeId.GATEWAY):
            for nexus in self.game.townhalls().ready:
                vespenes = self.game.vespene_geyser.closer_than(13.0, nexus)
                for vespene in vespenes:
                    worker = self.game.select_build_worker(vespene.position)
                    if worker is not None and (not self.game.structures(UnitTypeId.ASSIMILATOR).amount or not self.game.structures(UnitTypeId.ASSIMILATOR).closer_than(1.0, vespene)):
                        worker.build(UnitTypeId.ASSIMILATOR, vespene)

    async def manage_proxy_worker(self):
        if self.proxy_worker:
            worker = self.game.workers.find_by_tag(self.proxy_worker)
            if worker:
                proxy_pylons = self.game.structures(UnitTypeId.PYLON).closer_than(2, self.game.bot.strategy_manager.proxy_pylon_position)
                if not proxy_pylons:
                    if worker.distance_to(self.game.bot.strategy_manager.proxy_pylon_position) > 5:
                        worker.move(self.game.bot.strategy_manager.proxy_pylon_position)
                    elif self.game.can_afford(UnitTypeId.PYLON):
                        worker.build(UnitTypeId.PYLON, self.game.bot.strategy_manager.proxy_pylon_position)
                else:
                    proxy_pylons = proxy_pylons.ready
                    if not proxy_pylons:
                        return
                    else:
                        proxy_pylon = proxy_pylons.first
                        if self.game.structures(UnitTypeId.CYBERNETICSCORE).ready and not self.game.structures(UnitTypeId.STARGATE) and self.game.can_afford(UnitTypeId.STARGATE):
                            await self.game.build(UnitTypeId.STARGATE, near=self.game.bot.strategy_manager.proxy_pylon_position.towards(self.game.game_info.map_center, 1), build_worker=worker)
                        elif (self.game.structures(UnitTypeId.STARGATE) or self.game.minerals > 250) and self.game.can_afford(UnitTypeId.SHIELDBATTERY):
                            if(self.game.structures(UnitTypeId.SHIELDBATTERY).amount < 1):
                                await self.game.build(UnitTypeId.SHIELDBATTERY, near=self.game.bot.strategy_manager.proxy_pylon_position, build_worker=worker)
                            elif self.game.structures(UnitTypeId.SHIELDBATTERY).amount < 2 and (self.game.units(UnitTypeId.STALKER) or self.game.already_pending(UnitTypeId.STALKER)):
                                await self.game.build(UnitTypeId.SHIELDBATTERY, near=self.game.bot.strategy_manager.proxy_pylon_position, build_worker=worker)
                            elif self.game.minerals > 300:
                                await self.game.build(UnitTypeId.SHIELDBATTERY, near=self.game.bot.strategy_manager.proxy_pylon_position.towards(self.game.enemy_start_locations[0], 3), build_worker=worker)
                    return
            else:
                self.proxy_worker = None
        else:
            if self.game.structures(UnitTypeId.ASSIMILATOR).exists:
                worker = self.game.select_build_worker(self.game.bot.strategy_manager.proxy_pylon_position)
                if worker:
                    self.proxy_worker = worker.tag
                    self.release_worker(worker.tag)
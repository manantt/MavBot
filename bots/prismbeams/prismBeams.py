import sc2, random
import argparse
import json
import math
from datetime import datetime
import numpy as np

from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.position import Point2, Point3
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.units import Units
from sc2.unit import Unit
from sc2.cache import property_cache_forever, property_cache_once_per_frame

from bots.prismbeams.strategy_manager import StrategyManager
from bots.prismbeams.worker_manager import WorkerManager

"""
TODO
no construir proxypylon hasta 50% cc
atacar edificios enemigos en mi base con 3 obreros
reservar mineral para el primer vr
construir 2º stargate en la main
no perseguir unidades más rápidas (phoenix)
si atacan la base proxy focus en los que atacan el pilón
mejorar workerrush

manejar obrero proxy
- si ataca un solo obrero atacarle mientras tenga escudo o no me esté atacando
- construir otro pilón si me van a tirar el primero mientras hay otros edificios
"""

class PrismBeams():
    def __init__(self, bot):
        self.bot = bot
        self.version = "1.0.1"
        self.deff_position = None
        self.worker_rush = False
        self.strategy_manager = StrategyManager(bot)
        self.worker_manager = WorkerManager(bot)

    async def on_step(self, iteration):
        await self.worker_manager.manage_workers()
        
        if not self.deff_position:
            self.deff_position = self.bot.start_location.towards(self.bot.mineral_field.closer_than(8, self.bot.start_location).center, 1)

        # strategy_calcs
        await self.strategy_manager.strategy_calcs()
        # train troops
        await self.train_probe()
        self.train_toops()
        
        # shield
        self.manage_shieldbatteries()
        # move troops
        await self.proxy_attack()
        # manage workers
        #await self.distribute_workers()
        # chronoboost
        await self.use_chronoboost()

    async def proxy_attack(self):
        for vr in self.bot.units(UnitTypeId.VOIDRAY):
            retreat_position = self.strategy_manager.proxy_pylon_position
            batteries = self.bot.structures(UnitTypeId.SHIELDBATTERY).filter(lambda b: b.distance_to(self.strategy_manager.proxy_pylon_position) < 20 and b.energy > 3).ready
            if batteries:
                retreat_position = batteries.closest_to(vr).position
            # attack objetive vr(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT)
            enemy_obj = await self.get_vr_attack_objetive()
            if vr.shield > 50 or vr.distance_to(retreat_position) < 1:
                if enemy_obj:
                    vr.attack(enemy_obj)
                    if isinstance(enemy_obj, Unit) and vr.distance_to(enemy_obj) <= 10 and enemy_obj.is_armored:
                        await self.use_prismatic_alignment(vr)
                    else:
                        self.cancel_prismatic_alignment(vr)
                else:
                    startx, starty = int(vr.position.x), int(vr.position.y)
                    endx, endy = int(self.bot.enemy_start_locations[0].towards(self.bot.game_info.map_center, -8).x), int(self.bot.enemy_start_locations[0].towards(self.bot.game_info.map_center, -8).y)
                    path = self.strategy_manager.get_safe_route(startx, starty, endx, endy)
                    if len(path) > 2:
                        vr.move(Point2([path[2][0], path[2][1]]))
                        if len(path) > 4:
                            vr.move(Point2([path[4][0], path[4][1]]), queue=True)
                        if len(path) > 6:
                            vr.move(Point2([path[6][0], path[6][1]]), queue=True)
                    else:
                        startx, starty = int(self.start_location.x), int(self.start_location.y)
                        path = self.strategy_manager.get_safe_route(startx, starty, endx, endy)
                        if not len(path) > 2:
                            self.strategy_manager.workers_killed = 10
            # retreat
            else:
                self.cancel_prismatic_alignment(vr)
                vr.move(retreat_position)

        for s in self.bot.units(UnitTypeId.STALKER):
            enemies = self.bot.enemy_units.closer_than(30, self.bot.start_location)
            if enemies:
                s.attack(enemies.closest_to(self.bot.start_location))
            else:
                s.move(self.deff_position)

    async def use_prismatic_alignment(self, vr):
        abilities = await self.bot.get_available_abilities(vr)
        if AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT in abilities:
            vr(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT)

    def cancel_prismatic_alignment(self, vr):
        vr(AbilityId.CANCEL_VOIDRAYPRISMATICALIGNMENT)

    async def get_vr_attack_objetive(self):
        close_distance = 18
        medium_distance = 50

        ignore_units = [
            # terran
            # protoss
            UnitTypeId.INTERCEPTOR, UnitTypeId.OBSERVER, UnitTypeId.ADEPTPHASESHIFT,
            # zerg
            UnitTypeId.LARVA, UnitTypeId.EGG, UnitTypeId.BROODLING, UnitTypeId.OVERLORD, UnitTypeId.OVERSEER, UnitTypeId.OVERLORDTRANSPORT
        ]
        ignore_structures = [
            # terran
            # protoss
            # zerg
            UnitTypeId.CREEPTUMOR,
            UnitTypeId.CREEPTUMORQUEEN,
            UnitTypeId.CREEPTUMORMISSILE,
            UnitTypeId.CREEPTUMORBURROWED
        ]
        can_attack_air_priority = [
            # terran
            UnitTypeId.BATTLECRUISER, 
            UnitTypeId.WIDOWMINE,
            UnitTypeId.WIDOWMINEBURROWED,
            UnitTypeId.RAVEN,
            UnitTypeId.CYCLONE,
            UnitTypeId.THORAP,
            UnitTypeId.MARINE,
            UnitTypeId.VIKINGFIGHTER,
            UnitTypeId.AUTOTURRET,
            UnitTypeId.GHOST,
            UnitTypeId.LIBERATOR,
            # protoss
            UnitTypeId.MOTHERSHIP,
            UnitTypeId.VOIDRAY,
            UnitTypeId.CARRIER,
            UnitTypeId.TEMPEST,
            UnitTypeId.STALKER,
            UnitTypeId.PHOENIX,
            UnitTypeId.ARCHON,
            UnitTypeId.SENTRY,
            UnitTypeId.HIGHTEMPLAR,
            # zerg
            UnitTypeId.INFESTEDTERRAN,
            UnitTypeId.MUTALISK,
            UnitTypeId.HYDRALISK,
            UnitTypeId.RAVAGER,
            UnitTypeId.QUEEN,
            UnitTypeId.INFESTOR,
            UnitTypeId.CORRUPTOR,
            UnitTypeId.VIPER,
            UnitTypeId.HYDRALISKBURROWED,
            UnitTypeId.QUEENBURROWED,
        ]
        can_attack_ground_priority = [
            # terran
            UnitTypeId.SIEGETANKSIEGED,
            UnitTypeId.MARAUDER,
            UnitTypeId.VIKINGASSAULT,
            UnitTypeId.SIEGETANK,
            UnitTypeId.BANSHEE,
            UnitTypeId.REAPER,
            UnitTypeId.HELLION,
            UnitTypeId.MEDIVAC,
            # protoss
            UnitTypeId.DARKTEMPLAR,
            UnitTypeId.IMMORTAL,
            UnitTypeId.DISRUPTOR,
            UnitTypeId.COLOSSUS,
            UnitTypeId.ZEALOT,
            UnitTypeId.ADEPT,
            UnitTypeId.WARPPRISM,
            # zerg
            UnitTypeId.BANELING,
            UnitTypeId.SWARMHOSTMP,
            UnitTypeId.LURKER,
            UnitTypeId.LURKERMP,
            UnitTypeId.LURKERMPBURROWED,
            UnitTypeId.BROODLORD,
            UnitTypeId.ROACH,
            UnitTypeId.ZERGLING,
            UnitTypeId.BANELINGCOCOON,
            UnitTypeId.BANELINGBURROWED,
            UnitTypeId.ZERGLINGBURROWED,
        ]
        high_treat_priority = [
            UnitTypeId.CYCLONE, UnitTypeId.VIKINGFIGHTER, UnitTypeId.VOIDRAY, 
        ]
        turrets_priority = [
            UnitTypeId.MISSILETURRET,
            UnitTypeId.PHOTONCANNON,
            UnitTypeId.SPINECRAWLER
        ]
        structures_priority = [
            # terran
            UnitTypeId.FACTORYTECHLAB, UnitTypeId.STARPORT, UnitTypeId.BUNKER, UnitTypeId.COMMANDCENTER, UnitTypeId.COMMANDCENTERFLYING, UnitTypeId.ORBITALCOMMAND, UnitTypeId.ORBITALCOMMANDFLYING, UnitTypeId.PLANETARYFORTRESS, UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED,
            # protoss
            UnitTypeId.DARKSHRINE, UnitTypeId.PYLON, UnitTypeId.NEXUS, 
            # zerg
            UnitTypeId.LURKERDEN, UnitTypeId.INFESTATIONPIT, UnitTypeId.HYDRALISKDEN, UnitTypeId.SPORECRAWLER, UnitTypeId.SPIRE, UnitTypeId.GREATERSPIRE, UnitTypeId.HATCHERY, UnitTypeId.LAIR, UnitTypeId.HIVE
        ]
        workers = [
            # terran
            UnitTypeId.MULE, UnitTypeId.SCV,
            # protoss
            UnitTypeId.PROBE,
            # zerg
            UnitTypeId.DRONE, UnitTypeId.DRONEBURROWED
        ]
        for unknown_unit in self.bot.enemy_units.filter(lambda u: u.type_id not in ignore_units + can_attack_air_priority + can_attack_ground_priority + workers):
            print(unknown_unit.type_id)
        #for unknown_unit in self.enemy_structures.filter(lambda u: u.type_id not in structures_priority + ignore_structures):
        #    print(unknown_unit.type_id)
        # priority 1: units that can attack air and are close to the pylon
        enemies = None
        for unit_type in can_attack_air_priority:
            enemies = self.bot.enemy_units.filter(lambda enemy: enemy.type_id == unit_type and enemy.distance_to(self.strategy_manager.proxy_pylon_position) < close_distance and enemy.is_visible)
            if enemies:
                enemy = min((unit1 for unit1 in enemies), key=lambda unit2: unit2.health + unit2.shield,)
                return enemy
        # priority 2: units that can't attack air and are close to the pylon
        for unit_type in can_attack_ground_priority:
            enemies = self.bot.enemy_units.filter(lambda enemy: enemy.type_id == unit_type and enemy.distance_to(self.strategy_manager.proxy_pylon_position) < close_distance and enemy.is_visible)
            if enemies:
                enemy = min((unit1 for unit1 in enemies), key=lambda unit2: unit2.health + unit2.shield,)
                return enemy
        # priority 3: units that can attack air and are in range to attack a vr
        for unit_type in can_attack_air_priority:
            enemies = self.bot.enemy_units.filter(lambda enemy: enemy.type_id == unit_type and enemy.is_visible)
            close_enemies = []
            for enemy in enemies:
                for vr in self.bot.units(UnitTypeId.VOIDRAY):
                    if enemy.distance_to(vr) < enemy.air_range + enemy.radius + vr.radius + 1 or (enemy.type_id in high_treat_priority and enemy.distance_to(vr) < close_distance):
                        close_enemies.append(enemy)
            if close_enemies:
                close_enemies = Units(close_enemies, self.bot)
                enemy = min((unit1 for unit1 in close_enemies), key=lambda unit2: unit2.health + unit2.shield,)
                return enemy
        # priority 4: scv or mule repairing a turret in range to attack a vr
        for unit_type in can_attack_air_priority:
            enemies = self.bot.enemy_units.filter(lambda enemy: enemy.type_id == unit_type and enemy.is_visible)
            close_enemies = []
            for enemy in enemies:
                for vr in self.bot.units(UnitTypeId.VOIDRAY):
                    if enemy.distance_to(vr) < enemy.air_range + enemy.radius + vr.radius or (enemy.type_id in high_treat_priority and enemy.distance_to(vr) < close_distance):
                        close_enemies.append(enemy)
            for turret in close_enemies:
                for worker_unit_type in [UnitTypeId.MULE, SCV]:
                    workers = self.bot.enemy_units.filter(lambda enemy: enemy.type_id == worker_unit_type and enemy.is_visible and worker.distance_to(turret) < 2 and worker.is_repairing)
                    if workers:
                        workers = Units(workers, self.bot)
                        enemy = min((unit1 for unit1 in workers), key=lambda unit2: unit2.health,)
                        return enemy
        # priority 5: turrets in range to attack a vr
        for unit_type in turrets_priority:
            enemies = self.bot.enemy_structures.filter(lambda enemy: enemy.type_id == unit_type and enemy.is_visible and (enemy.type_id != UnitTypeId.PHOTONCANNON or enemy.is_powered))
            close_enemies = []
            for enemy in enemies:
                for vr in self.bot.units(UnitTypeId.VOIDRAY):
                    if enemy.distance_to(vr) < enemy.air_range + enemy.radius + vr.radius:
                        close_enemies.append(enemy)
            if close_enemies:
                close_enemies = Units(close_enemies, self.bot)
                enemy = min((unit1 for unit1 in close_enemies), key=lambda unit2: unit2.health + unit2.shield,)
                return enemy
        # priority 6: workers in medium distance to a vr
        for unit_type in workers:
            enemies = self.bot.enemy_units.filter(lambda enemy: enemy.type_id == unit_type and enemy.is_visible and enemy.distance_to(self.bot.start_location) > close_distance)
            if enemies:
                if self.bot.units(UnitTypeId.VOIDRAY):
                    return enemies.closest_to(self.bot.units(UnitTypeId.VOIDRAY).center)
        if self.strategy_manager.workers_killed < 6:
            return None
        # priority 7: priority structures
        for unit_type in structures_priority:
            enemies = self.bot.enemy_structures.filter(lambda enemy: enemy.type_id == unit_type and enemy.is_visible)
            if enemies:
                return enemies.closest_to(self.strategy_manager.proxy_pylon_position)
        # priority 8: units that can attack air and are in medium distance to a vr
        for unit_type in can_attack_air_priority:
            enemies = self.bot.enemy_units.filter(lambda enemy: enemy.type_id == unit_type and enemy.is_visible and enemy.distance_to(self.bot.units(UnitTypeId.VOIDRAY).center) < medium_distance)
            if enemies:
                return enemies.closest_to(self.strategy_manager.proxy_pylon_position)
        # priority 9: units that can't attack air and are in medium distance to a vr
        for unit_type in can_attack_ground_priority:
            enemies = self.bot.enemy_units.filter(lambda enemy: enemy.type_id == unit_type and enemy.is_visible and enemy.distance_to(self.bot.units(UnitTypeId.VOIDRAY).center) < medium_distance)
            if enemies:
                return enemies.closest_to(self.strategy_manager.proxy_pylon_position)
        # priority 10: closest building
        if self.bot.enemy_structures.exclude_type(ignore_structures):
            return self.bot.enemy_structures.exclude_type(ignore_structures).closest_to(self.strategy_manager.proxy_pylon_position)
        # priority 11: find hidden base
        return await self.strategy_manager.get_obj_base()

    # train methods
    async def train_probe(self):
        for nexus in self.bot.townhalls().ready:
            # rally points
            if self.bot.supply_workers == 12:
                nexus(AbilityId.RALLY_NEXUS, list(self.bot.main_base_ramp.protoss_wall_buildings)[0])
            elif self.bot.supply_workers == 15:
                nexus(AbilityId.RALLY_NEXUS, list(self.bot.main_base_ramp.protoss_wall_buildings)[1])
            else:
                nexus(AbilityId.RALLY_NEXUS, self.bot.mineral_field.closest_to(nexus))
            # train conditions
            if not self.bot.already_pending(UnitTypeId.PYLON) and not self.bot.structures(UnitTypeId.PYLON):
                return
            if not self.bot.already_pending(UnitTypeId.GATEWAY) and not self.bot.structures(UnitTypeId.GATEWAY) and self.bot.supply_workers == 13:
                return
            if not self.bot.already_pending(UnitTypeId.CYBERNETICSCORE) and not self.bot.structures(UnitTypeId.CYBERNETICSCORE) and self.bot.supply_workers == 16:
                return
            if self.bot.supply_workers >= 17 and self.bot.structures(UnitTypeId.SHIELDBATTERY).amount < 2:
                return
            if self.bot.can_afford(UnitTypeId.PROBE) and self.bot.units(UnitTypeId.PROBE).amount < 21:
                if nexus.is_idle:
                    nexus.train(UnitTypeId.PROBE)

    def train_toops(self):
        for sg in self.bot.structures(UnitTypeId.STARGATE).ready.idle:
            if self.bot.can_afford(UnitTypeId.VOIDRAY):
                sg.train(UnitTypeId.VOIDRAY)

        if not self.bot.units(UnitTypeId.STALKER) and not self.bot.already_pending(UnitTypeId.STALKER) and self.bot.structures(UnitTypeId.CYBERNETICSCORE).ready and self.bot.structures(UnitTypeId.SHIELDBATTERY):
            for gw in self.bot.structures(UnitTypeId.GATEWAY).ready.idle:
                if self.bot.can_afford(UnitTypeId.STALKER):
                    gw.train(UnitTypeId.STALKER)

    def manage_shieldbatteries(self):
        for s in self.bot.structures(UnitTypeId.SHIELDBATTERY).filter(lambda unit: unit.energy > 0).ready:
            for unit in self.bot.units.filter(lambda unit: unit.shield_percentage < 100 and unit.distance_to(s) < 8):
                s(AbilityId.SMART, unit)
                break
            for unit in self.bot.structures.filter(lambda unit: unit.shield_percentage < 100 and unit.distance_to(s) < 8):
                s(AbilityId.SMART, unit)
                break

    async def use_chronoboost(self):
        for nexus in self.bot.townhalls().ready:
            abilities = await self.bot.get_available_abilities(nexus)
            if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                nexuses = self.bot.townhalls().ready
                stargates = self.bot.structures(UnitTypeId.STARGATE).ready
                random_building = None
                if len(stargates) > 0:
                    random_building = random.choice(stargates)
                else:
                    if not self.bot.structures(UnitTypeId.PYLON).amount == 0 and self.bot.already_pending(UnitTypeId.GATEWAY) and self.bot.supply_workers < 13:
                        random_building = random.choice(nexuses)
                    else:
                        return
                if not random_building.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                    if not random_building.is_idle:
                        nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, random_building)

    def do_worker_rush(self):
        if self.worker_rush:
            for worker in self.bot.workers:
                if worker.shield > 1 or self.bot.workers.amount > 8:
                    worker.attack(self.bot.enemy_start_locations[0])
                else:
                    enemy = self.bot.enemy_units
                    if(self.bot.enemy_units):
                        closest_enemy = self.bot.enemy_units.closest_to(worker)
                        worker.move(worker.position.towards(closest_enemy.position, -3))
                    else:    
                        worker.attack(self.bot.enemy_start_locations[0])

    ###################### EVENTS
    async def on_unit_created(self, unit):
        if not self.worker_manager.gw_worker and unit.type_id == UnitTypeId.PROBE and self.bot.structures(UnitTypeId.PYLON):
            self.worker_manager.gw_worker = unit.tag
        if not self.worker_manager.cc_worker and unit.type_id == UnitTypeId.PROBE and self.bot.supply_workers == 16:
            self.worker_manager.cc_worker = unit.tag

    async def on_unit_destroyed(self, unit_tag):
        # removes enemy units from cache
        for unitType in self.strategy_manager.cachedUnits:
            if unit_tag in self.strategy_manager.cachedUnits[unitType]:
                if unitType in ['Drone', 'SCV', 'MULE', 'Probe']:
                    self.strategy_manager.workers_killed += 1
                self.strategy_manager.cachedUnits[unitType].remove(unit_tag)

    async def on_building_construction_complete(self, structure):
        if structure.type_id == UnitTypeId.ASSIMILATOR:
            self.worker_manager.gas_fields[structure.tag] = []

from sc2.units import Units
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.constants import *
from sc2.cache import property_cache_once_per_frame
from sc2.data import Race

from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

from typing import Optional, Union  # mypy type checking
import random

# TODO: improve deffensive positions
# TODO: micro-game

class UnitManager:
    def __init__(self, game):
        self.game = game
        self.ground_deff_squad = {} # to do
        self.idle_squad = {} # to do
        self.off_squads = [] # to do
        self.off_group = []
        self.off_group2 = []
        self.distance_to_deffend = 22
        self.rush_done = False
        self.cachedUnits = {}
        self.fighter_units = {UnitTypeId.ZEALOT, UnitTypeId.STALKER, UnitTypeId.SENTRY, UnitTypeId.ARCHON, UnitTypeId.COLOSSUS, UnitTypeId.VOIDRAY, UnitTypeId.MOTHERSHIP, UnitTypeId.PHOENIX}
        self.PRIORITY_TARGET_ORDER = {
            Race.Protoss: [
                # can attack air
                {'unitid':UnitTypeId.OBSERVER, 'range':7, 'near_mothership':True}, # observer in my face
                # damaged, in range
                {'unitid':UnitTypeId.MOTHERSHIP, 'range':12, 'hp':0.4}, # omg finish that
                {'unitid':UnitTypeId.VOIDRAY, 'range':10, 'hp':0.5}, 
                {'unitid':UnitTypeId.CARRIER, 'range':10, 'hp':0.5}, 
                {'unitid':UnitTypeId.TEMPEST, 'range':10, 'hp':0.5}, 
                {'unitid':UnitTypeId.STALKER, 'range':10, 'hp':0.5}, 
                {'unitid':UnitTypeId.PHOENIX, 'range':9, 'hp':0.5}, 
                {'unitid':UnitTypeId.PHOTONCANNON, 'range':8, 'hp':0.5}, 
                {'unitid':UnitTypeId.ARCHON, 'range':8, 'hp':0.4}, # so tanky
                {'unitid':UnitTypeId.SENTRY, 'range':8, 'hp':0.5}, 
                # full hp, in range
                {'unitid':UnitTypeId.VOIDRAY, 'range':8}, 
                {'unitid':UnitTypeId.STALKER, 'range':9}, 
                {'unitid':UnitTypeId.MOTHERSHIP, 'range':8}, 
                {'unitid':UnitTypeId.PHOENIX, 'range':8}, 
                {'unitid':UnitTypeId.CARRIER, 'range':8}, 
                {'unitid':UnitTypeId.TEMPEST, 'range':8}, 
                {'unitid':UnitTypeId.HIGHTEMPLAR, 'range':8}, 
                {'unitid':UnitTypeId.PHOTONCANNON, 'range':8}, 
                {'unitid':UnitTypeId.ARCHON, 'range':8}, 
                {'unitid':UnitTypeId.SENTRY, 'range':8}, 
                # full hp, not in range
                {'unitid':UnitTypeId.VOIDRAY, 'range':20}, 
                {'unitid':UnitTypeId.STALKER, 'range':20}, 
                {'unitid':UnitTypeId.MOTHERSHIP, 'range':20}, 
                #{'unitid':UnitTypeId.PHOENIX, 'range':20}, 
                {'unitid':UnitTypeId.CARRIER, 'range':20}, 
                {'unitid':UnitTypeId.HIGHTEMPLAR, 'range':20}, 
                {'unitid':UnitTypeId.PHOTONCANNON, 'range':20}, 
                {'unitid':UnitTypeId.ARCHON, 'range':20}, 
                {'unitid':UnitTypeId.SENTRY, 'range':20}, 
                {'unitid':UnitTypeId.TEMPEST, 'range':20}, # too much range
                # cannot attack air
                {'unitid':UnitTypeId.OBSERVER, 'range':20},
                {'unitid':UnitTypeId.WARPPRISM, 'range':20},
                {'unitid':UnitTypeId.PROBE, 'range':20},
                {'unitid':UnitTypeId.DARKTEMPLAR, 'range':20},
                {'unitid':UnitTypeId.ORACLE, 'range':20},
                {'unitid':UnitTypeId.COLOSSUS, 'range':20},
                {'unitid':UnitTypeId.DISRUPTOR, 'range':20},
                {'unitid':UnitTypeId.IMMORTAL, 'range':20},
                {'unitid':UnitTypeId.ADEPT, 'range':20},
                {'unitid':UnitTypeId.ZEALOT, 'range':20},

                {'unitid':UnitTypeId.NEXUS, 'range':50},
                {'unitid':UnitTypeId.PYLON, 'range':20},
                {'unitid':UnitTypeId.PROBE, 'range':50},
            ],
            Race.Terran: [
                # can attack air
                {'unitid':UnitTypeId.RAVEN, 'range':7}, # observer in my face
                # damaged, in range
                {'unitid':UnitTypeId.BATTLECRUISER, 'range':10, 'hp':0.5}, 
                {'unitid':UnitTypeId.WIDOWMINE, 'range':10, 'hp':0.5}, 
                {'unitid':UnitTypeId.WIDOWMINEBURROWED, 'range':10, 'hp':0.5}, 
                {'unitid':UnitTypeId.CYCLONE, 'range':10, 'hp':0.5}, 
                {'unitid':UnitTypeId.THORAP, 'range':10, 'hp':0.5}, 
                {'unitid':UnitTypeId.THOR, 'range':10, 'hp':0.5}, 
                {'unitid':UnitTypeId.MARINE, 'range':10, 'hp':0.5},
                {'unitid':UnitTypeId.VIKINGFIGHTER, 'range':10, 'hp':0.5}, 
                {'unitid':UnitTypeId.AUTOTURRET, 'range':10, 'hp':0.5}, 
                {'unitid':UnitTypeId.GHOST, 'range':10, 'hp':0.5}, 
                {'unitid':UnitTypeId.MEDIVAC, 'range':8, 'hp':0.5}, # closer
                {'unitid':UnitTypeId.LIBERATOR, 'range':10, 'hp':0.5}, 
                # full hp, in range
                {'unitid':UnitTypeId.BATTLECRUISER, 'range':9}, 
                {'unitid':UnitTypeId.WIDOWMINE, 'range':9}, 
                {'unitid':UnitTypeId.WIDOWMINEBURROWED, 'range':9}, 
                {'unitid':UnitTypeId.THORAP, 'range':9}, 
                {'unitid':UnitTypeId.THOR, 'range':9}, 
                {'unitid':UnitTypeId.MARINE, 'range':9},
                {'unitid':UnitTypeId.VIKINGFIGHTER, 'range':9}, 
                {'unitid':UnitTypeId.AUTOTURRET, 'range':9}, 
                {'unitid':UnitTypeId.GHOST, 'range':9}, 
                {'unitid':UnitTypeId.CYCLONE, 'range':9}, 
                {'unitid':UnitTypeId.LIBERATOR, 'range':9}, 
                {'unitid':UnitTypeId.SCV, 'range':9, 'repairing':True},
                {'unitid':UnitTypeId.MISSILETURRET, 'range':9}, 
                {'unitid':UnitTypeId.BUNKER, 'range':9}, 
                {'unitid':UnitTypeId.MEDIVAC, 'range':8}, # closer
                # full hp, not in range
                {'unitid':UnitTypeId.BATTLECRUISER, 'range':20}, 
                {'unitid':UnitTypeId.WIDOWMINE, 'range':20}, 
                {'unitid':UnitTypeId.WIDOWMINEBURROWED, 'range':20}, 
                {'unitid':UnitTypeId.THORAP, 'range':20}, 
                {'unitid':UnitTypeId.THOR, 'range':20}, 
                {'unitid':UnitTypeId.MARINE, 'range':20},
                {'unitid':UnitTypeId.VIKINGFIGHTER, 'range':20}, 
                {'unitid':UnitTypeId.AUTOTURRET, 'range':20}, 
                {'unitid':UnitTypeId.GHOST, 'range':20}, 
                {'unitid':UnitTypeId.CYCLONE, 'range':20}, 
                {'unitid':UnitTypeId.LIBERATOR, 'range':20}, 
                {'unitid':UnitTypeId.MEDIVAC, 'range':20}, # closer
                {'unitid':UnitTypeId.BUNKER, 'range':20},
                # cannot attack air
                {'unitid':UnitTypeId.RAVEN, 'range':20},
                {'unitid':UnitTypeId.SCV, 'range':20},
                {'unitid':UnitTypeId.MULE, 'range':20},
                {'unitid':UnitTypeId.VIKINGASSAULT, 'range':20},
                {'unitid':UnitTypeId.SIEGETANKSIEGED, 'range':20},
                {'unitid':UnitTypeId.REAPER, 'range':20},
                {'unitid':UnitTypeId.MARAUDER, 'range':20},
                {'unitid':UnitTypeId.LIBERATORAG, 'range':20},
                {'unitid':UnitTypeId.HELLION, 'range':20},
                {'unitid':UnitTypeId.HELLIONTANK, 'range':20},
                {'unitid':UnitTypeId.SIEGETANK, 'range':20},
                {'unitid':UnitTypeId.BANSHEE, 'range':20},
                {'unitid':UnitTypeId.ORBITALCOMMAND, 'range':20},
                {'unitid':UnitTypeId.PLANETARYFORTRESS, 'range':20},

                {'unitid':UnitTypeId.COMMANDCENTER, 'range':50},
                {'unitid':UnitTypeId.SUPPLYDEPOT, 'range':20},
                {'unitid':UnitTypeId.SUPPLYDEPOTLOWERED, 'range':20},
                {'unitid':UnitTypeId.SCV, 'range':50},
            ],
            Race.Zerg: [
                # can attack air
                {'unitid':UnitTypeId.OVERSEER, 'range':7}, # observer in my face
                # damaged, in range
                {'unitid':UnitTypeId.INFESTEDTERRAN, 'range':9, 'hp':0.5},  
                {'unitid':UnitTypeId.MUTALISK, 'range':9, 'hp':0.5},  
                {'unitid':UnitTypeId.RAVAGER, 'range':10, 'hp':0.5}, # more range
                {'unitid':UnitTypeId.HYDRALISK, 'range':9, 'hp':0.5},  
                {'unitid':UnitTypeId.SPORECRAWLER, 'range':9, 'hp':0.5},  
                {'unitid':UnitTypeId.QUEEN, 'range':9, 'hp':0.5},  
                {'unitid':UnitTypeId.INFESTOR, 'range':9, 'hp':0.5},  
                {'unitid':UnitTypeId.CORRUPTOR, 'range':9, 'hp':0.5},  
                {'unitid':UnitTypeId.VIPER, 'range':9, 'hp':0.5},  
                #full hp, in range
                {'unitid':UnitTypeId.INFESTEDTERRAN, 'range':9},  
                {'unitid':UnitTypeId.MUTALISK, 'range':9},  
                {'unitid':UnitTypeId.RAVAGER, 'range':9},  
                {'unitid':UnitTypeId.HYDRALISK, 'range':9},  
                {'unitid':UnitTypeId.SPORECRAWLER, 'range':9},  
                {'unitid':UnitTypeId.QUEEN, 'range':9},  
                {'unitid':UnitTypeId.INFESTOR, 'range':9},  
                {'unitid':UnitTypeId.CORRUPTOR, 'range':9},  
                {'unitid':UnitTypeId.VIPER, 'range':9}, 
                # full hp, not in range
                {'unitid':UnitTypeId.INFESTEDTERRAN, 'range':20},  
                {'unitid':UnitTypeId.MUTALISK, 'range':20},  
                {'unitid':UnitTypeId.RAVAGER, 'range':20},  
                {'unitid':UnitTypeId.HYDRALISK, 'range':20},  
                {'unitid':UnitTypeId.SPORECRAWLER, 'range':20},  
                {'unitid':UnitTypeId.QUEEN, 'range':20},  
                {'unitid':UnitTypeId.INFESTOR, 'range':20},  
                {'unitid':UnitTypeId.CORRUPTOR, 'range':20},  
                {'unitid':UnitTypeId.VIPER, 'range':20}, 
                # cannot attack air
                {'unitid':UnitTypeId.DRONE, 'range':20},
                {'unitid':UnitTypeId.ZERGLING, 'range':20},
                {'unitid':UnitTypeId.BANELING, 'range':20},
                {'unitid':UnitTypeId.ROACH, 'range':20},
                {'unitid':UnitTypeId.LURKER, 'range':20},
                {'unitid':UnitTypeId.SWARMHOSTMP, 'range':20},
                {'unitid':UnitTypeId.LOCUSTMP, 'range':20},
                {'unitid':UnitTypeId.CHANGELING, 'range':20},
                {'unitid':UnitTypeId.BROODLING, 'range':20},
                {'unitid':UnitTypeId.NYDUSCANAL, 'range':20},
                {'unitid':UnitTypeId.OVERSEER, 'range':20},
                {'unitid':UnitTypeId.BROODLORD, 'range':20},
                {'unitid':UnitTypeId.SPINECRAWLER, 'range':20},
                {'unitid':UnitTypeId.OVERLORD, 'range':20},

                {'unitid':UnitTypeId.HIVE, 'range':50},
                {'unitid':UnitTypeId.LAIR, 'range':50},
                {'unitid':UnitTypeId.HATCHERY, 'range':50},
                {'unitid':UnitTypeId.DRONE, 'range':50},
            ],
        }

    async def move_troops(self):
        self.set_off_squad()
        await self.deff()
        await self.att() 
        await self.phoenix_move()
        await self.scout()
        self.checkEnemyUnits()

    def checkEnemyUnits(self):
        for enemy in self.game.enemy_units:
            if not enemy.is_structure:
                if enemy.name not in self.cachedUnits.keys():
                    self.cachedUnits.update({enemy.name: []})
                if enemy.tag not in self.cachedUnits[enemy.name]:
                    self.cachedUnits[enemy.name].append(enemy.tag)

    def worker_is_building(self, worker) -> bool:
        #Checks if the unit is an probe that is currently building.
        return worker.is_using_ability(AbilityId.PROTOSSBUILD_NEXUS) or \
            worker.is_using_ability(AbilityId.PROTOSSBUILD_PYLON) or \
            worker.is_using_ability(AbilityId.PROTOSSBUILD_ASSIMILATOR) or \
            worker.is_using_ability(AbilityId.PROTOSSBUILD_GATEWAY) or \
            worker.is_using_ability(AbilityId.PROTOSSBUILD_FORGE) or \
            worker.is_using_ability(AbilityId.PROTOSSBUILD_FLEETBEACON) or \
            worker.is_using_ability(AbilityId.PROTOSSBUILD_TWILIGHTCOUNCIL) or \
            worker.is_using_ability(AbilityId.PROTOSSBUILD_PHOTONCANNON) or \
            worker.is_using_ability(AbilityId.PROTOSSBUILD_STARGATE) or \
            worker.is_using_ability(AbilityId.PROTOSSBUILD_TEMPLARARCHIVE) or \
            worker.is_using_ability(AbilityId.PROTOSSBUILD_DARKSHRINE) or \
            worker.is_using_ability(AbilityId.PROTOSSBUILD_ROBOTICSBAY) or \
            worker.is_using_ability(AbilityId.PROTOSSBUILD_ROBOTICSFACILITY) or \
            worker.is_using_ability(AbilityId.PROTOSSBUILD_CYBERNETICSCORE) or \
            worker.is_using_ability(AbilityId.BUILD_SHIELDBATTERY) or \
            worker.is_using_ability(AbilityId.PROTOSSBUILD_CANCEL)

        # deffensive position
    @property#_cache_once_per_frame
    def deffensive_position(self):
        # deffend enemy attack
        enemyAttacking = False
        for nexus in self.game.townhalls():
            if self.game.enemy_units.amount and self.game.enemy_units.closer_than(self.distance_to_deffend, nexus.position).amount:
                enemyAttacking = True
            if self.game.enemy_structures and self.game.enemy_structures.closer_than(self.distance_to_deffend, nexus.position).amount:
                enemyStructures = True
        if(enemyAttacking):
            return self.game.enemy_units.closest_to(self.game.start_location).position
        # deffensive position
        if self.game.townhalls().amount <= 2:
            return self.game.main_base_ramp.top_center
        else:
            nexus = self.game.townhalls().first
            d = nexus.distance_to(self.game.game_info.map_center.towards(self.game.start_location, 30))
            for n in self.game.townhalls():
                if n.distance_to(self.game.game_info.map_center.towards(self.game.start_location, 30)) < d:
                    d = n.distance_to(self.game.game_info.map_center.towards(self.game.start_location, 30))
                    nexus = n
            return nexus.position.towards(self.game.game_info.map_center, 10)

    # posición hacia la que se quiere atacar
    @property#_cache_once_per_frame
    def offensive_position(self):
        enemy_buildings = self.game.enemy_structures.exclude_type(UnitTypeId.CREEPTUMOR).exclude_type(UnitTypeId.CREEPTUMORQUEEN).exclude_type(UnitTypeId.CREEPTUMORMISSILE).exclude_type(UnitTypeId.CREEPTUMORBURROWED)
        if len(enemy_buildings) > 0:
            for squad in self.off_squads:
                if squad:
                    if self.game.units.tags_in(squad):
                        center = self.game.units.tags_in(squad).center
                        return enemy_buildings.closest_to(center).position
            else:
                return enemy_buildings.closest_to(self.game.start_location).position
        else:
            return self.game.enemy_start_locations[0]

    # send idle units to deffend
    async def deff(self):
        deff_group = self.units_not_in_squad.filter(lambda unit: unit.type_id in self.fighter_units)
        await self.attack_move(deff_group, self.deffensive_position, self.game.start_location)
        #await self.sentry_deff()
        await self.game.bot.ability_manager.use_hallucination()

    async def sentry_deff(self):
        sentrys = self.game.units.filter(lambda unit: unit.type_id in {UnitTypeId.SENTRY})
        for sentry in sentrys:
            sentry.attack(self.game.main_base_ramp.top_center.towards(self.game.start_location, 2))

    async def att(self):
        for squad in self.off_squads:
            off_squad = self.game.units.tags_in(squad)
            await self.attack_move(off_squad, self.offensive_position, self.deffensive_position)

    async def phoenix_move(self):
        # todo: update to squads
        for squad in self.off_squads:
            if squad:
                ball_center = self.game.units.tags_in(squad).center
                closest_enemy_position = self.game.enemy_start_locations[0]
                enemies = self.game.enemy_units
                if enemies:
                    # attack objetive
                    attack_range = 15
                    priority = [
                        UnitTypeId.WIDOWMINEBURROWED, UnitTypeId.WIDOWMINE, UnitTypeId.CYCLONE, UnitTypeId.VIKINGFIGHTER, UnitTypeId.GHOST, UnitTypeId.RAVEN, UnitTypeId.MEDIVAC, UnitTypeId.LIBERATOR, UnitTypeId.BATTLECRUISER, UnitTypeId.BANSHEE,
                        UnitTypeId.CORRUPTOR, UnitTypeId.VIPER, UnitTypeId.MUTALISK, UnitTypeId.RAVAGER, UnitTypeId.QUEEN, UnitTypeId.HYDRALISK, UnitTypeId.INFESTOR, UnitTypeId.OVERSEER, UnitTypeId.OVERLORD, 
                        UnitTypeId.PHOENIX, UnitTypeId.CARRIER, UnitTypeId.TEMPEST, UnitTypeId.VOIDRAY, UnitTypeId.STALKER, UnitTypeId.MOTHERSHIP, UnitTypeId.OBSERVER, 
                    ]
                    for unit_type in priority:
                        enemies_of_type = self.game.enemy_units.filter(lambda unit: unit.type_id in {unit_type})
                        if enemies_of_type:
                            enemy = enemies_of_type.closest_to(ball_center)
                            #if enemy.position.distance_to(ball_center) > attack_range:
                            #    continue
                            if enemy.is_flying and enemy.is_visible:
                                for phoenix in self.game.units.filter(lambda unit: unit.type_id in {UnitTypeId.PHOENIX}):
                                    if phoenix.is_using_ability(AbilityId.GRAVITONBEAM_GRAVITONBEAM):
                                        continue
                                    phoenix.attack(enemy)
                                    return
                            else:
                                for phoenix in self.game.units.filter(lambda unit: unit.type_id in {UnitTypeId.PHOENIX}):
                                    phoenix(AbilityId.GRAVITONBEAM_GRAVITONBEAM, enemy)
                                    return
                    # stay in backline
                    closest_enemy_position = enemies.closest_to(ball_center)
                for phoenix in self.game.units.filter(lambda unit: unit.type_id in {UnitTypeId.PHOENIX}):
                    phoenix.move(ball_center.towards(closest_enemy_position, -3))
                return
        
        for phoenix in self.game.units.filter(lambda unit: unit.type_id in {UnitTypeId.PHOENIX}):
            phoenix.attack(self.deffensive_position)

    async def attack_move(self, units, attack_position, retreat_position, do_ball=False):
        if units.amount:
            combatients = units.filter(lambda e: e.shield > 0 or e.health >= e.health_max/3)
            injured = units.filter(lambda e: e.shield <= 0 and e.health < e.health_max/3)
            # retreat injured
            for i in injured:
                if i.ground_range > 1 and i.weapon_cooldown > 3:
                    i.move(retreat_position)
                else:
                    i.attack(retreat_position)
            # find best objetive
            closest_distance = 9999999
            if combatients and self.game.enemy_units and self.game.enemy_units.closer_than(20, combatients.center.position).amount:
                if self.game.units(UnitTypeId.MOTHERSHIP).amount and self.game.units(UnitTypeId.MOTHERSHIP).closer_than(20, combatients.center.position):
                    ball_center = self.game.units(UnitTypeId.MOTHERSHIP).first
                else:
                    ball_center = combatients.center
                #for unit in units: 
                #   dist = self.game.enemy_units.filter(lambda unit: unit.type_id in self.PRIORITY_TARGET_ORDER).closest_distance_to(unit)
                #   if dist < closest_distance:
                #       ball_center = unit
                if ball_center: #closest ally to enemies
                    for priority in self.PRIORITY_TARGET_ORDER[self.game.enemy_race]:
                        unit_type = priority['unitid']
                        attrange = priority['range']
                        minhp = priority['hp'] if 'hp' in priority else 1

                        enemies = self.game.enemy_units
                        if enemies:
                            enemies = enemies.closer_than(attrange, ball_center.position).filter(lambda u: u.can_be_attacked)
                        if self.game.enemy_structures:
                            enemies.extend(self.game.enemy_structures.closer_than(attrange, ball_center.position))
                        enemies = enemies.filter(lambda u: u.type_id in {unit_type})
                        enemies = enemies.filter(lambda u: u.health_max+u.shield_max == 0 or (u.health + u.shield)/(u.health_max+u.shield_max) <= minhp)
                        if('repairing' in priority):
                            enemies = enemies.filter(lambda u: u.is_repairing)

                        if enemies:
                            closest = enemies.closest_to(ball_center)
                            for unit in combatients:
                                if unit.type_id in {UnitTypeId.STALKER} and unit.weapon_cooldown > 12:
                                    unit.move(retreat_position)
                                else:
                                    unit.attack(closest)
                                    if unit.type_id in {UnitTypeId.VOIDRAY} and closest.is_armored and unit.distance_to(closest) <= 6:
                                        unit(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT)

                            return
            else:
                # regroup ball
                ball_combatients = combatients.filter(lambda u: u.type_id in {UnitTypeId.VOIDRAY, UnitTypeId.MOTHERSHIP})
                if attack_position == self.offensive_position or ball_combatients.amount >= 5:
                    dispersion = 0
                    if ball_combatients.amount:
                        for unit in ball_combatients:
                            dispersion += unit.distance_to(ball_combatients.center)
                            if unit.type_id == UnitTypeId.MOTHERSHIP:
                                dispersion += 2 * unit.distance_to(ball_combatients.center) # mothership triplicates its incluence
                        dispersion = dispersion / ball_combatients.amount
                        if dispersion > 2:
                            for unit in ball_combatients:
                                # kite to regroup
                                if unit.ground_range > 1 and unit.weapon_cooldown > 3:
                                    unit.move(ball_combatients.center)
                                else:
                                    unit.attack(ball_combatients.center)
                            return
            # default attack
            if combatients and self.game.enemy_units and self.game.enemy_units.closer_than(20, combatients.center.position).amount:
                for unit in self.game.enemy_units.closer_than(20, combatients.center.position):
                    print("Unknown unit: "+str(unit.type_id))
            if combatients.amount:
                for unit in combatients.further_than(1, attack_position):
                    unit.attack(attack_position)

    def is_in_off_squad(self, unit):
        for key in self.off_squads:
            if unit.tag in self.off_squads[key]:
                return key
        return False

    @property
    def units_not_in_squad(self):
        units = self.game.units.filter(lambda unit: unit.type_id in self.fighter_units)
        for squad in self.off_squads:
            if units:
                units = units.tags_not_in(squad)
        return units

    def set_off_squad(self):
        available_units = self.units_not_in_squad()
        if available_units:
            # check if must create a new off squad
            if not self.rush_done:
                for unit_type in self.game.bot.strategy_manager.min_to_rush:
                    if self.game.bot.strategy_manager.min_to_rush[unit_type] > 0:
                        units_of_type = available_units.filter(lambda unit: unit.type_id in {unit_type})
                        if not units_of_type or units_of_type.amount < self.game.bot.strategy_manager.min_to_rush[unit_type]:
                            return False
                self.rush_done = True
            else:
                for unit_type in self.game.bot.strategy_manager.min_to_attack:
                    if self.game.bot.strategy_manager.min_to_attack[unit_type] > 0:
                        units_of_type = available_units.filter(lambda unit: unit.type_id in {unit_type})
                        if not units_of_type or units_of_type.amount < self.game.bot.strategy_manager.min_to_attack[unit_type]:
                            return False
            # create the off squad
            new_off_squad = []
            for unit_type in self.game.bot.strategy_manager.min_to_attack:
                if self.game.bot.strategy_manager.min_to_attack[unit_type] != -1:
                    units_of_type = available_units.filter(lambda unit: unit.type_id in {unit_type})
                    for u in units_of_type:
                       new_off_squad.append(u.tag)
            self.off_squads.append(new_off_squad)
            return True

    # moves observers
    async def scout(self):
        idle_observers = self.game.units(UnitTypeId.OBSERVER)
        # give vision to combatients
        for squad in self.off_squads:
            if squad:
                off_units = self.game.units.tags_in(self.off_squads[0])
                if len(off_units) and idle_observers.amount and self.game.bot.strategy_manager.cloack_units_detected:
                    off_scout_position = off_units.center
                    off_observer = idle_observers.closest_to(off_scout_position)
                    off_observer.move(off_scout_position)
                    idle_observers.remove(off_observer)
                    break
        deff_units = self.units_not_in_squad()
        if len(deff_units) and idle_observers.amount and self.game.bot.strategy_manager.cloack_units_detected:
            deff_scout_position = deff_units.center
            deff_observer = idle_observers.closest_to(deff_scout_position)
            deff_observer.move(deff_scout_position)
            idle_observers.remove(deff_observer)
        # look for new enemy expansions
        if idle_observers.amount:
            for scout in idle_observers:
                if scout.is_idle:
                    positions_to_scout = Units([], self.game)
                    for p in self.game.expansion_locations_list:
                        if (not self.game.units.amount or not self.game.units().closer_than(10, p).amount):
                            if not self.game.enemy_units.amount or not self.game.enemy_units.closer_than(10, p).amount:
                                if not self.game.enemy_structures.exclude_type(UnitTypeId.CREEPTUMOR).exclude_type(UnitTypeId.CREEPTUMORQUEEN).exclude_type(UnitTypeId.CREEPTUMORMISSILE).exclude_type(UnitTypeId.CREEPTUMORBURROWED).amount or not self.game.enemy_structures.exclude_type(UnitTypeId.CREEPTUMOR).exclude_type(UnitTypeId.CREEPTUMORQUEEN).exclude_type(UnitTypeId.CREEPTUMORMISSILE).exclude_type(UnitTypeId.CREEPTUMORBURROWED).closer_than(10, p).amount:
                                    positions_to_scout.append(p)
                    if positions_to_scout:
                        move_to = random.choice(positions_to_scout).position
                        scout.move(move_to)
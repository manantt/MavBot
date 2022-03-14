from sc2.units import Units
from sc2.constants import *
from sc2.cache import property_cache_forever, property_cache_once_per_frame
from sc2.position import Point2

from bots.flyingball.constants import *

import math
import random
import json

class StrategyManager:
    def __init__(self, game):
        self.game = game

        # STRATEGY CONFIG
        self.wall = 0 # in progress
        self.worker_rush = False # to do
        self.cannon_rush = False # in progress
        self.dark_templar_rush = False # to do
        self.voidray_ball = True # to do

        # GENERAL STRATEGY CONFIG
        self.probe_scout = False # to do
        self.build_wall = False # to do
        self.build_cannons = False
        self.panic_deff = False
        self.build_shields = False
        self.observer_delay = 60
        self.build_ramp1_cannon = False # to do
        self.build_ramp2_cannon = False # to do
        self.observer_stretegy = OBSERVER_NORMAL # to do
        self.observer_amount = [2, 4]
        self.oracle_harass = False # to do
        self.adept_harass = False # to do
        self.phoenix_harass = False # in progress
        self.phoenix_amount = 2
        self.allucination_bait = False # to do

        # TROOPS CONFIG
        self.max_troops = {
            UnitTypeId.ZEALOT: 0,
            UnitTypeId.STALKER: 0,
            UnitTypeId.SENTRY: 0,
            UnitTypeId.IMMORTAL: 0,
            UnitTypeId.COLOSSUS: 0,
            UnitTypeId.VOIDRAY: 0,
            UnitTypeId.MOTHERSHIP: 0,
            UnitTypeId.PHOENIX: 0
        }
        self.min_to_rush = {
            UnitTypeId.ZEALOT: -1,
            UnitTypeId.STALKER: -1,
            UnitTypeId.SENTRY: -1,
            UnitTypeId.IMMORTAL: -1,
            UnitTypeId.COLOSSUS: -1,
            UnitTypeId.VOIDRAY: -1,
            UnitTypeId.MOTHERSHIP: -1,
            UnitTypeId.PHOENIX: -1
        }
        self.min_to_attack = {
            UnitTypeId.ZEALOT: -1,
            UnitTypeId.STALKER: -1,
            UnitTypeId.SENTRY: -1,
            UnitTypeId.IMMORTAL: -1,
            UnitTypeId.COLOSSUS: -1,
            UnitTypeId.VOIDRAY: -1,
            UnitTypeId.MOTHERSHIP: -1,
            UnitTypeId.PHOENIX: -1
        }
        # INGAME VARS
        self.rush_complete = False
        self.initialized = False

        self.main_ramp = None
        self.wall_completed = False
        self.cloack_units_detected = False
        self.worker_rush_detected = False # to do
        self.cannon_rush_detected = False # to do
        self.under_attack = False # to do
        # probe scout vars
        self.scout_worker = None
        
    def prepare_strat(self):
        if not self.initialized:
            self.initialized = True
            # load config
            actual_map = self.game.game_info.local_map_path
            # TODO

    async def do_strat(self):
        self.prepare_strat()
        self.check_cloacked()    
        self.do_worker_rush()

    def doing_strat(self):
        """ Returns true if an actual strategy should override general bot decision making """
        if self.cannon_rush and not self.cannon_rush_complete:
            return True
        if self.worker_rush:
            return True
        if self.wall != 0:
            return True
        return False

    def do_worker_rush(self):
        if self.worker_rush:
            n = self.game.townhalls().first
            for worker in self.game.workers:
                if worker.shield > 1 or self.game.workers.amount > 8 or worker.distance_to(n.position) < 5:
                    worker.attack(self.game.enemy_start_locations[0])
                else:
                    enemy = self.game.enemy_units
                    if(self.game.enemy_units):
                        closest_enemy = self.game.enemy_units.closest_to(worker)
                        worker.move(worker.position.towards(closest_enemy.position, -3))
                    else:    
                        worker.move(n)

    def check_cloacked(self):
        if not self.cloack_units_detected and self.game.enemy_units.filter(lambda unit: unit.is_cloaked).amount:
            self.cloack_units_detected = True

    def enemy_ramp(self):
        try:
            return min(
                (ramp for ramp in self.game.game_info.map_ramps if len(ramp.upper) in {2, 5}),
                key=lambda r: self.game.enemy_start_locations[0].distance_to(r.top_center),
            ).bottom_center
        except ValueError:
            # Hardcoded hotfix for Honorgrounds LE map, as that map has a large main base ramp with inbase natural
            return min(
                (ramp for ramp in self.game.game_info.map_ramps if len(ramp.upper) in {4, 9}),
                key=lambda r: self.game.enemy_start_locations[0].distance_to(r.top_center),
            ).bottom_center

    def enemy_natural(self):
        closest = None
        distance = math.inf
        for el in self.game.expansion_locations_list:
            if el.distance_to(self.game.enemy_start_locations[0]) > self.game.EXPANSION_GAP_THRESHOLD:
                def is_near_to_expansion(t):
                    return t.distance_to(el) < self.game.EXPANSION_GAP_THRESHOLD
                if any(map(is_near_to_expansion, self.game.townhalls)):
                    # already taken
                    continue
                startp = self.game.enemy_start_locations[0]
                d = startp.distance_to(el)
                if d is None:
                    continue
                if d < distance:
                    distance = d
                    closest = el
        return closest

    def get_intersections(self, a, b, r, map_center):
        dist_a_b = a.distance_to(b)
        if(dist_a_b >= 2*r):
            return a.towards(b, r)
        else: # two intersection points
            intersections = list(a.circle_intersection(b, 11))
            i1 = Point2(intersections[0])
            i2 = Point2(intersections[1])
            if i1.distance_to(map_center) < i2.distance_to(map_center):
                return i1
            return i2
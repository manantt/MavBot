from sc2.units import Units
from sc2.constants import *
from sc2.cache import property_cache_forever, property_cache_once_per_frame
from sc2.position import Point2, Point3
from sc2.data import Race

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

import math
import numpy as np
#import cv2

from datetime import datetime


class StrategyManager:
    def __init__(self, game):
        self.game = game
        self.cachedUnits = {}
        self.workers_killed = 0
        self.proxy_pylon_position = None
        self.enemy_main_spoted = False
        self.bases = []

    async def strategy_calcs(self):
        self.checkEnemyUnits()
        self.check_enemy_main()
        if not self.bases:
                self.bases = await self.init_bases()
        if not self.proxy_pylon_position:
            await self.choose_proxy_pylon_position()
        self.update_bases()


    def check_enemy_main(self):
        if not self.enemy_main_spoted:
            enemy_th = self.game.enemy_structures.filter(lambda u: u.type_id in [UnitTypeId.COMMANDCENTER, UnitTypeId.COMMANDCENTERFLYING, UnitTypeId.ORBITALCOMMAND, UnitTypeId.PLANETARYFORTRESS, UnitTypeId.ORBITALCOMMANDFLYING, UnitTypeId.NEXUS, UnitTypeId.HATCHERY, UnitTypeId.LAIR, UnitTypeId.HIVE])
            if enemy_th:
                enemy_th = enemy_th.closer_than(5, self.game.enemy_start_locations[0])
                if enemy_th:
                    self.enemy_main_spoted = True

    async def init_bases(self):
        bases = []
        now = datetime.now()
        for el in self.game.expansion_locations_list:
            distance = await self.game._client.query_pathing(self.game.enemy_start_locations[0], el)
            if not distance:
                distance = 0
            bases.append({"position": el, "date": now, "distance": distance})
        return bases

    def update_bases(self):
        for base in self.bases:
            units = self.game.units.filter(lambda u: u.distance_to(base["position"]) < 5)
            if units:
                base["date"] = datetime.now()

    async def get_obj_base(self):
        if not self.enemy_main_spoted:
            return self.game.enemy_start_locations[0]
        # get last unseen closest to enemy base
        closest = None
        for base in self.bases:
            if not closest:
                closest = base
            elif base["date"] < closest["date"]:
                closest = base
            elif base["date"] == closest["date"]:
                if base["distance"] < closest["distance"]:
                    closest = base
        return closest['position']

    ########## PROXY POSITION
    async def choose_proxy_pylon_position(self):
        enemy_locations = [self.game.enemy_start_locations[0]]
        closest = None
        distance = math.inf
        for el in self.game.expansion_locations_list:
            def is_near_to_expansion(t):
                return t.distance_to(el) < self.game.EXPANSION_GAP_THRESHOLD

            if any(map(is_near_to_expansion, enemy_locations)):
                # already taken
                continue

            startp = self.game.enemy_start_locations[0]
            d = await self.game._client.query_pathing(startp, el)
            if d is None:
                continue

            if d < distance:
                distance = d
                closest = el
        enemy_locations.append(closest)
        closest = None
        distance = math.inf
        for el in self.game.expansion_locations_list:
            def is_near_to_expansion(t):
                return t.distance_to(el) < self.game.EXPANSION_GAP_THRESHOLD

            if any(map(is_near_to_expansion, enemy_locations)):
                # already taken
                continue

            startp = self.game.enemy_start_locations[0]
            d = await self.game._client.query_pathing(startp, el)
            dfly = el.distance_to(startp)
            if d is None:
                continue

            if dfly < distance:
                distance = dfly
                closest = el

        self.proxy_pylon_position = closest

    ########## MEMORY
    def checkEnemyUnits(self):
        for enemy in self.game.enemy_units:
            if not enemy.is_structure:
                if enemy.name not in self.cachedUnits.keys():
                    self.cachedUnits.update({enemy.name: []})
                if enemy.tag not in self.cachedUnits[enemy.name]:
                    self.cachedUnits[enemy.name].append(enemy.tag)

    ########## PATHFINDING
    def get_safe_route(self, startx, starty, endx, endy):
        grid = Grid(matrix=self.turrets_map())
        start = grid.node(startx, starty)
        end = grid.node(endx, endy)
        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, grid)
        return path

    def turrets_map(self):
        map_data = np.copy(self.empty_map())
        self.add_enemies(map_data)
        return map_data

    def empty_map(self):
        map_data = np.zeros(
            (
                self.game.game_info.map_size[1],
                self.game.game_info.map_size[0],
                1,
            ),
            np.uint8,
        )
        map_data.fill(1)
        return map_data

    def add_enemies(self, map_data):
        pass
        """for unit in self.game.enemy_structures(set([MISSILETURRET, SPINECRAWLER])).filter(lambda t: not t.build_progress < 1):
            cv2.circle(
                map_data,
                (
                    int(unit.position[0]),
                    int(unit.position[1]),
                ),
                int(unit.radius)+int(unit.air_range)+3,
                0,
                -1,
            )
        for unit in self.game.enemy_structures(PHOTONCANNON).filter(lambda t: t.is_powered and not t.build_progress < 1):
            cv2.circle(
                map_data,
                (
                    int(unit.position[0]),
                    int(unit.position[1]),
                ),
                int(unit.radius)+int(unit.air_range)+3,
                0,
                -1,
            )
        for unit in self.game.enemy_structures(BUNKER).filter(lambda t: not t.build_progress < 1):
            cv2.circle(
                map_data,
                (
                    int(unit.position[0]),
                    int(unit.position[1]),
                ),
                int(unit.radius)+5+3,
                0,
                -1,
            )"""
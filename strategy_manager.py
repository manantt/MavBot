from sc2.units import Units
from sc2.constants import *
from sc2.cache import property_cache_forever, property_cache_once_per_frame
from sc2.position import Point2, Point3
from sc2.data import Race

import math
import random
"""     
    EphemeronLE.SC2Map
        [PYLON, Point2((130.0, 50.0))],
        [PHOTONCANNON, Point2((130.0, 48.0))],
        [PHOTONCANNON, Point2((128.0, 48.0))],
        [PHOTONCANNON, Point2((132.0, 47.0))],
        [PHOTONCANNON, Point2((126.0, 48.0))],
        [PHOTONCANNON, Point2((134.0, 46.0))],
        [PHOTONCANNON, Point2((132.0, 49.0))],
        [PHOTONCANNON, Point2((128.0, 50.0))],
        [PHOTONCANNON, Point2((126.0, 50.0))],
        [PHOTONCANNON, Point2((134.0, 48.0))],

        [PYLON, Point2((30.0, 119.0))],
        [PHOTONCANNON, Point2((30.0, 111.0))],
        [PHOTONCANNON, Point2((32.0, 111.0))],
        [PHOTONCANNON, Point2((28.0, 112.0))],
        [PHOTONCANNON, Point2((26.0, 113.0))],
        [PHOTONCANNON, Point2((34.0, 111.0))],
        [PHOTONCANNON, Point2((28.0, 110.0))],
        [PHOTONCANNON, Point2((26.0, 111.0))],
        [PHOTONCANNON, Point2((32.0, 109.0))],
        [PHOTONCANNON, Point2((34.0, 109.0))],
    AcropolisLE.SC2Map
        [PYLON, Point2((35.0, 112.0))],
        [PHOTONCANNON, Point2((35.0, 114.0))],
        [PHOTONCANNON, Point2((33.0, 115.0))],
        [PHOTONCANNON, Point2((37.0, 114.0))],
        [PHOTONCANNON, Point2((39.0, 114.0))],
        [PHOTONCANNON, Point2((31.0, 116.0))],
        [PHOTONCANNON, Point2((37.0, 112.0))],
        [PHOTONCANNON, Point2((33.0, 113.0))],
        [PHOTONCANNON, Point2((39.0, 112.0))],
        [PHOTONCANNON, Point2((31.0, 114.0))],

        [PYLON, Point2((141.0, 61.0))],
        [PHOTONCANNON, Point2((141.0, 59.0))],
        [PHOTONCANNON, Point2((143.0, 58.0))],
        [PHOTONCANNON, Point2((145.0, 58.0))],
        [PHOTONCANNON, Point2((139.0, 59.0))],
        [PHOTONCANNON, Point2((137.0, 59.0))],
        [PHOTONCANNON, Point2((143.0, 60.0))],
        [PHOTONCANNON, Point2((139.0, 61.0))],
        [PHOTONCANNON, Point2((145.0, 60.0))],
        [PHOTONCANNON, Point2((137.0, 61.0))],
    ThunderbirdLE.SC2Map
        [PYLON, Point2((46.0, 105.0))],
        [PHOTONCANNON, Point2((46.0, 107.0))],
        [PHOTONCANNON, Point2((44.0, 107.0))],
        [PHOTONCANNON, Point2((48.0, 108.0))],
        [PHOTONCANNON, Point2((50.0, 109.0))],
        [PHOTONCANNON, Point2((42.0, 107.0))],
        [PHOTONCANNON, Point2((48.0, 106.0))],
        [PHOTONCANNON, Point2((44.0, 105.0))],
        [PHOTONCANNON, Point2((50.0, 107.0))],
        [PHOTONCANNON, Point2((42.0, 105.0))],

        [PYLON, Point2((144.0, 51.0))],
        [PHOTONCANNON, Point2((144.0, 49.0))],
        [PHOTONCANNON, Point2((146.0, 50.0))],
        [PHOTONCANNON, Point2((148.0, 51.0))],
        [PHOTONCANNON, Point2((150.0, 51.0))],
        [PHOTONCANNON, Point2((142.0, 48.0))],
        [PHOTONCANNON, Point2((142.0, 50.0))],
        [PHOTONCANNON, Point2((146.0, 52.0))],
        [PHOTONCANNON, Point2((148.0, 53.0))],
        [PHOTONCANNON, Point2((150.0, 53.0))],
    DiscoBloodbathLE.SC2Map
        [PYLON, Point2((49.0, 140.0))],
        [PHOTONCANNON, Point2((47.0, 139.0))],
        [PHOTONCANNON, Point2((49.0, 138.0))],
        [PHOTONCANNON, Point2((45.0, 140.0))],
        [PHOTONCANNON, Point2((47.0, 141.0))],
        [PHOTONCANNON, Point2((45.0, 142.0))],

        [PYLON, Point2((150.0, 40.0))],
        [PHOTONCANNON, Point2((152.0, 42.0))],
        [PHOTONCANNON, Point2((154.0, 41.0))],
        [PHOTONCANNON, Point2((150.0, 43.0))],
        [PHOTONCANNON, Point2((152.0, 40.0))],
        [PHOTONCANNON, Point2((154.0, 39.0))],
    TritonLE.SC2Map
        [PYLON, Point2((84.0, 158.0))],
        [PHOTONCANNON, Point2((82.0, 158.0))],
        [PHOTONCANNON, Point2((81.0, 160.0))],
        [PHOTONCANNON, Point2((83.0, 156.0))],
        [PHOTONCANNON, Point2((80.0, 162.0))],
        [PHOTONCANNON, Point2((84.0, 154.0))],
        [PHOTONCANNON, Point2((85.0, 156.0))],
        [PHOTONCANNON, Point2((83.0, 160.0))],
        [PHOTONCANNON, Point2((82.0, 162.0))],
        [PHOTONCANNON, Point2((86.0, 154.0))],

        [PYLON, Point2((131.0, 46.0))],
        [PHOTONCANNON, Point2((133.0, 46.0))],
        [PHOTONCANNON, Point2((132.0, 48.0))],
        [PHOTONCANNON, Point2((134.0, 44.0))],
        [PHOTONCANNON, Point2((135.0, 42.0))],
        [PHOTONCANNON, Point2((131.0, 50.0))],
        [PHOTONCANNON, Point2((132.0, 44.0))],
        [PHOTONCANNON, Point2((133.0, 42.0))],
        [PHOTONCANNON, Point2((130.0, 48.0))],
        [PHOTONCANNON, Point2((129.0, 50.0))],
    WintersGateLE.SC2Map
        [PYLON, Point2((45.0, 109.0))],
        [PHOTONCANNON, Point2((45.0, 111.0))],
        [PHOTONCANNON, Point2((47.0, 110.0))],
        [PHOTONCANNON, Point2((49.0, 109.0))],
        [PHOTONCANNON, Point2((43.0, 113.0))],
        [PHOTONCANNON, Point2((41.0, 114.0))],
        [PHOTONCANNON, Point2((43.0, 111.0))],
        [PHOTONCANNON, Point2((47.0, 108.0))],
        [PHOTONCANNON, Point2((49.0, 107.0))],
        [PHOTONCANNON, Point2((41.0, 112.0))],

        [PYLON, Point2((147.0, 56.0))],
        [PHOTONCANNON, Point2((146.0, 54.0))],
        [PHOTONCANNON, Point2((144.0, 55.0))],
        [PHOTONCANNON, Point2((142.0, 56.0))],
        [PHOTONCANNON, Point2((148.0, 53.0))],
        [PHOTONCANNON, Point2((150.0, 52.0))],
        [PHOTONCANNON, Point2((145.0, 57.0))],
        [PHOTONCANNON, Point2((149.0, 55.0))],
        [PHOTONCANNON, Point2((143.0, 58.0))],
        [PHOTONCANNON, Point2((151.0, 54.0))],
    WorldofSleepersLE.SC2Map
        [PYLON, Point2((138.0, 116.0))],
        [PHOTONCANNON, Point2((139.0, 118.0))],
        [PHOTONCANNON, Point2((140.0, 116.0))],
        [PHOTONCANNON, Point2((142.0, 116.0))],
        [PHOTONCANNON, Point2((144.0, 115.0))],
        [PHOTONCANNON, Point2((138.0, 120.0))],
        [PHOTONCANNON, Point2((137.0, 118.0))],
        [PHOTONCANNON, Point2((136.0, 120.0))],
        [PHOTONCANNON, Point2((142.0, 114.0))],

        [PYLON, Point2((45.0, 52.0))],
        [PHOTONCANNON, Point2((43.0, 51.0))],
        [PHOTONCANNON, Point2((45.0, 50.0))],
        [PHOTONCANNON, Point2((47.0, 49.0))],
        [PHOTONCANNON, Point2((41.0, 52.0))],
        [PHOTONCANNON, Point2((39.0, 53.0))],
        [PHOTONCANNON, Point2((47.0, 51.0))],
        [PHOTONCANNON, Point2((43.0, 53.0))],
        [PHOTONCANNON, Point2((41.0, 54.0))],
        [PHOTONCANNON, Point2((49.0, 50.0))],
"""
class StrategyManager:
    def __init__(self, game):
        self.game = game

        # ingame vars
        self.initialized = False
        self.cloack_units_detected = False
        self.under_attack = False # to do

        # enemy/map/race depending vars
        self.build_cannons = True
        self.build_ramp1_cannon = False # to do
        self.build_ramp2_cannon = False # to do
        self.build_wall = False # to do
        self.observer_rush = False # to do
        self.ground_defenses_list = [2, 0, 0, 0] # to do
        self.worker_rush = False # to do
        self.oracle_harass = False # to do
        self.adept_harass = False # to do
        self.phoenix_harass = False # in progress
        self.allucination_bait = False # to do
        self.probe_scout = True

        # probe scout vars
        self.scout_worker = None

        # cannon rush vars
        self.cannon_rush = True # in progress
        self.cannon_rush_failed = False # to do
        self.cannon_rush_complete = False
        self.cannon_rush_worker = None
        self.cannon_rush_worker_position = Point2()
        self.building_positions = None
        self.start_hidden = True
        self.visible_complete = False
        self.ladder_maps_building_position = { # in progress
            "AcropolisLE.SC2Map": [
                [  # top
                    [PYLON, Point2((52.0, 135.0))],
                    [PHOTONCANNON, Point2((46.0, 133.0))],
                    [PHOTONCANNON, Point2((47.0, 131.0))],
                    [PYLON, Point2((46.0, 135.0))],
                    [PHOTONCANNON, Point2((40.0, 137.0))],
                    [PHOTONCANNON, Point2((40.0, 135.0))],
                    [PHOTONCANNON, Point2((41.0, 139.0))],
                ],
                [ # bottom
                    [PYLON, Point2((124.0, 37.0))],
                    [PHOTONCANNON, Point2((130.0, 39.0))],
                    [PHOTONCANNON, Point2((129.0, 41.0))],
                    [PYLON, Point2((130.0, 37.0))],
                    [PHOTONCANNON, Point2((136.0, 35.0))],
                    [PHOTONCANNON, Point2((136.0, 37.0))],
                    [PHOTONCANNON, Point2((136.0, 39.0))],
                ]
            ],
            "DiscoBloodbathLE.SC2Map": [
                [  # top
                    [PYLON, Point2((54.0, 129.0))],
                    [PHOTONCANNON, Point2((49.0, 126.0))],
                    [PYLON, Point2((50.0, 124.0))],
                    [PHOTONCANNON, Point2((52.0, 124.0))],
                    [PHOTONCANNON, Point2((44.0, 122.0))],
                    [PHOTONCANNON, Point2((45.0, 120.0))],
                    [PHOTONCANNON, Point2((47.0, 119.0))],
                ],
                [ # bottom
                    [PYLON, Point2((146.0, 51.0))],
                    [PHOTONCANNON, Point2((151.0, 54.0))],
                    [PHOTONCANNON, Point2((147.0, 57.0))],
                    [PYLON, Point2((149.0, 56.0))],
                    [PHOTONCANNON, Point2((154.0, 60.0))],
                    [PHOTONCANNON, Point2((155.0, 58.0))],
                    [PHOTONCANNON, Point2((152.0, 61.0))],
                ]
            ],
            "EphemeronLE.SC2Map": [
                [  # top
                    [PYLON, Point2((112.0, 30.0))],
                    [PHOTONCANNON, Point2((117.0, 27.0))],
                    [PHOTONCANNON, Point2((118.0, 29.0))],
                    [PYLON, Point2((118.0, 31.0))],
                    [PHOTONCANNON, Point2((124.0, 30.0))],
                    [PHOTONCANNON, Point2((123.0, 28.0))],
                    [PHOTONCANNON, Point2((122.0, 26.0))]
                ],
                [ # bottom
                    [PYLON, Point2((48.0, 130.0))],
                    [PHOTONCANNON, Point2((42.0, 128.0))],
                    [PHOTONCANNON, Point2((42.0, 130.0))],
                    [PYLON, Point2((43.0, 132.0))],
                    [PHOTONCANNON, Point2((38.0, 135.0))],
                    [PHOTONCANNON, Point2((37.0, 133.0))],
                    [PHOTONCANNON, Point2((37.0, 131.0))]
                ]
            ],
            "ThunderbirdLE.SC2Map": [
                [  # top
                    [PYLON, Point2((58.0, 131.0))],
                    [PHOTONCANNON, Point2((52.0, 131.0))],
                    [PHOTONCANNON, Point2((52.0, 129.0))],
                    [PHOTONCANNON, Point2((52.0, 132.0))],
                    [PYLON, Point2((53.0, 133.0))],
                    [PHOTONCANNON, Point2((47.0, 135.0))],
                    [PHOTONCANNON, Point2((47.0, 133.0))],
                    [PHOTONCANNON, Point2((47.0, 131.0))],
                ],
                [ # bottom
                    [PYLON, Point2((134.0, 25.0))],
                    [PHOTONCANNON, Point2((140.0, 26.0))],
                    [PHOTONCANNON, Point2((140.0, 24.0))],
                    [PYLON, Point2((140.0, 22.0))],
                    [PHOTONCANNON, Point2((146.0, 24.0))],
                    [PHOTONCANNON, Point2((146.0, 22.0))],
                    [PHOTONCANNON, Point2((146.0, 20.0))],
                ]
            ],
            "TritonLE.SC2Map": [
                [  # top
                    [PYLON, Point2((65.0, 142.0))],
                    [PHOTONCANNON, Point2((65.0, 148.0))],
                    [PHOTONCANNON, Point2((61.0, 147.0))],
                    [PYLON, Point2((63.0, 148.0))],
                    [PHOTONCANNON, Point2((61.0, 154.0))],
                    [PHOTONCANNON, Point2((59.0, 153.0))],
                    [PHOTONCANNON, Point2((58.0, 151.0))],
                ],
                [ # bottom
                    [PYLON, Point2((151.0, 62.0))],
                    [PHOTONCANNON, Point2((152.0, 56.0))],
                    [PHOTONCANNON, Point2((156.0, 58.0))],
                    [PYLON, Point2((154.0, 57.0))],
                    [PHOTONCANNON, Point2((158.0, 52.0))],
                    [PHOTONCANNON, Point2((159.0, 54.0))],
                    [PHOTONCANNON, Point2((156.0, 51.0))],
                ]
            ],
            "WintersGateLE.SC2Map":[
                [  # top
                    [PYLON, Point2((70.0, 135.0))],
                    [PHOTONCANNON, Point2((64.0, 137.0))],
                    [PHOTONCANNON, Point2((64.0, 133.0))],
                    [PYLON, Point2((64.0, 135.0))],
                    [PHOTONCANNON, Point2((58.0, 135.0))],
                    [PHOTONCANNON, Point2((58.0, 137.0))],
                    [PHOTONCANNON, Point2((58.0, 133.0))],
                ],
                [ # bottom
                    [PYLON, Point2((124.0, 25.0))],
                    [PHOTONCANNON, Point2((130.0, 25.0))],
                    [PHOTONCANNON, Point2((129.0, 29.0))],
                    [PYLON, Point2((130.0, 27.0))],
                    [PHOTONCANNON, Point2((136.0, 28.0))],
                    [PHOTONCANNON, Point2((136.0, 26.0))],
                    [PHOTONCANNON, Point2((135.0, 30.0))],
                ]
            ],
            "WorldofSleepersLE.SC2Map": [
                [  # top
                    [PHOTONCANNON, Point2((46.0, 30.0))],
                    [PHOTONCANNON, Point2((44.0, 34.0))],
                    [PYLON, Point2((45.0, 32.0))],
                    [PHOTONCANNON, Point2((40.0, 28.0))],
                    [PHOTONCANNON, Point2((39.0, 32.0))],
                    [PHOTONCANNON, Point2((39.0, 30.0))],
                ],
                [ # bottom
                    [PYLON, Point2((134.0, 133.0))],
                    [PHOTONCANNON, Point2((140.0, 135.0))],
                    [PHOTONCANNON, Point2((137.0, 138.0))],
                    [PYLON, Point2((139.0, 137.0))],
                    [PHOTONCANNON, Point2((144.0, 141.0))],
                    [PHOTONCANNON, Point2((145.0, 139.0))],
                    [PHOTONCANNON, Point2((142.0, 142.0))],
                ]
            ]
        }

        # phoenix harass vars
        self.phoenix_objetive = None

    def prepare_strat(self):
        if not self.initialized:
            self.initialized = True
            # cannon rush
            actual_map = self.game.game_info.local_map_path
            if actual_map in self.ladder_maps_building_position:
                pos = 0 if self.game.start_location.distance_to(Point2((0,0))) > self.game.enemy_start_locations[0].distance_to(Point2((0,0))) else 1
                self.building_positions = self.ladder_maps_building_position[actual_map][pos]
                #a = self.enemy_natural()
                #b = self.enemy_ramp()
                #self.building_positions = [[PYLON, self.get_intersections(a, b, 11, self.game.game_info.map_center)]]
                if self.building_positions:
                    self.cannon_rush_worker_position = self.building_positions[0][1].towards(self.game.game_info.map_center, 5)
                else:
                    self.cannon_rush_worker_position = self.game.game_info.map_center
            else:
                print("fail")
                self.cannon_rush = False
            #if True or self.game._game_info.player_races[3 - self.game.player_id] == 1: # terran
            #    self.building_positions.reverse()

    async def do_strat(self):
        self.prepare_strat()
        self.check_cloacked()    
        await self.do_cannon_rush()
        self.do_phoenix_harass()

    def doing_strat(self):
        #return True
        """ Returns true if an actual strategy should override general bot decision making """
        if self.cannon_rush and not self.cannon_rush_complete:
            return True
        return False

    async def do_cannon_rush(self):
        if self.cannon_rush:
            # train probes
            should_train_probe = False
            if self.game.can_afford(PROBE) and self.game.units(PROBE).amount == 12 and self.game.structures(PHOTONCANNON).amount == 2:
                should_train_probe = True
            if self.game.can_afford(PROBE) and self.game.structures(PHOTONCANNON).amount / 2 > self.game.units(PROBE).amount - 12:
                should_train_probe = True
            if self.game.can_afford(PROBE) and self.game.structures(PHOTONCANNON).amount > 17 and self.game.units(PROBE).amount < 100:
                should_train_probe = True
            if should_train_probe:
                for nexus in self.game.townhalls().ready.idle:
                    self.game.do(nexus.train(PROBE))
                    break
            # select one worker
            worker = self.game.units(PROBE).find_by_tag(self.cannon_rush_worker)
            if not worker:
                self.cannon_rush_worker = self.game.units(PROBE).random.tag
                worker = self.game.units(PROBE).find_by_tag(self.cannon_rush_worker)
                # move to position
                self.game.combined_actions.append(worker.move(self.cannon_rush_worker_position))
            # place first pylon
            if not self.game.structures(PYLON).amount and self.game.can_afford(PYLON) and not self.game.already_pending(PYLON):
                await self.game.build(PYLON, near=self.game.townhalls().first.position.towards(self.game.game_info.map_center, 7))
            # build forge
            if self.game.structures(PYLON).ready.amount and self.game.can_afford(FORGE) and not self.game.structures(FORGE).amount and not self.game.already_pending(FORGE):
                await self.game.build(FORGE, near=self.game.structures(PYLON).ready.random.position.towards(self.game.game_info.map_center, 4))
            if self.game.structures(FORGE).amount:
                # build cheese buildings
                self.cannon_rush_complete = False
                pending_building = False
                could_place_building = False
                for building in self.building_positions:
                    could_place_building = False
                    if not self.game.structures(building[0]).amount or not self.game.structures(building[0]).closer_than(1, building[1]).amount:
                        if self.game.can_afford(building[0]) and self.game.can_place(building[0], building[1]):
                            if building[0] != PHOTONCANNON or self.game.structures(PYLON).filter(lambda unit: unit.distance_to(building[1]) < 6.5).amount:
                                if not pending_building or building[0] == PHOTONCANNON:
                                    self.game.do(worker.build(building[0], building[1]))
                                    could_place_building = True
                                    if not building[1] == self.building_positions[len(self.building_positions)-1]:
                                        pending_building = True
                                    break
                                else:
                                    pending_building = True
                            else:
                                pending_building = True
                        else:
                            pending_building = True
                    else:
                        if not building[1] == self.building_positions[len(self.building_positions)-1]:
                            could_place_building = True
                if not could_place_building:
                    pending_building = True
                if not pending_building or self.game.minerals > 750:
                    self.cannon_rush_complete = True
                if not self.game.already_pending(PHOTONCANNON) and not self.game.already_pending(PYLON):
                    for probe in self.game.units(PROBE).filter(lambda unit: unit.shield < unit.shield_max):
                        enemy_units = self.game.enemy_units.filter(lambda unit: unit.distance_to(probe) < unit.ground_range + 1)
                        if enemy_units:
                            if self.game.units(PHOTONCANNON).amount:
                                self.game.do(probe.move(self.cannon_rush_worker_position.towards(probe.position, 2)))
                            else:
                                self.game.do(probe.move(self.game.townhalls().first))
            # to do: check if strategy failed

    def check_cloacked(self):
        if not self.cloack_units_detected and self.game.enemy_units.filter(lambda unit: unit.is_cloaked).amount:
            self.cloack_units_detected = True

    @property
    def ground_defenses(self):
        return {
            ZEALOT: self.ground_defenses_array[0],
            STALKER: self.ground_defenses_array[1],
            SENTRY: self.ground_defenses_array[2],
            IMMORTAL: self.ground_defenses_array[3],
        }

    def find_phoenix_objetive(self):
        enemy_bases = self.game.enemy_structures.filter(lambda unit: unit.type_id in {NEXUS, COMMANDCENTER, HATCHERY})
        if enemy_bases:
            return enemy_bases.furthest_to(self.game.enemy_start_locations[0]).position.towards(self.game.game_info.map_center, -10)
        return self.game.enemy_start_locations[0].position.towards(self.game.game_info.map_center, -10)

    def do_phoenix_harass(self):
        if self.phoenix_harass:
            # go in
            if self.game.units(PHOENIX).amount >= 2 and (self.game.units(PHOENIX).filter(lambda unit: unit.energy > 50).amount or self.game.enemy_units.filter(lambda unit: unit.has_buff(GRAVITONBEAM))):
                if not self.phoenix_objetive:
                    self.phoenix_objetive = self.find_phoenix_objetive()
                first_phoenix = self.game.units(PHOENIX).closest_to(self.phoenix_objetive)
                near_enemies = self.game.enemy_units.filter(lambda unit: unit.can_attack_air and unit.distance_to(first_phoenix) < unit.air_range + 2)
                for p in self.game.units(PHOENIX):
                    if p.is_using_ability(GRAVITONBEAM_GRAVITONBEAM):
                        continue
                    turrets = self.game.enemy_structures.filter(lambda unit: unit.type_id in {SPORECRAWLER, MISSILETURRET, PHOTONCANNON})
                    for t in turrets:
                        if p.distance_to(t) < t.air_range + 2:
                            self.game.combined_actions.append(p.move(t.position.towards(p, -t.air_range-2)))
                            continue
                    if not near_enemies.amount:
                        if p.distance_to(self.phoenix_objetive) > 5:
                            if p.distance_to(self.game.units(PHOENIX).center) > 2:
                                self.game.combined_actions.append(p.move(self.game.units(PHOENIX).center))
                            else:
                                self.game.combined_actions.append(p.move(self.phoenix_objetive))
                        else:
                            enemy_workers = self.game.enemy_units.filter(lambda unit: unit.type_id in {PROBE, DRONE, SCV})
                            if enemy_workers:
                                floating_worker = enemy_workers.filter(lambda unit: unit.has_buff(GRAVITONBEAM))
                                if floating_worker:
                                    self.game.combined_actions.append(p.attack(floating_worker.first))
                                else:
                                    self.game.do(p(AbilityId.GRAVITONBEAM_GRAVITONBEAM, enemy_workers.closest_to(p)))
                                    break
                    if near_enemies.amount == 1:
                        # todo: attack it
                        if near_enemies.first.has_buff(GRAVITONBEAM):
                            self.game.combined_actions.append(p.attack(near_enemies.first))
                        elif near_enemies.first.is_flying and near_enemies.first.is_visible:
                            self.game.combined_actions.append(p.attack(near_enemies.first))
                        elif not near_enemies.first.is_massive and near_enemies.first.is_visible:
                            if p.distance_to(near_enemies.first) > 5:
                                self.game.combined_actions.append(p.move(near_enemies.first.position.towards(p.position, 4.5)))
                            else:
                                self.game.do(p(AbilityId.GRAVITONBEAM_GRAVITONBEAM, near_enemies.first))
                                break
                        else:
                            self.game.combined_actions.append(p.move(self.phoenix_objetive))
                    if near_enemies.amount > 1:
                        closest = near_enemies.closest_to(p)
                        self.game.combined_actions.append(p.move(p.position.towards(closest.position, -9.5)))
                        # run away kitting air units
            else:
                self.phoenix_objetive = None
                # go back
                for p in self.game.units(PHOENIX):
                    if p.distance_to(self.game.start_location.position) > 20:
                        self.game.combined_actions.append(p.move(self.game.start_location.position))

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
        for el in self.game.expansion_locations:
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
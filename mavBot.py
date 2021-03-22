import sc2, random
import argparse
import json
from datetime import datetime

from WorkerRushBot import WorkerRushBot

from sc2 import run_game, maps, Race, Difficulty, position
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.position import Point2, Point3
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId

from unit_manager import UnitManager
from upgrade_manager import UpgradeManager
from build_manager import BuildManager
from train_manager import TrainManager
from ability_manager import AbilityManager
from worker_manager import WorkerManager
#from debug_manager import DebugManager
from strategy_manager import StrategyManager

class MavBot(sc2.BotAI):
    def __init__(self):
        self.version = "1.3.1"
        self.opp_id = self.find_opp_id()
        self.unit_manager = UnitManager(self)
        self.upgrade_manager = UpgradeManager(self)
        self.build_manager = BuildManager(self)
        self.train_manager = TrainManager(self)
        self.ability_manager = AbilityManager(self)
        self.worker_manager = WorkerManager(self)
        #self.debug_manager = DebugManager(self)
        self.strategy_manager = StrategyManager(self)
        self.debug = False
        self.load_config()
        self.combined_actions = [];

    async def on_step(self, iteration):
        if iteration == 1:
            await self.on_1st_step()
        if iteration % 10 == 0:
            await self.on_10_step()
        if iteration < 500:
            self.check_worker_rush()
        self.cancel_buildings()
        await self.strategy_manager.do_strat()
        if not self.strategy_manager.doing_strat():
            await self.train_manager.train_troops()
            await self.build_manager.build()
            await self.unit_manager.move_troops()
            await self.ability_manager.use_abilities()
            self.upgrade_manager.research_upgrades()
        """await self._do_actions(self.combined_actions)
        self.combined_actions.clear()"""
        #await self.debug_manager.draw_debug()

    async def on_1st_step(self):
        await self._client.chat_send(self.version, team_only=False)
<<<<<<< HEAD
        print(self.opponent_id)
=======
        print(datetime.now())
        print(self.opp_id)
        print("----------")
>>>>>>> b5b0ae38d6eef772219f122e463df6c48f9e7c4b

    async def on_10_step(self):
        await self.worker_manager.manage_workers()

    async def on_unit_destroyed(self, unit_tag):
        # removes units from offensive groups when destroyed
        for unit in self.unit_manager.off_group:
            if unit == unit_tag:
                self.unit_manager.off_group.remove(unit)
        # removes enemy units from cache
        for unitType in self.unit_manager.cachedUnits:
            if unit_tag in self.unit_manager.cachedUnits[unitType]:
                self.unit_manager.cachedUnits[unitType].remove(unit_tag)

<<<<<<< HEAD
    async def on_building_construction_started(self, unit):
        pass
        if(unit.type_id in [PYLON, PHOTONCANNON, NEXUS]):
            print(unit.type_id)
            print(unit.position)
            print("---------")
=======
    #async def on_building_construction_started(self, unit):
    #    pass
    #    if(unit.type_id in [PYLON, PHOTONCANNON, NEXUS]):
    #        print(unit.type_id)
    #        print(unit.position)
    #        print("---------")
>>>>>>> b5b0ae38d6eef772219f122e463df6c48f9e7c4b

    def on_end(self, game_result):
        print(game_result)
        print(self.state.score.score)

    def cancel_buildings(self):
        #find the buildings that are building, and have low health.
        for building in self.units.filter(lambda b: b.build_progress < 1 and b.health + b.shield < 21 and b.shield < b.health):
            self.combined_actions.append(building(CANCEL))

    def find_opp_id(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--OpponentId', type=str, nargs="?", help='Opponent Id')
        args, unknown = parser.parse_known_args()
        if args.OpponentId:
            return args.OpponentId
        return None

    def check_worker_rush(self):
        if self.enemy_units.filter(lambda u: u.type_id in {PROBE, DRONE, SCV}).amount > 2:
            if self.enemy_units.filter(lambda u: u.type_id in {PROBE, DRONE, SCV}).closer_than(8, self.start_location).amount > 2:
                self.strategy_manager.worker_rush = True

    def load_config(self):
        opp_id = self.opp_id #"d563cb5d-2794-449c-8587-3673bb96f6f3"
        conf_file = 'data/conf.json'
        config = None
        # load conf
        with open(conf_file) as json_file:
            config_all = json.load(json_file)
            # debug 
            if opp_id in config_all:
                print("found")
                config = config_all[opp_id]
            else:
                config = config_all["default"]
                #if opp_id:
                #    config_all[opp_id] = config
                #    with open(conf_file, 'w') as outfile:
                #        json.dump(config_all, outfile)
        if config:
            self.strategy_manager.wall = config["wall"]
            self.strategy_manager.ground_defenses_list = config["ground_defenses"]
            self.strategy_manager.phoenix_harass = config["phoenix_rush_vulnerable"]
            self.strategy_manager.min_off_vr_rush = config["void_rush"]
            self.strategy_manager.min_off_vr = config["void_off"]
            self.strategy_manager.observer_delay = config["observer_delay"]
            self.strategy_manager.panic_deff = config["panic_deff"]
            self.strategy_manager.build_mothership = config["mothership"]
            self.strategy_manager.worker_rush = config["worker_rush_vulnerable"]

if __name__ == "__main__":
    mapsS8 = [
        "AcropolisLE",
        "DiscoBloodbathLE",
        "EphemeronLE",
        "ThunderbirdLE",
        "TritonLE",
        "WintersGateLE",
        "WorldofSleepersLE",
    ]
    run_game(
        maps.get("DeathAura505"),
        [  # random.choice(mapsS8)), [
            Bot(Race.Protoss, MavBot()),
            #Bot(Race.Protoss, WorkerRushBot()),
            Computer(
<<<<<<< HEAD
                Race.Zerg, Difficulty.VeryHard
=======
                Race.Zerg, Difficulty.VeryEasy
>>>>>>> b5b0ae38d6eef772219f122e463df6c48f9e7c4b
            ),  # VeryHard CheatVision CheatMoney CheatInsane
        ],
        realtime=False,
    )

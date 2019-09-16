import sc2, random

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

# import keras

"""
TODO:
- Neural network -> decide best strategy
- Clean next expansion before expanding
- Deff ag cannon rush
- Calc %win in baserush and retret attack if necessary
- Use allucinations to scout
- More upgrades
- Deff workers against flying units
"""


class MavBot(sc2.BotAI):
    def __init__(self):
        self.unit_manager = UnitManager(self)
        self.upgrade_manager = UpgradeManager(self)
        self.build_manager = BuildManager(self)
        self.train_manager = TrainManager(self)
        self.ability_manager = AbilityManager(self)
        self.worker_manager = WorkerManager(self)
        #self.debug_manager = DebugManager(self)
        self.strategy_manager = StrategyManager(self)
        self.debug = False
        self.combined_actions = [];

    async def on_step(self, iteration):
        if iteration == 1:
            await self.on_1st_step()
        if iteration % 10 == 0:
            await self.on_10_step()
        self.strategy_manager.do_strat()
        await self.train_manager.train_troops()
        await self.build_manager.build()
        await self.unit_manager.move_troops()
        await self.ability_manager.use_abilities()
        self.upgrade_manager.research_upgrades()
        await self._do_actions(self.combined_actions)
        self.combined_actions.clear()
        #await self.debug_manager.draw_debug()


    async def on_1st_step(self):
        pass

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

    def on_end(self, game_result):
        print(game_result)
        print(self.state.score.score)

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
        maps.get("ThunderbirdLE"),
        [  # random.choice(mapsS8)), [
            Bot(Race.Protoss, MavBot()),
            Computer(
                Race.Zerg, Difficulty.CheatInsane
            ),  # VeryHard CheatVision CheatMoney CheatInsane
        ],
        realtime=False,
    )

import sc2, random
import argparse
import json
from datetime import datetime
from sc2.bot_ai import BotAI
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.position import Point2, Point3
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.unit_typeid import UnitTypeId

from bots.flyingball.unit_manager import UnitManager
from bots.flyingball.upgrade_manager import UpgradeManager
from bots.flyingball.build_manager import BuildManager
from bots.flyingball.train_manager import TrainManager
from bots.flyingball.ability_manager import AbilityManager
from bots.flyingball.worker_manager import WorkerManager
#from bots.flyingball.debug_manager import DebugManager
from bots.flyingball.strategy_manager import StrategyManager
from bots.flyingball.base_manager import BaseManager

# TODO
"""
deff worker rush
deff cannon rush
"""

class FlyingBall():
    def __init__(self, bot, strat):
        self.version = "1.5.0"
        self.bot = bot
        self.unit_manager = UnitManager(bot)
        self.upgrade_manager = UpgradeManager(bot)
        self.build_manager = BuildManager(bot)
        self.train_manager = TrainManager(bot)
        self.ability_manager = AbilityManager(bot)
        self.worker_manager = WorkerManager(bot)
        #self.debug_manager = DebugManager(bot)
        self.strategy_manager = StrategyManager(bot)
        self.base_manager = BaseManager(bot)
        self.load_config(strat)
        #self.load_config("test")
        self.debug = False

    async def on_step(self, iteration):
        if iteration % 10 == 0:
            await self.on_10_step()
        await self.strategy_manager.do_strat()
        if not self.strategy_manager.doing_strat():
            await self.train_manager.train_troops()
            await self.build_manager.build()
            await self.unit_manager.move_troops()
            await self.ability_manager.use_abilities()
            self.upgrade_manager.research_upgrades()
        #await self.debug_manager.draw_debug()

    async def on_10_step(self):
        await self.worker_manager.manage_workers()

    async def on_unit_created(self, unit):
        pass

    async def on_unit_destroyed(self, unit_tag):
        # removes units from offensive groups when destroyed
        for squad in self.unit_manager.off_squads:
            for unit in squad:
                if unit == unit_tag:
                    squad.remove(unit)
        # removes enemy units from cache
        for unitType in self.unit_manager.cachedUnits:
            if unit_tag in self.unit_manager.cachedUnits[unitType]:
                self.unit_manager.cachedUnits[unitType].remove(unit_tag)

    async def on_building_construction_started(self, unit):
        pass

    async def on_building_construction_complete(self, structure):
        pass

    def on_end(self, game_result):
        pass

    def load_config(self, strat):
        config = None
        conf_file = 'data/strategies/'+str(strat)+'.json' 
        try:
            f = open(conf_file)
            f.close()
        except IOError:
            conf_file = 'data/strategies/1.json'
        # load conf
        with open(conf_file) as json_file:
            config = json.load(json_file)
        if "troops" in config:
            for unit_type in config["troops"]:
                self.strategy_manager.max_troops[getattr(UnitTypeId, unit_type)] = config["troops"][unit_type]["max_amount"] \
                    if "max_amount" in config["troops"][unit_type] else 0
                self.strategy_manager.min_to_rush[getattr(UnitTypeId, unit_type)] = config["troops"][unit_type]["min_to_rush"] \
                    if "min_to_rush" in config["troops"][unit_type] else -1
                self.strategy_manager.min_to_attack[getattr(UnitTypeId, unit_type)] = config["troops"][unit_type]["min_to_attack"] \
                    if "min_to_attack" in config["troops"][unit_type] else -1
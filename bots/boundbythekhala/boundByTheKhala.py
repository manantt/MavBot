import sc2, random, math, argparse, json
from datetime import datetime

from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.position import Point2, Point3
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.units import Units

from bots.boundbythekhala.unit_manager import UnitManager
from bots.boundbythekhala.upgrade_manager import UpgradeManager
from bots.boundbythekhala.build_manager import BuildManager
from bots.boundbythekhala.ability_manager import AbilityManager
from bots.boundbythekhala.base_manager import BaseManager
from bots.boundbythekhala.train_manager import TrainManager
from bots.boundbythekhala.strategy_manager import StrategyManager

# TODO
"""
deff worker rush
deff cannon rush
salir del rango de ciclones
no perseguir phoenix
cambiar already_pending por placeholder (múltiples edificios a la vez)
habilidades mothership
prioridades de ataque por tipo de unidad
lógica scout utilizando basemanager
lógica de dónde atacar utilizando basemanager
bug offgroups se agrupan? 
"""

class BoundByTheKhala():
    def __init__(self, bot, strat):
        self.bot = bot
        self.initialized = False
        self.unit_manager = UnitManager(bot) #act
        self.upgrade_manager = UpgradeManager(bot)
        self.build_manager = BuildManager(bot)
        self.ability_manager = AbilityManager(bot)
        self.base_manager = BaseManager(bot)
        self.train_manager = TrainManager(bot)
        self.strategy_manager = StrategyManager(bot)
        self.load_config(strat)

    async def on_step(self, iteration):
        await self.base_manager.update_bases()
        await self.train_manager.train_troops()
        await self.build_manager.build()
        await self.unit_manager.move_troops()
        await self.ability_manager.use_abilities()
        self.upgrade_manager.research_upgrades()

    async def on_unit_created(self, unit):
        # build order probes
        if not self.build_manager.first_pylon_probe and unit.type_id == UnitTypeId.PROBE and not self.bot.structures(UnitTypeId.PYLON) and self.bot.workers.amount == 13:
            self.build_manager.first_pylon_probe = unit.tag
        elif not self.build_manager.cc_probe and unit.type_id == UnitTypeId.PROBE and self.bot.supply_used == 19:
            self.build_manager.cc_probe = unit.tag
            self.base_manager.bussy_probes.append(unit.tag)

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
        # init vespene workers list
        if structure.type_id == UnitTypeId.ASSIMILATOR:
            for base in self.base_manager.bases:
                if structure.distance_to(base.position) < 13:
                    base.vespene_worker_tags[structure.tag] = []
                    if self.bot.workers:
                        w = self.bot.workers.closest_to(structure)
                        self.base_manager.release_worker(w) # releases closest worker to start gas extraction
                    return

    # TODO: on nexus destroyed release workers

    def on_end(self, game_result):
        print(game_result)

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
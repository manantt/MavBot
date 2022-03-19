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
        # GENERAL STRATEGY CONFIG
        self.build_cannons = False
        self.observer_delay = 60
        self.observer_amount = [2, 4]
        # INGAME VARS
        self.cloack_units_detected = False
        
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
        

    async def do_strat(self):
        self.check_cloacked()    

    def check_cloacked(self):
        if not self.cloack_units_detected and self.game.enemy_units.filter(lambda unit: unit.is_cloaked).amount:
            self.cloack_units_detected = True
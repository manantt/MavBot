from sc2.units import Units
from sc2.constants import *
from sc2.cache import property_cache_forever, property_cache_once_per_frame
from sc2.position import Point2, Point3

import random

class StrategyManager:
	def __init__(self, game):
		self.game = game
		self.game_steps = [
			0, # early
			1, # 2nd nexus construction started
			2, # 1st attack group created
		]
		self.objetive_proves = [20, 64, 64]
		self.objetive_zealots = [4, 4, 4]
		self.objetive_observers = [0, 1, 2]
		self.objetive_voidrays = [31, 31, 31]
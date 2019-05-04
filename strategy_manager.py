from psc2.sc2.units import Units
from psc2.sc2.constants import *
from psc2.sc2.cache import property_cache_forever, property_cache_once_per_frame
from psc2.sc2.position import Point2, Point3

import random
"""
IN
mapa
oponente
raza

OUT
1- VR -> 2 base
2- 2 base -> VR
3- 3 base -> VR
4- 1 base -> 2 oracles -> 2 base -> VR
5- 2 base -> 2 oracles -> VR
5- 1 base -> cannons -> VR -> 2 bases
6- 2 base -> cannons -> VR 
7- 3 base -> cannons -> VR
8- worker rush
9- proxy cannons
"""
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
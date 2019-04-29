from sc2.units import Units
from sc2.constants import *
from sc2.cache import property_cache_forever, property_cache_once_per_frame
from sc2.position import Point2, Point3

import random

class DebugManager:
	def __init__(self, game):
		self.game = game

	async def draw_debug(self):
		self.debug_units()
		self.debug_deffensive_position()
		self.debug_offesinsive_group()
		self.debug_deffense_area()
		await self.game._client.send_debug()

	#get the heightmap offset.	
	@property_cache_forever
	def height_offset(self):
		nexus = self.game.units(NEXUS).ready.random
		if nexus:
			return self.getHeight(nexus.position) - nexus.position3d.z - 1
		else:
			return 130

	def debug_units(self):
		self.game._client.debug_text_2d('Ally units:', Point2([0.02, 0.015]), Point3((25, 25, 230)), 14)
		self.game._client.debug_text_screen('Enemy units:', Point2([0.2, 0.015]), Point3((230, 25, 25)), 14)
		count = 1
		for unitType in self.game.unit_manager.cachedUnits.keys():
			count += 1
			self.game._client.debug_text_2d(str(len(self.game.unit_manager.cachedUnits[unitType])) + " " + unitType, Point2([0.025, 0.005 + 0.015 * count]), Point3((40, 40, 245)), 12)
		count = 1
		for unitType in self.game.unit_manager.cachedUnits.keys():
			count += 1
			self.game._client.debug_text_2d(str(len(self.game.unit_manager.cachedUnits[unitType])) + " " + unitType, Point2([0.205, 0.005 + 0.015 * count]), Point3((245, 40, 40)), 12)

	def debug_deffensive_position(self):
		self.game._client.debug_sphere_out(self.turn3d(self.game.unit_manager.deffensive_position), 1, Point3((132, 0, 66)))

	def debug_offesinsive_group(self):
		if self.game.unit_manager.off_group.amount > 0:
			print("si")
			first_unit = self.game.unit_manager.off_group.closest_to(self.game.unit_manager.posicion_ofensiva)
			self.game._client.debug_sphere_out(first_unit.position3d, 1, Point3((230, 30, 66)))
			self.game._client.debug_sphere_out(first_unit.position3d, 10, Point3((132, 0, 66)))

	def debug_deffense_area(self):
		for nexus in self.game.units(NEXUS):
			self.game._client.debug_sphere_out(self.turn3d(nexus.position), 20, Point3((132, 0, 66)))

	def turn3d(self, p2):
		return Point3((p2.position.x, p2.position.y, self.getHeight(p2.position) - self.height_offset))

	def getHeight(self, pos):
		x = int(pos.x)
		y = int(pos.y)
		if x < 1:
			x = 1
		if y < 1:
			y = 1
		return self.game.game_info.terrain_height[x, y]

	
from psc2.sc2.units import Units
from psc2.sc2.constants import *
from psc2.sc2.cache import property_cache_forever, property_cache_once_per_frame
from psc2.sc2.position import Point2, Point3

import random
import cv2
import numpy as np

class DebugManager:
	def __init__(self, game):
		self.game = game
		self.map_image = None

	async def draw_debug(self):
		self.draw_map()
		self.debug_score()
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

	def debug_score(self):
		#self.state.score
		self.game._client.debug_text_2d("Score: " + str(self.game.state.score.score), Point2([0.4, 0.015]), Point3((245, 245, 200)), 12)

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
		if self.game.units(VOIDRAY).amount > 0:
			first_unit = self.game.units(VOIDRAY).closest_to(self.game.unit_manager.posicion_ofensiva)
			self.game._client.debug_sphere_out(first_unit.position3d, 1, Point3((230, 30, 66)))
			self.game._client.debug_sphere_out(self.turn3d(first_unit.position), 15, Point3((132, 0, 66)))
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

	@property_cache_forever
	def map(self):
		map_scale = 3
		h_min = 255
		h_max = 0
		print(self.game.state.psionic_matrix)
		for x in range(0, self.game.game_info.map_size[0] - 1):
			for y in range(0, self.game.game_info.map_size[1] - 1):
				h = self.game.game_info.terrain_height[x, y]
				if h > h_max:
					h_max = h
				if h < h_min:
					h_min = h
		multiplier = 150 / (h_max - h_min)
		map_data = np.zeros((self.game.game_info.map_size[1]*map_scale, self.game.game_info.map_size[0]*map_scale, 3), np.uint8)
		for x in range(0, self.game.game_info.map_size[0] - 1):
			for y in range(0, self.game.game_info.map_size[1] - 1):
				color = (self.game.game_info.terrain_height[x, y] - h_min) * multiplier
				cv2.rectangle(map_data, (x*map_scale, y*map_scale), (x*map_scale+map_scale, y*map_scale+map_scale), (color, color, color), -1)
		for r in self.game.game_info.map_ramps:
			for p in r.points:
				cv2.circle(map_data, (int(p[0]*map_scale), int(p[1]*map_scale)), 2, (120, 100, 100), -1)
			for p in r.upper:
				cv2.circle(map_data, (int(p[0]*map_scale), int(p[1]*map_scale)), 1, (160, 140, 140), -1)
			for p in r.lower:
				cv2.circle(map_data, (int(p[0]*map_scale), int(p[1]*map_scale)), 1, (100, 80, 80), -1)
				#cv2.line(map_data, (r.upper.x, r.upper.y),(r.lower.x, r.lower.y), 1, (200,200,200))
		return map_data

	def draw_map(self):
		map_scale = 3
		map_data = np.copy(self.map)
		# minerals
		for mineral in self.game.state.resources:
			mine_pos = mineral.position
			cv2.circle(map_data, (int(mine_pos[0]*map_scale), int(mine_pos[1]*map_scale)), int(mineral.radius+map_scale), (255, 255, 86), -1)
        # vespene
		for g in self.game.state.vespene_geyser:
			g_pos = g.position
			cv2.circle(map_data, (int(g_pos[0]*map_scale), int(g_pos[1]*map_scale)), int(g.radius+map_scale), (0, 127, 63), -1)
		# neutral units self.observation.raw_data.units
		#for unit in self.game.state.towers:
		#	cv2.circle(map_data, (int(unit.position[0]*map_scale), int(unit.position[1]*map_scale)), int(unit.radius*map_scale), (0, 250, 250), -1)
		for unit in self.game.state.destructables:
			cv2.circle(map_data, (int(unit.position[0]*map_scale), int(unit.position[1]*map_scale)), int(unit.radius*map_scale), (80, 100, 120), -1)
		# ally units
		for unit in self.game.units:
			if unit.is_structure:
				cv2.rectangle(map_data, (int(unit.position[0]*map_scale)-map_scale, int(unit.position[1]*map_scale)-map_scale), (int(unit.position[0]*map_scale+unit.radius*map_scale), int(unit.position[1]*map_scale+unit.radius*map_scale)), (0, 255, 0), -1)
			else:
				cv2.circle(map_data, (int(unit.position[0]*map_scale), int(unit.position[1]*map_scale)), int(unit.radius*map_scale), (0, 255, 0), -1)
		for unit in self.game.known_enemy_units:
			if unit.is_structure:
				cv2.rectangle(map_data, (int(unit.position[0]*map_scale)-map_scale, int(unit.position[1]*map_scale)-map_scale), (int(unit.position[0]*map_scale+unit.radius*map_scale), int(unit.position[1]*map_scale+unit.radius*map_scale)), (0, 0, 255), -1)
			else:
				cv2.circle(map_data, (int(unit.position[0]*map_scale), int(unit.position[1]*map_scale)), int(unit.radius*map_scale), (0, 0, 255), -1)
		flipped = cv2.flip(map_data, 0)
		resized = flipped#cv2.resize(flipped, dsize=None, fx=2, fy=2)
		cv2.imshow('Intel', resized)
		cv2.waitKey(1)

	
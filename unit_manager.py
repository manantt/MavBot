from sc2.units import Units
from sc2.constants import *
from sc2.cache import property_cache_once_per_frame

import random

# TODO: improve deffensive positions
# TODO: micro-game

class UnitManager:
	def __init__(self, game):
		self.game = game
		self.off_group = Units([], game)
		self.distance_to_deffend = 22
		self.cachedUnits = {}

	async def move_troops(self):
		await self.set_off()
		await self.deff()
		await self.att() 
		await self.scout()
		self.checkEnemyUnits()

	def checkEnemyUnits(self):
		for enemy in self.game.known_enemy_units:
			if not enemy.is_structure:
				if enemy.name not in self.cachedUnits.keys():
					self.cachedUnits.update({enemy.name: []})
				if enemy.tag not in self.cachedUnits[enemy.name]:
					self.cachedUnits[enemy.name].append(enemy.tag)

	# deffensive position
	@property_cache_once_per_frame
	def deffensive_position(self):
		# deffend enemy attack
		enemyAttacking = False
		for nexus in self.game.units(NEXUS):
			if self.game.known_enemy_units.closer_than(self.distance_to_deffend, nexus.position).amount > 0:
				enemyAttacking = True
			if self.game.known_enemy_structures.closer_than(self.distance_to_deffend, nexus.position).amount > 0:
				enemyStructures = True
		if(enemyAttacking):
			return self.game.known_enemy_units.closest_to(self.game.start_location).position
		# deffensive position
		if self.game.units(NEXUS).amount < 3:
			return self.game.main_base_ramp.top_center
		else:
			nexus = self.game.units(NEXUS).first
			d = nexus.distance_to(self.game.game_info.map_center)
			for n in self.game.units(NEXUS):
				if n.distance_to(self.game.game_info.map_center) < d:
					d = n.distance_to(self.game.game_info.map_center)
					nexus = n
			return nexus.position.towards(self.game.game_info.map_center, 10)

	# posición hacia la que se quiere atacar
	@property_cache_once_per_frame
	def posicion_ofensiva(self):
		if len(self.game.known_enemy_structures.exclude_type(CREEPTUMOR).exclude_type(CREEPTUMORQUEEN).exclude_type(CREEPTUMORMISSILE).exclude_type(CREEPTUMORBURROWED)) > 0 :
			return self.game.known_enemy_structures.exclude_type(CREEPTUMOR).exclude_type(CREEPTUMORQUEEN).exclude_type(CREEPTUMORMISSILE).exclude_type(CREEPTUMORBURROWED).closest_to(self.game.start_location).position
		else:
			return self.game.enemy_start_locations[0]

	# send idle units to deffend
	async def deff(self):
		for vr in self.game.units(VOIDRAY).further_than(1, self.deffensive_position):
			if vr not in self.off_group:
				await self.game.do(vr.attack(self.deffensive_position))
		for z in self.game.units(ZEALOT).further_than(1, self.deffensive_position):
			if z not in self.off_group:
				await self.game.do(z.attack(self.deffensive_position))
		if self.game.units(VOIDRAY).amount == 0 and self.game.units(ZEALOT).amount == 0 and len(self.game.known_enemy_units) > 1:
			for p in self.game.units(PROBE):
				await self.game.do(p.attack(self.deffensive_position))

	async def att(self):
		# TODO: move as one
		target = None
		if self.off_group.amount > 0:
			first_unit = self.off_group.closest_to(self.posicion_ofensiva)
			for enemy in self.game.known_enemy_units.closer_than(10, first_unit.position):
				if not enemy.is_structure:
					print(enemy.name)
		for unit in self.off_group.further_than(1, self.posicion_ofensiva):
			await self.game.do(unit.attack(self.posicion_ofensiva))

	# new offensive group conditions
	async def set_off(self):
		if self.off_group.amount == 0 and self.game.units(VOIDRAY).amount >= 2:
			for vr in self.game.units(VOIDRAY):
				self.off_group.append(vr)

	# moves observers
	async def scout(self):
		if len(self.game.units(OBSERVER)) > 0:
			for scout in self.game.units(OBSERVER):
				if scout.is_idle:
					positions_to_scout = Units([], self.game)
					for p in self.game.expansion_locations:
						if self.game.units().closer_than(10, p).amount == 0 and self.game.known_enemy_units.closer_than(10, p).amount == 0 and self.game.known_enemy_structures.exclude_type(CREEPTUMOR).exclude_type(CREEPTUMORQUEEN).exclude_type(CREEPTUMORMISSILE).exclude_type(CREEPTUMORBURROWED).closer_than(10, p).amount == 0:
							positions_to_scout.append(p)
					if positions_to_scout:
						move_to = random.choice(positions_to_scout).position
						await self.game.do(scout.move(move_to))
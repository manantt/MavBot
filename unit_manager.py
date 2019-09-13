from sc2.units import Units
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.constants import *
from sc2.cache import property_cache_once_per_frame

from typing import Optional, Union  # mypy type checking
import random

# TODO: improve deffensive positions
# TODO: micro-game

class UnitManager:
	def __init__(self, game):
		self.game = game
		self.off_group = []
		self.distance_to_deffend = 22
		self.cachedUnits = {}
		self.HIGH_PRIORITY_TARGET_ORDER = [
			STALKER, PHOENIX, WIDOWMINEBURROWED, WIDOWMINE, CYCLONE, MARINE, THOR, HYDRALISK, CORRUPTOR, LIBERATOR, VIKING, BATTLECRUISER, 
			PHOTONCANNON, MISSILETURRET, SPORECRAWLER,
			VOIDRAY, CARRIER, TEMPEST, MOTHERSHIP, SENTRY, HIGHTEMPLAR, ARCHON, MUTALISK, QUEEN, INFESTOR, GHOST
		]
		self.LOW_PRIORITY_TARGET_ORDER = [
			PROBE, SCV, DRONE, OVERLORD,
			ZERGLING, REAPER, 
			HATCHERY, COMMANDCENTER, NEXUS
		]

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
	@property#_cache_once_per_frame
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
			d = nexus.distance_to(self.game.game_info.map_center.towards(self.game.start_location, 30))
			for n in self.game.units(NEXUS):
				if n.distance_to(self.game.game_info.map_center.towards(self.game.start_location, 30)) < d:
					d = n.distance_to(self.game.game_info.map_center.towards(self.game.start_location, 30))
					nexus = n
			return nexus.position.towards(self.game.game_info.map_center, 10)

	# posición hacia la que se quiere atacar
	@property#_cache_once_per_frame
	def posicion_ofensiva(self):
		if len(self.game.known_enemy_structures.exclude_type(CREEPTUMOR).exclude_type(CREEPTUMORQUEEN).exclude_type(CREEPTUMORMISSILE).exclude_type(CREEPTUMORBURROWED)) > 0 :
			return self.game.known_enemy_structures.exclude_type(CREEPTUMOR).exclude_type(CREEPTUMORQUEEN).exclude_type(CREEPTUMORMISSILE).exclude_type(CREEPTUMORBURROWED).closest_to(self.game.start_location).position
		else:
			return self.game.enemy_start_locations[0]

	# send idle units to deffend
	async def deff(self):
		#deff_group = Units([], )
		deff_group = self.game.units.filter(lambda unit: unit.type_id in {ZEALOT, VOIDRAY}).tags_not_in(self.off_group)
		await self.attack_move(deff_group, self.deffensive_position, self.game.start_location)

	async def att(self):
		off_group = self.game.units.tags_in(self.off_group)
		await self.attack_move(off_group, self.posicion_ofensiva, self.deffensive_position)

	async def attack_move(self, units, attack_position, retreat_position):
		if units.amount > 0:
			combatients = units.filter(lambda e: e.shield > 0)
			injured = units.filter(lambda e: e.shield <= 0 and e.health < e.health_max/3)
			# retreat injured
			for i in injured:
				await self.game.do(i.move(retreat_position))
			# if there are no combatients in the attack group disolve it
			if combatients.amount == 0 and attack_position == self.posicion_ofensiva:
				self.off_group = []
				return
			# closest ally to enemies
			closest_distance = 9999999
			if self.game.known_enemy_units.filter(lambda unit: unit.type_id in self.HIGH_PRIORITY_TARGET_ORDER):
				for unit in units: #closest_distance_to
					dist = self.game.known_enemy_units.filter(lambda unit: unit.type_id in self.HIGH_PRIORITY_TARGET_ORDER).closest_distance_to(unit)
					if dist < closest_distance:
						first_unit = unit
				if first_unit:
					#first_unit = self.game.units.closest_to(attack_position)
					near_enemies = self.game.known_enemy_units.closer_than(12, first_unit.position)
					for unit_type in self.HIGH_PRIORITY_TARGET_ORDER:
						enemy = near_enemies.filter(lambda u: u.type_id in {unit_type})
						if enemy:
							closest = enemy.closest_to(first_unit)
							for unit in combatients:
								# kite
								#if unit.ground_range > 1 and unit.weapon_cooldown > 3:
								#	closest_to_unit = near_enemies.closest_to(unit)
								#	await self.game.do(unit.move(closest_to_unit.position.towards(unit.position, unit.ground_range)))
								#else:
								await self.game.do(unit.attack(closest))
							return
			# regroup ball
			if attack_position == self.posicion_ofensiva:
				dispersion = 0
				for unit in combatients:
					dispersion += unit.distance_to(combatients.center)
				dispersion = dispersion / combatients.amount
				if dispersion > 2:
					for unit in combatients:
						await self.game.do(unit.attack(combatients.center))
					return
			# default attack
			for unit in combatients.further_than(1, attack_position):
				await self.game.do(unit.attack(attack_position))

	# new offensive group conditions
	async def set_off(self):
		if len(self.off_group) == 0 and self.game.units(VOIDRAY).amount >= 12:
			for vr in self.game.units(VOIDRAY):
				self.off_group.append(vr.tag)

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

	# returns how much does a enemy ground unit have to surround a wall to reach the ally unit position
	# for example, it returns 2 if the path it must walk is the double of the straight line distance between them
	async def terrain_adventage(self, ally_unit: Union[Unit, Point2], enemy_unit: Union[Unit, Point2]) -> float:
		startp = enemy_unit
		if isinstance(startp, Unit):
			startp = startp.position
		finp = ally_unit
		if isinstance(finp, Unit):
			finp = finp.position
		return await self.game._client.query_pathing(startp, finp)

	# closest position where ally unit have an advantage against the enemy due to terrain limitations
	# advantage_type: 1=enemy can not attack, 2=only enemy first line can attack, 3=enemy is just in range, only enemy first unit can attack
	def closest_advantaged_terrain(
		self, ally_unit: Unit, enemy_unit: Unit, min_terrain_advantage=1.5, advantage_type=2, 
		walk_throug_enemies=False, max_distance=15
	) -> Optional[Point2]:
		if ally_unit.ground_range < enemy_unit.range or enemy_unit.is_flying:
			return None
		# 1- find closest terrain wall that is closer to ally unit than to enemy unit
		# 2- move the point terrain-perpendicularly backwards a distance equals to enemy range
		return Point2([100, 100])
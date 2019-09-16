from sc2.units import Units
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.constants import *
from sc2.cache import property_cache_once_per_frame
from sc2.ids.ability_id import AbilityId

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
			STALKER, PHOENIX, LIBERATOR, VIKING, BATTLECRUISER, 
			WIDOWMINEBURROWED, WIDOWMINE, CYCLONE, MARINE, THOR, 
			HYDRALISK, CORRUPTOR, 

			PHOTONCANNON, MISSILETURRET, SPORECRAWLER,

			VOIDRAY, CARRIER, TEMPEST, MOTHERSHIP, HIGHTEMPLAR, ARCHON, SENTRY, 
			GHOST,
			MUTALISK, QUEEN, INFESTOR
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
		for enemy in self.game.enemy_units:
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
		for nexus in self.game.townhalls():
			if self.game.enemy_units.amount and self.game.enemy_units.closer_than(self.distance_to_deffend, nexus.position).amount:
				enemyAttacking = True
			if self.game.enemy_structures and self.game.enemy_structures.closer_than(self.distance_to_deffend, nexus.position).amount:
				enemyStructures = True
		if(enemyAttacking):
			return self.game.enemy_units.closest_to(self.game.start_location).position
		# deffensive position
		if self.game.townhalls().amount <= 2:
			return self.game.main_base_ramp.top_center
		else:
			nexus = self.game.townhalls().first
			d = nexus.distance_to(self.game.game_info.map_center.towards(self.game.start_location, 30))
			for n in self.game.townhalls():
				if n.distance_to(self.game.game_info.map_center.towards(self.game.start_location, 30)) < d:
					d = n.distance_to(self.game.game_info.map_center.towards(self.game.start_location, 30))
					nexus = n
			return nexus.position.towards(self.game.game_info.map_center, 10)

	# posición hacia la que se quiere atacar
	@property#_cache_once_per_frame
	def posicion_ofensiva(self):
		if len(self.game.enemy_structures.exclude_type(CREEPTUMOR).exclude_type(CREEPTUMORQUEEN).exclude_type(CREEPTUMORMISSILE).exclude_type(CREEPTUMORBURROWED)) > 0 :
			return self.game.enemy_structures.exclude_type(CREEPTUMOR).exclude_type(CREEPTUMORQUEEN).exclude_type(CREEPTUMORMISSILE).exclude_type(CREEPTUMORBURROWED).closest_to(self.game.start_location).position
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

	async def attack_move(self, units, attack_position, retreat_position, do_ball=False):
		if units.amount:
			combatients = units.filter(lambda e: e.shield > 0 or e.health >= e.health_max/3)
			injured = units.filter(lambda e: e.shield <= 0 and e.health < e.health_max/3)
			# retreat injured
			for i in injured:
				if i.ground_range > 1 and i.weapon_cooldown > 3:
					self.game.combined_actions.append(i.move(retreat_position))
				else:
					self.game.combined_actions.append(i.attack(retreat_position))
			# if there are no combatients in the attack group disolve it
			if not combatients.amount:
				if attack_position == self.posicion_ofensiva:
					self.off_group = []
				return
			# find best objetive
			closest_distance = 9999999
			if self.game.enemy_units.filter(lambda unit: unit.type_id in self.HIGH_PRIORITY_TARGET_ORDER):
				for unit in units: 
					dist = self.game.enemy_units.filter(lambda unit: unit.type_id in self.HIGH_PRIORITY_TARGET_ORDER).closest_distance_to(unit)
					if dist < closest_distance:
						first_unit = unit
				if first_unit: #closest ally to enemies
					near_enemies = self.game.enemy_units.closer_than(20, first_unit.position)
					for unit_type in self.HIGH_PRIORITY_TARGET_ORDER:
						enemy = near_enemies.filter(lambda u: u.type_id in {unit_type})
						if enemy:
							closest = enemy.closest_to(first_unit)
							for unit in combatients:
								self.game.combined_actions.append(unit.attack(closest))
								if unit.type_id in {VOIDRAY}:
									self.game.combined_actions.append(unit(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT))

							return
			# regroup ball
			vr_combatients = combatients.filter(lambda u: u.type_id in {VOIDRAY})
			if attack_position == self.posicion_ofensiva or vr_combatients.amount >= 5:
				dispersion = 0
				if vr_combatients.amount:
					for unit in vr_combatients:
						dispersion += unit.distance_to(vr_combatients.center)
					dispersion = dispersion / vr_combatients.amount
					if dispersion > 2:
						for unit in vr_combatients:
							# kite to regroup
							if unit.ground_range > 1 and unit.weapon_cooldown > 3:
								self.game.combined_actions.append(unit.move(vr_combatients.center))
							else:
								self.game.combined_actions.append(unit.attack(vr_combatients.center))
						return
			# default attack
			if combatients.amount:
				for unit in combatients.further_than(1, attack_position):
					self.game.combined_actions.append(unit.attack(attack_position))

	# new offensive group conditions
	async def set_off(self):
		if len(self.off_group) == 0 and self.game.units(VOIDRAY).amount >= 12:
			for vr in self.game.units(VOIDRAY):
				self.off_group.append(vr.tag)

	# moves observers
	async def scout(self):
		idle_observers = self.game.units(OBSERVER)
		# give vision to combatients
		off_units = self.game.units.tags_in(self.off_group)
		if len(off_units) and idle_observers.amount and self.game.strategy_manager.cloack_units_detected:
			off_scout_position = off_units.center
			off_observer = idle_observers.closest_to(off_scout_position)
			self.game.combined_actions.append(off_observer.move(off_scout_position))
			idle_observers.remove(off_observer)
		deff_units = self.game.units.filter(lambda unit: unit.type_id in {VOIDRAY}).tags_not_in(self.off_group)
		if len(deff_units) and idle_observers.amount and self.game.strategy_manager.cloack_units_detected:
			deff_scout_position = deff_units.center
			deff_observer = idle_observers.closest_to(deff_scout_position)
			self.game.combined_actions.append(deff_observer.move(deff_scout_position))
			idle_observers.remove(deff_observer)
		# look for new enemy expansions
		if idle_observers.amount:
			for scout in idle_observers:
				if scout.is_idle:
					positions_to_scout = Units([], self.game)
					for p in self.game.expansion_locations:
						if (not self.game.units.amount or not self.game.units().closer_than(10, p).amount):
							if not self.game.enemy_units.amount or not self.game.enemy_units.closer_than(10, p).amount:
								if not self.game.enemy_structures.exclude_type(CREEPTUMOR).exclude_type(CREEPTUMORQUEEN).exclude_type(CREEPTUMORMISSILE).exclude_type(CREEPTUMORBURROWED).amount or not self.game.enemy_structures.exclude_type(CREEPTUMOR).exclude_type(CREEPTUMORQUEEN).exclude_type(CREEPTUMORMISSILE).exclude_type(CREEPTUMORBURROWED).closer_than(10, p).amount:
									positions_to_scout.append(p)
					if positions_to_scout:
						move_to = random.choice(positions_to_scout).position
						self.game.combined_actions.append(scout.move(move_to))

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

	# closest position where ally unit have an advantage over the enemy due to terrain limitations
	def closest_advantaged_terrain(
		self, ally_unit: Unit, enemy_unit: Unit, min_terrain_advantage=1.5, advantage_type=1, 
		walk_throug_enemie=False, max_distance=15
	) -> Optional[Point2]:
		"""
		ally_unit: the ally unit that will be positioned
		enemy_unit: the enemy unit we want to gain advantage over
		min_terrain advantage: refers to terrain_advantage() function
		advantage_type: 1=enemy can not attack, 2=only enemy first line can attack, 3=enemy is just in range, only enemy first unit can attack
		walk_throug_enemie: if False the returned position wont make the unit pass across the enemy
		max_distance: from the ally unit to the returned point
		"""
		if ally_unit.ground_range < enemy_unit.range or enemy_unit.is_flying:
			return None
		# 1- find closest terrain wall that is closer to ally unit than to enemy unit
		# 2- move the point terrain-perpendicularly backwards a distance equals to enemy range
		return Point2([100, 100])
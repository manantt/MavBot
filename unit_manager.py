from sc2.units import Units
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.constants import *
from sc2.cache import property_cache_once_per_frame
from sc2.ids.ability_id import AbilityId
from sc2 import Race

from typing import Optional, Union  # mypy type checking
import random

# TODO: improve deffensive positions
# TODO: micro-game

class UnitManager:
	def __init__(self, game):
		self.game = game
		self.ground_deff_squad = {} # to do
		self.idle_squad = {} # to do
		self.off_squads = [] # to do
		self.off_group = []
		self.off_group2 = []
		self.distance_to_deffend = 22
		self.cachedUnits = {}
		self.PRIORITY_TARGET_ORDER = {
			Race.Protoss: [
				# can attack air
				{'unitid':OBSERVER, 'range':7, 'near_mothership':True}, # observer in my face
				# damaged, in range
				{'unitid':MOTHERSHIP, 'range':12, 'hp':0.4}, # omg finish that
				{'unitid':VOIDRAY, 'range':10, 'hp':0.5}, 
				{'unitid':CARRIER, 'range':10, 'hp':0.5}, 
				{'unitid':TEMPEST, 'range':10, 'hp':0.5}, 
				{'unitid':STALKER, 'range':10, 'hp':0.5}, 
				{'unitid':PHOENIX, 'range':9, 'hp':0.5}, 
				{'unitid':PHOTONCANNON, 'range':8, 'hp':0.5}, 
				{'unitid':ARCHON, 'range':8, 'hp':0.4}, # so tanky
				{'unitid':SENTRY, 'range':8, 'hp':0.5}, 
				# full hp, in range
				{'unitid':VOIDRAY, 'range':8}, 
				{'unitid':STALKER, 'range':9}, 
				{'unitid':MOTHERSHIP, 'range':8}, 
				{'unitid':PHOENIX, 'range':8}, 
				{'unitid':CARRIER, 'range':8}, 
				{'unitid':TEMPEST, 'range':8}, 
				{'unitid':HIGHTEMPLAR, 'range':8}, 
				{'unitid':PHOTONCANNON, 'range':8}, 
				{'unitid':ARCHON, 'range':8}, 
				{'unitid':SENTRY, 'range':8}, 
				# full hp, not in range
				{'unitid':VOIDRAY, 'range':20}, 
				{'unitid':STALKER, 'range':20}, 
				{'unitid':MOTHERSHIP, 'range':20}, 
				{'unitid':PHOENIX, 'range':20}, 
				{'unitid':CARRIER, 'range':20}, 
				{'unitid':HIGHTEMPLAR, 'range':20}, 
				{'unitid':PHOTONCANNON, 'range':20}, 
				{'unitid':ARCHON, 'range':20}, 
				{'unitid':SENTRY, 'range':20}, 
				{'unitid':TEMPEST, 'range':20}, # too much range
				# cannot attack air
				{'unitid':OBSERVER, 'range':20},
				{'unitid':WARPPRISM, 'range':20},
				{'unitid':PROBE, 'range':20},
				{'unitid':DARKTEMPLAR, 'range':20},
				{'unitid':ORACLE, 'range':20},
				{'unitid':COLOSSUS, 'range':20},
				{'unitid':DISRUPTOR, 'range':20},
				{'unitid':IMMORTAL, 'range':20},
				{'unitid':ADEPT, 'range':20},
				{'unitid':ZEALOT, 'range':20},

				{'unitid':NEXUS, 'range':50},
				{'unitid':PYLON, 'range':20},
				{'unitid':PROBE, 'range':50},
			],
			Race.Terran: [
				# can attack air
				{'unitid':RAVEN, 'range':7}, # observer in my face
				# damaged, in range
				{'unitid':BATTLECRUISER, 'range':10, 'hp':0.5}, 
				{'unitid':WIDOWMINE, 'range':10, 'hp':0.5}, 
				{'unitid':WIDOWMINEBURROWED, 'range':10, 'hp':0.5}, 
				{'unitid':CYCLONE, 'range':10, 'hp':0.5}, 
				{'unitid':THORAP, 'range':10, 'hp':0.5}, 
				{'unitid':THOR, 'range':10, 'hp':0.5}, 
				{'unitid':MARINE, 'range':10, 'hp':0.5},
				{'unitid':VIKINGFIGHTER, 'range':10, 'hp':0.5}, 
				{'unitid':AUTOTURRET, 'range':10, 'hp':0.5}, 
				{'unitid':GHOST, 'range':10, 'hp':0.5}, 
				{'unitid':MEDIVAC, 'range':8, 'hp':0.5}, # closer
				{'unitid':LIBERATOR, 'range':10, 'hp':0.5}, 
				# full hp, in range
				{'unitid':BATTLECRUISER, 'range':9}, 
				{'unitid':WIDOWMINE, 'range':9}, 
				{'unitid':WIDOWMINEBURROWED, 'range':9}, 
				{'unitid':THORAP, 'range':9}, 
				{'unitid':THOR, 'range':9}, 
				{'unitid':MARINE, 'range':9},
				{'unitid':VIKINGFIGHTER, 'range':9}, 
				{'unitid':AUTOTURRET, 'range':9}, 
				{'unitid':GHOST, 'range':9}, 
				{'unitid':CYCLONE, 'range':9}, 
				{'unitid':LIBERATOR, 'range':9}, 
				{'unitid':MISSILETURRET, 'range':9}, 
				{'unitid':BUNKER, 'range':9}, 
				{'unitid':MEDIVAC, 'range':8}, # closer
				# full hp, not in range
				{'unitid':BATTLECRUISER, 'range':20}, 
				{'unitid':WIDOWMINE, 'range':20}, 
				{'unitid':WIDOWMINEBURROWED, 'range':20}, 
				{'unitid':THORAP, 'range':20}, 
				{'unitid':THOR, 'range':20}, 
				{'unitid':MARINE, 'range':20},
				{'unitid':VIKINGFIGHTER, 'range':20}, 
				{'unitid':AUTOTURRET, 'range':20}, 
				{'unitid':GHOST, 'range':20}, 
				{'unitid':CYCLONE, 'range':20}, 
				{'unitid':LIBERATOR, 'range':20}, 
				{'unitid':MEDIVAC, 'range':20}, # closer
				{'unitid':BUNKER, 'range':20},
				# cannot attack air
				{'unitid':RAVEN, 'range':20},
				{'unitid':SCV, 'range':20},
				{'unitid':MULE, 'range':20},
				{'unitid':VIKINGASSAULT, 'range':20},
				{'unitid':SIEGETANKSIEGED, 'range':20},
				{'unitid':REAPER, 'range':20},
				{'unitid':MARAUDER, 'range':20},
				{'unitid':LIBERATORAG, 'range':20},
				{'unitid':HELLION, 'range':20},
				{'unitid':HELLIONTANK, 'range':20},
				{'unitid':SIEGETANK, 'range':20},
				{'unitid':BANSHEE, 'range':20},
				{'unitid':ORBITALCOMMAND, 'range':20},
				{'unitid':PLANETARYFORTRESS, 'range':20},

				{'unitid':COMMANDCENTER, 'range':50},
				{'unitid':SUPPLYDEPOT, 'range':20},
				{'unitid':SUPPLYDEPOTLOWERED, 'range':20},
				{'unitid':SCV, 'range':50},
			],
			Race.Zerg: [
				# can attack air
				{'unitid':OVERSEER, 'range':7}, # observer in my face
				# damaged, in range
				{'unitid':INFESTEDTERRAN, 'range':9, 'hp':0.5},  
				{'unitid':MUTALISK, 'range':9, 'hp':0.5},  
				{'unitid':RAVAGER, 'range':10, 'hp':0.5}, # more range
				{'unitid':HYDRALISK, 'range':9, 'hp':0.5},  
				{'unitid':SPORECRAWLER, 'range':9, 'hp':0.5},  
				{'unitid':QUEEN, 'range':9, 'hp':0.5},  
				{'unitid':INFESTOR, 'range':9, 'hp':0.5},  
				{'unitid':CORRUPTOR, 'range':9, 'hp':0.5},  
				{'unitid':VIPER, 'range':9, 'hp':0.5},  
				#full hp, in range
				{'unitid':INFESTEDTERRAN, 'range':9},  
				{'unitid':MUTALISK, 'range':9},  
				{'unitid':RAVAGER, 'range':9},  
				{'unitid':HYDRALISK, 'range':9},  
				{'unitid':SPORECRAWLER, 'range':9},  
				{'unitid':QUEEN, 'range':9},  
				{'unitid':INFESTOR, 'range':9},  
				{'unitid':CORRUPTOR, 'range':9},  
				{'unitid':VIPER, 'range':9}, 
				# full hp, not in range
				{'unitid':INFESTEDTERRAN, 'range':20},  
				{'unitid':MUTALISK, 'range':20},  
				{'unitid':RAVAGER, 'range':20},  
				{'unitid':HYDRALISK, 'range':20},  
				{'unitid':SPORECRAWLER, 'range':20},  
				{'unitid':QUEEN, 'range':20},  
				{'unitid':INFESTOR, 'range':20},  
				{'unitid':CORRUPTOR, 'range':20},  
				{'unitid':VIPER, 'range':20}, 
				# cannot attack air
				{'unitid':DRONE, 'range':20},
				{'unitid':ZERGLING, 'range':20},
				{'unitid':BANELING, 'range':20},
				{'unitid':ROACH, 'range':20},
				{'unitid':LURKER, 'range':20},
				{'unitid':SWARMHOSTMP, 'range':20},
				{'unitid':LOCUSTMP, 'range':20},
				{'unitid':CHANGELING, 'range':20},
				{'unitid':BROODLING, 'range':20},
				{'unitid':NYDUSCANAL, 'range':20},
				{'unitid':OVERSEER, 'range':20},
				{'unitid':BROODLORD, 'range':20},
				{'unitid':SPINECRAWLER, 'range':20},
				{'unitid':OVERLORD, 'range':20},

				{'unitid':HIVE, 'range':50},
				{'unitid':LAIR, 'range':50},
				{'unitid':HATCHERY, 'range':50},
				{'unitid':DRONE, 'range':50},
			],
		}

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
	def offensive_position(self):
		enemy_buildings = self.game.enemy_structures.exclude_type(CREEPTUMOR).exclude_type(CREEPTUMORQUEEN).exclude_type(CREEPTUMORMISSILE).exclude_type(CREEPTUMORBURROWED)
		if len(enemy_buildings) > 0 :
			if len(self.off_group):
				center = self.game.units.tags_in(self.off_group).center
				return enemy_buildings.closest_to(center).position
			else:
				return enemy_buildings.closest_to(self.game.start_location).position
		else:
			return self.game.enemy_start_locations[0]

	# send idle units to deffend
	async def deff(self):
		deff_units = {ZEALOT, STALKER, SENTRY, ARCHON, COLOSSUS, VOIDRAY, MOTHERSHIP}
		deff_group = self.game.units.filter(lambda unit: unit.type_id in deff_units).tags_not_in(self.off_group).tags_not_in(self.off_group2)
		if self.game.strategy_manager.panic_deff:
			for unit in deff_group:
				if unit.distance_to(self.game.start_location) > 5 or unit.type_id == MOTHERSHIP:
					self.game.combined_actions.append(unit.move(self.deffensive_position))
				else:
					self.game.combined_actions.append(unit.attack(self.deffensive_position))
		else:
			await self.attack_move(deff_group, self.deffensive_position, self.game.start_location)
			#await self.sentry_deff()
			await self.game.ability_manager.use_hallucination()

	async def sentry_deff(self):
		sentrys = self.game.units.filter(lambda unit: unit.type_id in {SENTRY})
		for sentry in sentrys:
			self.game.combined_actions.append(sentry.attack(self.game.main_base_ramp.top_center.towards(self.game.start_location, 2)))

	async def att(self):
		off_group = self.game.units.tags_in(self.off_group)
		await self.attack_move(off_group, self.offensive_position, self.deffensive_position)
		off_group2 = self.game.units.tags_in(self.off_group2)
		await self.attack_move(off_group2, self.offensive_position, self.deffensive_position)

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
				if attack_position == self.offensive_position:
					self.off_group = [] # to do: fix
				return
			# find best objetive
			closest_distance = 9999999
			if self.game.enemy_units and self.game.enemy_units.closer_than(20, combatients.center.position).amount:
				if self.game.units(MOTHERSHIP).amount and self.game.units(MOTHERSHIP).closer_than(20, combatients.center.position):
					ball_center = self.game.units(MOTHERSHIP).first
				else:
					ball_center = combatients.center
				#for unit in units: 
				#	dist = self.game.enemy_units.filter(lambda unit: unit.type_id in self.PRIORITY_TARGET_ORDER).closest_distance_to(unit)
				#	if dist < closest_distance:
				#		ball_center = unit
				if ball_center: #closest ally to enemies
					for priority in self.PRIORITY_TARGET_ORDER[self.game.enemy_race]:
						unit_type = priority['unitid']
						attrange = priority['range']
						minhp = priority['hp'] if 'hp' in priority else 1
<<<<<<< HEAD
						enemies = self.game.enemy_units.closer_than(attrange, ball_center.position).filter(lambda u: u.can_be_attacked)
=======
						enemies = self.game.enemy_units
						if enemies:
							enemies = enemies.closer_than(attrange, ball_center.position).filter(lambda u: u.can_be_attacked)
>>>>>>> b5b0ae38d6eef772219f122e463df6c48f9e7c4b
						if self.game.enemy_structures:
							enemies.extend(self.game.enemy_structures.closer_than(attrange, ball_center.position))
						enemies = enemies.filter(lambda u: u.type_id in {unit_type})
						enemies = enemies.filter(lambda u: u.health_max+u.shield_max == 0 or (u.health + u.shield)/(u.health_max+u.shield_max) <= minhp)
						if enemies:
							closest = enemies.closest_to(ball_center)
							for unit in combatients:
								if unit.type_id in {STALKER} and unit.weapon_cooldown > 1:
									self.game.combined_actions.append(unit.move(retreat_position))
								else:
									self.game.combined_actions.append(unit.attack(closest))
									if unit.type_id in {VOIDRAY} and closest.is_armored and unit.distance_to(closest) <= 6:
										self.game.combined_actions.append(unit(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT))

							return
			else:
				# regroup ball
				ball_combatients = combatients.filter(lambda u: u.type_id in {VOIDRAY, MOTHERSHIP})
				if attack_position == self.offensive_position or ball_combatients.amount >= 5:
					dispersion = 0
					if ball_combatients.amount:
						for unit in ball_combatients:
							dispersion += unit.distance_to(ball_combatients.center)
							if unit.type_id == MOTHERSHIP:
								dispersion += 2 * unit.distance_to(ball_combatients.center) # mothership triplicates its incluence
						dispersion = dispersion / ball_combatients.amount
						if dispersion > 2:
							for unit in ball_combatients:
								# kite to regroup
								if unit.ground_range > 1 and unit.weapon_cooldown > 3:
									self.game.combined_actions.append(unit.move(ball_combatients.center))
								else:
									self.game.combined_actions.append(unit.attack(ball_combatients.center))
							return
			# default attack
			if self.game.enemy_units and self.game.enemy_units.closer_than(20, combatients.center.position).amount:
				for unit in self.game.enemy_units.closer_than(20, combatients.center.position):
					print("Unknown unit: "+str(unit.type_id))
			if combatients.amount:
				for unit in combatients.further_than(1, attack_position):
					self.game.combined_actions.append(unit.attack(attack_position))

	# new offensive group conditions
	async def set_off(self):
		# group 1
		if len(self.off_group) == 0 and (self.game.units(VOIDRAY).tags_not_in(self.off_group2).tags_not_in(self.off_group).amount >= self.game.strategy_manager.min_off_vr or (not self.game.strategy_manager.rush_complete and self.game.units(VOIDRAY).tags_not_in(self.off_group2).tags_not_in(self.off_group).amount >= self.game.strategy_manager.min_off_vr_rush)):
			self.game.strategy_manager.rush_complete = True
			for vr in self.game.units(VOIDRAY).tags_not_in(self.off_group2):
				self.off_group.append(vr.tag)
			if not self.game.strategy_manager.panic_deff:
				for ms in self.game.units(MOTHERSHIP).tags_not_in(self.off_group2):
					self.off_group.append(ms.tag)
		#group 2
		if len(self.off_group2) == 0 and self.game.units(VOIDRAY).tags_not_in(self.off_group).tags_not_in(self.off_group2).amount >= self.game.strategy_manager.min_off_vr:
			for vr in self.game.units(VOIDRAY).tags_not_in(self.off_group):
				self.off_group2.append(vr.tag)
			if not self.game.strategy_manager.panic_deff:
				for ms in self.game.units(MOTHERSHIP).tags_not_in(self.off_group):
					self.off_group2.append(ms.tag)

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
		path_distance = await self.game._client.query_pathing(startp, finp)
		if path_distance is None:
			path_distance = float('inf')
		distance = startp.distance_to_point2(finp)
		return path_distance / distance - 1

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

	def load_unit(self, unit):
		if unit.name == 'VoidRay':
			obj = voidray(unit)

class ProUnit(Unit):
	def __init__(self):
		self.SHIELD_TO_ADVANCE = 0.01
		self.HP_TO_RETREAT = 0.33
		self.HIT_AND_RUN = True
		self.WEAPON_COOLDOWN_TO_REATTACK = 3
		self.TARGET_PRIORITY = {}
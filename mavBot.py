import sc2, random

from sc2 import run_game, maps, Race, Difficulty, position
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.position import Point2, Point3
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId

from unit_manager import UnitManager
from upgrade_manager import UpgradeManager
from build_manager import BuildManager
from train_manager import TrainManager
from ability_manager import AbilityManager
from worker_manager import WorkerManager
from debug_manager import DebugManager
from strategy_manager import StrategyManager

#import keras

"""
TODO:
- Neural network -> decide best strategy
- Clean next expansion before expanding
- Deff ag cannon rush
- Calc %win in baserush and retret attack if necessary
- Use allucinations to scout
- More upgrades
- Deff workers against flying units
"""

class MavBot(sc2.BotAI):
	def __init__(self):
		self.unit_manager = UnitManager(self)
		self.upgrade_manager = UpgradeManager(self)
		self.build_manager = BuildManager(self)
		self.train_manager = TrainManager(self)
		self.ability_manager = AbilityManager(self)
		self.worker_manager = WorkerManager(self)
		self.debug_manager = DebugManager(self)
		self.strategy_manager = StrategyManager(self)
		self.debug = True

	async def on_step(self, iteration):
		if iteration == 1:
			await self.on_1st_step()
		if iteration % 10 == 0:
			await self.on_10_step()
		await self.train_manager.train_troops()
		await self.build_manager.build()
		await self.unit_manager.move_troops()
		await self.ability_manager.use_abilities()
		await self.upgrade_manager.research_upgrades()
		if self.debug:
			await self.debug_manager.draw_debug()

	async def on_1st_step(self):
		pass

	async def on_10_step(self):
		await self.worker_manager.manage_workers()

	async def on_unit_destroyed(self, unit_tag):
		# removes units from offensive groups when destroyed
		for unit in self.unit_manager.off_group:
			if unit == unit_tag:
				self.unit_manager.off_group.remove(unit)
		# removes enemy units from cache
		for unitType in self.unit_manager.cachedUnits:
			if unit_tag in self.unit_manager.cachedUnits[unitType]:
				self.unit_manager.cachedUnits[unitType].remove(unit_tag)

	def on_end(self, game_result):
		print(game_result)
		print(self.state.score.score)

	async def distribute_workers(self, resource_ratio: float = 2):
		"""
		Distributes workers across all the bases taken.
		Keyword `resource_ratio` takes a float. If the current minerals to gas
		ratio is bigger than `resource_ratio`, this function prefer filling geysers
		first, if it is lower, it will prefer sending workers to minerals first.
		This is only for workers that need to be moved anyways, it will NOT will
		geysers on its own.
		NOTE: This function is far from optimal, if you really want to have
		refined worker control, you should write your own distribution function.
		For example long distance mining control and moving workers if a base was killed
		are not being handled.
		WARNING: This is quite slow when there are lots of workers or multiple bases.
		"""
		if not self.state.mineral_field or not self.workers or not self.townhalls.ready:
			return
		actions = []
		worker_pool = [worker for worker in self.workers.idle]
		bases = self.townhalls.ready
		geysers = self.geysers.ready

		# list of places that need more workers
		deficit_mining_places = []

		for mining_place in bases | geysers:
			difference = mining_place.surplus_harvesters
			# perfect amount of workers, skip mining place
			if not difference:
				continue
			if mining_place.is_vespene_geyser:
				# get all workers that target the gas extraction site
				# or are on their way back from it
				local_workers = self.workers.filter(
					lambda unit: unit.order_target == mining_place.tag
					or (unit.is_carrying_vespene and unit.order_target == bases.closest_to(mining_place).tag)
				)
			else:
				# get tags of minerals around expansion
				local_minerals_tags = {
					mineral.tag for mineral in self.state.mineral_field if mineral.distance_to(mining_place) <= 8
				}
				# get all target tags a worker can have
				# tags of the minerals he could mine at that base
				# get workers that work at that gather site
				local_workers = self.workers.filter(
					lambda unit: unit.order_target in local_minerals_tags
					or (unit.is_carrying_minerals and unit.order_target == mining_place.tag)
				)
			# too many workers
			if difference > 0:
				for worker in local_workers[:difference]:
					worker_pool.append(worker)
			# too few workers
			# add mining place to deficit bases for every missing worker
			else:
				deficit_mining_places += [mining_place for _ in range(-difference)]

		# prepare all minerals near a base if we have too many workers
		# and need to send them to the closest patch
		if len(worker_pool) > len(deficit_mining_places):
			all_minerals_near_base = [
				mineral
				for mineral in self.mineral_fields
				if any(mineral.distance_to(base) <= 8 for base in self.townhalls.ready)
			]
		# distribute every worker in the pool
		for worker in worker_pool:
			# as long as have workers and mining places
			if deficit_mining_places:
				# choose only mineral fields first if current mineral to gas ratio is less than target ratio
				if self.vespene and self.minerals / self.vespene < resource_ratio:
					possible_mining_places = [place for place in deficit_mining_places if not place.vespene_contents]
				# else prefer gas
				else:
					possible_mining_places = [place for place in deficit_mining_places if place.vespene_contents]
				# if preferred type is not available any more, get all other places
				if not possible_mining_places:
					possible_mining_places = deficit_mining_places
				# find closest mining place
				current_place = min(deficit_mining_places, key=lambda place: place.distance_to(worker))
				# remove it from the list
				deficit_mining_places.remove(current_place)
				# if current place is a gas extraction site, go there
				if current_place.vespene_contents:
					actions.append(worker.gather(current_place))
				# if current place is a gas extraction site,
				# go to the mineral field that is near and has the most minerals left
				else:
					local_minerals = [
						mineral for mineral in self.state.mineral_field if mineral.distance_to(current_place) <= 8
					]
					target_mineral = max(local_minerals, key=lambda mineral: mineral.mineral_contents)
					actions.append(worker.gather(target_mineral))
			# more workers to distribute than free mining spots
			# send to closest if worker is doing nothing
			elif worker.is_idle and all_minerals_near_base:
				target_mineral = min(all_minerals_near_base, key=lambda mineral: mineral.distance_to(worker))
				actions.append(worker.gather(target_mineral))
			else:
				# there are no deficit mining places and worker is not idle
				# so dont move him
				pass

		await self.do_actions(actions)

if __name__ == '__main__':
	mapsS8 = [
		"Acropolis",
		"Artana", 
		"Bandwidth",
		"CrystalCavern",
		"DigitalFrontier",
		"Ephemeron",
		"OldSunshine",
		"PrimusQ9",
		"Reminiscence",
		"Sanglune",
		"TheTimelessVoid",
		"Treachery",
		"Triton",
		"Urzagol"
	]
	run_game(maps.get("TheTimelessVoid"),[#random.choice(mapsS8)), [
		Bot(Race.Protoss, MavBot()),
		Computer(Race.Terran, Difficulty.VeryHard) #VeryHard CheatVision CheatMoney CheatInsane
		], realtime=False)
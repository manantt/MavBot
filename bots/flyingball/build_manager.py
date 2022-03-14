from sc2.units import Units
from sc2.constants import *

class BuildManager:
	def __init__(self, game):
		self.game = game

	# build priority order
	async def build(self):
		await self.build_pylon()
		await self.build_forge()
		await self.build_cannon()
		await self.build_roboticsfacility()
		await self.build_roboticsbay()
		await self.build_fleetbeacon()
		await self.build_gateway()
		await self.build_cyberneticscore()
		await self.build_stargate()
		await self.build_shield()
		await self.build_nexus()
		self.build_asimilator()

	# build conditions
	def should_build_forge(self):
		if self.game.bot.strategy_manager.build_cannons and self.game.structures(UnitTypeId.PYLON).ready.amount and self.game.structures(UnitTypeId.GATEWAY).amount and self.game.can_afford(UnitTypeId.FORGE) and self.game.structures(UnitTypeId.FORGE).amount < 1 and not self.game.already_pending(UnitTypeId.FORGE):
			return True
		return False

	def should_build_cannon(self):
		if self.game.bot.strategy_manager.build_cannons:
			if self.game.structures(UnitTypeId.PYLON).ready.amount > 0 and self.game.can_afford(UnitTypeId.PHOTONCANNON) and not self.game.already_pending(UnitTypeId.PHOTONCANNON):
				return True
		return False

	def should_build_pylon(self): # todo: remove fix
		if self.game.townhalls().amount > 0 and self.game.can_afford(UnitTypeId.PYLON) and not self.game.already_pending(UnitTypeId.PYLON):
			if self.game.supply_left < 2 and self.game.structures(UnitTypeId.PYLON).amount == 0:
				return True
			if self.game.supply_left < 4:
				return True
			if self.game.supply_left < 9 and self.game.bot.strategy_manager.max_troops[UnitTypeId.MOTHERSHIP] and not self.game.units(UnitTypeId.MOTHERSHIP).amount and self.game.structures(UnitTypeId.FLEETBEACON).amount:
				return True
		return False

	def should_build_gateway(self):
		if self.game.structures(UnitTypeId.PYLON).ready.exists:
			max_gateways = 2 if self.game.bot.strategy_manager.max_troops[UnitTypeId.ZEALOT] + self.game.bot.strategy_manager.max_troops[UnitTypeId.STALKER] + self.game.bot.strategy_manager.max_troops[UnitTypeId.SENTRY] > 4 else 1
			if self.game.structures(UnitTypeId.GATEWAY).amount < max_gateways:
				if self.game.can_afford(UnitTypeId.GATEWAY) and not self.game.already_pending(UnitTypeId.GATEWAY):
					return True
		return False

	def should_build_cyberneticscore(self):
		if self.game.structures(UnitTypeId.PYLON).ready.exists and self.game.structures(UnitTypeId.GATEWAY).ready.exists:
			if not self.game.structures(UnitTypeId.CYBERNETICSCORE):
				if self.game.can_afford(UnitTypeId.CYBERNETICSCORE) and not self.game.already_pending(UnitTypeId.CYBERNETICSCORE):
					return True
		return False

	def should_build_stargate(self):
		if self.game.bot.strategy_manager.max_troops[UnitTypeId.VOIDRAY] == 0:
			return False
		if self.game.structures(UnitTypeId.PYLON).ready.exists and self.game.structures(UnitTypeId.CYBERNETICSCORE).ready.exists:
			if self.game.can_afford(UnitTypeId.STARGATE) and not self.game.already_pending(UnitTypeId.STARGATE):
				if self.game.bot.strategy_manager.panic_deff and self.game.structures(UnitTypeId.STARGATE).amount:
					return False
				if (self.game.structures(UnitTypeId.STARGATE).amount < 1) or (self.game.structures(UnitTypeId.STARGATE).amount < 2 and self.game.units(UnitTypeId.VOIDRAY).amount > 1 and not self.game.already_pending(UnitTypeId.STARGATE)) or (self.game.minerals > 300 * self.game.structures(UnitTypeId.STARGATE).amount and self.game.vespene > 400):
					return True
		return False

	def should_build_roboticsfacility(self):
		if self.game.structures(UnitTypeId.PYLON).ready.exists and self.game.structures(UnitTypeId.CYBERNETICSCORE).ready.exists:
			if self.game.can_afford(UnitTypeId.ROBOTICSFACILITY) and not self.game.already_pending(UnitTypeId.ROBOTICSFACILITY):
				if self.game.structures(UnitTypeId.ROBOTICSFACILITY).amount < 1 and not self.game.already_pending(UnitTypeId.ROBOTICSFACILITY) and (self.game.supply_used >= self.game.bot.strategy_manager.observer_delay or self.game.bot.strategy_manager.cloack_units_detected):
					return True
		return False

	async def should_build_nexus(self):
		if self.game.bot.strategy_manager.panic_deff:
			return False
		# TODO: clean expansion first
		if self.game.can_afford(UnitTypeId.NEXUS) and ((not self.game.already_pending(UnitTypeId.NEXUS) and (self.game.townhalls().amount - 1) * 2 <= self.game.units(UnitTypeId.VOIDRAY).amount) or (self.game.minerals > 1500 and not self.game.already_pending(UnitTypeId.NEXUS)) and await self.game.get_next_expansion()):
			return True
		return False

	def should_build_asimilator(self):
		if self.game.can_afford(UnitTypeId.ASSIMILATOR) and self.game.structures(UnitTypeId.GATEWAY).exists:
			return True
		return False

	def should_build_fleetbeacon(self):
		if self.game.bot.strategy_manager.max_troops[UnitTypeId.MOTHERSHIP] and self.game.structures(UnitTypeId.PYLON).ready.exists and self.game.structures(UnitTypeId.STARGATE).ready.exists and (self.game.units(UnitTypeId.VOIDRAY).amount >= 3 or self.game.bot.strategy_manager.panic_deff):
			if self.game.can_afford(UnitTypeId.FLEETBEACON) and not self.game.already_pending(UnitTypeId.FLEETBEACON) and not self.game.structures(UnitTypeId.FLEETBEACON).amount:
				return True
		return False

	def should_build_roboticsbay(self):
		if self.game.bot.strategy_manager.max_troops[UnitTypeId.COLOSSUS] and self.game.structures(UnitTypeId.PYLON).ready.exists and self.game.structures(UnitTypeId.ROBOTICSFACILITY).ready.exists and self.game.units(UnitTypeId.MOTHERSHIP).amount:
			if self.game.can_afford(UnitTypeId.ROBOTICSBAY) and not self.game.already_pending(UnitTypeId.ROBOTICSBAY) and not self.game.structures(UnitTypeId.ROBOTICSBAY).amount:
				return True
		return False

	def should_build_shield(self):
		if self.game.bot.strategy_manager.build_shields and self.game.structures(UnitTypeId.PYLON).ready.exists and self.game.structures(UnitTypeId.GATEWAY).ready.exists and self.game.minerals > 500 + 50*self.game.structures(UnitTypeId.SHIELDBATTERY).amount:
			return True
		return False

	# build methods
	async def build_forge(self):
		if self.should_build_forge():
			pylons = self.game.structures(UnitTypeId.PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(UnitTypeId.PYLON).ready
			await self.game.build(FORGE, near=pylons.random.position.towards(self.game.game_info.map_center, 4))

	async def build_cannon(self):
		if self.should_build_cannon():
			for n in self.game.townhalls():
				if self.game.structures(UnitTypeId.PYLON).ready.closer_than(8, n.position.towards(self.game.game_info.map_center, -5.5)).amount:
					if not self.game.structures(UnitTypeId.PHOTONCANNON) or self.game.structures(UnitTypeId.PHOTONCANNON).closer_than(8, n.position.towards(self.game.game_info.map_center, -5.5)).amount < 1:
						await self.game.build(UnitTypeId.PHOTONCANNON, near=n.position.towards(self.game.game_info.map_center, -5.5))

	async def build_pylon(self):
		if self.should_build_pylon():
			if self.game.bot.strategy_manager.panic_deff:
				if self.game.structures(UnitTypeId.PYLON).amount == 0:
					await self.game.build(UnitTypeId.PYLON, list(self.game.main_base_ramp.corner_depots)[0])
					return
				if self.game.structures(UnitTypeId.PYLON).amount == 1:
					await self.game.build(UnitTypeId.PYLON, list(self.game.main_base_ramp.corner_depots)[1])
					return
			if self.game.structures(UnitTypeId.PYLON).amount:
				for n in self.game.townhalls():
					if not self.game.structures(UnitTypeId.PYLON).closer_than(8, n.position.towards(self.game.game_info.map_center, -8)).amount:
						await self.game.build(UnitTypeId.PYLON, near=n.position.towards(self.game.game_info.map_center, -8))
						return
			await self.game.build(UnitTypeId.PYLON, near=self.game.start_location.towards(self.game.game_info.map_center, 7))

	async def build_gateway(self):
		if self.should_build_gateway():
			if self.game.bot.strategy_manager.panic_deff:
				await self.game.build(UnitTypeId.GATEWAY, self.game.main_base_ramp.barracks_in_middle)
				return
			pylons = self.game.structures(UnitTypeId.PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(UnitTypeId.PYLON).ready
			await self.game.build(UnitTypeId.GATEWAY, near=pylons.random.position.towards(self.game.game_info.map_center, 4))

	async def build_cyberneticscore(self):
		if self.should_build_cyberneticscore():
			pylons = self.game.structures(UnitTypeId.PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(UnitTypeId.PYLON).ready
			await self.game.build(UnitTypeId.CYBERNETICSCORE, near=pylons.random.position.towards(self.game.game_info.map_center, 4))

	async def build_stargate(self):
		if self.should_build_stargate():
			pylons = self.game.structures(UnitTypeId.PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(UnitTypeId.PYLON).ready
			if self.game.bot.strategy_manager.panic_deff:
				await self.game.build(UnitTypeId.STARGATE, near=pylons.random.position.towards(self.game.game_info.map_center, 1))
			else:
				await self.game.build(UnitTypeId.STARGATE, near=pylons.random.position.towards(self.game.game_info.map_center, 4))

	async def build_roboticsfacility(self):
		if self.should_build_roboticsfacility():
			pylons = self.game.structures(UnitTypeId.PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(UnitTypeId.PYLON).ready
			await self.game.build(UnitTypeId.ROBOTICSFACILITY, near=pylons.random.position.towards(self.game.game_info.map_center, 2))

	async def build_fleetbeacon(self):
		if self.should_build_fleetbeacon():
			pylons = self.game.structures(UnitTypeId.PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(UnitTypeId.PYLON).ready
			await self.game.build(UnitTypeId.FLEETBEACON, near=pylons.random.position.towards(self.game.game_info.map_center, 5))

	async def build_roboticsbay(self):
		if self.should_build_roboticsbay():
			pylons = self.game.structures(UnitTypeId.PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(UnitTypeId.PYLON).ready
			await self.game.build(ROBOTICSBAY, near=pylons.random.position.towards(self.game.game_info.map_center, 5))

	async def build_shield(self):
		if self.should_build_shield():
			pylons = self.game.structures(UnitTypeId.PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(UnitTypeId.PYLON).ready
			await self.game.build(UnitTypeId.SHIELDBATTERY, near=pylons.random.position.towards(self.game.start_location, 1))

	async def build_nexus(self):
		if await self.should_build_nexus():
			await self.game.expand_now()
	
	def build_asimilator(self):
		if self.should_build_asimilator():
			for nexus in self.game.townhalls().ready:
				vespenes = self.game.vespene_geyser.closer_than(13.0, nexus)
				for vespene in vespenes:
					worker = self.game.select_build_worker(vespene.position)
					if worker is not None and (not self.game.structures(UnitTypeId.ASSIMILATOR).amount or not self.game.structures(UnitTypeId.ASSIMILATOR).closer_than(1.0, vespene)):
						worker.build(UnitTypeId.ASSIMILATOR, vespene)
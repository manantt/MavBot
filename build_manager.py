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
		if self.game.strategy_manager.build_cannons and self.game.structures(PYLON).ready.amount and self.game.structures(GATEWAY).amount and self.game.can_afford(FORGE) and self.game.structures(FORGE).amount < 1 and not self.game.already_pending(FORGE):
			return True
		return False

	def should_build_cannon(self):
		if self.game.strategy_manager.build_cannons:
			if self.game.structures(PYLON).ready.amount > 0 and self.game.can_afford(PHOTONCANNON) and not self.game.already_pending(PHOTONCANNON):
				return True
		return False

	def should_build_pylon(self): # todo: remove fix
		if self.game.townhalls().amount > 0 and self.game.can_afford(PYLON) and not self.game.already_pending(PYLON):
			if self.game.supply_left < 2 and self.game.structures(PYLON).amount == 0:
				return True
			if self.game.supply_left < 4:
				return True
			if self.game.supply_left < 9 and self.game.strategy_manager.build_mothership and not self.game.units(MOTHERSHIP).amount and self.game.structures(FLEETBEACON).amount:
				return True
		return False

	def should_build_gateway(self):
		if self.game.structures(PYLON).ready.exists:
			max_gateways = 2 if self.game.strategy_manager.ground_defenses[ZEALOT] + self.game.strategy_manager.ground_defenses[STALKER] + self.game.strategy_manager.ground_defenses[SENTRY] > 4 else 1
			if self.game.structures(GATEWAY).amount < max_gateways:
				if self.game.can_afford(GATEWAY) and not self.game.already_pending(GATEWAY):
					return True
		return False

	def should_build_cyberneticscore(self):
		if self.game.structures(PYLON).ready.exists and self.game.structures(GATEWAY).ready.exists:
			if not self.game.structures(CYBERNETICSCORE):
				if self.game.can_afford(CYBERNETICSCORE) and not self.game.already_pending(CYBERNETICSCORE):
					return True
		return False

	def should_build_stargate(self):
		if self.game.structures(PYLON).ready.exists and self.game.structures(CYBERNETICSCORE).ready.exists:
			if self.game.can_afford(STARGATE) and not self.game.already_pending(STARGATE):
				if self.game.strategy_manager.panic_deff and self.game.structures(STARGATE).amount:
					return False
				if (self.game.structures(STARGATE).amount < 1) or (self.game.structures(STARGATE).amount < 2 and self.game.units(VOIDRAY).amount > 1 and not self.game.already_pending(STARGATE)) or (self.game.minerals > 300 * self.game.structures(STARGATE).amount and self.game.vespene > 400):
					return True
		return False

	def should_build_roboticsfacility(self):
		if self.game.structures(PYLON).ready.exists and self.game.structures(CYBERNETICSCORE).ready.exists:
			if self.game.can_afford(ROBOTICSFACILITY) and not self.game.already_pending(ROBOTICSFACILITY):
				if self.game.structures(ROBOTICSFACILITY).amount < 1 and not self.game.already_pending(ROBOTICSFACILITY) and (self.game.units(VOIDRAY).amount >= self.game.strategy_manager.observer_delay or self.game.strategy_manager.cloack_units_detected):
					return True
		return False

	async def should_build_nexus(self):
		if self.game.strategy_manager.panic_deff:
			return False
		# TODO: clean expansion first
		if self.game.can_afford(NEXUS) and ((not self.game.already_pending(NEXUS) and (self.game.townhalls().amount - 1) * 2 <= self.game.units(VOIDRAY).amount) or (self.game.minerals > 1500 and not self.game.already_pending(NEXUS)) and await self.game.get_next_expansion()):
			return True
		return False

	def should_build_asimilator(self):
		if self.game.can_afford(ASSIMILATOR) and self.game.structures(GATEWAY).exists:
			return True
		return False

	def should_build_fleetbeacon(self):
		if self.game.strategy_manager.build_mothership and self.game.structures(PYLON).ready.exists and self.game.structures(STARGATE).ready.exists and (self.game.units(VOIDRAY).amount >= 3 or self.game.strategy_manager.panic_deff):
			if self.game.can_afford(FLEETBEACON) and not self.game.already_pending(FLEETBEACON) and not self.game.structures(FLEETBEACON).amount:
				return True
		return False

	def should_build_roboticsbay(self):
		if self.game.strategy_manager.ground_defenses[COLOSSUS] and self.game.structures(PYLON).ready.exists and self.game.structures(ROBOTICSFACILITY).ready.exists and self.game.units(MOTHERSHIP).amount:
			if self.game.can_afford(ROBOTICSBAY) and not self.game.already_pending(ROBOTICSBAY) and not self.game.structures(ROBOTICSBAY).amount:
				return True
		return False

	def should_build_shield(self):
		if self.game.strategy_manager.build_shields and self.game.structures(PYLON).ready.exists and self.game.structures(GATEWAY).ready.exists and self.game.minerals > 500 + 50*self.game.structures(SHIELDBATTERY).amount:
			return True
		return False

	# build methods
	async def build_forge(self):
		if self.should_build_forge():
			pylons = self.game.structures(PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(PYLON).ready
			await self.game.build(FORGE, near=pylons.random.position.towards(self.game.game_info.map_center, 4))

	async def build_cannon(self):
		if self.should_build_cannon():
			for n in self.game.townhalls():
				if self.game.structures(PYLON).ready.closer_than(8, n.position.towards(self.game.game_info.map_center, -5.5)).amount:
					if not self.game.structures(PHOTONCANNON) or self.game.structures(PHOTONCANNON).closer_than(8, n.position.towards(self.game.game_info.map_center, -5.5)).amount < 1:
						await self.game.build(PHOTONCANNON, near=n.position.towards(self.game.game_info.map_center, -5.5))

	async def build_pylon(self):
		if self.should_build_pylon():
			if self.game.strategy_manager.panic_deff:
				if self.game.structures(PYLON).amount == 0:
					await self.game.build(PYLON, list(self.game.main_base_ramp.corner_depots)[0])
					return
				if self.game.structures(PYLON).amount == 1:
					await self.game.build(PYLON, list(self.game.main_base_ramp.corner_depots)[1])
					return
			if self.game.structures(PYLON).amount:
				for n in self.game.townhalls():
					if not self.game.structures(PYLON).closer_than(8, n.position.towards(self.game.game_info.map_center, -8)).amount:
						await self.game.build(PYLON, near=n.position.towards(self.game.game_info.map_center, -8))
						return
			await self.game.build(PYLON, near=self.game.start_location.towards(self.game.game_info.map_center, 7))

	async def build_gateway(self):
		if self.should_build_gateway():
			if self.game.strategy_manager.panic_deff:
				await self.game.build(GATEWAY, self.game.main_base_ramp.barracks_in_middle)
				return
			pylons = self.game.structures(PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(PYLON).ready
			await self.game.build(GATEWAY, near=pylons.random.position.towards(self.game.game_info.map_center, 4))

	async def build_cyberneticscore(self):
		if self.should_build_cyberneticscore():
			pylons = self.game.structures(PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(PYLON).ready
			await self.game.build(CYBERNETICSCORE, near=pylons.random.position.towards(self.game.game_info.map_center, 4))

	async def build_stargate(self):
		if self.should_build_stargate():
			pylons = self.game.structures(PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(PYLON).ready
			if self.game.strategy_manager.panic_deff:
				await self.game.build(STARGATE, near=pylons.random.position.towards(self.game.game_info.map_center, 1))
			else:
				await self.game.build(STARGATE, near=pylons.random.position.towards(self.game.game_info.map_center, 4))

	async def build_roboticsfacility(self):
		if self.should_build_roboticsfacility():
			pylons = self.game.structures(PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(PYLON).ready
			await self.game.build(ROBOTICSFACILITY, near=pylons.random.position.towards(self.game.game_info.map_center, 2))

	async def build_fleetbeacon(self):
		if self.should_build_fleetbeacon():
			pylons = self.game.structures(PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(PYLON).ready
			await self.game.build(FLEETBEACON, near=pylons.random.position.towards(self.game.game_info.map_center, 5))

	async def build_roboticsbay(self):
		if self.should_build_roboticsbay():
			print("SIII")
			pylons = self.game.structures(PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(PYLON).ready
			await self.game.build(ROBOTICSBAY, near=pylons.random.position.towards(self.game.game_info.map_center, 5))

	async def build_shield(self):
		if self.should_build_shield():
			pylons = self.game.structures(PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(PYLON).ready
			await self.game.build(SHIELDBATTERY, near=pylons.random.position.towards(self.game.start_location, 1))

	async def build_nexus(self):
		if await self.should_build_nexus():
			await self.game.expand_now()
	
	def build_asimilator(self):
		if self.should_build_asimilator():
			for nexus in self.game.townhalls().ready:
				vespenes = self.game.vespene_geyser.closer_than(13.0, nexus)
				for vespene in vespenes:
					worker = self.game.select_build_worker(vespene.position)
					if worker is not None and (not self.game.structures(ASSIMILATOR).amount or not self.game.structures(ASSIMILATOR).closer_than(1.0, vespene)):
						self.game.combined_actions.append(worker.build(ASSIMILATOR, vespene))
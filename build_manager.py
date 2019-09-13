from sc2.units import Units
from sc2.constants import *

# TODO: build forge
# TODO: build cannons 

class BuildManager:
	def __init__(self, game):
		self.game = game

	# build priority order
	async def build(self):
		await self.build_pylon()
		#await self.build_forge()
		#await self.build_cannon()
		await self.build_gateway()
		await self.build_cyberneticscore()
		await self.build_stargate()
		await self.build_roboticsfacility()
		await self.build_nexus()
		await self.build_asimilator()

	# build conditions
	def should_build_forge(self):
		if self.game.units(PYLON).ready.amount > 0 and self.game.can_afford(FORGE) and self.game.units(FORGE).amount < 1 and not self.game.already_pending(FORGE):
			return True
		return False

	def should_build_cannon(self):
		if self.game.units(PYLON).ready.amount > 0 and self.game.can_afford(PHOTONCANNON) and not self.game.already_pending(PHOTONCANNON):
			return True
		return False

	def should_build_pylon(self):
		if self.game.units(NEXUS).amount > 0 and self.game.can_afford(PYLON) and not self.game.already_pending(PYLON):
			if self.game.supply_left < 2 and self.game.units(PYLON).amount == 0:
				return True
			elif self.game.supply_left < 4:
				return True
		return False

	def should_build_gateway(self):
		if self.game.units(PYLON).ready.exists:
			if not self.game.units(GATEWAY).exists:
				if self.game.can_afford(GATEWAY) and not self.game.already_pending(GATEWAY):
					return True
		return False

	def should_build_cyberneticscore(self):
		if self.game.units(PYLON).ready.exists and self.game.units(GATEWAY).ready.exists:
			if not self.game.units(CYBERNETICSCORE):
				if self.game.can_afford(CYBERNETICSCORE) and not self.game.already_pending(CYBERNETICSCORE):
					return True
		return False

	def should_build_stargate(self):
		if self.game.units(PYLON).ready.exists and self.game.units(CYBERNETICSCORE).ready.exists:
			if self.game.can_afford(STARGATE) and not self.game.already_pending(STARGATE):
				if (self.game.units(STARGATE).amount < 1) or (self.game.units(STARGATE).amount < 3 and self.game.units(VOIDRAY).amount > 1 and not self.game.already_pending(STARGATE)) or self.game.minerals > 300 * self.game.units(STARGATE).amount:
					return True
		return False

	def should_build_roboticsfacility(self):
		if self.game.units(PYLON).ready.exists and self.game.units(CYBERNETICSCORE).ready.exists:
			if self.game.can_afford(ROBOTICSFACILITY) and not self.game.already_pending(ROBOTICSFACILITY):
				if self.game.units(ROBOTICSFACILITY).amount < 1 and not self.game.already_pending(ROBOTICSFACILITY) and self.game.units(VOIDRAY).amount > 10:
					return True
		return False

	def should_build_nexus(self):
		# TODO: clean expansion first
		if self.game.can_afford(NEXUS) and ((not self.game.already_pending(NEXUS) and (self.game.units(NEXUS).amount - 1) * 2 <= self.game.units(VOIDRAY).amount) or self.game.minerals > 1500):
			return True
		return False

	def should_build_asimilator(self):
		if self.game.can_afford(ASSIMILATOR) and self.game.units(GATEWAY).exists:
			return True
		return False

	# build methods
	async def build_forge(self):
		if self.should_build_forge():
			await self.game.build(FORGE, near=self.game.units(PYLON).ready.random.position.towards(self.game.game_info.map_center, 4))

	async def build_cannon(self):
		if self.should_build_cannon():
			for n in self.game.units(NEXUS):
				if self.game.units(PHOTONCANNON).closer_than(4, n).amount < 1:
					await self.game.build(PHOTONCANNON, near=n.position.towards(self.game.game_info.map_center, -2))

	async def build_pylon(self):
		if self.should_build_pylon():
			await self.game.build(PYLON, near=self.game.units(NEXUS).first.position.towards(self.game.game_info.map_center, 7))
	
	async def build_gateway(self):
		if self.should_build_gateway():
			await self.game.build(GATEWAY, near=self.game.units(PYLON).ready.random.position.towards(self.game.game_info.map_center, 4))

	async def build_cyberneticscore(self):
		if self.should_build_cyberneticscore():
			await self.game.build(CYBERNETICSCORE, near=self.game.units(PYLON).ready.random.position.towards(self.game.game_info.map_center, 4))

	async def build_stargate(self):
		if self.should_build_stargate():
			await self.game.build(STARGATE, near=self.game.units(PYLON).ready.random.position.towards(self.game.game_info.map_center, 4))

	async def build_roboticsfacility(self):
		if self.should_build_roboticsfacility():
			await self.game.build(ROBOTICSFACILITY, near=self.game.units(PYLON).ready.random.position.towards(self.game.game_info.map_center, 4))

	async def build_nexus(self):
		if self.should_build_nexus():
			await self.game.expand_now()
	
	async def build_asimilator(self):
		if self.should_build_asimilator():
			for nexus in self.game.units(NEXUS).ready:
				vespenes = self.game.state.vespene_geyser.closer_than(13.0, nexus)
				for vespene in vespenes:
					worker = self.game.select_build_worker(vespene.position)
					if worker is not None and not self.game.units(ASSIMILATOR).closer_than(1.0, vespene):
						await self.game.do(worker.build(ASSIMILATOR, vespene))
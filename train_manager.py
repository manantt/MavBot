from sc2.units import Units
from sc2.constants import *

# TODO: train one sentry

class TrainManager:
	def __init__(self, game):
		self.game = game
		self.max_probes = 64
		self.probes_per_nexus = 20

	# troop train priority order
	async def train_troops(self):
		await self.train_voidray()
		await self.train_zealot()
		await self.train_probe()
		await self.train_observer()

	# train conditions
	def should_train_probe(self):
		if self.game.can_afford(PROBE):
			num_nexus = self.game.units(NEXUS).amount
			max_probes = min(self.max_probes, num_nexus * self.probes_per_nexus)
			if self.game.units(PROBE).amount < max_probes:
				return True
		return False

	def should_train_voidray(self):
		if self.game.can_afford(VOIDRAY):
			return True
		return False

	def should_train_zealot(self):
		# TODO: pending zealots should be considered in amount
		if self.game.can_afford(ZEALOT) and self.game.units(ZEALOT).amount < 4:
			return True
		return False

	def should_train_observer(self):
		if self.game.can_afford(OBSERVER):
			if self.game.units(OBSERVER).amount < 2 and self.game.units(ROBOTICSFACILITY).ready.noqueue.amount > 0:
				return True
		return False

	# train methods
	async def train_probe(self):
		for nexus in self.game.units(NEXUS).ready.noqueue:
			if self.should_train_probe():
				await self.game.do(nexus.train(PROBE))

	async def train_voidray(self):
		for sg in self.game.units(STARGATE).ready.noqueue:
			if self.should_train_voidray():
				await self.game.do(sg.train(VOIDRAY))

	async def train_zealot(self):
		for gw in self.game.units(GATEWAY).ready.noqueue:
			if self.should_train_zealot():
				await self.game.do(gw.train(ZEALOT))

	async def train_observer(self):
		if self.should_train_observer():
			robotic = self.game.units(ROBOTICSFACILITY).ready.noqueue.first
			if robotic:
				await self.game.do(robotic.train(OBSERVER))

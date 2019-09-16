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
		await self.train_observer()
		await self.train_voidray()
		await self.train_zealot()
		await self.train_probe()

	# train conditions
	def should_train_probe(self):
		if self.game.can_afford(PROBE):
			num_nexus = self.game.townhalls().amount
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
		if self.game.can_afford(ZEALOT) and self.game.units(ZEALOT).amount < 2:
			return True
		return False

	def should_train_observer(self):
		if self.game.can_afford(OBSERVER) and self.game.structures(ROBOTICSFACILITY).ready.idle.amount > 0:
			if self.game.units(OBSERVER).amount < 2:
				return True
			if self.game.strategy_manager.cloack_units_detected and self.game.units(OBSERVER).amount < 4:
				return True
		return False

	# train methods
	async def train_probe(self):
		for nexus in self.game.townhalls().ready.idle:
			if self.should_train_probe():
				self.game.do(nexus.train(PROBE))

	async def train_voidray(self):
		for sg in self.game.structures(STARGATE).ready.idle:
			if self.should_train_voidray():
				self.game.do(sg.train(VOIDRAY))

	async def train_zealot(self):
		for gw in self.game.structures(GATEWAY).ready.idle:
			if self.should_train_zealot():
				self.game.do(gw.train(ZEALOT))

	async def train_observer(self):
		if self.should_train_observer():
			robotic = self.game.structures(ROBOTICSFACILITY).ready.idle.first
			if robotic:
				self.game.do(robotic.train(OBSERVER))

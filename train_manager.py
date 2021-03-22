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
		await self.train_mothership()
		await self.train_phoenix()
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
			if self.game.units(VOIDRAY).amount < self.game.strategy_manager.min_off_vr_rush:
				return True
			if self.game.units(MOTHERSHIP).amount or not self.game.strategy_manager.build_mothership:
				return True
			if self.game.structures(FLEETBEACON).amount and self.game.already_pending(MOTHERSHIP):
				return True
			if self.game.minerals > 650 and self.game.vespene > 550:
				return True
		return False

	def should_train_zealot(self):
		if self.game.can_afford(ZEALOT) and self.game.units(ZEALOT).amount < self.game.strategy_manager.ground_defenses[ZEALOT] and not self.game.already_pending(ZEALOT):
			return True
		return False

	def should_train_mothership(self):
		if self.game.strategy_manager.build_mothership and self.game.can_afford(MOTHERSHIP) and not self.game.units(MOTHERSHIP).amount:
			return True
		return False

	def should_train_phoenix(self):
		if self.game.can_afford(PHOENIX) and self.game.units(PHOENIX).amount < self.game.strategy_manager.phoenix_amount and not self.game.already_pending(PHOENIX) and self.game.strategy_manager.phoenix_harass:
			return True
		return False

	def should_train_observer(self):
		if self.game.can_afford(OBSERVER) and self.game.structures(ROBOTICSFACILITY).ready.idle.amount > 0:
			if self.game.units(OBSERVER).amount < self.game.strategy_manager.observer_amount[0]:
				return True
			if self.game.strategy_manager.cloack_units_detected and self.game.units(OBSERVER).amount < self.game.strategy_manager.observer_amount[1]:
				return True
		return False

	# train methods
	async def train_probe(self):
		if(self.game.minerals > 2000 and self.max_probes == 64):
			self.max_probes = 48
		if(self.game.minerals < 300 and self.max_probes == 48):
			self.max_probes = 64
		for nexus in self.game.townhalls().ready.idle:
			if self.should_train_probe():
				self.game.do(nexus.train(PROBE))

	async def train_voidray(self):
		for sg in self.game.structures(STARGATE).ready.idle:
			if self.should_train_voidray():
				self.game.do(sg.train(VOIDRAY))
				return

	async def train_phoenix(self):
		for sg in self.game.structures(STARGATE).ready.idle:
			if self.should_train_phoenix():
				self.game.do(sg.train(PHOENIX))
				return

	async def train_zealot(self):
		for gw in self.game.structures(GATEWAY).ready.idle:
			if self.should_train_zealot():
				self.game.do(gw.train(ZEALOT))

	async def train_observer(self):
		if self.should_train_observer():
			robotic = self.game.structures(ROBOTICSFACILITY).ready.idle.first
			if robotic:
				self.game.do(robotic.train(OBSERVER))

	async def train_mothership(self):
		if self.should_train_mothership():
			nexus = self.game.structures(NEXUS).ready.closest_to(self.game.unit_manager.deffensive_position)
			if nexus:
				self.game.do(nexus.train(MOTHERSHIP))

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
		await self.train_colossus()
		await self.train_phoenix()
		await self.train_stalker()
		await self.train_voidray()
		await self.train_sentry()
		await self.train_zealot()
		await self.train_probe()

	# train conditions
	def should_train_probe(self):
		if self.game.can_afford(UnitTypeId.PROBE):
			num_nexus = self.game.townhalls().amount
			max_probes = min(self.max_probes, num_nexus * self.probes_per_nexus)
			if self.game.units(UnitTypeId.PROBE).amount < max_probes:
				return True
		return False

	def should_train_voidray(self):
		if self.game.units(UnitTypeId.VOIDRAY).amount >= self.game.bot.strategy_manager.max_troops[UnitTypeId.VOIDRAY]:
			return False
		if self.game.can_afford(UnitTypeId.VOIDRAY):
			if self.game.units(UnitTypeId.VOIDRAY).amount < self.game.bot.strategy_manager.min_to_rush[UnitTypeId.VOIDRAY]:
				return True
			if self.game.units(UnitTypeId.COLOSSUS).amount < self.game.bot.strategy_manager.max_troops[UnitTypeId.COLOSSUS] and self.game.structures(UnitTypeId.ROBOTICSFACILITY).amount:
				return False
			if self.game.units(UnitTypeId.MOTHERSHIP).amount or not self.game.bot.strategy_manager.max_troops[UnitTypeId.MOTHERSHIP]:
				return True
			if self.game.structures(UnitTypeId.FLEETBEACON).amount and self.game.already_pending(UnitTypeId.MOTHERSHIP):
				return True
			if self.game.minerals > 650 and self.game.vespene > 550:
				return True
		return False

	def should_train_zealot(self):
		if self.game.units(UnitTypeId.ZEALOT).amount >= self.game.bot.strategy_manager.max_troops[UnitTypeId.ZEALOT]:
			return False
		if self.game.can_afford(UnitTypeId.ZEALOT) and self.game.units(UnitTypeId.ZEALOT).amount < self.game.bot.strategy_manager.max_troops[UnitTypeId.ZEALOT] and not self.game.already_pending(UnitTypeId.ZEALOT):
			return True
		return False

	def should_train_stalker(self):
		if self.game.units(UnitTypeId.STALKER).amount >= self.game.bot.strategy_manager.max_troops[UnitTypeId.STALKER]:
			return False
		if self.game.can_afford(UnitTypeId.STALKER) and self.game.units(UnitTypeId.STALKER).amount < self.game.bot.strategy_manager.max_troops[UnitTypeId.STALKER] and not self.game.already_pending(UnitTypeId.STALKER):
			return True
		return False

	def should_train_sentry(self):
		if self.game.units(UnitTypeId.SENTRY).amount >= self.game.bot.strategy_manager.max_troops[UnitTypeId.SENTRY]:
			return False
		if self.game.can_afford(UnitTypeId.SENTRY) and self.game.units(UnitTypeId.SENTRY).amount < self.game.bot.strategy_manager.max_troops[UnitTypeId.SENTRY] and not self.game.already_pending(UnitTypeId.SENTRY):
			return True
		return False

	def should_train_colossus(self):
		if self.game.units(UnitTypeId.COLOSSUS).amount >= self.game.bot.strategy_manager.max_troops[UnitTypeId.COLOSSUS]:
			return False
		if self.game.can_afford(UnitTypeId.COLOSSUS) and self.game.units(UnitTypeId.COLOSSUS).amount < self.game.bot.strategy_manager.max_troops[UnitTypeId.COLOSSUS] and not self.game.already_pending(UnitTypeId.COLOSSUS):
			return True
		return False

	def should_train_mothership(self):
		if self.game.units(UnitTypeId.MOTHERSHIP).amount >= self.game.bot.strategy_manager.max_troops[UnitTypeId.MOTHERSHIP]:
			return False
		if self.game.bot.strategy_manager.max_troops[UnitTypeId.MOTHERSHIP] and self.game.can_afford(UnitTypeId.MOTHERSHIP) and not self.game.units(UnitTypeId.MOTHERSHIP).amount:
			return True
		return False

	def should_train_phoenix(self):
		if self.game.units(UnitTypeId.PHOENIX).amount >= self.game.bot.strategy_manager.max_troops[UnitTypeId.PHOENIX]:
			return False
		if self.game.can_afford(UnitTypeId.PHOENIX) and not self.game.already_pending(UnitTypeId.PHOENIX) and self.game.units(UnitTypeId.VOIDRAY).amount >= self.game.bot.strategy_manager.min_to_rush[UnitTypeId.VOIDRAY] - 1:
			return True
		return False

	def should_train_observer(self):
		if self.game.can_afford(UnitTypeId.OBSERVER) and self.game.structures(UnitTypeId.ROBOTICSFACILITY).ready.idle.amount > 0:
			if self.game.units(UnitTypeId.OBSERVER).amount < self.game.bot.strategy_manager.observer_amount[0]:
				return True
			if self.game.bot.strategy_manager.cloack_units_detected and self.game.units(UnitTypeId.OBSERVER).amount < self.game.bot.strategy_manager.observer_amount[1]:
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
				nexus.train(UnitTypeId.PROBE)

	async def train_voidray(self):
		for sg in self.game.structures(UnitTypeId.STARGATE).ready.idle:
			if self.should_train_voidray():
				sg.train(UnitTypeId.VOIDRAY)
				return

	async def train_phoenix(self):
		for sg in self.game.structures(UnitTypeId.STARGATE).ready.idle:
			if self.should_train_phoenix():
				sg.train(UnitTypeId.PHOENIX)
				return

	async def train_zealot(self):
		for gw in self.game.structures(UnitTypeId.GATEWAY).ready.idle:
			if self.should_train_zealot():
				gw.train(UnitTypeId.ZEALOT)

	async def train_stalker(self):
		for gw in self.game.structures(UnitTypeId.GATEWAY).ready.idle:
			if self.should_train_stalker():
				gw.train(UnitTypeId.STALKER)

	async def train_sentry(self):
		for gw in self.game.structures(UnitTypeId.GATEWAY).ready.idle:
			if self.should_train_sentry():
				gw.train(UnitTypeId.SENTRY)

	async def train_colossus(self):
		if self.should_train_colossus():
			robotic = self.game.structures(UnitTypeId.ROBOTICSFACILITY).ready.idle
			if robotic:
				robotic.first.train(UnitTypeId.COLOSSUS)

	async def train_observer(self):
		if self.should_train_observer():
			robotic = self.game.structures(UnitTypeId.ROBOTICSFACILITY).ready.idle
			if robotic:
				robotic.first.train(UnitTypeId.OBSERVER)

	async def train_mothership(self):
		if self.should_train_mothership():
			nexus = self.game.structures(UnitTypeId.NEXUS).ready.closest_to(self.game.bot.unit_manager.deffensive_position)
			if nexus:
				nexus.train(UnitTypeId.MOTHERSHIP)

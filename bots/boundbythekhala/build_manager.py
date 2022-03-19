from sc2.units import Units
from sc2.constants import *

class BuildManager:
	def __init__(self, game):
		self.game = game
		# build order properties
		self.build_complete = False
		self.first_pylon_probe = None
		self.first_gw_probe = None
		self.cc_probe = None
		self.sg_probe = None
		self.first_pylon_position = None

	# build priority order
	async def build(self):
		if self.build_complete:
			await self.build_general()
		else:
			await self.build_order_stargate()

	async def build_general(self):
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

	async def build_order_stargate(self):
		await self.bo_build_pylon()
		await self.bo_build_gateway()
		await self.bo_build_assimilator()
		await self.bo_build_cyberneticscore()
		await self.bo_build_nexus()
		await self.bo_build_stargate()

	"""
	BUILD ORDER METHODS
	"""
	async def bo_build_first_pylon(self):
		if not self.first_pylon_position:
			self.first_pylon_position = self.game.start_location.towards(self.game.game_info.map_center, 7)
		if self.first_pylon_probe:
			worker = self.game.workers.find_by_tag(self.first_pylon_probe)
			if not worker:
				self.first_pylon_probe = False
				return
			if self.game.can_afford(UnitTypeId.PYLON):
				await self.game.build(UnitTypeId.PYLON, near=self.first_pylon_position, build_worker=worker)
			else:
				worker.move(self.first_pylon_position)

	async def bo_build_pylon(self):
		# 1st pylon
		if not self.game.structures(UnitTypeId.PYLON).amount and not self.game.already_pending(UnitTypeId.PYLON):
			await self.bo_build_first_pylon()
			return
		elif self.first_pylon_probe:
			if self.first_pylon_probe in self.game.bot.base_manager.bussy_probes:
				self.game.bot.base_manager.bussy_probes.remove(self.first_pylon_probe)
			self.first_pylon_probe = None
		# 2nd pylon
		if self.cc_probe and self.game.structures(UnitTypeId.NEXUS).amount == 2:
			if self.game.structures(UnitTypeId.PYLON).amount == 1:
				worker = self.game.workers.find_by_tag(self.cc_probe)
				if worker:
					pylon_position = self.game.structures(UnitTypeId.NEXUS).closest_to(self.game.game_info.map_center).position.towards(self.game.game_info.map_center, 5)
					if self.game.can_afford(UnitTypeId.PYLON):
						await self.game.build(UnitTypeId.PYLON, near=pylon_position, build_worker=worker)
					elif not self.game.placeholders(UnitTypeId.PYLON):
						worker.move(pylon_position)
			else:
				worker = self.game.workers.find_by_tag(self.cc_probe)
				if worker:
					worker.gather(self.game.mineral_field.closest_to(self.game.start_location))
				self.game.bot.base_manager.bussy_probes.remove(self.cc_probe)
				self.cc_probe = None
		# 3th
		if self.game.structures(UnitTypeId.PYLON).amount == 2 and self.game.structures(UnitTypeId.WARPGATE).amount + self.game.structures(UnitTypeId.GATEWAY).amount + self.game.placeholders(UnitTypeId.GATEWAY).amount == 4:
			await self.game.build(UnitTypeId.PYLON, self.first_pylon_position)
		# 4th
		if self.game.structures(UnitTypeId.PYLON).amount == 3 and not self.game.already_pending(UnitTypeId.PYLON) and self.game.units(STALKER).amount == 3:
			await self.game.build(UnitTypeId.PYLON, self.game.start_location.towards(self.game.game_info.map_center, -11))

	async def bo_build_gateway(self):
		if self.game.structures(UnitTypeId.PYLON).amount == 1 and not self.game.structures(UnitTypeId.GATEWAY) and not self.game.structures(UnitTypeId.WARPGATE):
			if not self.game.already_pending(UnitTypeId.PYLON) or self.game.structures(UnitTypeId.PYLON).first.build_progress > 0.8 and not self.game.placeholders(UnitTypeId.GATEWAY):
				if not self.first_gw_probe:
					worker = self.game.select_build_worker(self.first_pylon_position)
					self.first_gw_probe = worker.tag
					self.game.bot.base_manager.bussy_probes.append(self.first_gw_probe)
					self.game.bot.base_manager.release_worker(worker)
				else:
					worker = self.game.workers.find_by_tag(self.first_gw_probe)
					if worker:
						if self.game.can_afford(UnitTypeId.GATEWAY):
							await self.game.build(UnitTypeId.GATEWAY, near=worker.position, build_worker=worker)
						elif worker.is_carrying_resource:
							worker(AbilityId.HARVEST_RETURN_PROBE)
						elif worker.position.distance_to(self.first_pylon_position) > 3:
							worker.move(self.first_pylon_position)
		elif self.first_gw_probe:
			self.game.bot.base_manager.bussy_probes.remove(self.first_gw_probe)
			self.first_gw_probe = None
		# 2nd, 3th and 4th
		if self.game.already_pending_upgrade(UpgradeId.BLINKTECH):
			if self.game.structures(UnitTypeId.PYLON) and self.game.structures(UnitTypeId.WARPGATE).amount + self.game.structures(UnitTypeId.GATEWAY).amount + self.game.placeholders(UnitTypeId.GATEWAY).amount < 4:
				await self.game.build(UnitTypeId.GATEWAY, self.game.structures(UnitTypeId.PYLON).random.position)

	async def bo_build_cyberneticscore(self):
		if self.game.structures(UnitTypeId.PYLON) and self.game.structures(UnitTypeId.GATEWAY) and not self.game.structures(UnitTypeId.CYBERNETICSCORE) and not self.game.already_pending(UnitTypeId.CYBERNETICSCORE):
			if not self.game.already_pending(UnitTypeId.GATEWAY) or self.game.structures(UnitTypeId.GATEWAY).first.build_progress > 0.8:
				if self.cc_probe:
					worker = self.game.workers.find_by_tag(self.cc_probe)
					if worker:
						cc_position = self.game.structures(UnitTypeId.PYLON).first.position.towards(self.game.structures(UnitTypeId.GATEWAY).first.position, -3)
						if self.game.can_afford(UnitTypeId.CYBERNETICSCORE):
							await self.game.build(UnitTypeId.CYBERNETICSCORE, near=cc_position, build_worker=worker)
						else:
							worker.move(cc_position)

	async def bo_build_nexus(self):
		if self.game.structures(UnitTypeId.CYBERNETICSCORE) and self.game.structures(UnitTypeId.NEXUS).amount < 2:
			if self.cc_probe:
				worker = self.game.workers.find_by_tag(self.cc_probe)
				if worker:
					nexus_position = await self.game.get_next_expansion()
					if self.game.can_afford(UnitTypeId.NEXUS):
						await self.game.build(UnitTypeId.NEXUS, near=nexus_position, build_worker=worker)
					elif not self.game.placeholders(UnitTypeId.NEXUS):
						worker.move(nexus_position)

	async def bo_build_assimilator(self):
		# 1st assim
		if self.game.already_pending(UnitTypeId.GATEWAY) and self.game.can_afford(UnitTypeId.ASSIMILATOR):
			nexus = self.game.townhalls().ready.first
			vespene = self.game.vespene_geyser.closer_than(13.0, nexus).furthest_to(self.game.game_info.map_center)
			if not self.game.structures(UnitTypeId.ASSIMILATOR).amount or not self.game.structures(UnitTypeId.ASSIMILATOR).closer_than(1.0, vespene):
				await self.game.build(UnitTypeId.ASSIMILATOR, vespene)
		# 2nd assim
		if self.game.structures(UnitTypeId.PYLON).amount == 2 and self.game.can_afford(UnitTypeId.ASSIMILATOR) and self.game.structures(UnitTypeId.ASSIMILATOR).amount < 2:
			nexus = self.game.townhalls().ready.first
			vespene = self.game.vespene_geyser.closer_than(13.0, nexus).closest_to(self.game.game_info.map_center)
			if not self.game.structures(UnitTypeId.ASSIMILATOR).amount or not self.game.structures(UnitTypeId.ASSIMILATOR).closer_than(1.0, vespene):
				await self.game.build(UnitTypeId.ASSIMILATOR, vespene)

	async def bo_build_stargate(self):
		if not self.game.structures(UnitTypeId.STARGATE).amount and not self.game.already_pending(UnitTypeId.STARGATE):
			if self.game.structures(UnitTypeId.PYLON) and not self.game.structures(UnitTypeId.STARGATE) and not self.game.already_pending(UnitTypeId.STARGATE):
				if self.game.structures(UnitTypeId.CYBERNETICSCORE) and self.game.vespene > 140:
					if not self.sg_probe:
						w = self.game.workers.closest_to(self.first_pylon_position)
						self.game.bot.base_manager.release_worker(w)
						self.sg_probe = w.tag
						self.game.bot.base_manager.bussy_probes.append(self.sg_probe)
					w = self.game.workers.find_by_tag(self.sg_probe)
					if w:
						if self.game.can_afford(UnitTypeId.STARGATE):
							await self.game.build(UnitTypeId.STARGATE, near=self.first_pylon_position, build_worker=w)
						else:
							w.move(self.first_pylon_position)
		elif self.sg_probe:
			if self.sg_probe in self.game.bot.base_manager.bussy_probes:
				self.game.bot.base_manager.bussy_probes.remove(self.sg_probe)
			self.sg_probe = None
			self.build_complete = True

	"""
	GENERAL BUILD METHODS
	"""
	# build conditions
	def should_build_forge(self):
		if self.game.bot.strategy_manager.build_cannons or self.game.minerals > 1000:
			if self.game.structures(UnitTypeId.PYLON).ready.amount and self.game.structures(UnitTypeId.GATEWAY).amount and self.game.can_afford(UnitTypeId.FORGE) and self.game.structures(UnitTypeId.FORGE).amount < 1 and not self.game.already_pending(UnitTypeId.FORGE):
				return True
		return False

	def should_build_cannon(self):
		if self.game.bot.strategy_manager.build_cannons or self.game.minerals > 1000:
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
			if max_gateways == 2 and self.game.minerals > 1000:
				max_gateways = self.game.townhalls().amount * 2
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
				if (self.game.structures(UnitTypeId.STARGATE).amount < 1) or (self.game.structures(UnitTypeId.STARGATE).amount < 2 and self.game.units(UnitTypeId.VOIDRAY).amount > 1 and not self.game.already_pending(UnitTypeId.STARGATE)) or (self.game.minerals > 300 * self.game.structures(UnitTypeId.STARGATE).amount and self.game.vespene > 400):
					return True
		return False

	def should_build_roboticsfacility(self):
		if self.game.structures(UnitTypeId.PYLON).ready.exists and self.game.structures(UnitTypeId.CYBERNETICSCORE).ready.exists:
			if self.game.can_afford(UnitTypeId.ROBOTICSFACILITY) and not self.game.already_pending(UnitTypeId.ROBOTICSFACILITY):
				if not self.game.structures(UnitTypeId.ROBOTICSFACILITY).amount and not self.game.already_pending(UnitTypeId.ROBOTICSFACILITY) and (self.game.supply_used >= self.game.bot.strategy_manager.observer_delay or self.game.bot.strategy_manager.cloack_units_detected):
					return True
		return False

	async def should_build_nexus(self):
		# TODO: clean expansion first
		if self.game.can_afford(UnitTypeId.NEXUS) and ((not self.game.already_pending(UnitTypeId.NEXUS) and (self.game.townhalls().amount - 1) * 2 <= self.game.units(UnitTypeId.VOIDRAY).amount) or (self.game.minerals > 1500 and not self.game.already_pending(UnitTypeId.NEXUS)) and await self.game.get_next_expansion()):
			return True
		return False

	def should_build_asimilator(self):
		if self.game.can_afford(UnitTypeId.ASSIMILATOR) and self.game.structures(UnitTypeId.GATEWAY).exists:
			return True
		return False

	def should_build_fleetbeacon(self):
		if self.game.bot.strategy_manager.max_troops[UnitTypeId.MOTHERSHIP] and self.game.structures(UnitTypeId.PYLON).ready.exists and self.game.structures(UnitTypeId.STARGATE).ready.exists and self.game.units(UnitTypeId.VOIDRAY).amount >= 3:
			if self.game.can_afford(UnitTypeId.FLEETBEACON) and not self.game.already_pending(UnitTypeId.FLEETBEACON) and not self.game.structures(UnitTypeId.FLEETBEACON).amount:
				return True
		return False

	def should_build_roboticsbay(self):
		if self.game.bot.strategy_manager.max_troops[UnitTypeId.COLOSSUS] and self.game.structures(UnitTypeId.PYLON).ready.exists and self.game.structures(UnitTypeId.ROBOTICSFACILITY).ready.exists and self.game.units(UnitTypeId.MOTHERSHIP).amount:
			if self.game.can_afford(UnitTypeId.ROBOTICSBAY) and not self.game.already_pending(UnitTypeId.ROBOTICSBAY) and not self.game.structures(UnitTypeId.ROBOTICSBAY).amount:
				return True
		return False

	def should_build_shield(self):
		return False
		if self.game.structures(UnitTypeId.PYLON).ready.exists and self.game.structures(UnitTypeId.GATEWAY).ready.exists and self.game.minerals > 500 + 50*self.game.structures(UnitTypeId.SHIELDBATTERY).amount:
			return True
		return False

	# build methods
	async def build_forge(self):
		if self.should_build_forge():
			pylons = self.game.structures(UnitTypeId.PYLON).ready.closer_than(20, self.game.start_location)
			if not pylons:
				pylons = self.game.structures(UnitTypeId.PYLON).ready
			await self.game.build(UnitTypeId.FORGE, near=pylons.random.position.towards(self.game.game_info.map_center, 4))

	async def build_cannon(self):
		if self.should_build_cannon():
			for n in self.game.townhalls():
				if self.game.structures(UnitTypeId.PYLON).ready.closer_than(8, n.position.towards(self.game.game_info.map_center, -5.5)).amount:
					if not self.game.structures(UnitTypeId.PHOTONCANNON) or self.game.structures(UnitTypeId.PHOTONCANNON).closer_than(8, n.position.towards(self.game.game_info.map_center, -5.5)).amount < 1:
						await self.game.build(UnitTypeId.PHOTONCANNON, near=n.position.towards(self.game.game_info.map_center, -5.5))

	async def build_pylon(self):
		if self.should_build_pylon():
			if self.game.structures(UnitTypeId.PYLON).amount:
				for n in self.game.townhalls():
					if not self.game.structures(UnitTypeId.PYLON).closer_than(8, n.position.towards(self.game.game_info.map_center, -8)).amount:
						await self.game.build(UnitTypeId.PYLON, near=n.position.towards(self.game.game_info.map_center, -8))
						return
			await self.game.build(UnitTypeId.PYLON, near=self.game.start_location.towards(self.game.game_info.map_center, 7))

	async def build_gateway(self):
		if self.should_build_gateway():
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
						if not self.game.placeholders(UnitTypeId.ASSIMILATOR).closer_than(1.0, vespene):
							worker.build(UnitTypeId.ASSIMILATOR, vespene)


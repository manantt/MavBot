from sc2.units import Units
from sc2.constants import *
from sc2.ids.ability_id import AbilityId
import random

# TODO: use sentry to scout
# TODO: improve prismaticalalignment

class AbilityManager:
	def __init__(self, game):
		self.game = game

	async def use_abilities(self):
		await self.use_chronoboost()
		#await self.use_prismaticalalignment()

	async def use_chronoboost(self):
		for nexus in self.game.townhalls().ready:
			abilities = await self.game.get_available_abilities(nexus)
			if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
				nexuses = self.game.townhalls().ready
				stargates = self.game.structures(STARGATE).ready
				random_building = None
				for nexus in nexuses:
					if not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
						for order in nexus.orders:
							if order.ability.id == NEXUSTRAINMOTHERSHIP_MOTHERSHIP:
								random_building = nexus
				if not random_building:
					if len(stargates) > 0:
						random_building = random.choice(stargates)
					else:
						if not self.game.structures(PYLON).amount == 0:
							random_building = random.choice(nexuses)
						else:
							return
				if not random_building.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
					if not random_building.is_idle:
						self.game.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, random_building))

	async def use_prismaticalalignment(self):
		for vr in self.game.units(VOIDRAY):
			#TODO: use only if attacking armored units
			abilities = await self.game.get_available_abilities(vr)
			if vr.weapon_cooldown > 0 and AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT in abilities:
				self.game.combined_actions.append(vr(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT))

	def should_use_forcefield(self):
		if self.game.enemy_units and self.game.enemy_units.closer_than(1, self.game.main_base_ramp.bottom_center).amount:
			return True
		return False

	async def use_forcefield(self):
		if self.should_use_forcefield():
			for sentry in self.game.units(SENTRY):
				abilities = await self.game.get_available_abilities(sentry)
				if AbilityId.FORCEFIELD_FORCEFIELD in abilities:
					self.game.combined_actions.append(sentry(AbilityId.FORCEFIELD_FORCEFIELD, self.game.main_base_ramp.bottom_center))
					return

	async def use_hallucination(self):
		for sentry in self.game.units(SENTRY):
			if self.game.enemy_units.amount and self.game.enemy_units.closer_than(7, sentry).amount:
				print("1")
				abilities = await self.game.get_available_abilities(sentry)
				if AbilityId.HALLUCINATION_ARCHON in abilities:
					print("2")
					self.game.combined_actions.append(sentry(AbilityId.HALLUCINATION_ARCHON))
					return
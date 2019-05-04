from psc2.sc2.units import Units
from psc2.sc2.constants import *
from psc2.sc2.ids.ability_id import AbilityId
import random

# TODO: use sentry to scout
# TODO: improve prismaticalalignment

class AbilityManager:
	def __init__(self, game):
		self.game = game

	async def use_abilities(self):
		await self.use_chronoboost()
		await self.use_prismaticalalignment()

	async def use_chronoboost(self):
		for nexus in self.game.units(NEXUS).ready:
			abilities = await self.game.get_available_abilities(nexus)
			if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
				nexuses = self.game.units(NEXUS).ready
				stargates = self.game.units(STARGATE).ready
				if len(stargates) > 0:
					random_building = random.choice(stargates)
				else:
					if not self.game.units(PYLON).amount == 0:
						random_building = random.choice(nexuses)
					else:
						return
				if not random_building.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
					if not random_building.noqueue:
						await self.game.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, random_building))

	async def use_prismaticalalignment(self):
		for vr in self.game.units(VOIDRAY):
			#TODO: use only if attacking armored units
			abilities = await self.game.get_available_abilities(vr)
			if vr.weapon_cooldown > 0 and AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT in abilities and True: #TODO: comprobar si hay suficiente amenaza para activar
				await self.game.do(vr(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT))
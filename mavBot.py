import sc2, random

from sc2 import run_game, maps, Race, Difficulty, position
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.position import Point2, Point3
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId

from unit_manager import UnitManager
from upgrade_manager import UpgradeManager
from build_manager import BuildManager
from train_manager import TrainManager
from ability_manager import AbilityManager
from worker_manager import WorkerManager
from debug_manager import DebugManager
from strategy_manager import StrategyManager

"""
TODO:
- Limpiar siguiente expansión (poner cañón en minerales)
- Defender de cannon rush
- Micro:
	- retirar heridos
	- focus sobre la mayor amenaza
	- mantener rango
- Calcular victoria en baserush y retirar ataque si es necesario
- Espiar con alucinaciones
- Mejoras faltantes
- Defender obreros de voladores
- Optimizar:
	- Asignar grupo de ataque y mover juntos
- Escaramuzas a por obreros
- Regreso en masa
"""

class MavBot(sc2.BotAI):
	def __init__(self):
		self.unit_manager = UnitManager(self)
		self.upgrade_manager = UpgradeManager(self)
		self.build_manager = BuildManager(self)
		self.train_manager = TrainManager(self)
		self.ability_manager = AbilityManager(self)
		self.worker_manager = WorkerManager(self)
		self.debug_manager = DebugManager(self)
		self.strategy_manager = StrategyManager(self)
		self.debug = True

	async def on_step(self, iteration):
		if iteration == 1:
			await self.on_1st_step()
		if iteration % 5 == 0:
			await self.on_5_step()
		await self.train_manager.train_troops()
		await self.build_manager.build()
		await self.unit_manager.move_troops()
		await self.ability_manager.use_abilities()
		await self.upgrade_manager.research_upgrades()
		if self.debug:
			await self.debug_manager.draw_debug()

	async def on_1st_step(self):
		pass

	async def on_5_step(self):
		await self.worker_manager.manage_workers()

	async def on_unit_destroyed(self, unit_tag):
		# removes units from offensive groups when destroyed
		for unit in self.unit_manager.off_group:
			if unit.tag == unit_tag:
				self.unit_manager.off_group.remove(unit)
		# removes enemy units from cache
		for unitType in self.unit_manager.cachedUnits:
			if unit_tag in self.unit_manager.cachedUnits[unitType]:
				self.unit_manager.cachedUnits[unitType].remove(unit_tag)

if __name__ == '__main__':
	mapsS8 = [
		"Acropolis",
		"Artana", 
		"Bandwidth",
		"CrystalCavern",
		"DigitalFrontier",
		"Ephemeron",
		"OldSunshine",
		"Primus",
		"Reminiscence",
		"Sanglune",
		"TheTimelessVoid",
		"Treachery",
		"Triton",
		"Urzagol"
	]
	run_game(maps.get(random.choice(mapsS8)), [
		Bot(Race.Protoss, MavBot()),
		Computer(Race.Protoss, Difficulty.CheatInsane) #VeryHard CheatVision CheatMoney CheatInsane
		], realtime=False)
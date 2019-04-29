from sc2.units import Units
from sc2.constants import *

class WorkerManager:
	def __init__(self, game):
		self.game = game

	async def manage_workers(self):
		# TODO: improve default logic
		await self.game.distribute_workers()
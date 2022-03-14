
import sc2
from sc2.constants import *

class WorkerRushBot():
    def __init__(self, bot):
        self.bot = bot

    async def on_step(self, iteration):
        # probe attack
        n = self.bot.townhalls()
        for worker in self.bot.workers:
            if worker.shield > 1 or self.bot.workers.amount > 8 or worker.distance_to(n.position) < 5:
                worker.attack(self.bot.enemy_start_locations[0])
            else:
                enemy = self.bot.enemy_units
                if(self.bot.enemy_units):
                    closest_enemy = self.bot.enemy_units.closest_to(worker)
                    worker.move(worker.position.towards(closest_enemy.position, -3))
                else:    
                    if n:
                        worker.move(n.first)
        # train probes
        for nexus in self.bot.townhalls().ready.idle:
            if self.bot.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)
        # TODO: train zealots
        # TODO: cancel buildings

    async def on_unit_created(self, unit):
        pass

    async def on_unit_destroyed(self, unit_tag):
        pass

    async def on_building_construction_started(self, unit):
        pass

    async def on_building_construction_complete(self, structure):
        pass

    def on_end(self, game_result):
        pass
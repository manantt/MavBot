
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer


class WorkerRushBot(sc2.BotAI):
    def __init__(self):
        self.combined_actions = [];

    async def on_step(self, iteration):
        for worker in self.workers:
            self.combined_actions.append(worker.attack(self.enemy_start_locations[0]))
        await self._do_actions(self.combined_actions)
        self.combined_actions.clear()

def main():
    run_game(
        maps.get("WorldofSleepersLE"),
        [Bot(Race.Zerg, WorkerRushBot()), Computer(Race.Protoss, Difficulty.Medium)],
        realtime=True
    )


if __name__ == "__main__":
    main()
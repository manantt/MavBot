import sys, sc2
from sc2.bot_ai import BotAI

from __init__ import run_ladder_game

# Load bot
from mavBot import MavBot

from sc2 import maps
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer

bot = Bot(Race.Protoss, MavBot())
class WorkerRushBot(BotAI):
    async def on_step(self, iteration):
        for worker in self.workers:
            worker.attack(self.enemy_start_locations[0])
bot2 = Bot(Race.Protoss, WorkerRushBot())

# Start game
if __name__ == "__main__":
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        result, opponentid = run_ladder_game(bot)
        print(result, " against opponent ", opponentid)
    else:
        # Local game
        print("Starting local game...")
        run_game(maps.get("HardwireAIE"), [bot, Computer(Race.Zerg, Difficulty.VeryHard)], realtime=False)
        #run_game(maps.get("HardwireAIE"), [bot, bot2], realtime=True)

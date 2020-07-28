import sc2, sys
from __init__ import run_ladder_game
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer

# Load bot
from mavBot import MavBot
bot = Bot(Race.Protoss, MavBot(), "MavBot")

# Start game
if __name__ == '__main__':
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        result, opponentid = run_ladder_game(bot)
        print(result," against opponent ", opponentid)
    else:
        # Local game
        print("Starting local game...")
        sc2.run_game(sc2.maps.get("WorldofSleepersLE"), [
            bot,
            Computer(Race.Protoss, Difficulty.VeryHard)
        ], realtime=True)

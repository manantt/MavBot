import sc2, sys
from __init__ import run_ladder_game
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer

# Load bot
from boundByTheKhala import BoundByTheKhala
bot = Bot(Race.Protoss, BoundByTheKhala(), "BoundByTheKhala")

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
        sc2.run_game(sc2.maps.get("HardwireAIE"), [
            bot,
            Computer(Race.Zerg, Difficulty.VeryHard)
        ], realtime=True)

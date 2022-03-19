from sc2.bot_ai import BotAI
from sc2.player import Bot
from sc2.constants import *
from sc2.data import Result

import json, argparse, random

from constants import *

from bots.prismbeams.prismBeams import PrismBeams
from bots.flyingball.flyingBall import FlyingBall
from bots.boundbythekhala.boundByTheKhala import BoundByTheKhala
from bots.proberush.WorkerRushBot import WorkerRushBot

class MavBot(BotAI):
    def __init__(self):
        self.version = "v2_1_2"
        self.worker_rush = False
        self.opp_id = self.find_opp_id()
        self.bots = [
            PrismBeams(self), 
            BoundByTheKhala(self, ZEALOT1_DEFF),
            BoundByTheKhala(self, ZEALOT1_DEFF_PH),
            BoundByTheKhala(self, STALKER1_DEFF_PH),
            BoundByTheKhala(self, STALKER4_DEFF),
            BoundByTheKhala(self, MOTHERSHIP),
            BoundByTheKhala(self, ZEALOT10_STALKER5_DEFF),
            BoundByTheKhala(self, STALKER_PUSH),
            WorkerRushBot(self)
        ]
        # if strat is None it will choose the best one for this matchup
        self.strat = None 
        if self.strat == None:
            self.bot = self.bots[0]
        else:
            self.bot = self.bots[self.strat]

    ## EVENTS ########################################################    
    async def on_step(self, iteration):
        if iteration < 500:
            self.check_worker_rush()
        self.choose_bot(iteration)
        self.cancel_buildings()
        if iteration == 10:
            await self.on_1st_step()
        await self.bot.on_step(iteration)
        
    async def on_1st_step(self):
        await self._client.chat_send("Tag:" + self.version, team_only=False)
        await self._client.chat_send("Tag:strat_" + str(self.strat), team_only=True)

    async def on_unit_created(self, unit):
        await self.bot.on_unit_created(unit)

    async def on_unit_destroyed(self, unit_tag):
        await self.bot.on_unit_destroyed(unit_tag)

    async def on_building_construction_started(self, unit):
        pass

    async def on_building_construction_complete(self, structure):
        await self.bot.on_building_construction_complete(structure)

    def on_end(self, game_result):
        self.save_result(game_result)

    ## COMMON METHODS ########################################################    
    """
    Chooses the best bot to play
    """
    def choose_bot(self, iteration):
        if self.worker_rush:
            self.bot = self.bots[WORKER_RUSH]
        if self.strat == None:
            self.strat = self.choose_strat()
            self.bot = self.bots[self.strat]

    def choose_strat(self):
        f = open("data/matches.txt", "r")
        matches = f.read()
        f.close()
        matches = matches.split(";")
        winrate = {}
        max_score = 0
        for strat, bot in enumerate(self.bots):
            match_count = 2
            score = 1
            for match in matches:
                match = match.split(":")
                if match[0] == str(self.opp_id) and str(strat) == match[1]:
                    match_count = match_count + 1
                    if match[2] == "Result.Victory":
                        score = score + 1
                    if match[2] == "Result.Draw":
                        score = score + 0.5
            winrate[strat] = score/match_count
            if winrate[strat] > max_score:
                max_score = winrate[strat]
        choices = []
        for strat in winrate:
            if winrate[strat] >= max_score:
                choices.append(strat)
        choice = random.choice(choices)
        print(choice)
        return choice

    def find_opp_id(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--OpponentId', type=str, nargs="?", help='Opponent Id')
        args, unknown = parser.parse_known_args()
        if args.OpponentId:
            return args.OpponentId
        return None

    """
    Cancels the construction of a building that is going to be destroyed
    """
    def cancel_buildings(self):
        min_health_to_cancel = 21 # TODO: calculate this dinamically, depending on enemy units attacking the building damage 
        for building in self.structures.filter(lambda b: b.build_progress < 1 and b.health + b.shield < min_health_to_cancel and b.shield < b.health):
            building(AbilityId.CANCEL)

    """
    Checks if enemy worker rushes
    """
    def check_worker_rush(self):
        if self.enemy_units.filter(lambda u: u.type_id in {UnitTypeId.PROBE, UnitTypeId.DRONE, UnitTypeId.SCV}).amount > 2:
            if self.enemy_units.filter(lambda u: u.type_id in {UnitTypeId.PROBE, UnitTypeId.DRONE, UnitTypeId.SCV}).closer_than(10, self.start_location).amount > 2:
                self.worker_rush = True

    def save_result(self, game_result):
        print("saving")
        matches = open("data/matches.txt", "a")
        matches.write(str(self.opp_id) + ":" + str(self.strat) + ":" + str(game_result) + ";")
        matches.close()
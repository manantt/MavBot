from sc2.units import Units
from sc2.constants import *

class WorkerManager:
    def __init__(self, game):
        self.game = game

    async def manage_workers(self):
        # TODO: improve default logic
        await self.distribute_workers()

    async def distribute_workers(self, resource_ratio: float = 2):
        if not self.game.mineral_field or not self.game.workers or not self.game.townhalls.ready:
            return
        worker_pool = [worker for worker in self.game.workers.idle]
        bases = self.game.townhalls.ready
        gas_buildings = self.game.gas_buildings.ready

        # list of places that need more workers
        deficit_mining_places = []

        for mining_place in bases | gas_buildings:
            difference = mining_place.surplus_harvesters
            # perfect amount of workers, skip mining place
            if not difference:
                continue
            if mining_place.has_vespene:
                # get all workers that target the gas extraction site
                # or are on their way back from it
                local_workers = self.game.workers.filter(
                    lambda unit: unit.order_target == mining_place.tag
                    or (unit.is_carrying_vespene and unit.order_target == bases.closest_to(mining_place).tag)
                )
            else:
                # get tags of minerals around expansion
                local_minerals_tags = {
                    mineral.tag for mineral in self.game.mineral_field if mineral.distance_to(mining_place) <= 8
                }
                # get all target tags a worker can have
                # tags of the minerals he could mine at that base
                # get workers that work at that gather site
                local_workers = self.game.workers.filter(
                    lambda unit: unit.order_target in local_minerals_tags
                    or (unit.is_carrying_minerals and unit.order_target == mining_place.tag)
                )
            # too many workers
            if difference > 0:
                for worker in local_workers[:difference]:
                    worker_pool.append(worker)
            # too few workers
            # add mining place to deficit bases for every missing worker
            else:
                deficit_mining_places += [mining_place for _ in range(-difference)]

        # prepare all minerals near a base if we have too many workers
        # and need to send them to the closest patch
        if len(worker_pool) > len(deficit_mining_places):
            all_minerals_near_base = [
                mineral
                for mineral in self.game.mineral_field
                if any(mineral.distance_to(base) <= 8 for base in self.game.townhalls.ready)
            ]
        # distribute every worker in the pool
        for worker in worker_pool:
            if worker.tag == self.game.strategy_manager.cannon_rush_worker:
                continue
            # as long as have workers and mining places
            if deficit_mining_places:
                # choose only mineral fields first if current mineral to gas ratio is less than target ratio
                if self.game.vespene and self.game.minerals / self.game.vespene < resource_ratio:
                    possible_mining_places = [place for place in deficit_mining_places if not place.vespene_contents]
                # else prefer gas
                else:
                    possible_mining_places = [place for place in deficit_mining_places if place.vespene_contents]
                # if preferred type is not available any more, get all other places
                if not possible_mining_places:
                    possible_mining_places = deficit_mining_places
                # find closest mining place
                current_place = min(deficit_mining_places, key=lambda place: place.distance_to(worker))
                # remove it from the list
                deficit_mining_places.remove(current_place)
                # if current place is a gas extraction site, go there
                if current_place.vespene_contents:
                    self.game.do(worker.gather(current_place))
                # if current place is a gas extraction site,
                # go to the mineral field that is near and has the most minerals left
                else:
                    local_minerals = (
                        mineral for mineral in self.game.mineral_field if mineral.distance_to(current_place) <= 8
                    )
                    # local_minerals can be empty if townhall is misplaced
                    target_mineral = max(local_minerals, key=lambda mineral: mineral.mineral_contents, default=None)
                    if target_mineral:
                        self.game.do(worker.gather(target_mineral))
            # more workers to distribute than free mining spots
            # send to closest if worker is doing nothing
            elif worker.is_idle and all_minerals_near_base:
                target_mineral = min(all_minerals_near_base, key=lambda mineral: mineral.distance_to(worker))
                self.game.do(worker.gather(target_mineral))
            else:
                # there are no deficit mining places and worker is not idle
                # so dont move him
                pass
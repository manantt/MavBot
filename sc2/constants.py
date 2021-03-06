from .data import Alliance, Attribute, CloakState, DisplayType, TargetType
from .ids.ability_id import *
from .ids.buff_id import *
from .ids.effect_id import *
from .ids.unit_typeid import *
from .ids.upgrade_id import *
from collections import defaultdict
from typing import Dict, Set

mineral_ids: Set[int] = {
    RICHMINERALFIELD.value,
    RICHMINERALFIELD750.value,
    MINERALFIELD.value,
    MINERALFIELD450.value,
    MINERALFIELD750.value,
    LABMINERALFIELD.value,
    LABMINERALFIELD750.value,
    PURIFIERRICHMINERALFIELD.value,
    PURIFIERRICHMINERALFIELD750.value,
    PURIFIERMINERALFIELD.value,
    PURIFIERMINERALFIELD750.value,
    BATTLESTATIONMINERALFIELD.value,
    BATTLESTATIONMINERALFIELD750.value,
    MINERALFIELDOPAQUE.value,
    MINERALFIELDOPAQUE900.value,
}
geyser_ids: Set[int] = {
    VESPENEGEYSER.value,
    SPACEPLATFORMGEYSER.value,
    RICHVESPENEGEYSER.value,
    PROTOSSVESPENEGEYSER.value,
    PURIFIERVESPENEGEYSER.value,
    SHAKURASVESPENEGEYSER.value,
}
transforming: Dict[UnitTypeId, AbilityId] = {
    # terran structures
    BARRACKS: LAND_BARRACKS,
    BARRACKSFLYING: LAND_BARRACKS,
    COMMANDCENTER: LAND_COMMANDCENTER,
    COMMANDCENTERFLYING: LAND_COMMANDCENTER,
    ORBITALCOMMAND: LAND_ORBITALCOMMAND,
    ORBITALCOMMANDFLYING: LAND_ORBITALCOMMAND,
    FACTORY: LAND_FACTORY,
    FACTORYFLYING: LAND_FACTORY,
    STARPORT: LAND_STARPORT,
    STARPORTFLYING: LAND_STARPORT,
    SUPPLYDEPOT: MORPH_SUPPLYDEPOT_RAISE,
    SUPPLYDEPOTLOWERED: MORPH_SUPPLYDEPOT_LOWER,
    # terran units
    HELLION: MORPH_HELLION,
    HELLIONTANK: MORPH_HELLBAT,
    LIBERATOR: MORPH_LIBERATORAAMODE,
    LIBERATORAG: MORPH_LIBERATORAGMODE,
    SIEGETANK: UNSIEGE_UNSIEGE,
    SIEGETANKSIEGED: SIEGEMODE_SIEGEMODE,
    THOR: MORPH_THOREXPLOSIVEMODE,
    THORAP: MORPH_THORHIGHIMPACTMODE,
    VIKINGASSAULT: MORPH_VIKINGASSAULTMODE,
    VIKINGFIGHTER: MORPH_VIKINGFIGHTERMODE,
    WIDOWMINE: BURROWUP,
    WIDOWMINEBURROWED: BURROWDOWN,
    # protoss structures
    GATEWAY: MORPH_GATEWAY,
    WARPGATE: MORPH_WARPGATE,
    # protoss units
    OBSERVER: MORPH_OBSERVERMODE,
    OBSERVERSIEGEMODE: MORPH_SURVEILLANCEMODE,
    WARPPRISM: MORPH_WARPPRISMTRANSPORTMODE,
    WARPPRISMPHASING: MORPH_WARPPRISMPHASINGMODE,
    # zerg structures
    SPINECRAWLER: SPINECRAWLERROOT_SPINECRAWLERROOT,
    SPINECRAWLERUPROOTED: SPINECRAWLERUPROOT_SPINECRAWLERUPROOT,
    SPORECRAWLER: SPORECRAWLERROOT_SPORECRAWLERROOT,
    SPORECRAWLERUPROOTED: SPORECRAWLERUPROOT_SPORECRAWLERUPROOT,
    # zerg units
    BANELING: BURROWUP_BANELING,
    BANELINGBURROWED: BURROWDOWN_BANELING,
    DRONE: BURROWUP_DRONE,
    DRONEBURROWED: BURROWDOWN_DRONE,
    HYDRALISK: BURROWUP_HYDRALISK,
    HYDRALISKBURROWED: BURROWDOWN_HYDRALISK,
    INFESTOR: BURROWUP_INFESTOR,
    INFESTORBURROWED: BURROWDOWN_INFESTOR,
    INFESTORTERRAN: BURROWUP_INFESTORTERRAN,
    INFESTORTERRANBURROWED: BURROWDOWN_INFESTORTERRAN,
    LURKERMP: BURROWUP_LURKER,
    LURKERMPBURROWED: BURROWDOWN_LURKER,
    OVERSEER: MORPH_OVERSEERMODE,
    OVERSEERSIEGEMODE: MORPH_OVERSIGHTMODE,
    QUEEN: BURROWUP_QUEEN,
    QUEENBURROWED: BURROWDOWN_QUEEN,
    ROACH: BURROWUP_ROACH,
    ROACHBURROWED: BURROWDOWN_ROACH,
    SWARMHOSTBURROWEDMP: BURROWDOWN_SWARMHOST,
    SWARMHOSTMP: BURROWUP_SWARMHOST,
    ULTRALISK: BURROWUP_ULTRALISK,
    ULTRALISKBURROWED: BURROWDOWN_ULTRALISK,
    ZERGLING: BURROWUP_ZERGLING,
    ZERGLINGBURROWED: BURROWDOWN_ZERGLING,
}
# For now only contains units that cost supply, used in bot_ai.do()
abilityid_to_unittypeid: Dict[AbilityId, UnitTypeId] = {
    # Protoss
    AbilityId.NEXUSTRAIN_PROBE: UnitTypeId.PROBE,
    AbilityId.GATEWAYTRAIN_ZEALOT: UnitTypeId.ZEALOT,
    AbilityId.WARPGATETRAIN_ZEALOT: UnitTypeId.ZEALOT,
    AbilityId.TRAIN_ADEPT: UnitTypeId.ADEPT,
    AbilityId.TRAINWARP_ADEPT: UnitTypeId.ADEPT,
    AbilityId.GATEWAYTRAIN_STALKER: UnitTypeId.STALKER,
    AbilityId.WARPGATETRAIN_STALKER: UnitTypeId.STALKER,
    AbilityId.GATEWAYTRAIN_SENTRY: UnitTypeId.SENTRY,
    AbilityId.WARPGATETRAIN_SENTRY: UnitTypeId.SENTRY,
    AbilityId.GATEWAYTRAIN_DARKTEMPLAR: UnitTypeId.DARKTEMPLAR,
    AbilityId.WARPGATETRAIN_DARKTEMPLAR: UnitTypeId.DARKTEMPLAR,
    AbilityId.GATEWAYTRAIN_HIGHTEMPLAR: UnitTypeId.HIGHTEMPLAR,
    AbilityId.WARPGATETRAIN_HIGHTEMPLAR: UnitTypeId.HIGHTEMPLAR,
    AbilityId.ROBOTICSFACILITYTRAIN_OBSERVER: UnitTypeId.OBSERVER,
    AbilityId.ROBOTICSFACILITYTRAIN_COLOSSUS: UnitTypeId.COLOSSUS,
    AbilityId.ROBOTICSFACILITYTRAIN_IMMORTAL: UnitTypeId.IMMORTAL,
    AbilityId.ROBOTICSFACILITYTRAIN_WARPPRISM: UnitTypeId.WARPPRISM,
    AbilityId.STARGATETRAIN_CARRIER: UnitTypeId.CARRIER,
    AbilityId.STARGATETRAIN_ORACLE: UnitTypeId.ORACLE,
    AbilityId.STARGATETRAIN_PHOENIX: UnitTypeId.PHOENIX,
    AbilityId.STARGATETRAIN_TEMPEST: UnitTypeId.TEMPEST,
    AbilityId.STARGATETRAIN_VOIDRAY: UnitTypeId.VOIDRAY,
    AbilityId.NEXUSTRAINMOTHERSHIP_MOTHERSHIP: UnitTypeId.MOTHERSHIP,
    # Terran
    AbilityId.COMMANDCENTERTRAIN_SCV: UnitTypeId.SCV,
    AbilityId.BARRACKSTRAIN_MARINE: UnitTypeId.MARINE,
    AbilityId.BARRACKSTRAIN_GHOST: UnitTypeId.GHOST,
    AbilityId.BARRACKSTRAIN_MARAUDER: UnitTypeId.MARAUDER,
    AbilityId.BARRACKSTRAIN_REAPER: UnitTypeId.REAPER,
    AbilityId.FACTORYTRAIN_HELLION: UnitTypeId.HELLION,
    AbilityId.FACTORYTRAIN_SIEGETANK: UnitTypeId.SIEGETANK,
    AbilityId.FACTORYTRAIN_THOR: UnitTypeId.THOR,
    AbilityId.FACTORYTRAIN_WIDOWMINE: UnitTypeId.WIDOWMINE,
    AbilityId.TRAIN_HELLBAT: UnitTypeId.HELLIONTANK,
    AbilityId.TRAIN_CYCLONE: UnitTypeId.CYCLONE,
    AbilityId.STARPORTTRAIN_RAVEN: UnitTypeId.RAVEN,
    AbilityId.STARPORTTRAIN_VIKINGFIGHTER: UnitTypeId.VIKINGFIGHTER,
    AbilityId.STARPORTTRAIN_MEDIVAC: UnitTypeId.MEDIVAC,
    AbilityId.STARPORTTRAIN_BATTLECRUISER: UnitTypeId.BATTLECRUISER,
    AbilityId.STARPORTTRAIN_BANSHEE: UnitTypeId.BANSHEE,
    AbilityId.STARPORTTRAIN_LIBERATOR: UnitTypeId.LIBERATOR,
    # Zerg
    AbilityId.LARVATRAIN_DRONE: UnitTypeId.DRONE,
    AbilityId.LARVATRAIN_OVERLORD: UnitTypeId.OVERLORD,
    AbilityId.LARVATRAIN_ZERGLING: UnitTypeId.ZERGLING,
    AbilityId.LARVATRAIN_ROACH: UnitTypeId.ROACH,
    AbilityId.LARVATRAIN_HYDRALISK: UnitTypeId.HYDRALISK,
    AbilityId.LARVATRAIN_MUTALISK: UnitTypeId.MUTALISK,
    AbilityId.LARVATRAIN_CORRUPTOR: UnitTypeId.CORRUPTOR,
    AbilityId.LARVATRAIN_ULTRALISK: UnitTypeId.ULTRALISK,
    AbilityId.LARVATRAIN_INFESTOR: UnitTypeId.INFESTOR,
    AbilityId.LARVATRAIN_VIPER: UnitTypeId.VIPER,
    AbilityId.LOCUSTTRAIN_SWARMHOST: UnitTypeId.SWARMHOSTMP,
    AbilityId.TRAINQUEEN_QUEEN: UnitTypeId.QUEEN,
}

IS_STRUCTURE = Attribute.Structure.value
IS_LIGHT = Attribute.Light.value
IS_ARMORED = Attribute.Armored.value
IS_BIOLOGICAL = Attribute.Biological.value
IS_MECHANICAL = Attribute.Mechanical.value
IS_MASSIVE = Attribute.Massive.value
IS_PSIONIC = Attribute.Psionic.value
UNIT_BATTLECRUISER = UnitTypeId.BATTLECRUISER
UNIT_ORACLE = UnitTypeId.ORACLE
TARGET_GROUND: Set[int] = {TargetType.Ground.value, TargetType.Any.value}
TARGET_AIR: Set[int] = {TargetType.Air.value, TargetType.Any.value}
TARGET_BOTH = TARGET_GROUND | TARGET_AIR
IS_SNAPSHOT = DisplayType.Snapshot.value
IS_VISIBLE = DisplayType.Visible.value
IS_MINE = Alliance.Self.value
IS_ENEMY = Alliance.Enemy.value
IS_CLOAKED: Set[int] = {CloakState.Cloaked.value, CloakState.CloakedDetected.value, CloakState.CloakedAllied.value}
IS_REVEALED: Set[int] = CloakState.CloakedDetected.value
CAN_BE_ATTACKED: Set[int] = {CloakState.NotCloaked.value, CloakState.CloakedDetected.value}
IS_CARRYING_MINERALS: Set[BuffId] = {BuffId.CARRYMINERALFIELDMINERALS, BuffId.CARRYHIGHYIELDMINERALFIELDMINERALS}
IS_CARRYING_VESPENE: Set[BuffId] = {
    BuffId.CARRYHARVESTABLEVESPENEGEYSERGAS,
    BuffId.CARRYHARVESTABLEVESPENEGEYSERGASPROTOSS,
    BuffId.CARRYHARVESTABLEVESPENEGEYSERGASZERG,
}
IS_CARRYING_RESOURCES: Set[BuffId] = IS_CARRYING_MINERALS | IS_CARRYING_VESPENE
IS_ATTACKING = {
    AbilityId.ATTACK,
    AbilityId.ATTACK_ATTACK,
    AbilityId.ATTACK_ATTACKTOWARDS,
    AbilityId.ATTACK_ATTACKBARRAGE,
    AbilityId.SCAN_MOVE,
}
IS_PATROLLING = AbilityId.PATROL_PATROL
IS_GATHERING = AbilityId.HARVEST_GATHER
IS_RETURNING = AbilityId.HARVEST_RETURN
IS_COLLECTING = {IS_GATHERING, IS_RETURNING}
IS_CONSTRUCTING_SCV: Set[AbilityId] = {
    AbilityId.TERRANBUILD_ARMORY,
    AbilityId.TERRANBUILD_BARRACKS,
    AbilityId.TERRANBUILD_BUNKER,
    AbilityId.TERRANBUILD_COMMANDCENTER,
    AbilityId.TERRANBUILD_ENGINEERINGBAY,
    AbilityId.TERRANBUILD_FACTORY,
    AbilityId.TERRANBUILD_FUSIONCORE,
    AbilityId.TERRANBUILD_GHOSTACADEMY,
    AbilityId.TERRANBUILD_MISSILETURRET,
    AbilityId.TERRANBUILD_REFINERY,
    AbilityId.TERRANBUILD_SENSORTOWER,
    AbilityId.TERRANBUILD_STARPORT,
    AbilityId.TERRANBUILD_SUPPLYDEPOT,
}
IS_REPAIRING: Set[AbilityId] = {AbilityId.EFFECT_REPAIR, AbilityId.EFFECT_REPAIR_MULE, AbilityId.EFFECT_REPAIR_SCV}
IS_DETECTOR: Set[UnitTypeId] = {
    UnitTypeId.OBSERVER,
    UnitTypeId.OBSERVERSIEGEMODE,
    UnitTypeId.RAVEN,
    UnitTypeId.MISSILETURRET,
    UnitTypeId.OVERSEER,
    UnitTypeId.OVERSEERSIEGEMODE,
    UnitTypeId.SPORECRAWLER,
}
UNIT_PHOTONCANNON = UnitTypeId.PHOTONCANNON
UNIT_COLOSSUS = UnitTypeId.COLOSSUS
# Used in unit_command.py and action.py to combine only certain abilities
COMBINEABLE_ABILITIES = {
    AbilityId.MOVE,
    AbilityId.ATTACK,
    AbilityId.SCAN_MOVE,
    AbilityId.SMART,
    AbilityId.STOP,
    AbilityId.HOLDPOSITION,
    AbilityId.PATROL,
    AbilityId.HARVEST_GATHER,
    AbilityId.HARVEST_RETURN,
    AbilityId.EFFECT_REPAIR,
    AbilityId.RALLY_BUILDING,
    AbilityId.RALLY_UNITS,
    AbilityId.RALLY_WORKERS,
    AbilityId.RALLY_MORPHING_UNIT,
    AbilityId.LIFT,
    AbilityId.BURROWDOWN,
    AbilityId.BURROWUP,
    AbilityId.SIEGEMODE_SIEGEMODE,
    AbilityId.UNSIEGE_UNSIEGE,
    AbilityId.MORPH_LIBERATORAAMODE,
    AbilityId.EFFECT_STIM,
    AbilityId.MORPH_UPROOT,
    AbilityId.EFFECT_BLINK,
    AbilityId.MORPH_ARCHON,
}
FakeEffectRadii: Dict[int, float] = {
    UnitTypeId.KD8CHARGE.value: 2,
    UnitTypeId.PARASITICBOMBDUMMY.value: 3,
    UnitTypeId.FORCEFIELD.value: 1.5,
}
FakeEffectID: Dict[int, str] = {
    UnitTypeId.KD8CHARGE.value: "KD8CHARGE",
    UnitTypeId.PARASITICBOMBDUMMY.value: "PARASITICBOMB",
    UnitTypeId.FORCEFIELD.value: "FORCEFIELD",
}


def return_NOTAUNIT():
    # NOTAUNIT = 0
    return NOTAUNIT


TERRAN_TECH_REQUIREMENT: Dict[UnitTypeId, UnitTypeId] = defaultdict(
    return_NOTAUNIT,
    {
        MISSILETURRET: ENGINEERINGBAY,
        SENSORTOWER: ENGINEERINGBAY,
        PLANETARYFORTRESS: ENGINEERINGBAY,
        BARRACKS: SUPPLYDEPOT,
        ORBITALCOMMAND: BARRACKS,
        BUNKER: BARRACKS,
        GHOST: GHOSTACADEMY,
        GHOSTACADEMY: BARRACKS,
        FACTORY: BARRACKS,
        ARMORY: FACTORY,
        HELLIONTANK: ARMORY,
        THOR: ARMORY,
        STARPORT: FACTORY,
        FUSIONCORE: STARPORT,
        BATTLECRUISER: FUSIONCORE,
    },
)
PROTOSS_TECH_REQUIREMENT: Dict[UnitTypeId, UnitTypeId] = defaultdict(
    return_NOTAUNIT,
    {
        PHOTONCANNON: FORGE,
        CYBERNETICSCORE: GATEWAY,
        SENTRY: CYBERNETICSCORE,
        STALKER: CYBERNETICSCORE,
        ADEPT: CYBERNETICSCORE,
        TWILIGHTCOUNCIL: CYBERNETICSCORE,
        SHIELDBATTERY: CYBERNETICSCORE,
        TEMPLARARCHIVE: TWILIGHTCOUNCIL,
        DARKSHRINE: TWILIGHTCOUNCIL,
        HIGHTEMPLAR: TEMPLARARCHIVE,
        DARKTEMPLAR: DARKSHRINE,
        STARGATE: CYBERNETICSCORE,
        TEMPEST: FLEETBEACON,
        CARRIER: FLEETBEACON,
        MOTHERSHIP: FLEETBEACON,
        ROBOTICSFACILITY: CYBERNETICSCORE,
        ROBOTICSBAY: ROBOTICSFACILITY,
        COLOSSUS: ROBOTICSBAY,
        DISRUPTOR: ROBOTICSBAY,
    },
)
ZERG_TECH_REQUIREMENT: Dict[UnitTypeId, UnitTypeId] = defaultdict(
    return_NOTAUNIT,
    {
        ZERGLING: SPAWNINGPOOL,
        QUEEN: SPAWNINGPOOL,
        ROACHWARREN: SPAWNINGPOOL,
        BANELINGNEST: SPAWNINGPOOL,
        SPINECRAWLER: SPAWNINGPOOL,
        SPORECRAWLER: SPAWNINGPOOL,
        ROACH: ROACHWARREN,
        BANELING: BANELINGNEST,
        LAIR: SPAWNINGPOOL,
        OVERSEER: LAIR,
        OVERLORDTRANSPORT: LAIR,
        INFESTATIONPIT: LAIR,
        INFESTOR: INFESTATIONPIT,
        SWARMHOSTMP: INFESTATIONPIT,
        HYDRALISKDEN: LAIR,
        HYDRALISK: HYDRALISKDEN,
        LURKERDENMP: HYDRALISKDEN,
        LURKERMP: LURKERDENMP,
        SPIRE: LAIR,
        MUTALISK: SPIRE,
        CORRUPTOR: SPIRE,
        NYDUSNETWORK: LAIR,
        HIVE: INFESTATIONPIT,
        VIPER: HIVE,
        ULTRALISKCAVERN: HIVE,
        GREATERSPIRE: HIVE,
        BROODLORD: GREATERSPIRE,
    },
)

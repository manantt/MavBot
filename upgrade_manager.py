from sc2.units import Units
from sc2.constants import *

# TODO: tier 2 and 3
# TODO: shields
# TODO: observers speed

class UpgradeManager:
	def __init__(self, game):
		self.game = game

	def research_upgrades(self):
		if self.should_upgrade_w1:
			self.upgrade_w1()
		if self.should_upgrade_a1:
			self.upgrade_a1()

	@property
	def should_upgrade_w1(self):
		if self.game.units(VOIDRAY).amount < 5:
			return False
		return not self.game.already_pending_upgrade(UpgradeId.PROTOSSAIRWEAPONSLEVEL1) and self.game.structures(CYBERNETICSCORE).ready.idle.amount and self.game.can_afford(UpgradeId.PROTOSSAIRWEAPONSLEVEL1)
	@property
	def should_upgrade_a1(self):
		if self.game.units(VOIDRAY).amount < 5:
			return False
		if not self.game.already_pending_upgrade(UpgradeId.PROTOSSAIRWEAPONSLEVEL1):
			return False
		return not self.game.already_pending_upgrade(UpgradeId.PROTOSSAIRARMORSLEVEL1) and self.game.structures(CYBERNETICSCORE).ready.idle.amount and self.game.can_afford(UpgradeId.PROTOSSAIRARMORSLEVEL1)

	def upgrade_w1(self):
		self.game.combined_actions.append(self.game.structures(CYBERNETICSCORE).ready.idle.first.research(UpgradeId.PROTOSSAIRWEAPONSLEVEL1))

	def upgrade_a1(self):
		self.game.combined_actions.append(self.game.structures(CYBERNETICSCORE).ready.idle.first.research(UpgradeId.PROTOSSAIRARMORSLEVEL1))
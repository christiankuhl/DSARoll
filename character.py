import json
from math import floor, ceil
from rule_constants import IMPAIRMENTS, SPECIES, SPELLS, trial_info, effect_info
from results import Success, Failure, AttackSuccess, AttackFailure, TP, W20

def round(n):
    if n - floor(n) < .5:
        return floor(n)
    else:
        return ceil(n)

class Character:
    def __init__(self, filename):
        with open(filename, "r") as file_handle:
            raw_data = json.load(file_handle)
        self.spells = {}
        self.long_range_weapons = {}
        self.melee_weapons = {}
        self.maneuvers = []
        for key, property in raw_data.items():
            setattr(self, key, property)
        self.maxLE = (SPECIES[self.species]["LE_GW"] + raw_data.get("LE_BONUS", 0)
                       + 2 * self.KO)
        self.ZK = (SPECIES[self.species]["ZK_GW"] + raw_data.get("ZK_BONUS", 0)
                   + round((2 * self.KO + self.KK) / 6))
        self.SK = (SPECIES[self.species]["SK_GW"] + raw_data.get("SK_BONUS", 0)
                    + round((self.MU + self.KL + self.IN) / 6))
        self.AW = raw_data.get("AW_BONUS", 0) + round(self.GE / 2)
        self._LE = self.maxLE
        self.impairments = {imp: 0 for imp in IMPAIRMENTS}
        self.pain_from_le = 0
        self.add_pain = 0
    @property
    def LE(self):
        return self._LE
    @LE.setter
    def LE(self, value):
        self._LE = value
        if value <= 5:
            self.pain_from_le = 4
        elif value <= .25 * self.maxLE:
            self.pain_from_le = 3
        elif value <= .5 * self.maxLE:
            self.pain_from_le = 2
        elif value <= .75 * self.maxLE:
            self.pain_from_le = 1
        else:
            self.pain_from_le = 0
    def FW(self, trial):
        fw = self.talents.get(trial, None)
        if fw is not None:
            return fw, 0
        fw = self.spells[trial]
        _, _, modifier = trial_info(trial)
        modifier_value = getattr(self, modifier, 0)
        return fw, modifier_value
    def do_trial(self, trial, bonus_or_malus=0):
        critical_hit = 0
        critical_miss = 0
        dice_rolls, _, _ = trial_info(trial)
        fp, modifier = self.FW(trial)
        for idx, base_property in enumerate(dice_rolls):
            die = W20()
            base_value = getattr(self, base_property)
            if die == 1:
                critical_hit += 1
            elif die == 20:
                critical_miss += 1
            dice_rolls[idx] = (base_property, die)
            fp += min(base_value + bonus_or_malus - die - modifier
                          - sum(self.impairments.values()), 0)
        if (fp >= 0 or critical_hit >= 2) and critical_miss < 2:
            if fp > 15:
                quality = 6
            elif fp > 12:
                quality = 5
            elif fp > 9:
                quality = 4
            elif fp > 6:
                quality = 3
            elif fp > 3:
                quality = 2
            else:
                quality = 1
            return Success(character=self,
                           trial=trial,
                           critical=critical_hit,
                           quality=quality,
                           dice_rolls=dice_rolls,
                           bonus_or_malus=bonus_or_malus)
        else:
            return Failure(character=self,
                           trial=trial,
                           critical=critical_miss,
                           dice_rolls=dice_rolls,
                           bonus_or_malus=bonus_or_malus)
    def attack(self, weapon_name, effects, lrw=False, parry=False, bonus_or_malus=0):
        if lrw:
            weapon = self.long_range_weapons[weapon_name]
            operation = "FK"
        elif parry:
            weapon = self.melee_weapons[weapon_name]
            operation = "PA"
        else:
            weapon = self.melee_weapons[weapon_name]
            operation = "AT"
        weapon = (weapon_name, weapon)
        effects = effect_info(effects, operation)
        effects["Bonus/Malus"] = (bonus_or_malus, 0)
        return self.attack_roll(weapon, operation, effects)
    def attack_roll(self, weapon, operation, effects):
        target_value = weapon[1][operation]
        attack_modifier = 0
        tp_modifier = 0
        critical = False
        possible_tp = None
        dice_rolls = []
        attack_effect = sum(a for (a, _) in effects.values())
        impairment_effect = sum(self.impairments.values())
        die = W20()
        retry = W20()
        dice_rolls.append(die)
        successful = lambda d: (d <= target_value + attack_effect
                                - impairment_effect)
        success = successful(die)
        if die == 1 and success and successful(retry):
            critical = True
            dice_rolls.append(retry)
        if die == 20 and not successful(retry):
            critical = True
            success = False
            dice_rolls.append(retry)
        if success:
            if operation not in ["AW", "PA"]:
                possible_tp = TP(weapon, effects)
            return AttackSuccess(character=self,
                                 weapon=weapon,
                                 operation=operation,
                                 critical=critical,
                                 dice_rolls=dice_rolls,
                                 effects=effects,
                                 possible_tp=possible_tp)
        else:
            return AttackFailure(character=self,
                                 weapon=weapon,
                                 operation=operation,
                                 critical=critical,
                                 dice_rolls=dice_rolls,
                                 effects=effects,
                                 possible_tp=None)
    def dodge(self, bonus_or_malus):
        effects = effect_info(self.maneuvers, "AW")
        effects["Bonus/Malus"] = (bonus_or_malus, 0)
        return self.attack_roll(weapon=(None, {"AW": self.AW}),
                                operation="AW",
                                effects=effects)

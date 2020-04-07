import json
import random
from rule_constants import TRIALS, IMPAIRMENTS, SPECIES, SPELLS, trial_info, \
                           ATTACK_EFFECTS
from math import floor, ceil

OP_TEXTS = {"AT": "Attacke", "PA": "Parade", "FK": "Schuss", "AW": "Ausweichen"}

def W20():
    return random.randint(1, 20)

def W6():
    return random.randint(1, 6)

def round(n):
    if n - floor(n) < .5:
        return floor(n)
    else:
        return ceil(n)

def TP(weapon, effects):
    pass

class Character:
    def __init__(self, filename):
        with open(filename, "r") as file_handle:
            raw_data = json.load(file_handle)
        self.spells = {}
        self.long_range_weapons = {}
        self.melee_weapons = {}
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
    def attack(self, weapon_name, effects, lrw=False, parry=False):
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
        effects = {effect: ATTACK_EFFECTS[effect] for effect in effects}
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
        return self.attack_roll(weapon=(None, {"AW": self.AW}),
                                operation="AW",
                                effects={"Bonus/Malus:": (bonus_or_malus, 0)})

class ResultMeta(type):
    def __repr__(cls):
        return cls.title

class Result(metaclass=ResultMeta):
    def __init__(self, character, trial, critical, dice_rolls, bonus_or_malus,
                 quality=None):
        self.character = character
        self.trial = trial
        self.critical = (critical >= 2)
        self.terrible = (critical == 3)
        self.dice_rolls = dice_rolls
        self.quality = quality
        self.bonus_or_malus = bonus_or_malus
        _, self.kind, self.modifier = trial_info(trial)
    def __repr__(self):
        if not self.terrible:
            res = (f"{self.character.name}s {self.kind} {self.trial} ist ein "
                     f"{'kritischer ' if self.critical else ''}{self.title}\n\n")
        else:
            res = (f"{self.character.name}s {self.kind} {self.trial} endet in einem"
                    f"schrecklichen Missgeschick!\n\n")
        return res
    def dice_str(self):
        res = (4 * " ").join(f"{pr}: {roll} / {getattr(self.character, pr)}"
                              for (pr, roll) in self.dice_rolls) + "\n"
        fw, modifier_value = self.character.FW(self.trial)
        if fw:
            res += f"\nBonus aus FW: {fw}"
        if modifier_value:
            res += f"\nMalus aus {self.modifier}: {-modifier_value}"
        if self.bonus_or_malus:
            res += f"\nBonus/Malus: {self.bonus_or_malus}"
        impairments = -sum(self.character.impairments.values())
        if impairments:
            res += f"\nMalus aus Effekten: {impairments}"
        return res

class Success(Result):
    title = "Erfolg!"
    def __repr__(self):
        return super().__repr__() + f"Qualitätsstufe {self.quality}\n\n" + self.dice_str()

class Failure(Result):
    title = "Fehlschlag!"
    def __repr__(self):
        return super().__repr__() + self.dice_str()

class AttackResult(metaclass=ResultMeta):
    def __init__(self, character, weapon, operation, critical, dice_rolls,
                 effects, possible_tp):
        self.character = character
        self.weapon = weapon[0]
        self.operation = operation
        self.critical = critical
        self.dice_rolls = dice_rolls
        self.effects = effects
        self.kind = OP_TEXTS[operation]
    def __repr__(self):
        wpn = f" ({self.weapon})" if self.weapon else ""
        return (f"{self.character.name}s {self.kind}{wpn} ist ein "
                 f"{'kritischer ' if self.critical else ''}{self.title}\n\n")

class AttackSuccess(AttackResult):
    title = "Erfolg!"

class AttackFailure(AttackResult):
    title = "Fehlschlag!"

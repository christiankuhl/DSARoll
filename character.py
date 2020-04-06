import json
import random
from constants import TRIALS, IMPAIRMENTS, SPECIES, SPELLS, trial_info
from math import floor, ceil

def W20():
    return random.randint(1, 20)

def W6():
    return random.randint(1, 6)

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
        res = (f"{self.character.name}s {self.kind} {self.trial} ist ein "
                 f"{'kritischer ' if self.critical else ''}Erfolg!\n\n"
                 f"Qualitätsstufe {self.quality}\n\n")
        res += self.dice_str()
        return res

class Failure(Result):
    title = "Fehlschlag!"
    def __repr__(self):
        if not self.terrible:
            res = (f"{self.character.name}s {self.kind} {self.trial} ist ein "
                    f"{'kritischer ' if self.critical else ''}Fehlschlag!\n\n")
        else:
            res = (f"{self.character.name}s {self.kind} {self.trial} endet in einem"
                    f"schrecklichen Missgeschick!\n\n")
        res += self.dice_str()
        return res

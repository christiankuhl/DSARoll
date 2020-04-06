import json
import random
from constants import TRIALS, IMPAIRMENTS, SPECIES

def W20():
    return random.randint(1, 20)

def W6():
    return random.randint(1, 6)

class Character:
    def __init__(self, filename):
        with open(filename, "r") as file_handle:
            raw_data = json.load(file_handle)
        for key, property in raw_data.items():
            setattr(self, key, property)
        self.maxLE = (SPECIES[self.species]["LE_GW"] + 2 * self.KO
                      + raw_data.get("LE_BONUS", 0))
        self._LE = self.maxLE
        self.impairments = {imp: 0 for imp in IMPAIRMENTS}
        self.pain_from_le = 0
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
    def do_trial(self, trial, bonus_or_malus=0):
        critical_hit = 0
        critical_miss = 0
        dice_rolls = []
        trials = TRIALS[trial]
        talent = self.talents[trial]
        for base_property in trials:
            die = W20()
            base_value = getattr(self, base_property)
            if die == 1:
                critical_hit += 1
            elif die == 20:
                critical_miss += 1
            dice_rolls.append((base_property, die))
            talent += min(base_value + bonus_or_malus - die
                          - sum(self.impairments.values()), 0)
        if talent >= 0 or critical_hit >= 2:
            if talent > 15:
                quality = 6
            elif talent > 12:
                quality = 5
            elif talent > 9:
                quality = 4
            elif talent > 6:
                quality = 3
            elif talent > 3:
                quality = 2
            else:
                quality = 1
            return Success(character=self,
                           trial=trial,
                           critical=(critical_hit>=2),
                           quality=quality,
                           dice_rolls=dice_rolls,
                           bonus_or_malus=bonus_or_malus)
        else:
            return Failure(character=self,
                           trial=trial,
                           critical=(critical_miss>=2),
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
        self.critical = critical
        self.dice_rolls = dice_rolls
        self.quality = quality
        self.bonus_or_malus = bonus_or_malus
    def dice_str(self):
        res = (4 * " ").join(f"{pr}: {roll} / {getattr(self.character, pr)}"
                              for (pr, roll) in self.dice_rolls) + "\n"
        talent = self.character.talents[self.trial]
        if talent:
            res += f"\nBonus aus Talent: {talent}"
        if self.bonus_or_malus:
            res += f"\nBonus/Malus: {self.bonus_or_malus}"
        impairments = -sum(self.character.impairments.values())
        if impairments:
            res += f"\nMalus aus Effekten: {impairments}"
        return res

class Success(Result):
    title = "Erfolg!"
    def __repr__(self):
        res = (f"{self.character.name} erzielt bei der Probe auf {self.trial} "
                 f"einen {'kritischen ' if self.critical else ''}Erfolg!\n\n"
                 f"Qualitätsstufe {self.quality}\n\n")
        res += self.dice_str()
        return res

class Failure(Result):
    title = "Fehlschlag!"
    def __repr__(self):
        res = (f"{self.character.name} erleidet bei der Probe auf {self.trial} "
                f"einen {'kritischen ' if self.critical else ''}Fehlschlag!\n\n")
        res += self.dice_str()
        return res

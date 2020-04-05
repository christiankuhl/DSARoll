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
        self._LE = SPECIES[self.species]["LE_GW"] + 2 * self.KO + raw_data.get("LE_BONUS", 0)
        self.impairments = {imp: 0 for imp in IMPAIRMENTS}
    def do_trial(self, trial):
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
            talent += min(base_value - die - sum(self.impairments.values()), 0)
        if talent >= 0:
            if talent > 9:
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
                           dice_rolls=dice_rolls)
        else:
            return Failure(character=self,
                           trial=trial,
                           critical=(critical_miss>=2),
                           dice_rolls=dice_rolls)

class ResultMeta(type):
    def __repr__(cls):
        return cls.title

class Result(metaclass=ResultMeta):
    def __init__(self, character, trial, critical, dice_rolls, quality=None):
        self.character = character
        self.trial = trial
        self.critical = critical
        self.dice_rolls = dice_rolls
        self.quality = quality

class Success(Result):
    title = "Erfolg!"
    def __repr__(self):
        return (f"{self.character.name} erzielt bei der Probe auf '{self.trial}' "
                 f"einen {'kritischen ' if self.critical else ''}Erfolg!")

class Failure(Result):
    title = "Fehlschlag!"
    def __repr__(self):
        return (f"{self.character.name} erleidet bei der Probe auf '{self.trial}' "
                f"einen {'kritischen ' if self.critical else ''}Fehlschlag!")

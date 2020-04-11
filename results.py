import random
from rule_constants import trial_info

OP_TEXTS = {"AT": "Attacke", "PA": "Parade", "FK": "Schuss", "AW": "Ausweichen"}

def W6():
    return random.randint(1, 6)

def W20():
    return random.randint(1, 20)

class TP:
    def __init__(self, weapon, effects):
        self.dice_rolls = []
        self.dice, self.bonus = weapon[1]["TP"]
        for _ in range(self.dice):
            self.dice_rolls.append(W6())
        self.result = sum(self.dice_rolls) + self.bonus + sum(b for (_, b) in effects.values())
        self.effects = effects
    def __repr__(self):
        dice_str = f" ({self.dice}W6+{self.bonus})" if not self.effects else ""
        res = f"\n\nMögliche TP: {self.result}{dice_str}"
        if self.effects:
               res += f"\n{self.dice}W6+{self.bonus}: {sum(self.dice_rolls) + self.bonus}"
        for effect, (_, value) in self.effects.items():
            res += f"\n{effect}: {value}"
        return res + "\n"

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
        for impairment, impact in self.character.impairments.items():
            if impact:
                res += f"\n{impairment}: {-impact}"
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
        self.weapon = weapon
        self.operation = operation
        self.critical = critical
        self.dice_rolls = dice_rolls
        self.effects = effects
        self.kind = OP_TEXTS[operation]
        self.possible_tp = possible_tp
    def dice_str(self):
        res = f"\n\n{self.operation}: {self.dice_rolls[0]} / {self.weapon[1][self.operation]}"
        if len(self.dice_rolls) > 1:
            res += f" (Bestätigungswurf: {self.dice_rolls[1]})"
        return res + "\n"
    def __repr__(self):
        wpn = f" ({self.weapon[0]})" if self.weapon[0] else ""
        res = (f"{self.character.name}s {self.kind}{wpn} ist ein "
                 f"{'kritischer ' if self.critical else ''}{self.title}")
        res += self.dice_str()
        for effect, impact in self.effects.items():
            if impact[0]:
                res += f"\n{effect}: {impact[0]}"
        for impairment, impact in self.character.impairments.items():
            if impact:
                res += f"\n{impairment}: {-impact}"
        if self.possible_tp:
            res += str(self.possible_tp)
        return res

class AttackSuccess(AttackResult):
    title = "Erfolg!"

class AttackFailure(AttackResult):
    title = "Fehlschlag!"

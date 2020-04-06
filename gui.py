from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QComboBox,\
                            QMessageBox, QHBoxLayout, QLabel, QGroupBox, QSpinBox
import os
from character import Character
from constants import TRIALS

class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.characters = {}
        for subdir, dirs, files in os.walk("characters"):
            for file in files:
                if file[-5:] == ".json":
                    character = Character(f"characters/{file}")
                    self.characters[character.name] = character
        self._init_gui()
    def _init_gui(self):
        self.setWindowTitle("DSARoll")
        layout = QGridLayout()
        layout.addLayout(self.character_choice(), 0, 0)
        layout.addWidget(self.impairment_block(), 1, 0, 4, 2)
        layout.addWidget(self.trial_choice(), 7, 0)
        self.magic_block = self.spell_choice()
        layout.addWidget(self.magic_block, 8, 0)
        self.setLayout(layout)
        self.toggle_magic()
        self.reset_spinners()
        self.show()
    @property
    def character(self):
        return self.characters[self.character_choice.currentText()]
    def roll(self, trial, bonus_or_malus):
        result = self.character.do_trial(trial, bonus_or_malus)
        msg = QMessageBox.information(self, str(type(result)), str(result), QMessageBox.Ok)
    def set_impairment(self, condition, value):
        self.character.impairments[condition] = value
    def change_le(self, value):
        self.character.LE = value
        self.impairments["Schmerz"].setMinimum(self.character.pain_from_le)
    def change_character(self):
        self.toggle_magic()
        self.reset_spinners()
    def toggle_magic(self):
        if self.character.spells:
            self.spell_choice.clear()
            self.spell_choice.insertItems(0, self.character.spells.keys())
            self.magic_block.setVisible(True)
        else:
            self.magic_block.setVisible(False)
            self.adjustSize()
    def reset_spinners(self):
        self.le_spinner.setMaximum(self.character.maxLE)
        self.le_spinner.setValue(self.character.LE)
        for (condition, value) in self.character.impairments.items():
            self.impairments[condition].setValue(value)
        self.impairments["Schmerz"].setMinimum(self.character.pain_from_le)
    def character_choice(self):
        char_choice = QGridLayout()
        label = QLabel()
        label.setText("Charakter:")
        self.character_choice = QComboBox()
        self.character_choice.insertItems(0, self.characters.keys())
        self.character_choice.currentTextChanged.connect(self.change_character)
        char_choice.addWidget(label, 0, 0)
        char_choice.addWidget(self.character_choice, 0, 1)
        self.le_spinner = QSpinBox()
        self.le_spinner.setMinimum(0)
        self.le_spinner.valueChanged.connect(self.change_le)
        label = QLabel()
        label.setText("Lebensenergie:")
        char_choice.addWidget(label, 0, 2)
        char_choice.addWidget(self.le_spinner, 0, 3)
        return char_choice
    def trial_choice(self):
        trial_frame = QGroupBox()
        trial_frame.setTitle("Proben")
        trial_grid = QGridLayout()
        self.trial_choice = QComboBox()
        self.trial_choice.insertItems(0, TRIALS.keys())
        trial_grid.addWidget(self.trial_choice, 0, 0)
        self.bonus_or_malus = QSpinBox()
        self.bonus_or_malus.setMinimum(-20)
        label = QLabel()
        label.setText("Bonus/Malus:")
        trial_grid.addWidget(label, 0, 1)
        trial_grid.addWidget(self.bonus_or_malus, 0, 2)
        roll = QPushButton('Würfeln')
        roll.clicked.connect(lambda: self.roll(self.trial_choice.currentText(),
                                               self.bonus_or_malus.value()))
        trial_grid.addWidget(roll, 0, 3)
        trial_frame.setLayout(trial_grid)
        return trial_frame
    def impairment_block(self):
        self.impairments = {}
        impairment_frame = QGroupBox()
        impairment_frame.setTitle("Effekte")
        grid = QGridLayout()
        conditions = []
        for row, (condition, value) in enumerate(self.character.impairments.items()):
            label = QLabel()
            label.setText(condition + ":")
            conditions.append(condition)
            self.impairments[condition] = QSpinBox()
            self.impairments[condition].setMaximum(4)
            self.impairments[condition].valueChanged.connect(
                lambda v, condition=condition: self.set_impairment(condition, v))
            grid.addWidget(label, row % 4, 2 * (row // 4))
            grid.addWidget(self.impairments[condition], row % 4, 2 * (row // 4) + 1)
        impairment_frame.setLayout(grid)
        return impairment_frame
    def spell_choice(self):
        spell_frame = QGroupBox()
        spell_frame.setTitle("Zaubersprüche")
        spell_grid = QGridLayout()
        self.spell_choice = QComboBox()
        spell_grid.addWidget(self.spell_choice, 0, 0)
        self.magic_bonus_or_malus = QSpinBox()
        self.magic_bonus_or_malus.setMinimum(-20)
        label = QLabel()
        label.setText("Bonus/Malus:")
        spell_grid.addWidget(label, 0, 1)
        spell_grid.addWidget(self.magic_bonus_or_malus, 0, 2)
        roll = QPushButton('Würfeln')
        roll.clicked.connect(lambda: self.roll(self.spell_choice.currentText(),
                                               self.magic_bonus_or_malus.value()))
        spell_grid.addWidget(roll, 0, 3)
        spell_frame.setLayout(spell_grid)
        return spell_frame

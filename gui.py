from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QComboBox,\
                            QMessageBox, QHBoxLayout, QLabel, QGroupBox, QSpinBox, \
                            QButtonGroup, QRadioButton
import os
from character import Character
from rule_constants import TRIALS, ATTACK_EFFECTS

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
        layout.addLayout(self._character_block(), 0, 0)
        layout.addWidget(self._impairment_block(), 1, 0, 4, 2)
        layout.addWidget(self._trial_block(), 7, 0)
        self.magic_block = self._spell_block()
        layout.addWidget(self.magic_block, 8, 0)
        self.weapons_block = self._weapons_block()
        layout.addLayout(self.weapons_block, 9, 0)
        self.setLayout(layout)
        self.toggle_magic()
        self.toggle_weapons()
        self.reset_spinners()
        self.show()
        self.adjustSize()
    @property
    def character(self):
        return self.characters[self.character_choice.currentText()]
    def roll(self, trial, bonus_or_malus):
        result = self.character.do_trial(trial, bonus_or_malus)
        QMessageBox.information(self, str(type(result)), str(result), QMessageBox.Ok)
    def attack(self, lrw, parry=False):
        bonus_or_malus = 0
        effects = []
        if lrw:
            weapon = self.lrw_choice.currentText()
            effects.append(self.lrw_range)
        else:
            weapon = self.mw_choice.currentText()
            if parry:
                bonus_or_malus = self.dodge_bonus_or_malus.value()
            else:
                effects.append(self.maneuver)
        result = self.character.attack(weapon, effects, lrw, parry, bonus_or_malus)
        QMessageBox.information(self, str(type(result)), str(result), QMessageBox.Ok)
    def dodge(self):
        result = self.character.dodge(self.dodge_bonus_or_malus.value())
        QMessageBox.information(self, str(type(result)), str(result), QMessageBox.Ok)
    def set_impairment(self, condition, value):
        self.character.impairments[condition] = value
    def change_le(self, value):
        self.character.LE = value
        self.impairments["Schmerz"].setMinimum(self.character.pain_from_le)
    def change_character(self):
        self.toggle_magic()
        self.toggle_weapons()
        self.reset_spinners()
    def toggle_magic(self):
        self.magic_block.setVisible(False)
        if self.character.spells:
            self.spell_choice.clear()
            self.spell_choice.insertItems(0, self.character.spells.keys())
            self.magic_block.setVisible(True)
        self.adjustSize()
    def toggle_weapons(self):
        self.mw_block.setVisible(False)
        self.lrw_block.setVisible(False)
        if self.character.melee_weapons:
            self.mw_choice.clear()
            self.mw_choice.insertItems(0, self.character.melee_weapons.keys())
            self.mw_block.setVisible(True)
            self.toggle_maneuvers()
        if self.character.long_range_weapons:
            self.lrw_choice.clear()
            self.lrw_choice.insertItems(0, self.character.long_range_weapons.keys())
            self.lrw_block.setVisible(True)
        self.adjustSize()
    def toggle_maneuvers(self):
        available = 0
        for btn in self.maneuver_grp.buttons()[1:]:
            if btn.text() not in self.character.maneuvers:
                btn.setVisible(False)
            else:
                btn.setVisible(True)
                available += 1
        no_selection = self.maneuver_grp.buttons()[0]
        no_selection.toggle()
        if available:
            no_selection.setVisible(True)
        else:
            no_selection.setVisible(False)
    def reset_spinners(self):
        self.le_spinner.setMaximum(self.character.maxLE)
        self.le_spinner.setValue(self.character.LE)
        for (condition, value) in self.character.impairments.items():
            self.impairments[condition].setValue(value)
        self.impairments["Schmerz"].setMinimum(self.character.pain_from_le)
    @property
    def lrw_range(self):
        for btn in self.range_grp.buttons():
            if btn.isChecked():
                return btn.text()
    @property
    def maneuver(self):
        for btn in self.maneuver_grp.buttons()[1:]:
            if btn.isChecked():
                return btn.text()
    def _character_block(self):
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
    def _trial_block(self):
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
        roll = QPushButton('Antreten')
        roll.clicked.connect(lambda: self.roll(self.trial_choice.currentText(),
                                               self.bonus_or_malus.value()))
        trial_grid.addWidget(roll, 0, 3)
        trial_frame.setLayout(trial_grid)
        return trial_frame
    def _impairment_block(self):
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
    def _spell_block(self):
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
        roll = QPushButton('Zaubern')
        roll.clicked.connect(lambda: self.roll(self.spell_choice.currentText(),
                                               self.magic_bonus_or_malus.value()))
        spell_grid.addWidget(roll, 0, 3)
        spell_frame.setLayout(spell_grid)
        return spell_frame
    def _weapons_block(self):
        weapon_grid = QGridLayout()
        self.mw_block = QGroupBox()
        self.lrw_block = QGroupBox()
        self.mw_block.setTitle("Nahkampfwaffen")
        self.lrw_block.setTitle("Fernkampfwaffen")
        mw_grid = self._mw_grid()
        lrw_grid = self._lrw_grid()
        self.mw_block.setLayout(mw_grid)
        self.lrw_block.setLayout(lrw_grid)
        weapon_grid.addWidget(self.lrw_block, 0, 0, 1, 3)
        weapon_grid.addWidget(self.mw_block, 1, 0, 1, 3)
        self.dodge_bonus_or_malus = QSpinBox()
        self.dodge_bonus_or_malus.setMinimum(-20)
        label = QLabel()
        label.setText("Bonus/Malus:")
        weapon_grid.addWidget(label, 2, 0)
        weapon_grid.addWidget(self.dodge_bonus_or_malus, 2, 1)
        dodge = QPushButton("Ausweichen")
        dodge.clicked.connect(self.dodge)
        weapon_grid.addWidget(dodge, 2, 2)
        return weapon_grid
    def _lrw_grid(self):
        lrw_grid = QGridLayout()
        self.lrw_choice = QComboBox()
        self.range_grp = QButtonGroup()
        near = QRadioButton()
        middle = QRadioButton()
        far = QRadioButton()
        near.setText("Nah")
        middle.setText("Mittel")
        far.setText("Weit")
        self.range_grp.addButton(near)
        self.range_grp.addButton(middle)
        self.range_grp.addButton(far)
        lrw_grid.addWidget(near, 0, 2)
        lrw_grid.addWidget(middle, 0, 3)
        lrw_grid.addWidget(far, 0, 4)
        lrw_grid.addWidget(self.lrw_choice, 0, 0, 1, 2)
        middle.toggle()
        shoot = QPushButton("Schießen")
        shoot.clicked.connect(lambda: self.attack(lrw=True))
        lrw_grid.addWidget(shoot, 0, 5)
        return lrw_grid
    def _mw_grid(self):
        mw_grid = QGridLayout()
        self.maneuver_grp = QButtonGroup()
        self.mw_choice = QComboBox()
        attack = QPushButton("Angriff")
        parry = QPushButton("Parieren")
        attack.clicked.connect(lambda: self.attack(lrw=False))
        parry.clicked.connect(lambda: self.attack(lrw=False, parry=True))
        mw_grid.addWidget(self.mw_choice, 0, 0)
        mw_grid.addWidget(attack, 0, 5)
        mw_grid.addWidget(parry, 1, 5)
        maneuvers = ["kein Manöver"] + list(ATTACK_EFFECTS["AT"].keys())
        maneuver_grid = QGridLayout()
        mw_grid.addLayout(maneuver_grid, 1, 0)
        for row, maneuver in enumerate(maneuvers):
            label = QLabel()
            label.setText(maneuver)
            radiobutton = QRadioButton()
            radiobutton.setText(maneuver)
            maneuver_grid.addWidget(radiobutton, row, 0)
            self.maneuver_grp.addButton(radiobutton)
        self.maneuver_grp.buttons()[0].toggle()
        return mw_grid

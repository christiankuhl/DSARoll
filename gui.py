from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QComboBox,\
                            QMessageBox
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
        layout = QVBoxLayout()
        self.character_choice = QComboBox()
        self.character_choice.insertItems(0, self.characters.keys())
        self.trial_choice = QComboBox()
        self.trial_choice.insertItems(0, TRIALS.keys())
        layout.addWidget(self.character_choice)
        layout.addWidget(self.trial_choice)
        roll = QPushButton('Würfeln')
        roll.clicked.connect(self.roll)
        layout.addWidget(roll)
        self.setLayout(layout)
        self.show()
    @property
    def character(self):
        return self.characters[self.character_choice.currentText()]
    @property
    def trial(self):
        return self.trial_choice.currentText()
    def roll(self):
        result = self.character.do_trial(self.trial)
        msg = QMessageBox.information(self, str(type(result)), str(result), QMessageBox.Ok)

#! /usr/bin/env python3

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from gui import GUI
    app = QApplication([])
    gui = GUI()
    app.exec_()

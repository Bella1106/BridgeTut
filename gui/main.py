"""
BridgeTut application entry point.

Starts the PySide6 desktop application.
"""

import sys  

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("BridgeTut")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
import sys
from PyQt5.QtWidgets import QApplication
from gui import HomeDent

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = HomeDent()
    window.show()

    sys.exit(app.exec())

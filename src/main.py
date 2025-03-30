import sys
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import AirGestureApp

def main():
    app = QApplication(sys.argv)
    window = AirGestureApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 
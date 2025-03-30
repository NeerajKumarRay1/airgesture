import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from src.airgesture.ui.main_window import AirGestureApp

def main():
    app = QApplication(sys.argv)
    window = AirGestureApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 
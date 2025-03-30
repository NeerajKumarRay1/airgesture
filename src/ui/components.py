from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtCore import Qt

class StatusLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                color: white;
                padding: 5px;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        self.setAlignment(Qt.AlignCenter)

class ControlButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2472a4;
            }
        """) 
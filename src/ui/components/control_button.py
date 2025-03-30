from PyQt5.QtWidgets import QPushButton

class ControlButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #2196f3, stop:1 #1976d2);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
                margin: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #1976d2, stop:1 #1565c0);
                border: 2px solid #64b5f6;
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #1565c0, stop:1 #0d47a1);
                transform: translateY(1px);
            }
        """) 
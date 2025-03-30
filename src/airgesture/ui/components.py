from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtCore import Qt

class StatusLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #1a237e, stop:1 #0d47a1);
                color: #ffffff;
                padding: 12px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #2196f3;
                margin: 5px;
            }
            QLabel:hover {
                border: 2px solid #64b5f6;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #0d47a1, stop:1 #1a237e);
            }
        """)
        self.setAlignment(Qt.AlignCenter)

class ControlButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.update_colors({
            'normal': ('#2196f3', '#1976d2'),
            'hover': ('#1976d2', '#1565c0'),
            'pressed': ('#1565c0', '#0d47a1')
        })
        
    def update_colors(self, colors):
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 {colors['normal'][0]}, 
                                          stop:1 {colors['normal'][1]});
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
                margin: 5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 {colors['hover'][0]}, 
                                          stop:1 {colors['hover'][1]});
                border: 2px solid #64b5f6;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 {colors['pressed'][0]}, 
                                          stop:1 {colors['pressed'][1]});
            }}
        """) 
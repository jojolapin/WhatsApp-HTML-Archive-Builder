"""PySide6 stylesheets: water-inspired light and dark themes."""

# Teal accent for primary actions; Stop button stays red (set inline in main_window).
# Light: soft blue-grey background, white panels, teal borders and accent.
# Dark: deep slate background, teal-tinted panels, cyan accent.

DARK_STYLE = """
    QWidget {
        background-color: #0f1729;
        color: #e2e8f0;
        font-size: 11pt;
    }
    QGroupBox {
        background-color: #1e3a4f;
        border: 1px solid #2d5a6b;
        border-radius: 12px;
        margin-top: 1.2ex;
        padding: 12px 12px 8px 12px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        left: 12px;
        color: #94a3b8;
    }
    QLineEdit {
        background-color: #1e293b;
        border: 1px solid #2d5a6b;
        border-radius: 10px;
        padding: 8px 10px;
        color: #e2e8f0;
    }
    QLineEdit:focus {
        border-color: #2dd4bf;
    }
    QCheckBox {
        padding: 8px;
    }
    QCheckBox::indicator {
        border: 2px solid #475569;
        background-color: #1e293b;
        border-radius: 4px;
        width: 16px;
        height: 16px;
    }
    QCheckBox::indicator:checked {
        background-color: #2dd4bf;
        border-color: #2dd4bf;
    }
    QPushButton {
        background-color: #1e3a4f;
        border: 1px solid #2d5a6b;
        border-radius: 10px;
        padding: 8px 14px;
        color: #e2e8f0;
    }
    QPushButton:hover {
        background-color: #234a62;
        border-color: #2dd4bf;
    }
    QPushButton:pressed {
        background-color: #16324a;
    }
    QPushButton:disabled {
        background-color: #1e293b;
        color: #64748b;
    }
    QPushButton#primaryButton {
        background-color: #14b8a6;
        border-color: #2dd4bf;
        color: #0f1729;
        font-weight: bold;
    }
    QPushButton#primaryButton:hover {
        background-color: #2dd4bf;
    }
    QPushButton#primaryButton:pressed {
        background-color: #0d9488;
    }
    QProgressBar {
        border: 1px solid #2d5a6b;
        border-radius: 10px;
        text-align: center;
        background-color: #1e293b;
    }
    QProgressBar::chunk {
        background-color: #2dd4bf;
        border-radius: 8px;
    }
    QComboBox {
        background-color: #1e293b;
        border: 1px solid #2d5a6b;
        border-radius: 10px;
        padding: 8px 10px;
        color: #e2e8f0;
    }
    QComboBox:hover {
        border-color: #2dd4bf;
    }
    QTabWidget::pane {
        border: 1px solid #2d5a6b;
        border-radius: 12px;
        background-color: #1e293b;
        margin-top: -1px;
    }
    QTabBar::tab {
        background-color: #1e3a4f;
        border: 1px solid #2d5a6b;
        padding: 8px 16px;
        margin-right: 4px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
    }
    QTabBar::tab:selected {
        background-color: #1e293b;
        border-bottom-color: #1e293b;
    }
    QMenuBar {
        background-color: #0f1729;
        color: #e2e8f0;
    }
    QMenuBar::item:selected {
        background-color: #1e3a4f;
    }
    QTextEdit {
        background-color: #1e293b;
        border: 1px solid #2d5a6b;
        border-radius: 10px;
        padding: 8px;
        color: #e2e8f0;
    }
"""

LIGHT_STYLE = """
    QWidget {
        background-color: #e8f4f8;
        color: #1a3a4a;
        font-size: 11pt;
    }
    QGroupBox {
        background-color: #ffffff;
        border: 1px solid #a8d4e6;
        border-radius: 12px;
        margin-top: 1.2ex;
        padding: 12px 12px 8px 12px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        left: 12px;
        color: #0d9488;
    }
    QLineEdit {
        background-color: #ffffff;
        border: 1px solid #a8d4e6;
        border-radius: 10px;
        padding: 8px 10px;
        color: #1a3a4a;
    }
    QLineEdit:focus {
        border-color: #0d9488;
    }
    QCheckBox {
        padding: 8px;
    }
    QCheckBox::indicator {
        border: 2px solid #99c2d4;
        background-color: #ffffff;
        border-radius: 4px;
        width: 16px;
        height: 16px;
    }
    QCheckBox::indicator:checked {
        background-color: #0d9488;
        border-color: #0d9488;
    }
    QPushButton {
        background-color: #f0f7fa;
        border: 1px solid #a8d4e6;
        border-radius: 10px;
        padding: 8px 14px;
        color: #1a3a4a;
    }
    QPushButton:hover {
        background-color: #e0f2f1;
        border-color: #0d9488;
    }
    QPushButton:pressed {
        background-color: #ccf0ee;
    }
    QPushButton:disabled {
        background-color: #e8f4f8;
        color: #94a3b8;
    }
    QPushButton#primaryButton {
        background-color: #0d9488;
        border-color: #0d9488;
        color: #ffffff;
        font-weight: bold;
    }
    QPushButton#primaryButton:hover {
        background-color: #0f766e;
    }
    QPushButton#primaryButton:pressed {
        background-color: #115e59;
    }
    QProgressBar {
        border: 1px solid #a8d4e6;
        border-radius: 10px;
        text-align: center;
        background-color: #ffffff;
    }
    QProgressBar::chunk {
        background-color: #0d9488;
        border-radius: 8px;
    }
    QComboBox {
        background-color: #ffffff;
        border: 1px solid #a8d4e6;
        border-radius: 10px;
        padding: 8px 10px;
        color: #1a3a4a;
    }
    QComboBox:hover {
        border-color: #0d9488;
    }
    QTabWidget::pane {
        border: 1px solid #a8d4e6;
        border-radius: 12px;
        background-color: #ffffff;
        margin-top: -1px;
    }
    QTabBar::tab {
        background-color: #f0f7fa;
        border: 1px solid #a8d4e6;
        padding: 8px 16px;
        margin-right: 4px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
    }
    QTabBar::tab:selected {
        background-color: #ffffff;
        border-bottom-color: #ffffff;
    }
    QMenuBar {
        background-color: #e8f4f8;
        color: #1a3a4a;
    }
    QMenuBar::item:selected {
        background-color: #e0f2f1;
    }
    QTextEdit {
        background-color: #ffffff;
        border: 1px solid #a8d4e6;
        border-radius: 10px;
        padding: 8px;
        color: #1a3a4a;
    }
"""

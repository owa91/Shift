import sys
from PyQt6.QtWidgets import QApplication
from ui import main as ui

app = QApplication(sys.argv)

ui.start(app)

sys.exit(app.exec())
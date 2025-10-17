from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QComboBox

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FluxConvert (Python) — MVP")
        lay = QVBoxLayout(self)
        self.label = QLabel("Drop files or choose a preset (placeholder).")
        lay.addWidget(self.label)
        self.combo = QComboBox()
        self.combo.addItems(["web-1080p", "image-web"])
        lay.addWidget(self.combo)
        btn = QPushButton("Choose Files…")
        btn.clicked.connect(self.pick)
        lay.addWidget(btn)

    def pick(self):
        QFileDialog.getOpenFileNames(self, "Pick inputs")

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(480, 240)
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

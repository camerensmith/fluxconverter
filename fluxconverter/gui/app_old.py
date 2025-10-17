from __future__ import annotations

import sys
from typing import List

from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QAction, QIcon, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QPushButton,
    QGroupBox, QLabel, QComboBox, QSpinBox, QLineEdit, QCheckBox, QRadioButton,
    QStatusBar, QGridLayout, QTabWidget
)
import requests


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FluxConverter — Media Conversion Tool")
        self.resize(840, 520)

        # --- Toolbar ---
        tb = QToolBar("Main")
        tb.setIconSize(QSize(20, 20))
        tb.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, tb)

        self.act_add_files = QAction(QIcon.fromTheme("document-open"), "Add files", self)
        self.act_add_folder = QAction(QIcon.fromTheme("folder-open"), "Add folder", self)
        self.act_remove = QAction(QIcon.fromTheme("edit-delete"), "Remove", self)
        self.act_process = QAction(QIcon.fromTheme("media-playback-start"), "Process", self)

        tb.addAction(self.act_add_files)
        tb.addAction(self.act_add_folder)
        tb.addAction(self.act_remove)
        tb.addSeparator()
        tb.addAction(self.act_process)

        donate_btn = QPushButton("Donate")
        donate_btn.setFixedHeight(26)
        tb.addWidget(QWidget())  # spacer (placeholder)
        tb.addSeparator()
        tb.addWidget(donate_btn)

        # --- Central layout ---
        central = QWidget()
        self.setCentralWidget(central)
        v = QVBoxLayout(central)
        v.setContentsMargins(8, 6, 8, 6)
        v.setSpacing(6)

        # File table
        self.table = QTableWidget(0, 8, self)
        self.table.setHorizontalHeaderLabels(
            ["File", "Title", "Artist", "Size (MB)", "Bitrate", "Mode", "Rate", "Status"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        
        # Enable drag and drop
        self.table.setAcceptDrops(True)
        self.table.setDragDropMode(QTableWidget.DropOnly)
        
        v.addWidget(self.table)

        # Lower control strip
        bottom = QHBoxLayout()
        bottom.setSpacing(12)

        # Bitrate group
        gb_bitrate = QGroupBox("Bitrate")
        g = QGridLayout(gb_bitrate)
        g.addWidget(QLabel("Mode:"), 0, 0)
        self.cb_mode = QComboBox()
        self.cb_mode.addItems(["Average", "Constant", "Variable"])
        g.addWidget(self.cb_mode, 0, 1)
        g.addWidget(QLabel("Rate (kbps):"), 1, 0)
        self.sb_kbps = QSpinBox()
        self.sb_kbps.setRange(8, 512)
        self.sb_kbps.setValue(130)
        g.addWidget(self.sb_kbps, 1, 1)
        bottom.addWidget(gb_bitrate, 1)

        # Modus group
        gb_modus = QGroupBox("Modus")
        g2 = QGridLayout(gb_modus)
        self.chk_joint_stereo = QCheckBox("Joint Stereo")
        self.cb_stereo_mode = QComboBox()
        self.cb_stereo_mode.addItems(["Joint Stereo", "Stereo", "Mono"])
        g2.addWidget(self.chk_joint_stereo, 0, 0, 1, 2)
        g2.addWidget(self.cb_stereo_mode, 1, 0, 1, 2)
        bottom.addWidget(gb_modus, 1)

        # Sample frequency group
        gb_sample = QGroupBox("Sample frequency")
        g3 = QGridLayout(gb_sample)
        self.chk_sample = QCheckBox()
        self.cb_sample = QComboBox()
        self.cb_sample.addItems(["44100 Hz", "48000 Hz", "32000 Hz", "22050 Hz"])
        g3.addWidget(self.chk_sample, 0, 0)
        g3.addWidget(self.cb_sample, 0, 1)
        bottom.addWidget(gb_sample, 1)

        # Destination group
        gb_dest = QGroupBox("Destination")
        g4 = QGridLayout(gb_dest)
        self.rb_custom = QRadioButton()
        self.rb_custom.setChecked(True)
        self.le_dest = QLineEdit()
        self.btn_browse = QPushButton("...")
        self.rb_output_folder = QRadioButton('Create "output" folder')
        self.rb_replace = QRadioButton("Replace")
        g4.addWidget(self.rb_custom, 0, 0)
        g4.addWidget(self.le_dest, 0, 1)
        g4.addWidget(self.btn_browse, 0, 2)
        g4.addWidget(self.rb_output_folder, 1, 0, 1, 3)
        g4.addWidget(self.rb_replace, 2, 0, 1, 3)
        # format selector
        g4.addWidget(QLabel("Format:"), 3, 0)
        self.cb_format = QComboBox()
        self.cb_format.addItems(["mp4", "mp3", "wav", "webm", "webp", "png", "jpg", "flac", "m4a"])
        g4.addWidget(self.cb_format, 3, 1)
        bottom.addWidget(gb_dest, 2)

        v.addLayout(bottom)

        # --- Status bar ---
        sb = QStatusBar()
        self.setStatusBar(sb)
        sb.showMessage("Standby — No files loaded")

        # --- Wire up actions ---
        self.act_add_files.triggered.connect(self.add_files)
        self.act_add_folder.triggered.connect(self.add_folder)
        self.act_remove.triggered.connect(self.remove_selected)
        self.act_process.triggered.connect(self.process_files)
        self.btn_browse.clicked.connect(self.choose_dest)

        # Defaults
        self.le_dest.setText(str(self.default_download_path()))

    # --- Slots ---
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Add audio files")
        for f in files:
            self._append_row(f)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Add folder")
        if folder:
            self._append_row(folder + "/*")  # scaffold placeholder

    def remove_selected(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True)
        for r in rows:
            self.table.removeRow(r)

    def process_files(self):
        count = self.table.rowCount()
        if count == 0:
            QMessageBox.information(self, "Nothing to do", "No files in the queue.")
            return
        
        # Process first file for now (can extend to batch later)
        first_path = self.table.item(0, 0).text()
        out_dir = self.le_dest.text()
        fmt = self.cb_format.currentText()
        
        try:
            resp = requests.post(
                "http://127.0.0.1:7845/run",
                json={
                    "input_path": first_path,
                    "output_dir": out_dir,
                    "output_format": fmt,
                },
                timeout=10,
            )
            if resp.ok:
                result = resp.json()
                job_id = result.get("job_id")
                output_path = result.get("output_path")
                
                # Update status in table
                self.table.setItem(0, 7, QTableWidgetItem("Processing..."))
                
                # Show success message with output path
                QMessageBox.information(
                    self, 
                    "Conversion Started", 
                    f"Job ID: {job_id}\nOutput: {output_path}\n\nCheck the output directory for your converted file."
                )
                
                # Start monitoring progress (simple version)
                self.monitor_job(job_id, 0)
            else:
                QMessageBox.warning(self, "Error", f"API error: {resp.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Request failed", str(e))

    def monitor_job(self, job_id: str, row: int):
        """Simple job monitoring - check status once."""
        try:
            resp = requests.get(f"http://127.0.0.1:7845/status/{job_id}", timeout=5)
            if resp.ok:
                status = resp.json()
                if status["status"] == "completed":
                    self.table.setItem(row, 7, QTableWidgetItem("Completed"))
                elif status["status"] == "failed":
                    self.table.setItem(row, 7, QTableWidgetItem(f"Failed: {status.get('error', 'Unknown error')}"))
                elif status["status"] == "processing":
                    self.table.setItem(row, 7, QTableWidgetItem(f"Processing... {status.get('progress', 0)}%"))
        except Exception:
            pass  # Ignore monitoring errors

    def choose_dest(self):
        d = QFileDialog.getExistingDirectory(self, "Choose destination", self.le_dest.text())
        if d:
            self.le_dest.setText(d)
            self.rb_custom.setChecked(True)

    # --- Helpers ---
    def _append_row(self, path: str):
        row = self.table.rowCount()
        self.table.insertRow(row)
        def item(text):
            it = QTableWidgetItem(text)
            it.setFlags(it.flags() ^ Qt.ItemIsEditable)
            return it
        self.table.setItem(row, 0, item(path))
        self.table.setItem(row, 1, item("—"))
        self.table.setItem(row, 2, item("—"))
        self.table.setItem(row, 3, item("—"))
        self.table.setItem(row, 4, item("—"))
        self.table.setItem(row, 5, item(self.cb_mode.currentText()))
        self.table.setItem(row, 6, item(str(self.sb_kbps.value())))
        self.table.setItem(row, 7, item("Queued"))

    def default_download_path(self):
        from pathlib import Path
        p = Path.home() / "Desktop"
        return str(p if p.exists() else Path.home())

    # --- Drag and Drop ---
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        for file_path in files:
            if file_path:  # Skip empty paths
                self._append_row(file_path)
        event.acceptProposedAction()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()



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
        self.resize(1000, 700)

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

        # --- Central layout with tabs ---
        central = QWidget()
        self.setCentralWidget(central)
        v = QVBoxLayout(central)
        v.setContentsMargins(8, 6, 8, 6)
        v.setSpacing(6)

        # Create tab widget
        self.tab_widget = QTabWidget()
        v.addWidget(self.tab_widget)

        # Create tabs
        self.create_audio_tab()
        self.create_video_tab()
        self.create_image_tab()

        # Common destination controls
        self.create_destination_controls()
        v.addLayout(self.dest_layout)

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

    def create_audio_tab(self):
        """Create the Audio conversion tab."""
        audio_tab = QWidget()
        layout = QVBoxLayout(audio_tab)
        
        # File table
        self.audio_table = QTableWidget(0, 6, self)
        self.audio_table.setHorizontalHeaderLabels(
            ["File", "Size (MB)", "Bitrate", "Mode", "Rate", "Status"]
        )
        self.audio_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.audio_table.setAlternatingRowColors(True)
        self.audio_table.horizontalHeader().setStretchLastSection(True)
        self.audio_table.verticalHeader().setVisible(False)
        
        # Enable drag and drop
        self.audio_table.setAcceptDrops(True)
        self.audio_table.setDragDropMode(QTableWidget.DropOnly)
        
        layout.addWidget(self.audio_table)

        # Audio-specific controls
        controls = QHBoxLayout()
        
        # Bitrate group
        gb_bitrate = QGroupBox("Bitrate")
        g = QGridLayout(gb_bitrate)
        g.addWidget(QLabel("Mode:"), 0, 0)
        self.audio_cb_mode = QComboBox()
        self.audio_cb_mode.addItems(["Average", "Constant", "Variable"])
        g.addWidget(self.audio_cb_mode, 0, 1)
        g.addWidget(QLabel("Rate (kbps):"), 1, 0)
        self.audio_sb_kbps = QSpinBox()
        self.audio_sb_kbps.setRange(8, 512)
        self.audio_sb_kbps.setValue(130)
        g.addWidget(self.audio_sb_kbps, 1, 1)
        controls.addWidget(gb_bitrate)

        # Audio format group
        gb_format = QGroupBox("Output Format")
        g2 = QGridLayout(gb_format)
        g2.addWidget(QLabel("Audio Format:"), 0, 0)
        self.audio_cb_format = QComboBox()
        self.audio_cb_format.addItems(["mp3", "wav", "flac", "m4a", "aac"])
        g2.addWidget(self.audio_cb_format, 0, 1)
        g2.addWidget(QLabel("Sample Rate:"), 1, 0)
        self.audio_cb_sample = QComboBox()
        self.audio_cb_sample.addItems(["44100 Hz", "48000 Hz", "32000 Hz", "22050 Hz"])
        g2.addWidget(self.audio_cb_sample, 1, 1)
        controls.addWidget(gb_format)

        layout.addLayout(controls)
        self.tab_widget.addTab(audio_tab, "🎵 Audio")

    def create_video_tab(self):
        """Create the Video conversion tab."""
        video_tab = QWidget()
        layout = QVBoxLayout(video_tab)
        
        # File table
        self.video_table = QTableWidget(0, 7, self)
        self.video_table.setHorizontalHeaderLabels(
            ["File", "Size (MB)", "Resolution", "Duration", "Codec", "Bitrate", "Status"]
        )
        self.video_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.video_table.setAlternatingRowColors(True)
        self.video_table.horizontalHeader().setStretchLastSection(True)
        self.video_table.verticalHeader().setVisible(False)
        
        # Enable drag and drop
        self.video_table.setAcceptDrops(True)
        self.video_table.setDragDropMode(QTableWidget.DropOnly)
        
        layout.addWidget(self.video_table)

        # Video-specific controls
        controls = QHBoxLayout()
        
        # Video format group
        gb_format = QGroupBox("Output Format")
        g = QGridLayout(gb_format)
        g.addWidget(QLabel("Video Format:"), 0, 0)
        self.video_cb_format = QComboBox()
        self.video_cb_format.addItems(["mp4", "webm", "avi", "mov"])
        g.addWidget(self.video_cb_format, 0, 1)
        g.addWidget(QLabel("Codec:"), 1, 0)
        self.video_cb_codec = QComboBox()
        self.video_cb_codec.addItems(["H.264", "H.265", "VP9", "AV1"])
        g.addWidget(self.video_cb_codec, 1, 1)
        controls.addWidget(gb_format)

        # Quality group
        gb_quality = QGroupBox("Quality")
        g2 = QGridLayout(gb_quality)
        g2.addWidget(QLabel("Resolution:"), 0, 0)
        self.video_cb_resolution = QComboBox()
        self.video_cb_resolution.addItems(["Original", "4K (3840x2160)", "1080p (1920x1080)", "720p (1280x720)", "480p (854x480)"])
        g2.addWidget(self.video_cb_resolution, 0, 1)
        g2.addWidget(QLabel("Bitrate:"), 1, 0)
        self.video_cb_bitrate = QComboBox()
        self.video_cb_bitrate.addItems(["Auto", "50 Mbps", "25 Mbps", "10 Mbps", "5 Mbps", "2 Mbps"])
        g2.addWidget(self.video_cb_bitrate, 1, 1)
        controls.addWidget(gb_quality)

        layout.addLayout(controls)
        self.tab_widget.addTab(video_tab, "🎬 Video")

    def create_image_tab(self):
        """Create the Image conversion tab."""
        image_tab = QWidget()
        layout = QVBoxLayout(image_tab)
        
        # File table
        self.image_table = QTableWidget(0, 6, self)
        self.image_table.setHorizontalHeaderLabels(
            ["File", "Size (MB)", "Dimensions", "Format", "Quality", "Status"]
        )
        self.image_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.image_table.setAlternatingRowColors(True)
        self.image_table.horizontalHeader().setStretchLastSection(True)
        self.image_table.verticalHeader().setVisible(False)
        
        # Enable drag and drop
        self.image_table.setAcceptDrops(True)
        self.image_table.setDragDropMode(QTableWidget.DropOnly)
        
        layout.addWidget(self.image_table)

        # Image-specific controls
        controls = QHBoxLayout()
        
        # Image format group
        gb_format = QGroupBox("Output Format")
        g = QGridLayout(gb_format)
        g.addWidget(QLabel("Image Format:"), 0, 0)
        self.image_cb_format = QComboBox()
        self.image_cb_format.addItems(["webp", "png", "jpg", "jpeg", "bmp", "tiff"])
        g.addWidget(self.image_cb_format, 0, 1)
        g.addWidget(QLabel("Quality:"), 1, 0)
        self.image_sb_quality = QSpinBox()
        self.image_sb_quality.setRange(1, 100)
        self.image_sb_quality.setValue(80)
        g.addWidget(self.image_sb_quality, 1, 1)
        controls.addWidget(gb_format)

        # Resize group
        gb_resize = QGroupBox("Resize")
        g2 = QGridLayout(gb_resize)
        g2.addWidget(QLabel("Width:"), 0, 0)
        self.image_sb_width = QSpinBox()
        self.image_sb_width.setRange(1, 8192)
        self.image_sb_width.setValue(1920)
        g2.addWidget(self.image_sb_width, 0, 1)
        g2.addWidget(QLabel("Height:"), 1, 0)
        self.image_sb_height = QSpinBox()
        self.image_sb_height.setRange(1, 8192)
        self.image_sb_height.setValue(1080)
        g2.addWidget(self.image_sb_height, 1, 1)
        controls.addWidget(gb_resize)

        layout.addLayout(controls)
        self.tab_widget.addTab(image_tab, "🖼️ Image")

    def create_destination_controls(self):
        """Create common destination controls."""
        self.dest_layout = QHBoxLayout()
        
        # Destination group
        gb_dest = QGroupBox("Destination")
        g = QGridLayout(gb_dest)
        self.rb_custom = QRadioButton("Custom folder")
        self.rb_custom.setChecked(True)
        self.le_dest = QLineEdit()
        self.btn_browse = QPushButton("...")
        self.rb_output_folder = QRadioButton('Create "output" folder')
        self.rb_replace = QRadioButton("Replace original")
        
        g.addWidget(self.rb_custom, 0, 0)
        g.addWidget(self.le_dest, 0, 1)
        g.addWidget(self.btn_browse, 0, 2)
        g.addWidget(self.rb_output_folder, 1, 0, 1, 3)
        g.addWidget(self.rb_replace, 2, 0, 1, 3)
        
        self.dest_layout.addWidget(gb_dest)

    # --- Slots ---
    def add_files(self):
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:  # Audio
            files, _ = QFileDialog.getOpenFileNames(self, "Add audio files", "", "Audio Files (*.mp3 *.wav *.flac *.m4a *.aac)")
        elif current_tab == 1:  # Video
            files, _ = QFileDialog.getOpenFileNames(self, "Add video files", "", "Video Files (*.mp4 *.webm *.avi *.mov *.mkv)")
        else:  # Image
            files, _ = QFileDialog.getOpenFileNames(self, "Add image files", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)")
        
        for f in files:
            self._append_row(f, current_tab)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Add folder")
        if folder:
            current_tab = self.tab_widget.currentIndex()
            self._append_row(folder + "/*", current_tab)

    def remove_selected(self):
        current_tab = self.tab_widget.currentIndex()
        table = self._get_current_table()
        rows = sorted({i.row() for i in table.selectedIndexes()}, reverse=True)
        for r in rows:
            table.removeRow(r)

    def process_files(self):
        current_tab = self.tab_widget.currentIndex()
        table = self._get_current_table()
        count = table.rowCount()
        if count == 0:
            QMessageBox.information(self, "Nothing to do", "No files in the queue.")
            return
        
        # Process first file for now
        first_path = table.item(0, 0).text()
        out_dir = self.le_dest.text()
        
        # Get format based on current tab
        if current_tab == 0:  # Audio
            fmt = self.audio_cb_format.currentText()
        elif current_tab == 1:  # Video
            fmt = self.video_cb_format.currentText()
        else:  # Image
            fmt = self.image_cb_format.currentText()
        
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
                table.setItem(0, -1, QTableWidgetItem("Processing..."))
                
                # Show success message
                QMessageBox.information(
                    self, 
                    "Conversion Started", 
                    f"Job ID: {job_id}\nOutput: {output_path}\n\nCheck the output directory for your converted file."
                )
                
                # Start monitoring progress
                self.monitor_job(job_id, 0, current_tab)
            else:
                QMessageBox.warning(self, "Error", f"API error: {resp.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Request failed", str(e))

    def choose_dest(self):
        d = QFileDialog.getExistingDirectory(self, "Choose destination", self.le_dest.text())
        if d:
            self.le_dest.setText(d)
            self.rb_custom.setChecked(True)

    # --- Helpers ---
    def _get_current_table(self):
        """Get the current table based on active tab."""
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:
            return self.audio_table
        elif current_tab == 1:
            return self.video_table
        else:
            return self.image_table

    def _append_row(self, path: str, tab_index: int):
        """Add a row to the appropriate table."""
        if tab_index == 0:
            table = self.audio_table
            headers = ["File", "Size (MB)", "Bitrate", "Mode", "Rate", "Status"]
        elif tab_index == 1:
            table = self.video_table
            headers = ["File", "Size (MB)", "Resolution", "Duration", "Codec", "Bitrate", "Status"]
        else:
            table = self.image_table
            headers = ["File", "Size (MB)", "Dimensions", "Format", "Quality", "Status"]
        
        row = table.rowCount()
        table.insertRow(row)
        
        def item(text):
            it = QTableWidgetItem(text)
            it.setFlags(it.flags() ^ Qt.ItemIsEditable)
            return it
        
        table.setItem(row, 0, item(path))
        for i in range(1, len(headers) - 1):
            table.setItem(row, i, item("—"))
        table.setItem(row, len(headers) - 1, item("Queued"))

    def monitor_job(self, job_id: str, row: int, tab_index: int):
        """Simple job monitoring."""
        try:
            resp = requests.get(f"http://127.0.0.1:7845/status/{job_id}", timeout=5)
            if resp.ok:
                status = resp.json()
                table = self._get_current_table()
                if status["status"] == "completed":
                    table.setItem(row, -1, QTableWidgetItem("Completed"))
                elif status["status"] == "failed":
                    table.setItem(row, -1, QTableWidgetItem(f"Failed: {status.get('error', 'Unknown error')}"))
                elif status["status"] == "processing":
                    table.setItem(row, -1, QTableWidgetItem(f"Processing... {status.get('progress', 0)}%"))
        except Exception:
            pass

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
        current_tab = self.tab_widget.currentIndex()
        for file_path in files:
            if file_path:
                self._append_row(file_path, current_tab)
        event.acceptProposedAction()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

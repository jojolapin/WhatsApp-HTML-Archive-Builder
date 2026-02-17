"""Main application window and entry point."""
import logging
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QProcess, QThread, Qt, QTimer, Slot, QUrl, QDate
from PySide6.QtGui import QAction, QClipboard, QDragEnterEvent, QDropEvent, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from whatsapp_archive.config import COMMON_TIMEZONES, VERSION, WHISPER_MODELS
from whatsapp_archive.gui.styles import DARK_STYLE, LIGHT_STYLE
from whatsapp_archive.gui.worker import ChatWorker
from whatsapp_archive.translations import TRANSLATIONS
from whatsapp_archive.parser import (
    MEDIA_FILENAME_RE,
    load_chat_messages,
    parse_message_datetime,
)
from whatsapp_archive.settings_store import load_settings, save_settings
from whatsapp_archive.utils import setup_logging

logger = logging.getLogger(__name__)


class MainWindow(QWidget):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.is_dark_theme = False
        self.current_lang = "en"

        self.setWindowTitle(TRANSLATIONS[self.current_lang]["window_title"])
        self.setGeometry(100, 100, 650, 600)

        self.spinner_timer = QTimer(self)
        self.spinner_chars = ["|", "/", "\u2014", "\\"]
        self.spinner_index = 0
        self.spinner_base_text = ""
        self.spinner_timer.timeout.connect(self._update_spinner)

        self.setup_ui()

        self.chat_file_path = None
        self.worker_thread = None
        self.worker = None

        self.setAcceptDrops(True)
        self._setup_menus()
        self._load_settings()

    def setup_ui(self):
        T = TRANSLATIONS[self.current_lang]
        self.main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        self.converter_tab = QWidget()
        self.tabs.addTab(self.converter_tab, T["tab_converter"])
        converter_layout = QVBoxLayout(self.converter_tab)

        self.input_group = QGroupBox(T["config_group"])
        input_layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        self.title_label = QLabel(T["title_label"])
        self.title_edit = QLineEdit("WhatsApp Chat Archive")
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.title_edit)
        input_layout.addLayout(title_layout)

        self.transcribe_checkbox = QCheckBox(T["transcribe_label"])
        self.transcribe_checkbox.setChecked(True)
        input_layout.addWidget(self.transcribe_checkbox)

        self.encrypt_checkbox = QCheckBox(T["encrypt_label"])
        self.encrypt_checkbox.setChecked(False)
        self.encrypt_checkbox.toggled.connect(self.on_encrypt_toggled)
        input_layout.addWidget(self.encrypt_checkbox)

        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Whisper model:"))
        self.whisper_model_combo = QComboBox()
        for display_name, _load_name, _local in WHISPER_MODELS:
            self.whisper_model_combo.addItem(display_name)
        self.whisper_model_combo.setCurrentIndex(len(WHISPER_MODELS) - 1)  # Large by default
        self.whisper_model_combo.currentIndexChanged.connect(self._save_settings)
        model_layout.addWidget(self.whisper_model_combo)
        input_layout.addLayout(model_layout)

        tz_layout = QHBoxLayout()
        tz_layout.addWidget(QLabel("Timezone:"))
        self.timezone_combo = QComboBox()
        for _label, tz_key in COMMON_TIMEZONES:
            self.timezone_combo.addItem(f"{_label} ({tz_key})", tz_key)
        default_idx = next((i for i, (_, k) in enumerate(COMMON_TIMEZONES) if k == "America/New_York"), 0)
        self.timezone_combo.setCurrentIndex(default_idx)
        self.timezone_combo.currentIndexChanged.connect(self._save_settings)
        tz_layout.addWidget(self.timezone_combo)
        input_layout.addLayout(tz_layout)

        self.filter_date_check = QCheckBox("Filter by date range")
        self.filter_date_check.setChecked(False)
        input_layout.addWidget(self.filter_date_check)
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("From:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate(2000, 1, 1))
        date_layout.addWidget(self.date_from)
        date_layout.addWidget(QLabel("To:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate(2030, 12, 31))
        date_layout.addWidget(self.date_to)
        input_layout.addLayout(date_layout)

        self.select_chat_btn = QPushButton(T["select_chat_btn"])
        self.select_chat_btn.clicked.connect(self.select_chat_file)
        input_layout.addWidget(self.select_chat_btn)

        self.chat_file_label = QLabel(T["chat_file_label"])
        self.chat_file_label.setStyleSheet("font-style: italic; color: #555;")
        input_layout.addWidget(self.chat_file_label)

        self.media_folder_label = QLabel(T["media_folder_label"])
        self.media_folder_label.setStyleSheet("font-style: italic; color: #555;")
        input_layout.addWidget(self.media_folder_label)

        self.input_group.setLayout(input_layout)
        converter_layout.addWidget(self.input_group)

        self.conv_group = QGroupBox(T["conv_group"])
        conv_layout = QVBoxLayout()

        self.run_btn = QPushButton(T["run_btn"])
        self.run_btn.setObjectName("primaryButton")
        self.run_btn.clicked.connect(self.run_conversion)
        self.run_btn.setEnabled(False)
        conv_layout.addWidget(self.run_btn)

        self.stop_btn = QPushButton(T["stop_btn"])
        self.stop_btn.clicked.connect(self.request_stop)
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px;")
        self.stop_btn.hide()
        conv_layout.addWidget(self.stop_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m")
        conv_layout.addWidget(self.progress_bar)

        self.status_label = QLabel(T["status_idle"])
        self.status_label.setWordWrap(True)
        conv_layout.addWidget(self.status_label)

        self.conv_group.setLayout(conv_layout)
        converter_layout.addWidget(self.conv_group)
        converter_layout.addStretch()

        self.how_to_tab = QWidget()
        self.tabs.addTab(self.how_to_tab, T["tab_how_to"])
        how_to_layout = QVBoxLayout(self.how_to_tab)
        self.how_to_text_edit = QTextEdit()
        self.how_to_text_edit.setReadOnly(True)
        self.how_to_text_edit.setHtml(T["how_to_use_content"])
        how_to_layout.addWidget(self.how_to_text_edit)

        self.stats_tab = QWidget()
        self.tabs.addTab(self.stats_tab, "Statistics")
        stats_layout = QVBoxLayout(self.stats_tab)
        self.stats_btn = QPushButton("Load statistics from selected chat file")
        self.stats_btn.clicked.connect(self._load_stats)
        self.stats_btn.setEnabled(False)
        stats_layout.addWidget(self.stats_btn)
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setPlaceholderText("Select a chat file, then click 'Load statistics'.")
        stats_layout.addWidget(self.stats_text)

        self.transcribe_tab = QWidget()
        self.tabs.addTab(self.transcribe_tab, T["tab_transcribe_file"])
        transcribe_layout = QVBoxLayout(self.transcribe_tab)

        self.transcribe_file_btn = QPushButton(T["transcribe_select_file_btn"])
        self.transcribe_file_btn.clicked.connect(self._select_transcribe_file)
        transcribe_layout.addWidget(self.transcribe_file_btn)
        self.transcribe_file_label = QLabel(T["transcribe_file_label"])
        self.transcribe_file_label.setWordWrap(True)
        transcribe_layout.addWidget(self.transcribe_file_label)

        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.transcribe_lang_combo = QComboBox()
        self.transcribe_lang_combo.addItem(T["transcribe_lang_en"], "en")
        self.transcribe_lang_combo.addItem(T["transcribe_lang_fr"], "fr")
        self.transcribe_lang_combo.addItem(T["transcribe_lang_auto"], None)
        lang_layout.addWidget(self.transcribe_lang_combo)
        transcribe_layout.addLayout(lang_layout)

        model_t_layout = QHBoxLayout()
        model_t_layout.addWidget(QLabel(T["transcribe_whisper_model"]))
        self.transcribe_model_combo = QComboBox()
        for display_name, _load_name, _local in WHISPER_MODELS:
            self.transcribe_model_combo.addItem(display_name)
        self.transcribe_model_combo.setCurrentIndex(len(WHISPER_MODELS) - 1)
        model_t_layout.addWidget(self.transcribe_model_combo)
        transcribe_layout.addLayout(model_t_layout)

        btn_row = QHBoxLayout()
        self.transcribe_btn = QPushButton(T["transcribe_btn"])
        self.transcribe_btn.setObjectName("primaryButton")
        self.transcribe_btn.clicked.connect(self._run_transcribe_file)
        self.transcribe_btn.setEnabled(False)
        self.transcribe_stop_btn = QPushButton(T["stop_btn"])
        self.transcribe_stop_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px;")
        self.transcribe_stop_btn.clicked.connect(self._request_transcribe_stop)
        self.transcribe_stop_btn.hide()
        btn_row.addWidget(self.transcribe_btn)
        btn_row.addWidget(self.transcribe_stop_btn)
        transcribe_layout.addLayout(btn_row)

        self.transcribe_status_label = QLabel(T["transcribe_status_idle"])
        self.transcribe_status_label.setWordWrap(True)
        transcribe_layout.addWidget(self.transcribe_status_label)

        self.transcribe_output = QTextEdit()
        self.transcribe_output.setReadOnly(True)
        self.transcribe_output.setPlaceholderText("Transcription will appear here.")
        transcribe_layout.addWidget(self.transcribe_output)

        out_btn_row = QHBoxLayout()
        self.transcribe_copy_btn = QPushButton(T["transcribe_copy_btn"])
        self.transcribe_copy_btn.clicked.connect(self._copy_transcription)
        self.transcribe_save_btn = QPushButton(T["transcribe_save_txt_btn"])
        self.transcribe_save_btn.clicked.connect(self._save_transcription_txt)
        out_btn_row.addWidget(self.transcribe_copy_btn)
        out_btn_row.addWidget(self.transcribe_save_btn)
        transcribe_layout.addLayout(out_btn_row)

        self.transcribe_file_path = None
        self.transcribe_process = None
        self.transcribe_output_temp_path = None

        footer_layout = QHBoxLayout()
        self.lang_button = QPushButton(T["lang_btn_fr"])
        self.lang_button.clicked.connect(self.toggle_language)
        self.theme_button = QPushButton(T["theme_btn_dark"])
        self.theme_button.clicked.connect(self.toggle_theme)
        self.version_label = QLabel(f"JojoLapin™ {VERSION}")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        footer_layout.addWidget(self.lang_button)
        footer_layout.addWidget(self.theme_button)
        footer_layout.addStretch()
        footer_layout.addWidget(self.version_label)
        self.main_layout.addLayout(footer_layout)

    def _setup_menus(self):
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu("&File")
        open_act = QAction("&Open chat file...", self)
        open_act.setShortcut(QKeySequence.StandardKey.Open)
        open_act.triggered.connect(self.select_chat_file)
        file_menu.addAction(open_act)
        file_menu.addSeparator()
        exit_act = QAction("E&xit", self)
        exit_act.setShortcut(QKeySequence.StandardKey.Quit)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)
        help_menu = menubar.addMenu("&Help")
        about_act = QAction("&About", self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)
        self.main_layout.insertWidget(0, menubar)

    def _show_about(self):
        QMessageBox.about(
            self,
            "About WhatsApp Archive Builder",
            f"<h3>WhatsApp Chat to HTML Converter</h3><p>Whisper Edition</p><p>Version {VERSION}</p><p>JojoLain™</p>",
        )

    def _load_settings(self):
        s = load_settings()
        self.is_dark_theme = s.get("theme_dark", False)
        if self.is_dark_theme:
            self.app.setStyleSheet(DARK_STYLE)
        self.current_lang = s.get("lang", "en")
        self.retranslate_ui()
        tz_key = s.get("timezone_key", "America/New_York")
        idx = next((i for i in range(self.timezone_combo.count()) if self.timezone_combo.itemData(i) == tz_key), 0)
        self.timezone_combo.blockSignals(True)
        self.timezone_combo.setCurrentIndex(idx)
        self.timezone_combo.blockSignals(False)
        self.whisper_model_combo.blockSignals(True)
        self.whisper_model_combo.setCurrentIndex(min(s.get("whisper_model_index", len(WHISPER_MODELS) - 1), len(WHISPER_MODELS) - 1))
        self.whisper_model_combo.blockSignals(False)
        if "window_x" in s and "window_y" in s and "window_width" in s and "window_height" in s:
            self.setGeometry(s["window_x"], s["window_y"], s["window_width"], s["window_height"])

    def _load_stats(self):
        if not self.chat_file_path or not self.chat_file_path.exists():
            self.stats_text.setPlainText("No chat file selected or file not found.")
            return
        import pytz
        from whatsapp_archive.config import DEFAULT_TIMEZONE
        tz = pytz.timezone(self.timezone_combo.currentData() or DEFAULT_TIMEZONE)
        try:
            messages = load_chat_messages(self.chat_file_path)
            for m in messages:
                m["datetime_obj"] = parse_message_datetime(m, local_tz=tz)
            parseable = [m for m in messages if m.get("datetime_obj")]
            parseable.sort(key=lambda x: x["datetime_obj"])

            participants = {}
            media_images = media_audio = media_video = media_other = 0
            for m in parseable:
                name = m.get("name") or "(system)"
                participants[name] = participants.get(name, 0) + 1
                msg = m.get("msg", "")
                mf = MEDIA_FILENAME_RE.search(msg) or MEDIA_FILENAME_RE.fullmatch(msg.strip())
                if mf:
                    fn = mf.group("fname")
                    low = fn.lower()
                    if low.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg")):
                        media_images += 1
                    elif low.endswith((".mp3", ".m4a", ".ogg", ".opus", ".wav", ".aac")):
                        media_audio += 1
                    elif low.endswith((".mp4", ".mov", ".mkv", ".webm")):
                        media_video += 1
                    else:
                        media_other += 1

            first_ts = parseable[0]["datetime_obj"] if parseable else None
            last_ts = parseable[-1]["datetime_obj"] if parseable else None
            lines = [
                f"Total messages: {len(parseable)}",
                f"Date range: {first_ts.strftime('%Y-%m-%d %H:%M') if first_ts else 'N/A'} — {last_ts.strftime('%Y-%m-%d %H:%M') if last_ts else 'N/A'}",
                "",
                "Participants:",
            ]
            for name, count in sorted(participants.items(), key=lambda x: -x[1]):
                lines.append(f"  • {name}: {count}")
            lines.extend([
                "",
                "Media:",
                f"  Images: {media_images}",
                f"  Audio: {media_audio}",
                f"  Video: {media_video}",
                f"  Other: {media_other}",
            ])
            self.stats_text.setPlainText("\n".join(lines))
        except Exception as e:
            self.stats_text.setPlainText(f"Error loading statistics: {e}")

    def _save_settings(self):
        prev = load_settings()
        last_dir = str(self.chat_file_path.parent) if self.chat_file_path else prev.get("last_directory", "")
        save_settings({
            "theme_dark": self.is_dark_theme,
            "lang": self.current_lang,
            "timezone_key": self.timezone_combo.currentData() or "America/New_York",
            "whisper_model_index": self.whisper_model_combo.currentIndex(),
            "last_directory": last_dir,
            "window_x": self.x(),
            "window_y": self.y(),
            "window_width": self.width(),
            "window_height": self.height(),
        })

    def closeEvent(self, event):
        self._save_settings()
        super().closeEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and Path(urls[0].toLocalFile()).suffix.lower() == ".txt":
                event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        T = TRANSLATIONS[self.current_lang]
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                path = Path(urls[0].toLocalFile())
                if path.suffix.lower() == ".txt" and path.exists():
                    self.chat_file_path = path
                    self.chat_file_label.setText(f"Chat File: {self.chat_file_path.name}")
                    self.media_folder_label.setText(f"Media Folder: {self.chat_file_path.parent}")
                    if self.is_dark_theme:
                        self.chat_file_label.setStyleSheet("font-style: normal; color: #fff;")
                        self.media_folder_label.setStyleSheet("font-style: normal; color: #fff;")
                    else:
                        self.chat_file_label.setStyleSheet("font-style: normal; color: #000;")
                        self.media_folder_label.setStyleSheet("font-style: normal; color: #000;")
                    self.run_btn.setEnabled(True)
                    self.stats_btn.setEnabled(True)
                    self.status_label.setText(T["status_idle"])
                    save_settings({**load_settings(), "last_directory": str(self.chat_file_path.parent)})
        event.acceptProposedAction()

    @Slot()
    def toggle_language(self):
        if self.current_lang == "en":
            self.current_lang = "fr"
        else:
            self.current_lang = "en"
        self.retranslate_ui()
        self._save_settings()

    def retranslate_ui(self):
        T = TRANSLATIONS[self.current_lang]
        self.setWindowTitle(T["window_title"])
        self.tabs.setTabText(0, T["tab_converter"])
        self.tabs.setTabText(1, T["tab_how_to"])
        self.input_group.setTitle(T["config_group"])
        self.title_label.setText(T["title_label"])
        self.transcribe_checkbox.setText(T["transcribe_label"])
        self.encrypt_checkbox.setText(T["encrypt_label"])
        self.select_chat_btn.setText(T["select_chat_btn"])
        if self.chat_file_label.text() in (TRANSLATIONS["en"]["chat_file_label"], TRANSLATIONS["fr"]["chat_file_label"]):
            self.chat_file_label.setText(T["chat_file_label"])
        if self.media_folder_label.text() in (TRANSLATIONS["en"]["media_folder_label"], TRANSLATIONS["fr"]["media_folder_label"]):
            self.media_folder_label.setText(T["media_folder_label"])
        self.conv_group.setTitle(T["conv_group"])
        self.run_btn.setText(T["run_btn"])
        self.stop_btn.setText(T["stop_btn"])
        current_status = self.status_label.text().split(" ")[0]
        if current_status in ("Idle.", "Prêt."):
            self.status_label.setText(T["status_idle"])
        self.how_to_text_edit.setHtml(T["how_to_use_content"])
        self.tabs.setTabText(2, "Statistics")
        self.tabs.setTabText(3, T["tab_transcribe_file"])
        self.transcribe_file_btn.setText(T["transcribe_select_file_btn"])
        self.transcribe_lang_combo.setItemText(0, T["transcribe_lang_en"])
        self.transcribe_lang_combo.setItemText(1, T["transcribe_lang_fr"])
        self.transcribe_lang_combo.setItemText(2, T["transcribe_lang_auto"])
        self.transcribe_btn.setText(T["transcribe_btn"])
        self.transcribe_copy_btn.setText(T["transcribe_copy_btn"])
        self.transcribe_save_btn.setText(T["transcribe_save_txt_btn"])
        if not self.transcribe_file_path:
            self.transcribe_file_label.setText(T["transcribe_file_label"])
        if self.transcribe_process is None and not self.transcribe_stop_btn.isVisible():
            self.transcribe_status_label.setText(T["transcribe_status_idle"])
        self.transcribe_stop_btn.setText(T["stop_btn"])
        if self.is_dark_theme:
            self.theme_button.setText(T["theme_btn_light"])
        else:
            self.theme_button.setText(T["theme_btn_dark"])
        if self.current_lang == "en":
            self.lang_button.setText(T["lang_btn_fr"])
        else:
            self.lang_button.setText(T["lang_btn_en"])

    @Slot(bool)
    def on_encrypt_toggled(self, checked):
        if checked:
            self.transcribe_checkbox.setChecked(True)
            self.transcribe_checkbox.setEnabled(False)
        else:
            self.transcribe_checkbox.setEnabled(True)

    @Slot()
    def _update_spinner(self):
        try:
            char = self.spinner_chars[self.spinner_index]
            self.status_label.setText(f"{self.spinner_base_text} {char}")
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)
        except Exception as e:
            logger.debug("Spinner error: %s", e)
            self.spinner_timer.stop()

    @Slot()
    def request_stop(self):
        T = TRANSLATIONS[self.current_lang]
        if self.worker:
            self.worker.request_stop()
            self.stop_btn.setEnabled(False)
            self.stop_btn.setText(T["stop_btn_stopping"])
            self.on_status("status_stop_requested", {})

    def _reset_buttons(self):
        T = TRANSLATIONS[self.current_lang]
        self.run_btn.setEnabled(True)
        self.select_chat_btn.setEnabled(True)
        self.stop_btn.hide()
        self.stop_btn.setEnabled(True)
        self.stop_btn.setText(T["stop_btn"])

    @Slot()
    def toggle_theme(self):
        T = TRANSLATIONS[self.current_lang]
        if self.is_dark_theme:
            self.app.setStyleSheet(LIGHT_STYLE)
            self.theme_button.setText(T["theme_btn_dark"])
            if not self.chat_file_path:
                self.chat_file_label.setStyleSheet("font-style: italic; color: #555;")
                self.media_folder_label.setStyleSheet("font-style: italic; color: #555;")
            else:
                self.chat_file_label.setStyleSheet("font-style: normal; color: #000;")
                self.media_folder_label.setStyleSheet("font-style: normal; color: #000;")
        else:
            self.app.setStyleSheet(DARK_STYLE)
            self.theme_button.setText(T["theme_btn_light"])
            if not self.chat_file_path:
                self.chat_file_label.setStyleSheet("font-style: italic; color: #888;")
                self.media_folder_label.setStyleSheet("font-style: italic; color: #888;")
            else:
                self.chat_file_label.setStyleSheet("font-style: normal; color: #fff;")
                self.media_folder_label.setStyleSheet("font-style: normal; color: #fff;")
        self.is_dark_theme = not self.is_dark_theme
        self._save_settings()

    @Slot()
    def select_chat_file(self):
        T = TRANSLATIONS[self.current_lang]
        s = load_settings()
        start_dir = s.get("last_directory", "") or str(Path.home())
        file_path, _ = QFileDialog.getOpenFileName(self, T["select_chat_title"], start_dir, T["select_chat_filter"])
        if not file_path:
            return
        self.chat_file_path = Path(file_path)
        self.chat_file_label.setText(f"Chat File: {self.chat_file_path.name}")
        self.media_folder_label.setText(f"Media Folder: {self.chat_file_path.parent}")
        if self.is_dark_theme:
            self.chat_file_label.setStyleSheet("font-style: normal; color: #fff;")
            self.media_folder_label.setStyleSheet("font-style: normal; color: #fff;")
        else:
            self.chat_file_label.setStyleSheet("font-style: normal; color: #000;")
            self.media_folder_label.setStyleSheet("font-style: normal; color: #000;")
        self.run_btn.setEnabled(True)
        self.status_label.setText(T["status_idle"])
        save_settings({
            **load_settings(),
            "last_directory": str(self.chat_file_path.parent),
        })

    def _select_transcribe_file(self):
        T = TRANSLATIONS[self.current_lang]
        s = load_settings()
        start_dir = s.get("last_directory", "") or str(Path.home())
        file_path, _ = QFileDialog.getOpenFileName(
            self, T["transcribe_select_file_btn"], start_dir, T["transcribe_select_filter"]
        )
        if not file_path:
            return
        self.transcribe_file_path = Path(file_path)
        self.transcribe_file_label.setText(str(self.transcribe_file_path))
        self.transcribe_btn.setEnabled(True)
        save_settings({**load_settings(), "last_directory": str(self.transcribe_file_path.parent)})

    def _run_transcribe_file(self):
        T = TRANSLATIONS[self.current_lang]
        if not self.transcribe_file_path or not self.transcribe_file_path.exists():
            QMessageBox.warning(self, T["error_title"], T["transcribe_no_file"])
            return
        lang_data = self.transcribe_lang_combo.currentData()
        lang_arg = "auto" if lang_data is None else lang_data
        model_index = self.transcribe_model_combo.currentIndex()

        self.transcribe_output_temp_path = Path(tempfile.mkstemp(suffix=".txt")[1])
        try:
            proc = QProcess(self)
            proc.setProgram(sys.executable)
            proc.setArguments([
                "-m", "whatsapp_archive.transcribe_cli",
                "--file", str(self.transcribe_file_path),
                "--output", str(self.transcribe_output_temp_path),
                "--language", lang_arg,
                "--model-index", str(model_index),
            ])
            proc.finished.connect(self._on_transcribe_process_finished)
            proc.errorOccurred.connect(self._on_transcribe_process_error)
            proc.start()
        except Exception as e:
            if self.transcribe_output_temp_path and self.transcribe_output_temp_path.exists():
                try:
                    self.transcribe_output_temp_path.unlink()
                except OSError:
                    pass
            self.transcribe_output_temp_path = None
            QMessageBox.critical(self, T["error_title"], str(e))
            return

        self.transcribe_process = proc
        self.transcribe_btn.setEnabled(False)
        self.transcribe_stop_btn.show()
        self.transcribe_stop_btn.setEnabled(True)
        self.transcribe_status_label.setText(T["transcribe_status_running"])

    def _request_transcribe_stop(self):
        T = TRANSLATIONS[self.current_lang]
        if self.transcribe_process and self.transcribe_process.state() != QProcess.ProcessState.NotRunning:
            self.transcribe_process.terminate()
            self.transcribe_stop_btn.setEnabled(False)
            self.transcribe_stop_btn.setText(T["stop_btn_stopping"])

    @Slot(int, int)
    def _on_transcribe_process_finished(self, exit_code: int, _exit_status: int):
        T = TRANSLATIONS[self.current_lang]
        proc = self.transcribe_process
        out_path = self.transcribe_output_temp_path
        self.transcribe_process = None
        self.transcribe_output_temp_path = None

        self.transcribe_btn.setEnabled(True)
        self.transcribe_stop_btn.hide()
        self.transcribe_stop_btn.setEnabled(True)
        self.transcribe_stop_btn.setText(T["stop_btn"])
        self.transcribe_status_label.setText(T["transcribe_status_idle"])

        if proc:
            proc.deleteLater()

        if not out_path or not out_path.exists():
            if exit_code != 0:
                self.transcribe_output.setPlainText(
                    T["status_stopped"] if exit_code != 0 else ""
                )
            return
        try:
            text = out_path.read_text(encoding="utf-8")
        except Exception as e:
            self.transcribe_output.setPlainText(f"Error reading result: {e}")
            try:
                out_path.unlink()
            except OSError:
                pass
            return
        try:
            out_path.unlink()
        except OSError:
            pass

        if text.startswith("ERROR: "):
            err_msg = text[7:].strip()
            self.transcribe_output.setPlainText(f"Error: {err_msg}")
            if exit_code != 0 and "error_stopped" not in err_msg.lower():
                QMessageBox.critical(self, T["error_title"], err_msg)
        else:
            self.transcribe_output.setPlainText(text)

    @Slot(int)
    def _on_transcribe_process_error(self, err):
        T = TRANSLATIONS[self.current_lang]
        out_path = self.transcribe_output_temp_path
        self.transcribe_process = None
        self.transcribe_output_temp_path = None
        self.transcribe_btn.setEnabled(True)
        self.transcribe_stop_btn.hide()
        self.transcribe_stop_btn.setEnabled(True)
        self.transcribe_stop_btn.setText(T["stop_btn"])
        self.transcribe_status_label.setText(T["transcribe_status_idle"])
        if out_path and out_path.exists():
            try:
                out_path.unlink()
            except OSError:
                pass
        msg = str(err) if err else "Process error"
        self.transcribe_output.setPlainText(f"Error: {msg}")
        QMessageBox.critical(self, T["error_title"], msg)

    def _copy_transcription(self):
        T = TRANSLATIONS[self.current_lang]
        text = self.transcribe_output.toPlainText()
        if text:
            cb = QApplication.clipboard()
            if cb:
                cb.setText(text)
            QMessageBox.information(self, "", T["transcribe_copied"])

    def _save_transcription_txt(self):
        T = TRANSLATIONS[self.current_lang]
        text = self.transcribe_output.toPlainText()
        s = load_settings()
        start_dir = s.get("last_directory", "") or str(Path.home())
        default_name = (self.transcribe_file_path.stem + "_transcription.txt") if self.transcribe_file_path else "transcription.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self, T["transcribe_save_title"], str(Path(start_dir) / default_name), T["transcribe_save_filter"]
        )
        if not file_path:
            return
        try:
            Path(file_path).write_text(text, encoding="utf-8")
            QMessageBox.information(self, "", T["transcribe_saved"].format(path=file_path))
        except Exception as e:
            QMessageBox.critical(self, T["error_title"], str(e))

    @Slot()
    def run_conversion(self):
        T = TRANSLATIONS[self.current_lang]
        if not self.chat_file_path:
            QMessageBox.warning(self, T["error_title"], T["error_missing_file"])
            return
        default_save_path = str(self.chat_file_path.parent / f"{self.chat_file_path.stem}_archive.html")
        out_file, _ = QFileDialog.getSaveFileName(self, T["save_html_title"], default_save_path, T["save_html_filter"])
        if not out_file:
            return
        out_path = Path(out_file)
        title = self.title_edit.text()
        transcribe_audio = self.transcribe_checkbox.isChecked()
        encrypt_media = self.encrypt_checkbox.isChecked()

        self.worker_thread = QThread()
        whisper_index = self.whisper_model_combo.currentIndex()
        timezone_str = self.timezone_combo.currentData() or "America/New_York"
        date_from = None
        date_to = None
        if self.filter_date_check.isChecked():
            date_from = self.date_from.date().toPython()
            date_to = self.date_to.date().toPython()
        self.worker = ChatWorker(
            self.chat_file_path,
            out_path,
            title,
            transcribe_audio,
            encrypt_media,
            self.current_lang,
            whisper_index,
            timezone_str,
            date_from,
            date_to,
        )
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.progress_updated.connect(self.on_progress)
        self.worker.status_updated.connect(self.on_status)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.run_btn.setEnabled(False)
        self.select_chat_btn.setEnabled(False)
        self.stop_btn.show()
        self.stop_btn.setEnabled(True)
        self.stop_btn.setText(T["stop_btn"])
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        self.worker_thread.start()

    @Slot(int, int)
    def on_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    @Slot(str, dict)
    def on_status(self, key, format_dict):
        T = TRANSLATIONS[self.current_lang]
        text = T.get(key, key)
        if format_dict:
            try:
                text = text.format(**format_dict)
            except KeyError:
                pass
        if key.startswith("status_transcribing") or key.startswith("status_encrypting"):
            self.spinner_base_text = text
            if not self.spinner_timer.isActive():
                self.spinner_index = 0
                self.spinner_timer.start(150)
        else:
            if self.spinner_timer.isActive():
                self.spinner_timer.stop()
            self.status_label.setText(text)
            self.spinner_base_text = ""

    @Slot(str, float)
    def on_finished(self, out_file_path, transcription_time):
        T = TRANSLATIONS[self.current_lang]
        if self.spinner_timer.isActive():
            self.spinner_timer.stop()
        self._reset_buttons()
        self.progress_bar.setValue(self.progress_bar.maximum())
        if self.encrypt_checkbox.isChecked():
            msg = T["finish_msg_encrypt"].format(file=out_file_path, folder=f"{Path(out_file_path).stem}_media")
            QMessageBox.information(self, T["finish_title"], msg)
        else:
            QMessageBox.information(self, T["finish_title"], T["finish_msg"].format(file=out_file_path))
        if transcription_time > 0:
            self.status_label.setText(T["status_done_time"].format(time=transcription_time))
        else:
            self.status_label.setText(T["status_done_no_time"])

    @Slot(str)
    def on_error(self, error_key):
        T = TRANSLATIONS[self.current_lang]
        if self.spinner_timer.isActive():
            self.spinner_timer.stop()
        self._reset_buttons()
        self.progress_bar.setValue(0)
        error_msg = T.get(error_key, error_key)
        if error_key == "error_stopped":
            self.status_label.setText(T["status_stopped"])
        else:
            self.status_label.setText(f"{T['error_title']}: {error_msg}")
            QMessageBox.critical(self, T["error_title"], f"{T['error_generic']}\n{error_msg}")


def main():
    setup_logging()
    app = QApplication(sys.argv)
    app.setStyleSheet(LIGHT_STYLE)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec())

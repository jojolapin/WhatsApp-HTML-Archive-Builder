"""Background worker for chat loading, Whisper transcription, and HTML building."""
import sys
from pathlib import Path

import whisper
from PySide6.QtCore import QObject, Signal, Slot
import pytz
from Crypto.Random import get_random_bytes

from whatsapp_archive.config import AUDIO_EXTENSIONS, WHISPER_MODELS
from whatsapp_archive.parser import (
    MEDIA_FILENAME_RE,
    build_media_lookup,
    get_media_path,
    load_chat_messages,
    load_folder_audio,
    parse_message_datetime,
)
from whatsapp_archive.html_builder import build_html


class ChatWorker(QObject):
    progress_updated = Signal(int, int)
    status_updated = Signal(str, dict)
    finished = Signal(str, float)
    error = Signal(str)

    def __init__(
        self,
        chat_file: Path,
        out_file: Path,
        title: str,
        transcribe_audio: bool,
        encrypt_media: bool,
        lang: str,
        whisper_model_index: int = -1,
        timezone_str: str = "America/New_York",
        date_from=None,
        date_to=None,
    ):
        super().__init__()
        self.chat_file = chat_file
        self.out_file = out_file
        self.title = title
        self.transcribe_audio = transcribe_audio
        self.encrypt_media = encrypt_media
        self.lang = lang
        self.whisper_model_index = whisper_model_index
        self.timezone_str = timezone_str
        self.date_from = date_from  # datetime.date or None
        self.date_to = date_to
        self.model = None
        self.stop_requested = False
        self.total_transcription_time = 0.0

    @Slot()
    def request_stop(self):
        self.stop_requested = True

    @Slot()
    def run(self):
        import logging
        logger = logging.getLogger(__name__)
        try:
            self.model = None
            self.total_transcription_time = 0.0
            encryption_key_hex = None

            if self.encrypt_media:
                self.transcribe_audio = True

            if self.transcribe_audio:
                self.status_updated.emit("status_looking_local_model", {})

                if getattr(sys, "frozen", False):
                    bundle_dir = Path(sys.executable).parent
                else:
                    bundle_dir = Path(__file__).resolve().parent.parent.parent

                idx = self.whisper_model_index
                if idx < 0 or idx >= len(WHISPER_MODELS):
                    idx = len(WHISPER_MODELS) - 1
                _display_name, load_name, local_file = WHISPER_MODELS[idx]
                model_file = (bundle_dir / local_file) if local_file else None
                if model_file and model_file.exists():
                    self.status_updated.emit("status_found_local_model", {"model_name": model_file.name})
                    self.model = whisper.load_model(str(model_file))
                else:
                    self.status_updated.emit("status_downloading_model", {})
                    self.model = whisper.load_model(load_name)
            else:
                self.status_updated.emit("status_skipping_model", {})

            if self.stop_requested:
                self.error.emit("error_stopped")
                return

            out_html_path = Path(self.out_file)
            media_output_folder = None
            if self.encrypt_media:
                encryption_key_bytes = get_random_bytes(16)
                encryption_key_hex = encryption_key_bytes.hex()
                media_output_folder = out_html_path.parent / (out_html_path.stem + "_media")
                media_output_folder.mkdir(exist_ok=True)
                self.status_updated.emit("status_creating_media_folder", {"folder_name": media_output_folder.name})

            self.status_updated.emit("status_loading_chat", {})
            messages = load_chat_messages(self.chat_file)

            chat_file_names = set()
            for msg in messages:
                msg_content = msg.get("msg", "")
                mf = MEDIA_FILENAME_RE.search(msg_content) or MEDIA_FILENAME_RE.fullmatch(msg_content.strip())
                if mf:
                    chat_file_names.add(mf.group("fname"))

            local_tz = pytz.timezone(self.timezone_str)
            for msg in messages:
                msg["datetime_obj"] = parse_message_datetime(msg, local_tz=local_tz)
            parseable_messages = [m for m in messages if m["datetime_obj"]]

            media_root = self.chat_file.parent
            self.status_updated.emit("status_scanning_audio", {})
            media_lookup = build_media_lookup(media_root)

            all_folder_audio = load_folder_audio(media_root, local_tz=local_tz)

            external_audios = []
            for audio_msg in all_folder_audio:
                if audio_msg["msg"] not in chat_file_names:
                    audio_msg["is_external_audio"] = True
                    external_audios.append(audio_msg)

            self.status_updated.emit("status_found_external", {"count": len(external_audios)})

            all_messages = parseable_messages + external_audios
            if self.date_from is not None:
                all_messages = [m for m in all_messages if m["datetime_obj"].date() >= self.date_from]
            if self.date_to is not None:
                all_messages = [m for m in all_messages if m["datetime_obj"].date() <= self.date_to]
            self.status_updated.emit("status_sorting", {"count": len(all_messages)})
            all_messages.sort(key=lambda m: m["datetime_obj"])

            if not all_messages:
                self.error.emit("status_no_messages")
                return

            audio_files_to_transcribe = 0
            if self.transcribe_audio and self.model:
                self.status_updated.emit("status_counting_audio", {})
                cache_dir = media_root / "_transcriptions_cache"

                for m in all_messages:
                    if self.stop_requested:
                        self.error.emit("error_stopped")
                        return
                    fn = None
                    is_external = m.get("is_external_audio", False)
                    msg_content = m.get("msg", "")
                    if is_external:
                        fn = msg_content
                    else:
                        mf = MEDIA_FILENAME_RE.search(msg_content) or MEDIA_FILENAME_RE.fullmatch(msg_content.strip())
                        if mf:
                            fn = mf.group("fname")
                    if fn and fn.lower().endswith(AUDIO_EXTENSIONS):
                        abs_match = get_media_path(media_lookup, fn)
                        if abs_match:
                            cache_file = cache_dir / (abs_match.stem + ".json")
                            if not cache_file.exists():
                                audio_files_to_transcribe += 1

            if self.stop_requested:
                self.error.emit("error_stopped")
                return

            self.status_updated.emit("status_building_html", {})
            build_html(
                all_messages,
                media_root,
                out_html_path,
                self.title,
                self.model,
                self,
                self.transcribe_audio,
                audio_files_to_transcribe,
                encryption_key_hex,
                media_output_folder,
                self.lang,
                media_lookup,
            )

            if self.stop_requested:
                self.error.emit("error_stopped")
                return

            self.finished.emit(str(self.out_file), self.total_transcription_time)

        except Exception as e:
            logger.exception("Worker run failed: %s", e)
            self.error.emit(str(e))

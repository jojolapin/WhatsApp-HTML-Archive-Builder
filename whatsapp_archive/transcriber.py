"""Whisper model loading, transcription, and cache handling."""
import json
import time
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from whatsapp_archive.gui.worker import ChatWorker


def transcribe_audio_file(
    model: Any,
    audio_path: Path,
    cache_dir: Path,
    worker: "ChatWorker",
    current_count: int,
    total_count: int,
) -> str:
    """Transcribe an audio file using Whisper. Uses JSON cache in cache_dir. Returns text or error string."""
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / (audio_path.stem + ".json")
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)["text"]
        except Exception:
            pass
    try:
        worker.status_updated.emit(
            "status_transcribing",
            {"current": current_count, "total": total_count, "filename": audio_path.name},
        )
        start_time = time.perf_counter()
        result = model.transcribe(str(audio_path))
        end_time = time.perf_counter()
        worker.total_transcription_time += end_time - start_time
        text = result.get("text", "").strip()
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"text": text}, f, ensure_ascii=False, indent=2)
        return text
    except Exception as e:
        return f"Transcription failed: {e}"

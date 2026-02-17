"""
Standalone CLI to transcribe one audio/video file with Whisper.
Runs in a separate process to avoid Qt/PyTorch thread conflicts (e.g. 0xC0000409 on Windows).
Usage: python -m whatsapp_archive.transcribe_cli --file PATH --output OUT.txt [--language en|fr|auto] [--model-index N]
"""
import argparse
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe one file with Whisper (subprocess helper).")
    parser.add_argument("--file", required=True, type=Path, help="Audio or video file path")
    parser.add_argument("--output", required=True, type=Path, help="Output .txt path for transcription")
    parser.add_argument("--language", default="auto", choices=("en", "fr", "auto"), help="Language code or auto")
    parser.add_argument("--model-index", type=int, default=-1, help="Whisper model index (0=tiny .. 4=large)")
    args = parser.parse_args()

    if not args.file.exists():
        args.output.write_text("ERROR: File not found.", encoding="utf-8")
        sys.exit(1)

    try:
        import whisper
        from whatsapp_archive.config import WHISPER_MODELS
    except Exception as e:
        args.output.write_text(f"ERROR: {e}", encoding="utf-8")
        sys.exit(1)

    if getattr(sys, "frozen", False):
        bundle_dir = Path(sys.executable).parent
    else:
        bundle_dir = Path(__file__).resolve().parent.parent

    idx = args.model_index
    if idx < 0 or idx >= len(WHISPER_MODELS):
        idx = len(WHISPER_MODELS) - 1
    _display_name, load_name, local_file = WHISPER_MODELS[idx]
    model_file = (bundle_dir / local_file) if local_file else None

    try:
        if model_file and model_file.exists():
            model = whisper.load_model(str(model_file))
        else:
            model = whisper.load_model(load_name)
    except Exception as e:
        args.output.write_text(f"ERROR: {e}", encoding="utf-8")
        sys.exit(1)

    lang = None if args.language == "auto" else args.language
    try:
        result = model.transcribe(str(args.file), language=lang)
        text = (result.get("text") or "").strip()
        args.output.write_text(text, encoding="utf-8")
    except Exception as e:
        args.output.write_text(f"ERROR: {e}", encoding="utf-8")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

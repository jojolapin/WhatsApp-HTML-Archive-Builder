"""Chat file parsing, regex patterns, message loading, and media lookup."""
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pytz

from whatsapp_archive.config import DEFAULT_TIMEZONE

# Regex patterns for WhatsApp chat format
DT_PATTERNS = [
    r'^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s(?P<time>\d{1,2}:\d{2}\s?(AM|PM))\s-\s(?P<name>[^:]+):\s(?P<msg>.*)$',
    r'^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s(?P<time>\d{1,2}:\d{2})\s-\s(?P<name>[^:]+):\s(?P<msg>.*)$',
    r'^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s(?P<time>\d{1,2}:\d{2}(?:\s?(AM|PM))?)\s-\s(?P<msg>.*)$',
]
MEDIA_FILENAME_RE = re.compile(
    r'(?P<fname>(?:IMG|VID|PTT|AUD|DOC|VOICE|STK)-\d{4,}-WA\d{4,}\.\w+|\S+\.(?:jpg|jpeg|png|gif|webp|bmp|svg|mp4|mov|mkv|webm|m4a|opus|ogg|mp3|wav|pdf|docx?|xlsx?|pptx?))',
    re.IGNORECASE,
)
MEDIA_OMITTED_RE = re.compile(
    r'(image omitted|photo omitted|video omitted|audio omitted|sticker omitted|media omitted)',
    re.IGNORECASE,
)
EXTERNAL_AUDIO_RE = re.compile(r'^(AUD|PTT)-(\d{8})-WA\d{4,}\.\w+$', re.IGNORECASE)

# Timezone for parsing (user can override via settings)
LOCAL_TZ = pytz.timezone(DEFAULT_TIMEZONE)
UTC_TZ = pytz.utc


def try_parse_line(line: str) -> Optional[dict[str, Any]]:
    """Try to parse a single chat line. Returns dict with date, time, name, msg or None."""
    line = line.rstrip("\r\n")
    for pat in DT_PATTERNS:
        m = re.match(pat, line)
        if m:
            gd = m.groupdict()
            return {
                "date": gd.get("date", ""),
                "time": gd.get("time", ""),
                "name": (gd.get("name") or "").strip() or None,
                "msg": gd.get("msg", ""),
            }
    return None


def load_chat_messages(chat_txt: Path) -> list[dict[str, Any]]:
    """Load and parse a WhatsApp _chat.txt file. Continuation lines are appended to previous message."""
    msgs = []
    with open(chat_txt, "r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            parsed = try_parse_line(raw)
            if parsed is None:
                if msgs:
                    msgs[-1]["msg"] += "\n" + raw.strip("\r\n")
                else:
                    msgs.append({"date": "", "time": "", "name": None, "msg": raw.strip()})
            else:
                msgs.append(parsed)
    return msgs


def load_folder_audio(media_root: Path, local_tz: Optional[Any] = None) -> list[dict[str, Any]]:
    """Scan media folder for external audio files (AUD-YYYYMMDD-WA*.ext). Returns list of message-like dicts."""
    tz = local_tz or LOCAL_TZ
    folder_audio_messages = []
    if not media_root.is_dir():
        return folder_audio_messages

    for item in media_root.iterdir():
        if item.is_file():
            m = EXTERNAL_AUDIO_RE.match(item.name)
            if m:
                date_str = m.group(2)
                try:
                    file_datetime = datetime.strptime(date_str, "%Y%m%d")
                    local_dt = tz.localize(file_datetime)
                    folder_audio_messages.append({
                        "datetime_obj": local_dt,
                        "date": local_dt.strftime("%m/%d/%y"),
                        "time": local_dt.strftime("%I:%M %p"),
                        "name": "External RECORDED Audio",
                        "msg": item.name,
                        "is_external_audio": False,
                    })
                except ValueError:
                    pass  # logged in legacy single-file if needed
    return folder_audio_messages


def parse_message_datetime(msg: dict[str, Any], local_tz: Optional[Any] = None) -> Optional[Any]:
    """Parse message date/time strings into a timezone-aware datetime. Returns None if unparseable."""
    tz = local_tz or LOCAL_TZ
    if msg.get("is_external_audio"):
        return msg.get("datetime_obj")

    date_str = msg.get("date")
    time_str = msg.get("time")
    if not date_str or not time_str:
        return None

    formats_to_try = [
        "%m/%d/%y, %I:%M %p",
        "%m/%d/%Y, %I:%M %p",
        "%m/%d/%y, %H:%M",
        "%m/%d/%Y, %H:%M",
    ]
    datetime_str = f"{date_str}, {time_str}"
    for fmt in formats_to_try:
        try:
            naive_dt = datetime.strptime(datetime_str, fmt)
            return tz.localize(naive_dt)
        except ValueError:
            continue
    return None


def build_media_lookup(media_root: Path) -> dict[str, Path]:
    """Build a single {lowercase_filename: Path} map with one os.walk. Use for O(1) lookups."""
    import os
    lookup = {}
    if not media_root.is_dir():
        return lookup
    for root, _, files in os.walk(media_root):
        for f in files:
            lookup[f.lower()] = Path(root) / f
    return lookup


def get_media_path(media_lookup: dict[str, Path], filename: str) -> Optional[Path]:
    """Resolve media file path from pre-built lookup (case-insensitive). Returns Path or None."""
    if not filename:
        return None
    return media_lookup.get(filename.lower())

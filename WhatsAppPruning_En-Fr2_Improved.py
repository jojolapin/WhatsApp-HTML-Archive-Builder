# whatsapp_chat_gui_pyside6_whisper_v2.0.1.py
import html
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import whisper

# --- NEW: Added pytz for timezone conversion ---
try:
    import pytz
except ImportError:
    print("Error: 'pytz' library not found.")
    print("Please install it by running: pip install pytz")
    sys.exit(1)

try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
except ImportError:
    print("Error: 'pycryptodome' library not found.")
    print("Please install it by running: pip install pycryptodome")
    sys.exit(1)
# --- END NEW ---

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QProgressBar, QFileDialog, QMessageBox, QGroupBox, QCheckBox,
    QTabWidget, QTextEdit
)
from PySide6.QtCore import QThread, QObject, Signal, Slot, Qt, QTimer

# ---------- TRANSLATION DICTIONARY (Updated) ----------
TRANSLATIONS = {
    "en": {
        "window_title": "WhatsApp Chat to HTML Converter – Whisper Edition",
        "tab_converter": "Converter",
        "tab_how_to": "How To Use",

        "config_group": "Configuration",
        "title_label": "Archive Title:",
        "transcribe_label": "Transcribe Audio Files (can be slow)",
        "encrypt_label": "Encrypt media for sharing (Slower, creates new folder)",
        "select_chat_btn": "1. Select Chat File (_chat.txt)",
        "chat_file_label": "No chat file selected.",
        "media_folder_label": "Media folder will be inferred from chat file location.",
        "conv_group": "Conversion",
        "run_btn": "2. Build HTML Archive",
        "stop_btn": "Stop Process",
        "stop_btn_stopping": "Stopping...",
        "status_idle": "Idle. Select a chat file to begin.",
        "theme_btn_dark": "Toggle Dark Mode",
        "theme_btn_light": "Toggle Light Mode",
        "lang_btn_fr": "Passer au Français (FR)",
        "lang_btn_en": "Switch to English (EN)",

        "select_chat_title": "Select WhatsApp Chat File",
        "select_chat_filter": "Text files (*.txt)",
        "save_html_title": "Save HTML Archive As...",
        "save_html_filter": "HTML files (*.html)",

        "error_title": "Error",
        "error_generic": "An error occurred:",
        "error_stopped": "Process stopped by user.",
        "error_missing_file": "Please select a chat file first.",

        "finish_title": "Conversion Complete",
        "finish_msg": "Successfully created HTML archive at:\n{file}",
        "finish_msg_encrypt": "Successfully created encrypted archive!\n\nRemember to .zip BOTH the file:\n{file}\nAND the folder:\n{folder}",

        "status_looking_local_model": "Looking for local Whisper model...",
        "status_found_local_model": "Found local model: {model_name}. Loading...",
        "status_downloading_model": "Local model 'large-v3.pt' not found. Downloading 'large' model...",
        "status_skipping_model": "Skipping Whisper model load.",
        "status_creating_media_folder": "Creating encrypted media folder: {folder_name}",
        "status_loading_chat": "Loading chat messages...",
        "status_scanning_audio": "Scanning folder for all audio files...",
        "status_found_external": "Found {count} external audio files.",
        "status_sorting": "Sorting {count} total messages...",
        "status_no_messages": "No messages or audio files could be loaded.",
        "status_counting_audio": "Counting audio files to transcribe...",
        "status_building_html": "Building HTML...",
        "status_transcribing": "Transcribing {current}/{total}: {filename}...",
        "status_encrypting": "Encrypting {filename}...",
        "status_processing": "Processing messages...",
        "status_stop_requested": "Stop requested, finishing current file...",
        "status_done_time": "Done! Total transcription time: {time:.2f} seconds.",
        "status_done_no_time": "Done! (No new transcriptions were needed).",
        "status_stopped": "Process stopped by user.",

        # --- HTML Translations ---
        "html_select_all": "Select all",
        "html_clear": "Clear",
        "html_invert": "Invert",
        "html_delete_selected": "Delete selected",
        "html_download_pruned": "Download Pruned HTML",
        "html_theme_dark": "🌙 Dark Theme",
        "html_theme_light": "☀️ Light Theme",
        "html_theme_vibrant": "🎨 Vibrant Theme",
        "html_search_placeholder": "Search messages…",
        "html_footer": "Rotate images, switch theme, and view transcriptions. No internet required.",
        "html_external_audio_name": "External RECORDED Audio",
        "html_show_transcription": "🎙️ Show Transcription",
        "html_transcribe_in_browser": "🎙️ Transcribe Audio (in browser)",
        # --- NEW HTML CONTROLS ---
        "html_save_states": "Save States",
        "html_reset_states": "Reset States",
        "html_states_saved": "Checkbox states saved!",
        "html_states_reset": "Checkbox states reset!",

        # --- How To Use Text (HTML) ---
        "how_to_use_content": """
            <h2>Welcome! Here's how to use this tool.</h2>

            <h3>Step 0: Get Your Chat File from WhatsApp</h3>
            <p>This application cannot access your phone. You must export your chat from the WhatsApp mobile app first.</p>
            <ol>
                <li>Open the WhatsApp chat you want to archive.</li>
                <li>Tap the three dots (⋮) in the top-right corner.</li>
                <li>Tap <strong>More</strong> > <strong>Export chat</strong>.</li>
                <li><strong>Crucially:</strong> When prompted "Include media?", choose <strong>WITHOUT MEDIA</strong>. This gives you the <code>_chat.txt</code> file.</li>
                <li>Save this <code>_chat.txt</code> file to your computer.</li>
                <li>Copy all the media (images, audio) from your phone's <code>WhatsApp/Media/</code> folder into the <strong>SAME FOLDER</strong> as your <code>_chat.txt</code> file.</li>
            </ol>

            <h3>Step 1: Configure Your Archive (Converter Tab)</h3>
            <ol>
                <li><strong>Archive Title:</strong> Give your HTML file a custom title.</li>
                <li><strong>Transcribe Audio Files:</strong> Check this to use the powerful local Whisper model to transcribe all audio. This is slow but very accurate and works 100% offline.</li>
                <li><strong>Encrypt media for sharing:</strong> Check this if you want to send the archive to a friend.
                    <ul>
                        <li>This forces transcription (slow) and then encrypts all media into a separate <code>_media</code> folder.</li>
                        <li>The media files will be unreadable. Only the HTML file will have the key to decrypt and play them.</li>
                        <li><strong>To share:</strong> You must <code>.zip</code> the <code>index.html</code> file AND the <code>index_media</code> folder together and use a host like <strong>Netlify</strong>. See the Netlify guide for more.</li>
                    </ul>
                </li>
                <li><strong>Select Chat File:</strong> Click this to select the <code>_chat.txt</code> file you exported in Step 0.</li>
            </ol>

            <h3>Step 2: Build the HTML File</h3>
            <ol>
                <li><strong>Build HTML Archive:</strong> Click this to start. It will ask you where to save the final <code>.html</code> file.</li>
                <li><strong>Stop Process:</strong> This button appears during a build. Click it to gracefully stop the process after it finishes its current file.</li>
                <li><strong>Status:</strong> Watch this label! It will tell you what the app is doing, including a countdown for transcriptions and a timer for the total work.</li>
            </ol>

            <h3>Using the HTML File</h3>
            <ol>
                <li><strong>Message Numbering:</strong> All visible messages are numbered sequentially. This numbering updates automatically if you filter or delete messages.</li>
                <li><strong>Priority Markers:</strong> You can click the small marker in the top-right of a message to cycle its priority (Red, Amber, Orange, White, None). This state is saved to your browser automatically.</li>
                <li><strong>Checkbox Controls:</strong> You can tick checkboxes next to messages.
                    <ul>
                        <li><strong>Save States:</strong> Click this to save the state of all checkboxes to your browser's local storage.</li>
                        <li><strong>Reset States:</strong> Click this to clear all saved checkbox states and uncheck all boxes.</li>
                        <li>Your saved states are loaded automatically every time you open the HTML file.</li>
                    </ul>
                </li>
                 <li><strong>Download Pruned HTML:</strong> This "Save" action now also bakes in the current message numbers and priority marker colors into the new HTML file.</li>
            </ol>
        """
    },
    "fr": {
        "window_title": "Convertisseur WhatsApp vers HTML – Édition Whisper",
        "tab_converter": "Convertisseur",
        "tab_how_to": "Mode d'emploi",

        "config_group": "Configuration",
        "title_label": "Titre de l'archive :",
        "transcribe_label": "Transcrire les fichiers audio (peut être lent)",
        "encrypt_label": "Crypter les médias pour le partage (Plus lent, crée un dossier)",
        "select_chat_btn": "1. Sélectionner le fichier de chat (_chat.txt)",
        "chat_file_label": "Aucun fichier de chat sélectionné.",
        "media_folder_label": "Le dossier multimédia sera déduit de l'emplacement du fichier de chat.",
        "conv_group": "Conversion",
        "run_btn": "2. Créer l'archive HTML",
        "stop_btn": "Arrêter le processus",
        "stop_btn_stopping": "Arrêt en cours...",
        "status_idle": "Prêt. Sélectionnez un fichier de chat pour commencer.",
        "theme_btn_dark": "Passer au mode Sombre",
        "theme_btn_light": "Passer au mode Clair",
        "lang_btn_fr": "Passer au Français (FR)",
        "lang_btn_en": "Switch to English (EN)",

        "select_chat_title": "Sélectionner le fichier de chat WhatsApp",
        "select_chat_filter": "Fichiers texte (*.txt)",
        "save_html_title": "Enregistrer l'archive HTML sous...",
        "save_html_filter": "Fichiers HTML (*.html)",

        "error_title": "Erreur",
        "error_generic": "Une erreur est survenue :",
        "error_stopped": "Processus arrêté par l'utilisateur.",
        "error_missing_file": "Veuillez d'abord sélectionner un fichier de chat.",

        "finish_title": "Conversion terminée",
        "finish_msg": "Archive HTML créée avec succès :\n{file}",
        "finish_msg_encrypt": "Archive cryptée créée avec succès !\n\nN'oubliez pas de zipper ENSEMBLE le fichier :\n{file}\nET le dossier :\n{folder}",

        "status_looking_local_model": "Recherche du modèle Whisper local...",
        "status_found_local_model": "Modèle local trouvé : {model_name}. Chargement...",
        "status_downloading_model": "Modèle local 'large-v3.pt' introuvable. Téléchargement du modèle 'large'...",
        "status_skipping_model": "Chargement du modèle Whisper ignoré.",
        "status_creating_media_folder": "Création du dossier média crypté : {folder_name}",
        "status_loading_chat": "Chargement des messages du chat...",
        "status_scanning_audio": "Analyse du dossier pour les fichiers audio...",
        "status_found_external": "Trouvé {count} fichiers audio externes.",
        "status_sorting": "Tri de {count} messages au total...",
        "status_no_messages": "Aucun message ou fichier audio n'a pu être chargé.",
        "status_counting_audio": "Comptage des fichiers audio à transcrire...",
        "status_building_html": "Création du HTML...",
        "status_transcribing": "Transcription {current}/{total} : {filename}...",
        "status_encrypting": "Cryptage de {filename}...",
        "status_processing": "Traitement des messages...",
        "status_stop_requested": "Arrêt demandé, fin du fichier actuel...",
        "status_done_time": "Terminé ! Temps total de transcription : {time:.2f} secondes.",
        "status_done_no_time": "Terminé ! (Aucune nouvelle transcription n'était nécessaire).",
        "status_stopped": "Processus arrêté par l'utilisateur.",

        # --- HTML Translations ---
        "html_select_all": "Tout Sél.",
        "html_clear": "Effacer",
        "html_invert": "Inverser",
        "html_delete_selected": "Suppr. Sél.",
        "html_download_pruned": "Télécharger HTML Nettoyé",
        "html_theme_dark": "🌙 Thème Sombre",
        "html_theme_light": "☀️ Thème Clair",
        "html_theme_vibrant": "🎨 Thème Vibrant",
        "html_search_placeholder": "Rechercher des messages…",
        "html_footer": "Pivotez les images, changez de thème et voyez les transcriptions. Pas d'Internet requis.",
        "html_external_audio_name": "Audio ENREGISTRÉ Externe",
        "html_show_transcription": "🎙️ Afficher la Transcription",
        "html_transcribe_in_browser": "🎙️ Transcrire (dans le navigateur)",
        # --- NEW HTML CONTROLS ---
        "html_save_states": "Sauv. États",
        "html_reset_states": "Réinit. États",
        "html_states_saved": "États des cases cochées enregistrés !",
        "html_states_reset": "États des cases cochées réinitialisés !",

        # --- How To Use Text (HTML) ---
        "how_to_use_content": """
            <h2>Bienvenue ! Voici comment utiliser cet outil.</h2>

            <h3>Étape 0 : Obtenez votre fichier de chat depuis WhatsApp</h3>
            <p>Cette application ne peut pas accéder à votre téléphone. Vous devez d'abord exporter votre discussion depuis l'application mobile WhatsApp.</p>
            <ol>
                <li>Ouvrez la discussion WhatsApp que vous souhaitez archiver.</li>
                <li>Appuyez sur les trois points (⋮) dans le coin supérieur droit.</li>
                <li>Appuyez sur <strong>Plus</strong> > <strong>Exporter la discussion</strong>.</li>
                <li><strong>Très important :</strong> Lorsqu'on vous demande "Inclure les médias ?", choisissez <strong>SANS LES MÉDIAS</strong>. Cela vous donnera le fichier <code>_chat.txt</code>.</li>
                <li>Enregistrez ce fichier <code>_chat.txt</code> sur votre ordinateur.</li>
                <li>Copiez tous les médias (images, audio) du dossier <code>WhatsApp/Media/</code> de votre téléphone dans le <strong>MÊME DOSSIER</strong> que votre fichier <code>_chat.txt</code>.</li>
            </ol>

            <h3>Étape 1 : Configurez votre archive (Onglet Convertisseur)</h3>
            <ol>
                <li><strong>Titre de l'archive :</strong> Donnez un titre personnalisé à votre fichier HTML.</li>
                <li><strong>Transcrire les fichiers audio :</strong> Cochez cette case pour utiliser le puissant modèle Whisper local pour transcrire tout l'audio. C'est lent mais très précis et fonctionne 100% hors ligne.</li>
                <li><strong>Crypter les médias pour le partage :</strong> Cochez cette case si vous souhaitez envoyer l'archive à un ami.
                    <ul>
                        <li>Cela force la transcription (lent) puis crypte tous les médias dans un dossier <code>_media</code> séparé.</li>
                        <li>Les fichiers multimédias seront illisibles. Seul le fichier HTML aura la clé pour les décrypter et les lire.</li>
                        <li><strong>Pour partager :</strong> Vous devez zipper <code>index.html</code> ET le dossier <code>index_media</code> ensemble et utiliser un hébergeur comme <strong>Netlify</strong>.</li>
                    </ul>
                </li>
                <li><strong>Sélectionner le fichier de chat :</strong> Cliquez ici pour sélectionner le fichier <code>_chat.txt</code> que vous avez exporté à l'étape 0.</li>
            </ol>

            <h3>Étape 2 : Créez le fichier HTML</h3>
            <ol>
                <li><strong>Créer l'archive HTML :</strong> Cliquez ici pour démarrer. L'application vous demandera où enregistrer le fichier <code>.html</code> final.</li>
                <li><strong>Arrêter le processus :</strong> Ce bouton apparaît lors de la création. Cliquez dessus pour arrêter le processus après la fin du fichier en cours.</li>
                <li><strong>Statut :</strong> Surveillez cette étiquette ! Elle vous indiquera ce que fait l'application, y compris un compte à rebours pour les transcriptions et un chronomètre pour le temps total.</li>
            </ol>

            <h3>Utilisation du Fichier HTML</h3>
            <ol>
                <li><strong>Numérotation des messages :</strong> Tous les messages visibles sont numérotés séquentiellement. Cette numérotation se met à jour automatiquement si vous filtrez ou supprimez des messages.</li>
                <li><strong>Marqueurs de priorité :</strong> Vous pouvez cliquer sur le petit marqueur en haut à droite d'un message pour changer sa priorité (Rouge, Ambre, Orange, Blanc, Aucun). Cet état est sauvegardé automatiquement dans votre navigateur.</li>
                <li><strong>Contrôles des cases :</strong> Vous pouvez cocher les cases à côté des messages.
                    <ul>
                        <li><strong>Sauv. États :</strong> Cliquez pour enregistrer l'état de toutes les cases dans le stockage local de votre navigateur.</li>
                        <li><strong>Réinit. États :</strong> Cliquez pour effacer tous les états de cases sauvegardés et décocher toutes les cases.</li>
                        <li>Vos états sauvegardés sont chargés automatiquement à chaque ouverture du fichier HTML.</li>
                    </ul>
                </li>
                <li><strong>Télécharger HTML Nettoyé :</strong> Cette action "Enregistrer" intègre désormais également les numéros de message actuels et les couleurs des marqueurs de priorité dans le nouveau fichier HTML.</li>
            </ol>
        """
    }
}
# --- END NEW ---

VERSION = "v2.0.1"  # Version not incremented, feature change

# ---------- STYLESHEETS (Unchanged) ----------
DARK_STYLE = """
    QWidget {
        background-color: #2b2b2b;
        color: #f0f0f0;
        font-size: 10pt;
    }
    QGroupBox {
        background-color: #3c3c3c;
        border: 1px solid #555;
        border-radius: 6px;
        margin-top: 1ex;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        left: 10px;
    }
    QLineEdit {
        background-color: #3c3c3c;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 5px;
    }
    QCheckBox {
        padding: 5px;
    }
    QCheckBox::indicator {
        border: 1px solid #777;
        background-color: #3c3c3c;
        border-radius: 3px;
        width: 14px;
        height: 14px;
    }
    QCheckBox::indicator:checked {
        background-color: #0078d4;
        border: 1px solid #0078d4;
    }
    QPushButton {
        background-color: #5a5a5a;
        border: 1px solid #777;
        border-radius: 4px;
        padding: 5px 10px;
    }
    QPushButton:hover {
        background-color: #6a6a6a;
    }
    QPushButton:pressed {
        background-color: #4a4a4a;
    }
    QPushButton:disabled {
        background-color: #444;
        color: #888;
    }
    QProgressBar {
        border: 1px solid #555;
        border-radius: 4px;
        text-align: center;
        background-color: #3c3c3c;
    }
    QProgressBar::chunk {
        background-color: #0078d4;
        border-radius: 3px;
    }
"""

LIGHT_STYLE = """
    QWidget {
        background-color: #f0f0f0;
        color: #000000;
        font-size: 10pt;
    }
    QGroupBox {
        background-color: #ffffff;
        border: 1px solid #ccc;
        border-radius: 6px;
        margin-top: 1ex;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        left: 10px;
    }
    QLineEdit {
        background-color: #ffffff;
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 5px;
    }
    QCheckBox {
        padding: 5px;
    }
    QCheckBox::indicator {
        border: 1px solid #adadad;
        background-color: #ffffff;
        border-radius: 3px;
        width: 14px;
        height: 14px;
    }
    QCheckBox::indicator:checked {
        background-color: #0078d4;
        border: 1px solid #0078d4;
    }
    QPushButton {
        background-color: #e1e1e1;
        border: 1px solid #adadad;
        border-radius: 4px;
        padding: 5px 10px;
    }
    QPushButton:hover {
        background-color: #e5e5e5;
    }
    QPushButton:pressed {
        background-color: #d1d1d1;
    }
    QPushButton:disabled {
        background-color: #dcdcdc;
        color: #999;
    }
    QProgressBar {
        border: 1px solid #ccc;
        border-radius: 4px;
        text-align: center;
        background-color: #ffffff;
    }
    QProgressBar::chunk {
        background-color: #0078d4;
        border-radius: 3px;
    }
"""

# ---------- PATTERNS (Unchanged) ----------
DT_PATTERNS = [
    r'^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s(?P<time>\d{1,2}:\d{2}\s?(AM|PM))\s-\s(?P<name>[^:]+):\s(?P<msg>.*)$',
    r'^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s(?P<time>\d{1,2}:\d{2})\s-\s(?P<name>[^:]+):\s(?P<msg>.*)$',
    r'^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s(?P<time>\d{1,2}:\d{2}(?:\s?(AM|PM))?)\s-\s(?P<msg>.*)$',
]
MEDIA_FILENAME_RE = re.compile(
    r'(?P<fname>(?:IMG|VID|PTT|AUD|DOC|VOICE|STK)-\d{4,}-WA\d{4,}\.\w+|\S+\.(?:jpg|jpeg|png|gif|webp|bmp|svg|mp4|mov|mkv|webm|m4a|opus|ogg|mp3|wav|pdf|docx?|xlsx?|pptx?))',
    re.IGNORECASE)
MEDIA_OMITTED_RE = re.compile(
    r'(image omitted|photo omitted|video omitted|audio omitted|sticker omitted|media omitted)', re.IGNORECASE)
EXTERNAL_AUDIO_RE = re.compile(r'^(AUD|PTT)-(\d{8})-WA\d{4,}\.\w+$', re.IGNORECASE)
AUDIO_EXTENSIONS = ('.mp3', '.m4a', '.ogg', '.opus', '.wav', '.aac')
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg')

# --- NEW: Define Timezones ---
EASTERN_TZ = pytz.timezone('America/New_York')
UTC_TZ = pytz.utc


# ---------- CHAT PARSER (Modified for Timezone) ----------
def try_parse_line(line: str):
    line = line.rstrip("\r\n")
    for pat in DT_PATTERNS:
        m = re.match(pat, line)
        if m:
            gd = m.groupdict()
            return {"date": gd.get("date", ""), "time": gd.get("time", ""),
                    "name": (gd.get("name") or "").strip() or None,
                    "msg": gd.get("msg", "")}
    return None


def load_chat_messages(chat_txt: Path):
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


def load_folder_audio(media_root: Path):
    folder_audio_messages = []
    if not media_root.is_dir():
        return folder_audio_messages

    for item in media_root.iterdir():
        if item.is_file():
            m = EXTERNAL_AUDIO_RE.match(item.name)
            if m:
                date_str = m.group(2)
                try:
                    # Create a naive datetime at midnight
                    file_datetime = datetime.strptime(date_str, '%Y%m%d')
                    # --- NEW: Localize to Eastern timezone ---
                    local_dt = EASTERN_TZ.localize(file_datetime)

                    folder_audio_messages.append({
                        "datetime_obj": local_dt,  # Store the timezone-aware object
                        "date": local_dt.strftime('%m/%d/%y'),
                        "time": local_dt.strftime('%I:%M %p'),  # Will be 12:00 AM
                        "name": "External RECORDED Audio",
                        "msg": item.name,
                        "is_external_audio": False
                    })
                except ValueError:
                    print(f"Could not parse date from filename: {item.name}")
    return folder_audio_messages


def parse_message_datetime(msg):
    # This check is now done in the worker, but we keep it for safety
    if msg.get("is_external_audio"):
        return msg.get("datetime_obj")

    date_str = msg.get("date")
    time_str = msg.get("time")

    if not date_str or not time_str:
        return None

    formats_to_try = [
        '%m/%d/%y, %I:%M %p',
        '%m/%d/%Y, %I:%M %p',
        '%m/%d/%y, %H:%M',
        '%m/%d/%Y, %H:%M',
    ]

    datetime_str = f"{date_str}, {time_str}"

    # --- NEW: Localize the parsed datetime ---
    for fmt in formats_to_try:
        try:
            naive_dt = datetime.strptime(datetime_str, fmt)
            # Localize the naive datetime to Eastern
            local_dt = EASTERN_TZ.localize(naive_dt)
            return local_dt
        except ValueError:
            continue
    # --- END NEW ---

    print(f"Could not parse datetime: {datetime_str}")
    return None


def find_media_case_insensitive(media_root: Path, filename: str):
    target = filename.lower()
    direct = media_root / filename
    if direct.exists(): return direct
    for root, _, files in os.walk(media_root):
        for f in files:
            if f.lower() == target:
                return Path(root) / f
    return None


# Removed color_for_name

# ---------- ENCRYPTION HELPER (Unchanged) ----------
def encrypt_file(input_path: Path, output_path: Path, key_hex: str, worker: 'ChatWorker'):
    try:
        key_bytes = bytes.fromhex(key_hex)
        cipher = AES.new(key_bytes, AES.MODE_GCM)

        with open(input_path, 'rb') as f:
            file_data = f.read()

        ciphertext, tag = cipher.encrypt_and_digest(file_data)

        with open(output_path, 'wb') as f:
            f.write(cipher.nonce)
            f.write(tag)
            f.write(ciphertext)

    except Exception as e:
        print(f"Failed to encrypt {input_path.name}: {e}")
        worker.status_updated.emit("status_encrypting_error", {"filename": input_path.name})


# ---------- WHISPER TRANSCRIPTION (Unchanged) ----------
def transcribe_audio_file(model, audio_path: Path, cache_dir: Path, worker: 'ChatWorker',
                          current_count: int, total_count: int):
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / (audio_path.stem + ".json")
    if cache_file.exists():
        try:
            return json.load(open(cache_file, "r", encoding="utf-8"))["text"]
        except Exception:
            pass
    try:
        worker.status_updated.emit("status_transcribing", {
            "current": current_count,
            "total": total_count,
            "filename": audio_path.name
        })

        start_time = time.perf_counter()
        result = model.transcribe(str(audio_path))
        end_time = time.perf_counter()
        worker.total_transcription_time += (end_time - start_time)

        text = result.get("text", "").strip()
        json.dump({"text": text}, open(cache_file, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        return text
    except Exception as e:
        return f"Transcription failed: {e}"


# ---------- HTML BUILDER (Modified for GMT) ----------
def build_html(messages, media_root: Path, out_html: Path, title: str,
               model, worker: 'ChatWorker', transcribe_audio: bool,
               total_audio_files: int, encryption_key: str,
               media_output_folder: Path, lang: str):
    html_t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    cache_dir = media_root / "_transcriptions_cache"

    # --- MODIFIED: Added CSS for numbering and priority markers ---
    css = r'''
:root{--bg-dark:#0b0c10;--bubble-dark:#1f2833;--text-dark:#eaf0f6;--meta-dark:#aab4bf;
--bg-light:#f8fafc;--bubble-light:#ffffff;--text-light:#111827;--meta-light:#4b5563;
--bg-vibrant:#121212;--text-vibrant:#ffffff;--bubble-vibrant:#1a1a1a;--meta-vibrant:#aaa;}
body{margin:0;font-family:system-ui,Segoe UI,Roboto,Ubuntu,Arial,sans-serif;transition:background .2s,color .2s}
body.theme-dark{background:var(--bg-dark);color:var(--text-dark)}
body.theme-dark .header{background:var(--bg-dark);border-bottom:1px solid var(--bubble-dark)}
body.theme-dark .msg{background:var(--bubble-bg-dark, var(--bubble-dark))}
body.theme-dark .meta{color:var(--meta-dark)}
body.theme-dark .toolbar button,body.theme-dark .toolbar select,body.theme-dark .search input{background:#222;color:#fff;border-color:#555}
body.theme-light{background:var(--bg-light);color:var(--text-light)}
body.theme-light .header{background:var(--bg-light);border-bottom:1px solid #e5e7eb}
body.theme-light .msg{background:var(--bubble-bg-light, var(--bubble-light));box-shadow:0 1px 2px rgba(0,0,0,0.05)}
body.theme-light .meta{color:var(--meta-light)}
body.theme-light .toolbar button,body.theme-light .toolbar select,body.theme-light .search input{background:#fff;color:#333;border-color:#ccc}
body.theme-vibrant{background:var(--bg-vibrant);color:var(--text-vibrant)}
body.theme-vibrant .header{background:var(--bg-vibrant);border-bottom:1px solid #333}
body.theme-vibrant .msg{background:var(--bubble-bg-vibrant, var(--bubble-vibrant))}
body.theme-vibrant .meta{color:var(--meta-vibrant)}
body.theme-vibrant .toolbar button,body.theme-vibrant .toolbar select,body.theme-vibrant .search input{background:#333;color:#fff;border-color:#666}
.header{position:sticky;top:0;padding:10px 16px;font-weight:600;z-index:10}
.toolbar{position:sticky;top:48px;padding:8px 16px;display:flex;gap:8px;flex-wrap:wrap;background:inherit;z-index:9}
.toolbar button,.toolbar select{padding:8px 10px;border:1px solid;border-radius:8px;cursor:pointer}
.search{padding:0 16px 8px;position:sticky;top:100px;background:inherit;z-index:9}
.search input{width:100%;padding:10px;border-radius:8px;border:1px solid;box-sizing:border-box}
.container{max-width:960px;margin:auto;padding:16px}
.msg{display:flex;gap:8px;align-items:flex-start;border-radius:14px;padding:10px 12px;margin:10px 0;line-height:1.35; border-left: 4px solid transparent; position: relative;}
.msg.msg-external{border:2px dashed #3b82f6 !important;background:rgba(59,130,246,0.05) !important}
body.theme-dark .msg.msg-external{background:rgba(59,130,246,0.1) !important}
.msg.msg-external .name { color: #FF8C00; font-weight: bold; }
.meta{font-size:12px;margin-bottom:6px;opacity:.8}
.name{font-weight:600}
.content{white-space:pre-wrap;word-wrap:break-word}
.attach img,.attach video{max-width:100%;height:auto;border-radius:8px;margin-top:8px}
.attach img{transition:transform .2s}
.attach img[data-src-encrypted], .attach audio[data-src-encrypted] {
    opacity: 0.5;
    border: 2px dashed #aaa;
}
.rotate-btn{margin-top:4px;padding:2px 6px;font-size:12px;background:#444;color:#fff;border:none;border-radius:6px;cursor:pointer}
.trans{margin-top:6px;padding:6px;border-left:3px solid #4ade80;background:rgba(0,0,0,0.1);font-size:0.9em}
.trans pre[contenteditable="true"]{outline:1px dashed #999;padding:4px;border-radius:4px}
.trans pre[contenteditable="true"]:focus{outline:2px solid #3b82f6}
.trans pre{white-space:pre-wrap;word-wrap:break-word;margin:0}
.footer{text-align:center;font-size:12px;color:#888;padding:20px}
.transcribe-btn{margin-top:8px;padding:6px 10px;font-size:12px;font-weight:500;background:#3b82f6;color:#fff;border:none;border-radius:6px;cursor:pointer}
.transcribe-btn:disabled{background:#555;cursor:default;opacity:0.8}
body.theme-light .transcribe-btn{background:#2563eb}
body.theme-light .transcribe-btn:disabled{background:#ccc}

/* --- NEW: Numbering and Priority CSS --- */
.msg-number {
    position: absolute;
    top: 6px;
    left: -8px;
    font-size: 10px;
    font-weight: bold;
    background: var(--meta-light);
    color: var(--bg-light);
    border-radius: 50%;
    width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 2px rgba(0,0,0,0.3);
    z-index: 1;
}
body.theme-dark .msg-number {
    background: var(--meta-dark);
    color: var(--bg-dark);
}
.msg-priority-marker {
    position: absolute;
    top: 0px;
    right: 0px;
    width: 24px;
    height: 12px;
    border: 1px solid var(--meta-light);
    border-top: none;
    border-right: none;
    cursor: pointer;
    border-bottom-left-radius: 8px;
    background-clip: padding-box;
}
body.theme-dark .msg-priority-marker {
    border-color: var(--meta-dark);
}
.msg-priority-marker[data-priority="none"] { background-color: transparent; }
.msg-priority-marker[data-priority="red"] { background-color: #ef4444; border-color: #ef4444; }
.msg-priority-marker[data-priority="amber"] { background-color: #f59e0b; border-color: #f59e0b; }
.msg-priority-marker[data-priority="orange"] { background-color: #f97316; border-color: #f97316; }
.msg-priority-marker[data-priority="white"] { background-color: #ffffff; border-color: #999; }
body.theme-dark .msg-priority-marker[data-priority="white"] { background-color: #ffffff; border-color: #fff; }
/* --- End NEW CSS --- */

@media (max-width: 600px){
 body{font-size:15px}
 .container{padding:8px}
 .header{padding:8px 12px}
 .toolbar{padding:8px 12px;gap:6px;position:sticky;top:44px}
 .toolbar button,.toolbar select{padding:6px 8px;font-size:13px}
 .search{padding:0 8px 8px;position:sticky:top:86px}
 .msg{margin:8px 0;padding:8px 10px;gap:6px}
 .msg-number { top: 2px; left: -6px; width: 16px; height: 16px; font-size: 9px; }
 .msg-priority-marker { width: 20px; height: 10px; }
}
'''

    # --- MODIFIED: JS logic updated to fix syntax errors and add new features ---
    js_constants = f'''
const HTML_STATES_SAVED = {json.dumps(html_t["html_states_saved"])};
const HTML_STATES_RESET = {json.dumps(html_t["html_states_reset"])};
const PRIORITIES = ["none", "red", "amber", "orange", "white"];
'''

    js_functions = r'''
let currentTheme='light';
function setTheme(t){
 document.body.classList.remove('theme-dark','theme-light','theme-vibrant');
 document.body.classList.add('theme-'+t);currentTheme=t;
 document.querySelector('.toolbar select').value = t;
}
function rotateImage(id){
 const img=document.getElementById(id);
 const angle=parseInt(img.getAttribute('data-angle')||'0')+90;
 img.style.transform='rotate('+angle+'deg)';
 img.setAttribute('data-angle',angle);
}
function filterMessages(){
 const q=document.getElementById('q').value.toLowerCase();
 document.querySelectorAll('.msg').forEach(c=>{
   const t=c.innerText.toLowerCase();
   c.style.display=t.includes(q)?'':'none';
 });
 updateMessageNumbers(); // <-- Update numbers after filtering
}
function getAllCards(){return Array.from(document.querySelectorAll('.msg'));}
function selectAll(){getAllCards().forEach(c=>c.querySelector('input[type="checkbox"]').checked=true);}
function clearAll(){getAllCards().forEach(c=>c.querySelector('input[type="checkbox"]').checked=false);}
function invertSel(){getAllCards().forEach(c=>{const cb=c.querySelector('input[type="checkbox"]');cb.checked=!cb.checked;});}
function deleteSelected(){
    getAllCards().filter(c=>c.querySelector('input[type="checkbox"]').checked).forEach(c=>c.remove());
    updateMessageNumbers(); // <-- Update numbers after deleting
}
function downloadHTML(){
 // 1. Bake in current numbers and priorities into attributes
 updateMessageNumbers();
 document.querySelectorAll('.msg').forEach(msg => {
    if (window.getComputedStyle(msg).display !== 'none') {
        // Bake in priority
        const marker = msg.querySelector('.msg-priority-marker');
        if (marker) {
            marker.setAttribute('data-priority', marker.dataset.priority);
        }
        // Bake in number
        const numBadge = msg.querySelector('.msg-number');
        if (numBadge) {
            numBadge.setAttribute('data-number', numBadge.textContent);
        }
    }
 });

 // 2. Clone the document
 const clonedDoc = document.cloneNode(true);

 // 3. Clean the clone
 clonedDoc.querySelectorAll('input[type="checkbox"]').forEach(el => el.remove());
 clonedDoc.querySelectorAll('.msg-priority-marker').forEach(el => el.removeAttribute('onclick'));
 const buttonsToRemove = [
   "selectAll()",
   "clearAll()",
   "invertSel()",
   "deleteSelected()",
   "downloadHTML()",
   "saveCheckboxStates()",
   "resetCheckboxStates()"
 ];
 clonedDoc.querySelectorAll('.toolbar button').forEach(btn => {
   const onclick = btn.getAttribute('onclick');
   if (buttonsToRemove.includes(onclick)) {
     btn.remove();
   }
 });

 // 4. Set final baked-in numbers in the clone (and remove from hidden)
 clonedDoc.querySelectorAll('.msg').forEach(msg => {
    const numBadge = msg.querySelector('.msg-number');
    if (numBadge) {
        const num = numBadge.getAttribute('data-number');
        if (num) {
            numBadge.textContent = num;
        } else {
            numBadge.remove(); // Remove badge from hidden messages
        }
        numBadge.removeAttribute('data-number');
    }
 });

 const doctype='<!doctype html>';
 const html=clonedDoc.documentElement.outerHTML;
 const blob=new Blob([doctype+'\n'+html],{type:'text/html'});
 const a=document.createElement('a');
 a.href=URL.createObjectURL(blob);
 const ts=new Date().toISOString().replace(/[:.]/g,'-');
 a.download='chat_pruned_'+ts+'.html';document.body.appendChild(a);a.click();a.remove();
}
function saveEdit(element) {
  if (element.id && window.localStorage) {
    try {
      localStorage.setItem(element.id, element.innerText);
    } catch (e) {
      console.error("LocalStorage save failed:", e);
    }
  }
}
function loadEdits() {
  if (!window.localStorage) return;
  const pres = document.querySelectorAll('pre[contenteditable="true"][id^="transcription-pre-"]');
  pres.forEach(pre => {
    const savedText = localStorage.getItem(pre.id);
    if (savedText !== null) {
      pre.innerText = savedText;
    }
  });
}

/* --- Checkbox Persistence --- */
function saveCheckboxStates() {
    try {
        const states = {};
        document.querySelectorAll('.msg input[type="checkbox"]').forEach(cb => {
            if(cb.id) { states[cb.id] = cb.checked; }
        });
        localStorage.setItem('checkboxStates', JSON.stringify(states));
        alert(HTML_STATES_SAVED);
    } catch (e) {
        console.error("Failed to save checkbox states:", e);
        alert("Error saving states. Browser storage might be full or disabled.");
    }
}
function loadCheckboxStates() {
    try {
        const states = JSON.parse(localStorage.getItem('checkboxStates') || '{}');
        Object.keys(states).forEach(id => {
            const cb = document.getElementById(id);
            if (cb) { cb.checked = states[id]; }
        });
    } catch (e) {
        console.error("Failed to load checkbox states:", e);
    }
}
function resetCheckboxStates() {
    localStorage.removeItem('checkboxStates');
    document.querySelectorAll('.msg input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
    });
    alert(HTML_STATES_RESET);
}
/* --- End Checkbox Persistence --- */

/* --- NEW: Priority Logic --- */
function cyclePriority(event) {
    event.stopPropagation();
    const marker = event.currentTarget;
    const currentPriority = marker.dataset.priority || 'none';
    const currentIndex = PRIORITIES.indexOf(currentPriority);
    const nextIndex = (currentIndex + 1) % PRIORITIES.length;
    marker.dataset.priority = PRIORITIES[nextIndex];
    savePriorities(); // Save to localStorage on change
}
function savePriorities() {
    try {
        const priorities = {};
        document.querySelectorAll('.msg[data-msg-id]').forEach(msg => {
            const id = msg.dataset.msgId;
            const priority = msg.querySelector('.msg-priority-marker').dataset.priority;
            priorities[id] = priority;
        });
        localStorage.setItem('msgPriorities', JSON.stringify(priorities));
    } catch (e) {
        console.error("Failed to save priorities:", e);
    }
}
function loadPriorities() {
    try {
        const priorities = JSON.parse(localStorage.getItem('msgPriorities') || '{}');
        Object.keys(priorities).forEach(id => {
            const msg = document.querySelector(`.msg[data-msg-id="${id}"]`);
            if (msg) {
                const marker = msg.querySelector('.msg-priority-marker');
                if (marker) {
                    marker.dataset.priority = priorities[id] || 'none';
                }
            }
        });
    } catch (e) {
        console.error("Failed to load priorities:", e);
    }
}
/* --- End Priority Logic --- */

/* --- NEW: Numbering Logic --- */
function updateMessageNumbers() {
    let count = 1;
    document.querySelectorAll('.msg').forEach(msg => {
        const numBadge = msg.querySelector('.msg-number');
        if (!numBadge) return; // Safety check

        if (window.getComputedStyle(msg).display !== 'none') {
            numBadge.textContent = count;
            numBadge.style.display = 'flex';
            count++;
        } else {
            numBadge.textContent = '';
            numBadge.style.display = 'none';
        }
    });
}
/* --- End Numbering Logic --- */

document.addEventListener('DOMContentLoaded', () => {
    loadEdits();
    loadCheckboxStates();
    loadPriorities(); // <-- Load priorities
    updateMessageNumbers(); // <-- Run numbering on load

    try {
        const themeSelector = document.querySelector('.toolbar select');
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            setTheme('dark');
        } else {
            setTheme('light');
        }

        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            setTheme(e.matches ? 'dark' : 'light');
        });
    } catch (e) {
        console.error("Error setting preferred color scheme:", e);
    }
});
'''
    # Combine the constants and functions into the final JS block
    js = js_constants + js_functions
    # --- END JS MODIFICATION ---

    # --- MODIFIED: Fixed JS f-string interpolation bug with QUADRUPLE braces ---
    # We must use .format() here because the f-string literal is raw (r''')
    js_whisper_constants = f'''
const HTML_SHOW_TRANSCRIPTION = {json.dumps(html_t["html_show_transcription"])};
'''
    js_whisper_functions = r'''
// In-browser transcription pipeline
let pipelinePromise = null;
const modelName = 'Xenova/whisper-tiny';
const modelRevision = 'v4.0.0-compat';

async function initWhisperTranscription(button, audioSrc) {
    try {
        button.disabled = true;
        button.textContent = 'Loading model (one-time download)...';
        if (!pipelinePromise) {
            const { pipeline } = await import('https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.1');
            pipelinePromise = pipeline('automatic-speech-recognition', modelName, {
                revision: modelRevision,
                progress_callback: (progress) => {
                    const firstButton = document.querySelector('.transcribe-btn[disabled]');
                    if (firstButton) {
                        firstButton.textContent = `Loading model... ${progress.status} (${Math.round(progress.progress)}%)`;
                    }
                }
            });
        }
        const recognizer = await pipelinePromise;
        button.textContent = 'Processing audio...';
        const output = await recognizer(audioSrc, {
            chunk_length_s: 30,
            stride_length_s: 5
        });
        const text = output.text ? output.text.trim() : '(No speech detected)';
        const details = document.createElement('details');
        details.className = 'trans';
        details.open = true;
        const summary = document.createElement('summary');
        summary.textContent = HTML_SHOW_TRANSCRIPTION;
        const pre = document.createElement('pre');
        pre.contentEditable = 'true';
        const placeholderId = button.parentElement.id;
        const preId = placeholderId.replace('transcribe-placeholder-', 'transcription-pre-');
        pre.id = preId;
        pre.setAttribute('oninput', 'saveEdit(this)');
        pre.textContent = text;
        details.appendChild(summary);
        details.appendChild(pre);
        button.parentElement.replaceWith(details);
    } catch (error) {
        console.error('Transcription failed:', error);
        button.textContent = 'Transcription Failed (Check console/internet)';
        button.disabled = false;
    }
}
'''
    js_whisper = js_whisper_constants + js_whisper_functions
    # --- END JS_WHISPER MODIFICATION ---

    js_decrypt = ""
    if encryption_key:
        js_decrypt = r'''
/* --- DECRYPTION LOGIC --- */
(async function() {
    if (!window.ENC_KEY) {
        console.log("No encryption key found.");
        return;
    }

    const hexToBytes = (hex) => {
        const bytes = new Uint8Array(hex.length / 2);
        for (let c = 0; c < hex.length; c += 2) {
            bytes[c / 2] = parseInt(hex.substr(c, 2), 16);
        }
        return bytes;
    };

    let cryptoKey;
    try {
        const keyBytes = hexToBytes(window.ENC_KEY);
        cryptoKey = await window.crypto.subtle.importKey(
            "raw", keyBytes, "AES-GCM", true, ["decrypt"]
        );
    } catch (e) {
        console.error("Failed to import encryption key:", e);
        return;
    }

    const elementsToDecrypt = document.querySelectorAll('[data-src-encrypted]');

    async function decryptMedia(element, url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Failed to fetch: ${url}`);
            }
            const encryptedData = await response.arrayBuffer();

            const nonce = encryptedData.slice(0, 16);
            const tag = encryptedData.slice(16, 32);
            const ciphertext = encryptedData.slice(32);

            const combinedData = new Uint8Array(ciphertext.byteLength + tag.byteLength);
            combinedData.set(new Uint8Array(ciphertext), 0);
            combinedData.set(new Uint8Array(tag), ciphertext.byteLength);

            const decryptedData = await window.crypto.subtle.decrypt(
                { name: "AES-GCM", iv: nonce },
                cryptoKey,
                combinedData
            );

            const blob = new Blob([decryptedData]);
            const objectURL = URL.createObjectURL(blob);
            element.src = objectURL;
            element.style.opacity = 1;
            element.style.border = 'none';
            element.removeAttribute('data-src-encrypted'); 

        } catch (e) {
            console.error("Failed to decrypt:", url, e);
            if (element.tagName === 'IMG') {
                element.alt = "Decryption Failed";
            }
        }
    }

    for (const el of elementsToDecrypt) {
        decryptMedia(el, el.dataset.srcEncrypted);
    }
})();
'''

    # --- MODIFIED: Use light/dark pairs for the two user colors ---
    unique_names_list = sorted(
        list({m.get("name") for m in messages if m.get("name") and m.get("name") != "External RECORDED Audio"}))

    # Define light and dark pairs for the two users
    color_palette = [
        {'light': '#e3f2fd', 'dark': '#0d2a40', 'border': '#a0cff0'},  # User 1 (Blue)
        {'light': '#f3e5f5', 'dark': '#3c2a3f', 'border': '#d6b6da'}  # User 2 (Purple)
    ]

    # Assign a color pair to each name
    colors = {name: color_palette[i % 2] for i, name in enumerate(unique_names_list)}

    # Special color for external audio (will be handled by CSS class)
    colors["External RECORDED Audio"] = {'light': '', 'dark': '', 'border': ''}
    # --- END MODIFICATION ---

    blocks = []
    audio_file_counter = 0

    for i, m in enumerate(messages):
        if worker.stop_requested:
            return

        msg_id = m.get("datetime_obj").strftime('%Y%m%d%H%M%S') + f"-{i}"

        # --- NEW: Create a unique, stable ID for the checkbox ---
        checkbox_id = f"cb-{msg_id}"

        date, time, name, msg = m.get("date", ""), m.get("time", ""), m.get("name"), m.get("msg", "")
        is_external = m.get("is_external_audio", False)

        # --- MODIFIED: Get color pair and set CSS variables ---
        default_pair = {'light': 'var(--bubble-light)', 'dark': 'var(--bubble-dark)', 'border': 'transparent'}
        color_pair = colors.get(name or "", default_pair)

        style_vars = (
            f'--bubble-bg-light: {color_pair["light"]}; '
            f'--bubble-bg-dark: {color_pair["dark"]}; '
            f'--bubble-bg-vibrant: {color_pair["dark"]}; '  # Use dark for vibrant
            f'border-left-color: {color_pair["border"]};'
        )
        # --- END MODIFICATION ---

        media_block = ""
        fn = None

        if is_external:
            fn = msg
            name = html_t["html_external_audio_name"]
            style_vars = ""  # Reset for external, use CSS class
        else:
            mf = MEDIA_FILENAME_RE.search(msg) or MEDIA_FILENAME_RE.fullmatch(msg.strip())
            if mf:
                fn = mf.group("fname")
            elif MEDIA_OMITTED_RE.search(msg):
                fn = None

        if fn:
            abs_match = find_media_case_insensitive(media_root, fn)
            if abs_match:
                esc_fn = html.escape(fn)
                if encryption_key:
                    output_filename = fn + ".aes"
                    output_path = media_output_folder / output_filename
                    rel_path = f"{media_output_folder.name}/{output_filename}"

                    if not output_path.exists():
                        worker.status_updated.emit("status_encrypting", {"filename": fn})
                        encrypt_file(abs_match, output_path, encryption_key, worker)

                    if fn.lower().endswith(IMAGE_EXTENSIONS):
                        img_id = f"img_{msg_id}"
                        media_block = f'''<div class="attach"><img id="{img_id}" data-src-encrypted="{html.escape(rel_path)}" alt="{esc_fn}" loading="lazy">
<button class="rotate-btn" onclick="rotateImage('{img_id}')">↻ Rotate</button></div>'''
                    elif fn.lower().endswith(AUDIO_EXTENSIONS):
                        pre_id = f"transcription-pre-{msg_id}"
                        text = transcribe_audio_file(model, abs_match, cache_dir, worker,
                                                     audio_file_counter, total_audio_files)
                        if worker.stop_requested: return
                        worker.status_updated.emit("status_processing", {})
                        esc_text = html.escape(text)
                        media_block = f'''<div class="attach"><audio controls preload="none" data-src-encrypted="{html.escape(rel_path)}"></audio>
<details class="trans"><summary>{html_t["html_show_transcription"]}</summary><pre id="{pre_id}" contenteditable="true" oninput="saveEdit(this)">{esc_text}</pre></details></div>'''
                    elif fn.lower().endswith(('.mp4', '.mov', '.mkv', '.webm')):
                        media_block = f'''<div class="attach"><video controls preload="none" data-src-encrypted="{html.escape(rel_path)}"></video></div>'''
                    else:
                        media_block = f'''<div class="attach"><a href="{html.escape(rel_path)}" target="_blank">{esc_fn} (Encrypted)</a></div>'''

                else:
                    rel_path = os.path.relpath(abs_match, out_html.parent)
                    esc_rel_path = html.escape(rel_path)

                    if fn.lower().endswith(IMAGE_EXTENSIONS):
                        img_id = f"img_{msg_id}"
                        media_block = f'''<div class="attach"><img id="{img_id}" src="{esc_rel_path}" alt="{esc_fn}" loading="lazy">
<button class="rotate-btn" onclick="rotateImage('{img_id}')">↻ Rotate</button></div>'''
                    elif fn.lower().endswith(AUDIO_EXTENSIONS):
                        pre_id = f"transcription-pre-{msg_id}"
                        if transcribe_audio and model:
                            cache_file = cache_dir / (abs_match.stem + ".json")
                            if not cache_file.exists():
                                audio_file_counter += 1
                            text = transcribe_audio_file(model, abs_match, cache_dir, worker,
                                                         audio_file_counter, total_audio_files)
                            if worker.stop_requested: return
                            worker.status_updated.emit("status_processing", {})
                            esc_text = html.escape(text)
                            media_block = f'''<div class="attach"><audio controls preload="none" src="{esc_rel_path}"></audio>
<details class="trans"><summary>{html_t["html_show_transcription"]}</summary><pre id="{pre_id}" contenteditable="true" oninput="saveEdit(this)">{esc_text}</pre></details></div>'''
                        else:
                            btn_container_id = f"transcribe-placeholder-{msg_id}"
                            media_block = f'''<div class="attach">
    <audio controls preload="none" src="{esc_rel_path}"></audio>
    <div id="{btn_container_id}" class="transcribe-placeholder">
        <button class="transcribe-btn" onclick="initWhisperTranscription(this, '{esc_rel_path}')">{html_t["html_transcribe_in_browser"]}</button>
    </div>
</div>'''
                    elif fn.lower().endswith(('.mp4', '.mov', '.mkv', '.webm')):
                        media_block = f'''<div class="attach"><video controls preload="none" src="{esc_rel_path}"></video></div>'''
                    else:
                        media_block = f'''<div class="attach"><a href="{esc_rel_path}" target="_blank">{esc_fn}</a></div>'''

        # --- NEW: Get timezone-aware datetimes ---
        dt_obj = m.get("datetime_obj")
        date_str = dt_obj.strftime('%m/%d/%y')
        time_str = dt_obj.strftime('%I:%M %p')  # 12-hour format

        gmt_dt = dt_obj.astimezone(UTC_TZ)
        gmt_time_str = gmt_dt.strftime('%H:%M %Z')  # 24-hour format + "GMT"

        meta = f'{html.escape(date_str)} {html.escape(time_str)} (<b>{html.escape(gmt_time_str)}</b>)'
        if name:
            meta = f'<span class="name">{html.escape(name)}</span> · {meta}'
        # --- END NEW ---

        external_class = ' msg-external' if is_external else ''

        if is_external:
            content_block = f'<div class="content" style="font-style: italic;">{html.escape(msg)}</div>'
        else:
            content_block = f'<div class="content">{html.escape(msg)}</div>'

        # --- MODIFIED: Added data-msg-id, number badge, and priority marker ---
        blocks.append(f'''
<div class="msg{external_class}" style="{style_vars}" data-msg-id="{msg_id}">
<input type="checkbox" style="margin-top:4px;" id="{checkbox_id}">
<div style="flex:1">
<div class="msg-number"></div>
<div class="msg-priority-marker" data-priority="none" onclick="cyclePriority(event)"></div>
<div class="meta">{meta}</div>
{content_block}
{media_block}
</div></div>''')
    # --- END MODIFICATION ---

    key_script = f"<script>window.ENC_KEY = '{encryption_key}';</script>" if encryption_key else ""
    decrypt_script = f"<script>{js_decrypt}</script>" if encryption_key else ""

    # --- MODIFIED: Added Save States and Reset States buttons to toolbar ---
    html_doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title><style>{css}</style></head>
<body class="theme-light"><div class="header"><h1>{html.escape(title)}</h1></div>
<div class="toolbar">
<button onclick="selectAll()">{html_t["html_select_all"]}</button>
<button onclick="clearAll()">{html_t["html_clear"]}</button>
<button onclick="invertSel()">{html_t["html_invert"]}</button>
<button onclick="deleteSelected()">{html_t["html_delete_selected"]}</button>
<button onclick="downloadHTML()">{html_t["html_download_pruned"]}</button>
<button onclick="saveCheckboxStates()">{html_t["html_save_states"]}</button>
<button onclick="resetCheckboxStates()">{html_t["html_reset_states"]}</button>
<select onchange="setTheme(this.value)">
<option value="light">{html_t["html_theme_light"]}</option>
<option value="dark">{html_t["html_theme_dark"]}</option>
<option value="vibrant">{html_t["html_theme_vibrant"]}</option>
</select></div>
<div class="search"><input id="q" type="search" placeholder="{html_t["html_search_placeholder"]}" oninput="filterMessages()"></div>
<div class="container">{''.join(blocks)}</div>
<div class="footer">{html_t["html_footer"]}</div>
{key_script}
<script>
{js}
</script>
<script type="module">
{js_whisper}
</script>
{decrypt_script}
</body></html>'''
    out_html.write_text(html_doc, encoding="utf-8")


# ---------- PYSIDE6 WORKER (Modified) ----------
class ChatWorker(QObject):
    progress_updated = Signal(int, int)
    status_updated = Signal(str, dict)
    finished = Signal(str, float)
    error = Signal(str)

    def __init__(self, chat_file: Path, out_file: Path, title: str,
                 transcribe_audio: bool, encrypt_media: bool, lang: str):
        super().__init__()
        self.chat_file = chat_file
        self.out_file = out_file
        self.title = title
        self.transcribe_audio = transcribe_audio
        self.encrypt_media = encrypt_media
        self.lang = lang
        self.model = None
        self.stop_requested = False
        self.total_transcription_time = 0.0

    @Slot()
    def request_stop(self):
        self.stop_requested = True

    @Slot()
    def run(self):
        try:
            self.model = None
            self.total_transcription_time = 0.0
            encryption_key_hex = None

            if self.encrypt_media:
                self.transcribe_audio = True

            if self.transcribe_audio:
                self.status_updated.emit("status_looking_local_model", {})

                if getattr(sys, 'frozen', False):
                    bundle_dir = Path(sys.executable).parent
                else:
                    bundle_dir = Path(__file__).parent

                model_file = bundle_dir / "large-v3.pt"

                if model_file.exists():
                    self.status_updated.emit("status_found_local_model", {"model_name": model_file.name})
                    self.model = whisper.load_model(str(model_file))
                else:
                    self.status_updated.emit("status_downloading_model", {})
                    self.model = whisper.load_model("large")
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

            # --- NEW: Parse all datetimes *after* loading ---
            for msg in messages:
                msg["datetime_obj"] = parse_message_datetime(msg)
            parseable_messages = [m for m in messages if m["datetime_obj"]]

            media_root = self.chat_file.parent
            self.status_updated.emit("status_scanning_audio", {})

            all_folder_audio = load_folder_audio(media_root)

            external_audios = []
            for audio_msg in all_folder_audio:
                if audio_msg["msg"] not in chat_file_names:
                    # Note: datetime_obj was already localized when loaded
                    audio_msg["is_external_audio"] = True
                    external_audios.append(audio_msg)

            self.status_updated.emit("status_found_external", {"count": len(external_audios)})

            all_messages = parseable_messages + external_audios
            self.status_updated.emit("status_sorting", {"count": len(all_messages)})
            # Sort all timezone-aware datetime objects
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
                        if mf: fn = mf.group("fname")

                    if fn and fn.lower().endswith(AUDIO_EXTENSIONS):
                        abs_match = find_media_case_insensitive(media_root, fn)
                        if abs_match:
                            cache_file = cache_dir / (abs_match.stem + ".json")
                            if not cache_file.exists():
                                audio_files_to_transcribe += 1

            if self.stop_requested:
                self.error.emit("error_stopped")
                return

            self.status_updated.emit("status_building_html", {})
            build_html(all_messages, media_root, out_html_path, self.title,
                       self.model, self, self.transcribe_audio,
                       audio_files_to_transcribe, encryption_key_hex,
                       media_output_folder, self.lang)

            if self.stop_requested:
                self.error.emit("error_stopped")
                return

            self.finished.emit(str(self.out_file), self.total_transcription_time)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            self.error.emit(str(e))


# ---------- PYSIDE6 GUI (Unchanged) ----------
class MainWindow(QWidget):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.is_dark_theme = False
        self.current_lang = "en"

        self.setWindowTitle(TRANSLATIONS[self.current_lang]["window_title"])
        self.setGeometry(100, 100, 650, 600)

        self.spinner_timer = QTimer(self)
        self.spinner_chars = ['|', '/', '—', '\\']
        self.spinner_index = 0
        self.spinner_base_text = ""
        self.spinner_timer.timeout.connect(self._update_spinner)

        self.setup_ui()

        self.chat_file_path = None
        self.worker_thread = None
        self.worker = None

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
        self.run_btn.clicked.connect(self.run_conversion)
        self.run_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        self.run_btn.setEnabled(False)
        conv_layout.addWidget(self.run_btn)

        self.stop_btn = QPushButton(T["stop_btn"])
        self.stop_btn.clicked.connect(self.request_stop)
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px;")
        self.stop_btn.hide()
        conv_layout.addWidget(self.stop_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
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

        footer_layout = QHBoxLayout()

        self.lang_button = QPushButton(T["lang_btn_fr"])
        self.lang_button.clicked.connect(self.toggle_language)

        self.theme_button = QPushButton(T["theme_btn_dark"])
        self.theme_button.clicked.connect(self.toggle_theme)

        self.version_label = QLabel(f"JojoLain™ {VERSION}")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        footer_layout.addWidget(self.lang_button)
        footer_layout.addWidget(self.theme_button)
        footer_layout.addStretch()
        footer_layout.addWidget(self.version_label)

        self.main_layout.addLayout(footer_layout)

    @Slot()
    def toggle_language(self):
        if self.current_lang == "en":
            self.current_lang = "fr"
        else:
            self.current_lang = "en"
        self.retranslate_ui()

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

        if self.chat_file_label.text() == TRANSLATIONS["en"]["chat_file_label"] or \
                self.chat_file_label.text() == TRANSLATIONS["fr"]["chat_file_label"]:
            self.chat_file_label.setText(T["chat_file_label"])

        if self.media_folder_label.text() == TRANSLATIONS["en"]["media_folder_label"] or \
                self.media_folder_label.text() == TRANSLATIONS["fr"]["media_folder_label"]:
            self.media_folder_label.setText(T["media_folder_label"])

        self.conv_group.setTitle(T["conv_group"])
        self.run_btn.setText(T["run_btn"])
        self.stop_btn.setText(T["stop_btn"])

        current_status = self.status_label.text().split(" ")[0]
        if current_status == "Idle." or current_status == "Prêt.":
            self.status_label.setText(T["status_idle"])

        self.how_to_text_edit.setHtml(T["how_to_use_content"])

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
            print(f"Spinner error: {e}")
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

    @Slot()
    def select_chat_file(self):
        T = TRANSLATIONS[self.current_lang]
        file_path, _ = QFileDialog.getOpenFileName(
            self, T["select_chat_title"], "", T["select_chat_filter"]
        )

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

    @Slot()
    def run_conversion(self):
        T = TRANSLATIONS[self.current_lang]
        if not self.chat_file_path:
            QMessageBox.warning(self, T["error_title"], T["error_missing_file"])
            return

        default_save_path = str(
            self.chat_file_path.parent / f"{self.chat_file_path.stem}_archive.html"
        )

        out_file, _ = QFileDialog.getSaveFileName(
            self, T["save_html_title"],
            default_save_path,
            T["save_html_filter"]
        )

        if not out_file:
            return

        out_path = Path(out_file)
        title = self.title_edit.text()
        transcribe_audio = self.transcribe_checkbox.isChecked()
        encrypt_media = self.encrypt_checkbox.isChecked()

        self.worker_thread = QThread()
        self.worker = ChatWorker(self.chat_file_path, out_path, title,
                                 transcribe_audio, encrypt_media, self.current_lang)
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
            msg = T["finish_msg_encrypt"].format(
                file=out_file_path,
                folder=f"{Path(out_file_path).stem}_media"
            )
            QMessageBox.information(self, T["finish_title"], msg)
        else:
            QMessageBox.information(self, T["finish_title"],
                                    T["finish_msg"].format(file=out_file_path))

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
    app = QApplication(sys.argv)
    app.setStyleSheet(LIGHT_STYLE)

    window = MainWindow(app)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

# WhatsApp Chat to HTML Converter – Whisper Edition

A desktop application that converts exported WhatsApp chat files (`.txt`) into rich, interactive HTML archives. Features include:

- **Audio transcription** using OpenAI's Whisper model (runs 100% offline)
- **Media encryption** for safe sharing via Netlify or similar hosts
- **Bilingual UI** (English / French)
- **Dark / Light / Vibrant themes** in both the desktop app and generated HTML
- **Message pruning** – select, filter, and download a cleaned HTML archive
- **Priority markers & checkbox states** saved to browser local storage

Built with **PySide6** (Qt for Python) for the desktop GUI.

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/whatsapp-chat-converter.git
cd whatsapp-chat-converter
```

### 2. Create a virtual environment and install dependencies

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the app

```bash
python WhatsAppPruning_En-Fr2_Improved.py
```

---

## PyCharm Setup (Step-by-Step)

> **This section solves the common "missing dependencies" problem** when opening the project in PyCharm.

### Option A: Open an existing clone

1. **File → Open** → select the project folder (the one containing `requirements.txt`)
2. PyCharm will detect the project. Wait for indexing to finish.
3. **Configure the Python interpreter:**
   - Go to **File → Settings → Project → Python Interpreter**
   - Click the gear icon ⚙ → **Add Interpreter → Add Local Interpreter**
   - Choose **Virtualenv Environment → New**
   - Set the base interpreter to your installed Python (3.11+)
   - Location should be `.venv` inside the project folder
   - Click **OK**
4. **Install dependencies:**
   - PyCharm should show a banner: *"Package requirements are not satisfied"* → click **Install requirements**
   - OR open the **Terminal** tab at the bottom and run:
     ```
     pip install -r requirements.txt
     ```
5. **Run the script:**
   - Right-click `WhatsAppPruning_En-Fr2_Improved.py` → **Run**
   - Or use the green ▶ button in the top-right

### Option B: Clone from GitHub directly in PyCharm

1. **File → New Project from Version Control**
2. Paste the GitHub repo URL
3. PyCharm clones the repo and opens it
4. Follow steps 3–5 from Option A above

### Troubleshooting PyCharm

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'whisper'` | Your interpreter is wrong. Go to Settings → Python Interpreter and make sure it points to `.venv` inside this project. Then run `pip install -r requirements.txt`. |
| `pip install` fails for `torch` | Make sure you have Python 3.11+ and a 64-bit OS. On Windows, torch requires 64-bit Python. |
| PyCharm uses system Python instead of `.venv` | In Settings → Python Interpreter, remove the system interpreter and add the `.venv` one as described above. |
| PySide6 not found after install | Close and reopen PyCharm, or click **File → Invalidate Caches → Restart**. |

---

## Dependencies

| Package | Purpose |
|---|---|
| `openai-whisper` | Offline audio transcription (brings PyTorch, NumPy, etc.) |
| `PySide6` | Desktop GUI (Qt 6 for Python) |
| `pycryptodome` | AES encryption for media files |
| `pytz` | Timezone conversion for message timestamps |

See `requirements.txt` for pinned versions.

---

## How It Works

1. Export your WhatsApp chat (without media) to get `_chat.txt`
2. Copy your media files into the same folder
3. Run the app, select the chat file, and configure options
4. Click **Build HTML Archive** to generate the interactive HTML file
5. Open the HTML file in any browser — no server needed

---

## License

Private project — LONAB 2026.

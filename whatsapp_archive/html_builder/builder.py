"""HTML archive builder: generates the full HTML document from messages and options."""
import html
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from whatsapp_archive.config import AUDIO_EXTENSIONS, IMAGE_EXTENSIONS
from whatsapp_archive.encryptor import encrypt_file
from whatsapp_archive.parser import (
    MEDIA_FILENAME_RE,
    MEDIA_OMITTED_RE,
    UTC_TZ,
    get_media_path,
)
from whatsapp_archive.translations import TRANSLATIONS
from whatsapp_archive.transcriber import transcribe_audio_file

if TYPE_CHECKING:
    from whatsapp_archive.gui.worker import ChatWorker


def build_html(messages, media_root: Path, out_html: Path, title: str,
               model, worker: 'ChatWorker', transcribe_audio: bool,
               total_audio_files: int, encryption_key: str,
               media_output_folder: Path, lang: str, media_lookup: dict):
    html_t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    cache_dir = media_root / "_transcriptions_cache"

    from whatsapp_archive.html_builder.css import HTML_CSS
    css = HTML_CSS

    # --- MODIFIED: JS updated to fix syntax errors and add new features ---
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
    total_messages = len(messages)

    for i, m in enumerate(messages):
        if worker.stop_requested:
            return
        worker.progress_updated.emit(i + 1, total_messages)

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
            abs_match = get_media_path(media_lookup, fn)
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



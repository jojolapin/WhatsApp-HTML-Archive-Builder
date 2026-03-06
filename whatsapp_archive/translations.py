"""EN/FR translation dicts for the WhatsApp Archive Builder."""
# pylint: disable=pointless-string-statement

TRANSLATIONS = {
    "en": {
        "window_title": "WhatsApp Chat to HTML Converter – Whisper Edition",
        "tab_converter": "Converter",
        "tab_how_to": "How To Use",
        "tab_transcribe_file": "Transcribe file",

        "transcribe_select_file_btn": "Select audio or video file",
        "transcribe_file_label": "No file chosen.",
        "transcribe_lang_en": "English",
        "transcribe_lang_fr": "French",
        "transcribe_lang_auto": "Auto-detect",
        "transcribe_btn": "Transcribe",
        "transcribe_status_idle": "Select a file and click Transcribe.",
        "transcribe_status_running": "Transcribing… please wait.",
        "transcribe_copy_btn": "Copy to clipboard",
        "transcribe_save_txt_btn": "Save as .txt",
        "transcribe_no_file": "Please select an audio or video file first.",
        "transcribe_save_filter": "Text files (*.txt)",
        "transcribe_save_title": "Save transcription as...",
        "transcribe_saved": "Saved to {path}",
        "transcribe_copied": "Copied to clipboard.",
        "transcribe_whisper_model": "Whisper model:",
        "transcribe_select_filter": "Audio/Video (*.mp3 *.m4a *.wav *.ogg *.opus *.aac *.mp4 *.mkv *.webm *.mov *.m4v);;All files (*.*)",

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
        "status_encrypting_error": "Failed to encrypt {filename}.",
        "status_processing": "Processing messages...",
        "status_stop_requested": "Stop requested, finishing current file...",
        "status_done_time": "Done! Total transcription time: {time:.2f} seconds.",
        "status_done_no_time": "Done! (No new transcriptions were needed).",
        "status_stopped": "Process stopped by user.",

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
        "html_save_states": "Save States",
        "html_reset_states": "Reset States",
        "html_states_saved": "Checkbox states saved!",
        "html_states_reset": "Checkbox states reset!",
        "html_note_placeholder": "Add a note…",
        "html_notes_saved": "Notes saved!",
        "html_message_deleted": "Message {num} — Deleted",
        "html_show_my_interventions": "Show my interventions",
        "html_show_all_msgs": "Show all messages",
        "html_report_pdf": "Report (PDF)",
        "html_report_word": "Report (Word)",
        "html_report_title": "Interventions Report",
        "html_report_subtitle": "— {title} — Generated {date}",
        "html_report_date": "Date",
        "html_report_msg_num": "Message #",
        "html_report_name": "Name",
        "html_report_note": "Note",
        "html_report_priority": "Priority",
        "html_report_selected": "Selected",
        "html_report_content": "Content",
        "html_report_transcription": "Transcription",
        "html_report_message_hidden": "Message hidden",
        "html_report_footer": "Report generated on {date} from HTML archive.",
        "html_report_no_interventions": "No interventions to report (no notes or priority markers).",
        "html_report_priority_red": "Red",
        "html_report_priority_amber": "Amber",
        "html_report_priority_orange": "Orange",
        "html_report_priority_white": "White",

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
        "tab_transcribe_file": "Transcrire un fichier",

        "transcribe_select_file_btn": "Sélectionner un fichier audio ou vidéo",
        "transcribe_file_label": "Aucun fichier choisi.",
        "transcribe_lang_en": "Anglais",
        "transcribe_lang_fr": "Français",
        "transcribe_lang_auto": "Détection automatique",
        "transcribe_btn": "Transcrire",
        "transcribe_status_idle": "Sélectionnez un fichier et cliquez sur Transcrire.",
        "transcribe_status_running": "Transcription en cours… veuillez patienter.",
        "transcribe_copy_btn": "Copier dans le presse-papiers",
        "transcribe_save_txt_btn": "Enregistrer en .txt",
        "transcribe_no_file": "Veuillez d'abord sélectionner un fichier audio ou vidéo.",
        "transcribe_save_filter": "Fichiers texte (*.txt)",
        "transcribe_save_title": "Enregistrer la transcription sous...",
        "transcribe_saved": "Enregistré sous {path}",
        "transcribe_copied": "Copié dans le presse-papiers.",
        "transcribe_whisper_model": "Modèle Whisper :",
        "transcribe_select_filter": "Audio/Vidéo (*.mp3 *.m4a *.wav *.ogg *.opus *.aac *.mp4 *.mkv *.webm *.mov *.m4v);;Tous les fichiers (*.*)",

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
        "status_encrypting_error": "Échec du cryptage de {filename}.",
        "status_processing": "Traitement des messages...",
        "status_stop_requested": "Arrêt demandé, fin du fichier actuel...",
        "status_done_time": "Terminé ! Temps total de transcription : {time:.2f} secondes.",
        "status_done_no_time": "Terminé ! (Aucune nouvelle transcription n'était nécessaire).",
        "status_stopped": "Processus arrêté par l'utilisateur.",

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
        "html_save_states": "Sauv. États",
        "html_reset_states": "Réinit. États",
        "html_states_saved": "États des cases cochées enregistrés !",
        "html_states_reset": "États des cases cochées réinitialisés !",
        "html_note_placeholder": "Ajouter une note…",
        "html_notes_saved": "Notes sauvegardées !",
        "html_message_deleted": "Message {num} — Supprimé",
        "html_show_my_interventions": "Voir mes interventions",
        "html_show_all_msgs": "Voir tous les messages",
        "html_report_pdf": "Rapport (PDF)",
        "html_report_word": "Rapport (Word)",
        "html_report_title": "Rapport des interventions",
        "html_report_subtitle": "— {title} — Généré le {date}",
        "html_report_date": "Date",
        "html_report_msg_num": "N° message",
        "html_report_name": "Nom",
        "html_report_note": "Note",
        "html_report_priority": "Priorité",
        "html_report_selected": "Sélectionné",
        "html_report_content": "Contenu",
        "html_report_transcription": "Transcription",
        "html_report_message_hidden": "Message masqué",
        "html_report_footer": "Rapport généré le {date} depuis l'archive HTML.",
        "html_report_no_interventions": "Aucune intervention à rapporter (pas de notes ni de marqueurs de priorité).",
        "html_report_priority_red": "Rouge",
        "html_report_priority_amber": "Ambre",
        "html_report_priority_orange": "Orange",
        "html_report_priority_white": "Blanc",

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

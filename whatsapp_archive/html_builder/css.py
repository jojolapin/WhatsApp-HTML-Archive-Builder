"""Embedded CSS for the generated HTML archive."""

HTML_CSS = r"""
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
.sticky-top{position:sticky;top:0;z-index:10;background:inherit;box-shadow:0 2px 8px rgba(0,0,0,0.06)}
body.theme-light .sticky-top{background:var(--bg-light)}
body.theme-dark .sticky-top{background:var(--bg-dark)}
body.theme-vibrant .sticky-top{background:var(--bg-vibrant)}
.header{padding:10px 16px;font-weight:600}
.toolbar{padding:8px 16px;display:flex;gap:8px;flex-wrap:wrap}
.toolbar button,.toolbar select{padding:8px 10px;border:1px solid;border-radius:8px;cursor:pointer}
.toolbar button.active{font-weight:bold;border-width:2px}
.search{padding:0 16px 8px}
.search input{width:100%;padding:10px;border-radius:8px;border:1px solid;box-sizing:border-box}
.container{max-width:960px;margin:auto;padding:16px}
.msg{display:flex;gap:8px;align-items:flex-start;border-radius:14px;padding:10px 12px;margin:10px 0;line-height:1.35; border-left: 4px solid transparent; position: relative; scroll-margin-top: 220px;}
.msg-body{display:flex;gap:8px;align-items:flex-start;flex:1;min-width:0;margin-left:2px;}
.msg-deleted-placeholder{display:none;flex:1;font-size:12px;font-style:italic;opacity:.85;padding:8px 0;}
.msg.msg-deleted .msg-body{display:none !important;}
.msg.msg-deleted .msg-deleted-placeholder{display:block !important;}
.msg.msg-highlight{box-shadow:0 0 0 4px #2563eb;background:#dbeafe !important;}
body.theme-light .msg.msg-highlight{box-shadow:0 0 0 4px #2563eb;background:#dbeafe !important;}
body.theme-dark .msg.msg-highlight{box-shadow:0 0 0 4px #60a5fa;background:rgba(59,130,246,0.35) !important;}
body.theme-vibrant .msg.msg-highlight{box-shadow:0 0 0 4px #3b82f6;background:rgba(59,130,246,0.3) !important;}
.search-highlight{background:rgba(234,179,8,0.55);border-radius:2px;padding:0 1px;}
body.theme-dark .search-highlight{background:rgba(234,179,8,0.45);color:var(--text-dark);}
body.theme-vibrant .search-highlight{background:rgba(234,179,8,0.4);}
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
.msg-note{
 min-width:400px;max-width:600px;min-height:60px;padding:6px 8px;
 border:1px dashed #ccc;border-radius:8px;font-size:12px;font-family:inherit;
 background:rgba(255,255,200,0.15);color:inherit;
 line-height:1.35;box-sizing:border-box;flex-shrink:0;
 overflow-wrap:break-word;word-wrap:break-word;white-space:pre-wrap;
 outline:none;
}
.msg-note.empty::before{content:attr(data-placeholder);color:#999;font-style:italic;}
.msg-note:focus{outline:2px solid #3b82f6;border-color:#3b82f6;outline-offset:0}
.msg-note ul,.msg-note ol{margin:0.25em 0;padding-left:1.5em;}
.msg-note li{margin:0.1em 0;}
.msg-note p{margin:0.25em 0;}
.msg-note p:first-child{margin-top:0;}
.msg-note p:last-child{margin-bottom:0;}
body.theme-dark .msg-note{border-color:#555;background:rgba(255,255,200,0.05)}
body.theme-dark .msg-note.empty::before{color:#777}
body.theme-vibrant .msg-note{border-color:#555;background:rgba(255,255,200,0.05)}
body.theme-vibrant .msg-note.empty::before{color:#777}
.msg-note.has-content{border-style:solid;background:rgba(255,255,200,0.25)}
body.theme-dark .msg-note.has-content{background:rgba(255,255,200,0.1)}
body.theme-vibrant .msg-note.has-content{background:rgba(255,255,200,0.1)}
.footer{text-align:center;font-size:12px;color:#888;padding:20px}
.transcribe-btn{margin-top:8px;padding:6px 10px;font-size:12px;font-weight:500;background:#3b82f6;color:#fff;border:none;border-radius:6px;cursor:pointer}
.transcribe-btn:disabled{background:#555;cursor:default;opacity:0.8}
body.theme-light .transcribe-btn{background:#2563eb}
body.theme-light .transcribe-btn:disabled{background:#ccc}

.msg-number {
    position: absolute;
    top: 6px;
    left: -8px;
    font-size: 10px;
    font-weight: bold;
    min-width: 18px;
    width: max-content;
    max-width: 52px;
    height: 18px;
    padding: 0 5px;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    box-shadow: 0 0 2px rgba(0,0,0,0.3);
    z-index: 1;
}
body.theme-light .msg-number {
    background: #1f2937;
    color: #ffffff;
}
body.theme-dark .msg-number {
    background: #374151;
    color: #ffffff;
}
body.theme-vibrant .msg-number {
    background: #4b5563;
    color: #ffffff;
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

@media (max-width: 600px){
 body{font-size:15px}
 .container{padding:8px}
 .header{padding:8px 12px}
 .toolbar{padding:8px 12px;gap:6px}
 .toolbar button,.toolbar select{padding:6px 8px;font-size:13px}
 .search{padding:0 8px 8px}
 .msg{margin:8px 0;padding:8px 10px;gap:6px;flex-wrap:wrap}
 .msg-note{min-width:100%;max-width:100%;min-height:40px;margin-top:6px;font-size:11px}
 .msg-number { top: 2px; left: -6px; min-width: 16px; max-width: 44px; height: 16px; padding: 0 4px; font-size: 9px; border-radius: 8px; }
 .msg-priority-marker { width: 20px; height: 10px; }
}
"""

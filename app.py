"""
Dentsu AI Research Assistant — v4.0 (Stable)
================================================
Updated for dentsu branding and langchain 1.x compatibility.
Fixes applied:
  1. User message appears IMMEDIATELY (uses st.chat_message natively)
  2. Answer displays right after agent finishes (no need to click history)
  3. Sources rendered as separate clean component — no raw HTML leak
  4. No stuck spinner — proper error handling
  5. PDF upload working
  6. Compatible with langchain==1.2.17, langchain-core==1.3.3,
     langchain-classic==1.0.5, langchain-community==0.4.1,
     langchain-openai==1.1.10 on Python 3.11
"""

import streamlit as st
import os
import re
import hashlib
import sqlite3
import uuid
import json
import base64
import html as html_lib
from datetime import datetime
from warnings import filterwarnings

filterwarnings("ignore")

st.set_page_config(
    page_title="Dentsu AI Research Assistant",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --green: #0033A0;
    --green-dim: rgba(0,51,160,0.10);
    --green-border: rgba(0,51,160,0.18);
    --green-glow: rgba(0,51,160,0.25);
    --bg-root: #0B0E13;
    --bg-surface: #11151C;
    --bg-card: #171C26;
    --bg-elevated: #1E2430;
    --text-100: #F0F2F5;
    --text-200: #C4CAD4;
    --text-300: #8B95A5;
    --text-400: #5E6878;
    --border: rgba(255,255,255,0.06);
    --border-focus: rgba(0,51,160,0.45);
    --blue: #6B8AFF;
    --blue-dim: rgba(107,138,255,0.10);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --shadow-lg: 0 8px 32px rgba(0,0,0,0.4);
}

html, body, .stApp {
    background: var(--bg-root) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-100) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] .stMarkdown span {
    color: var(--text-200) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
}

.brand-box {
    padding: 1.5rem 1rem 1.2rem 1rem; text-align: center;
    border-bottom: 1px solid var(--border); margin-bottom: 1rem;
}
.brand-box .logo {
    font-size: 1.3rem; font-weight: 700; color: var(--green);
    letter-spacing: 0.12em;
    display: flex; align-items: center; justify-content: center; gap: 0.45rem;
}
.brand-box .sub {
    font-size: 0.65rem; color: var(--text-400);
    letter-spacing: 0.18em; text-transform: uppercase; margin-top: 4px;
}

.user-pill {
    display: flex; align-items: center; gap: 0.6rem;
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius-sm); padding: 0.55rem 0.75rem; margin: 0.6rem 0;
}
.user-pill .av {
    width: 30px; height: 30px; border-radius: 50%;
    background: linear-gradient(135deg, var(--green), #001A5C);
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.75rem; color: #0B0E13; flex-shrink: 0;
}
.user-pill .nm { font-weight: 600; font-size: 0.82rem; color: var(--text-100); }
.user-pill .rl { font-size: 0.68rem; color: var(--text-400); }

.sd { border: none; border-top: 1px solid var(--border); margin: 0.9rem 0; }

/* Login */
.login-wrap {
    max-width: 400px; margin: 8vh auto 0 auto; padding: 2.5rem 2rem;
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius-lg); box-shadow: var(--shadow-lg);
}
.login-wrap .l-title {
    text-align: center; font-size: 1.5rem; font-weight: 700;
    color: var(--green); letter-spacing: 0.06em; margin-bottom: 0.25rem;
}
.login-wrap .l-sub {
    text-align: center; font-size: 0.78rem; color: var(--text-400); margin-bottom: 1.8rem;
}

/* Chat message area overrides — make st.chat_message look great */
[data-testid="stChatMessage"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.8rem 1rem !important;
    margin-bottom: 0.5rem !important;
    color: var(--text-100) !important;
    font-family: 'Inter', sans-serif !important;
}

/* User messages — green tint */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, rgba(0,51,160,0.10), rgba(0,51,160,0.05)) !important;
    border: 1px solid var(--green-border) !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] td,
[data-testid="stChatMessage"] span {
    color: var(--text-100) !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 {
    color: var(--text-100) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
}

[data-testid="stChatMessage"] code {
    background: rgba(255,255,255,0.06) !important;
    color: #e0c285 !important;
    font-family: 'JetBrains Mono', monospace !important;
    padding: 0.15em 0.4em !important;
    border-radius: 4px !important;
}

[data-testid="stChatMessage"] pre {
    background: #0D1117 !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}

[data-testid="stChatMessage"] a {
    color: var(--blue) !important;
}

[data-testid="stChatMessage"] blockquote {
    border-left: 3px solid var(--green) !important;
    background: var(--green-dim) !important;
    padding: 0.3em 0.9em !important;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0 !important;
}

[data-testid="stChatMessage"] table th {
    background: var(--bg-elevated) !important;
    border-bottom: 2px solid var(--green-border) !important;
}

[data-testid="stChatMessage"] table td {
    border-bottom: 1px solid var(--border) !important;
}

/* Source chips */
.src-box {
    margin-top: 0.5rem; padding-top: 0.5rem;
    border-top: 1px solid rgba(255,255,255,0.06);
}
.src-label {
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #5E6878; margin-bottom: 0.35rem;
}
.src-chips { display: flex; flex-wrap: wrap; gap: 0.3rem; }
.src-chip {
    display: inline-flex; align-items: center; gap: 0.25rem;
    background: #1E2430; border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px; padding: 0.2rem 0.6rem;
    font-size: 0.68rem; color: #8B95A5;
    text-decoration: none !important; transition: all 0.15s;
}
.src-chip:hover {
    border-color: rgba(0,51,160,0.3); color: #0033A0; background: rgba(0,51,160,0.08);
}
.src-chip .sd2 {
    width: 5px; height: 5px; border-radius: 50%; background: #6B8AFF; flex-shrink: 0;
}

/* Tool badge */
.tbadge {
    display: inline-block; margin-top: 0.3rem;
    background: rgba(0,51,160,0.08); border: 1px solid rgba(0,51,160,0.18);
    border-radius: 20px; padding: 0.12rem 0.55rem;
    font-size: 0.62rem; font-weight: 500; color: #0033A0;
    font-family: 'JetBrains Mono', monospace;
}

/* Welcome */
.welcome-area { text-align: center; padding: 12vh 2rem 4rem 2rem; }
.welcome-area .w-icon {
    width: 56px; height: 56px; border-radius: 16px;
    background: var(--green-dim); border: 1px solid var(--green-border);
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 1.5rem; margin-bottom: 1.2rem;
}
.welcome-area h2 { font-size: 1.4rem; font-weight: 600; color: var(--text-100); margin-bottom: 0.5rem; }
.welcome-area p { font-size: 0.88rem; color: var(--text-400); max-width: 420px; margin: 0 auto; line-height: 1.6; }

/* Doc item */
.doc-item {
    display: flex; align-items: center; gap: 0.4rem;
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 6px; padding: 0.35rem 0.6rem; margin: 0.25rem 0;
    font-size: 0.75rem; color: var(--text-200);
}
.doc-item .di { color: var(--green); flex-shrink: 0; }

/* Streamlit overrides */
.stTextInput > div > div > input {
    background: var(--bg-elevated) !important; border: 1px solid var(--border) !important;
    color: var(--text-100) !important; border-radius: var(--radius-sm) !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--border-focus) !important; box-shadow: 0 0 0 3px var(--green-dim) !important;
}
.stButton > button {
    font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
    border-radius: var(--radius-sm) !important; transition: all 0.2s !important;
    font-size: 0.84rem !important;
}
form .stButton > button {
    background: var(--green) !important; color: #0B0E13 !important; border: none !important;
}
form .stButton > button:hover {
    box-shadow: 0 4px 16px var(--green-glow) !important; transform: translateY(-1px) !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: var(--bg-card) !important; color: var(--text-200) !important;
    border: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--bg-elevated) !important; border-color: var(--green-border) !important;
    color: var(--text-100) !important;
}
.stFileUploader > div {
    background: var(--bg-card) !important; border: 1px dashed rgba(255,255,255,0.1) !important;
    border-radius: var(--radius-sm) !important;
}
.stChatInput > div {
    background: var(--bg-card) !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
}
.stChatInput textarea {
    color: var(--text-100) !important; font-family: 'Inter', sans-serif !important;
}
.stSpinner > div > div { border-top-color: var(--green) !important; }
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: var(--text-300) !important;
    font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 0.6rem 1.2rem !important;
    border-bottom: 2px solid transparent !important;
    white-space: nowrap !important;
}
.stTabs [aria-selected="true"] {
    color: var(--green) !important; border-bottom-color: var(--green) !important;
}
.stAlert { border-radius: var(--radius-sm) !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--bg-elevated); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════

DB_PATH = "research_assistant.db"

def init_database():
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY, username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL, display_name TEXT,
        role TEXT DEFAULT 'user', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS conversations (
        conversation_id TEXT PRIMARY KEY, user_id TEXT NOT NULL,
        title TEXT DEFAULT 'New Chat',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY, conversation_id TEXT NOT NULL,
        role TEXT NOT NULL, content TEXT NOT NULL,
        sources TEXT, tool_calls TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS documents (
        doc_id TEXT PRIMARY KEY, user_id TEXT NOT NULL,
        filename TEXT NOT NULL, file_type TEXT, content_preview TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit(); conn.close()

def _hash(pw):
    return hashlib.sha256(f"dentsu_salt_2025_{pw}".encode()).hexdigest()

def register_user(username, password):
    uid = str(uuid.uuid4()); display = username.strip().title()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("INSERT INTO users VALUES (?,?,?,?,?,CURRENT_TIMESTAMP)",
                     (uid, username.lower().strip(), _hash(password), display, "user"))
        conn.commit(); conn.close()
        return {"user_id": uid, "username": username.lower().strip(), "display_name": display, "role": "user"}
    except sqlite3.IntegrityError:
        conn.close(); return None

def authenticate(username, password):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT user_id,username,display_name,role FROM users WHERE username=? AND password_hash=?",
                       (username.lower().strip(), _hash(password))).fetchone()
    conn.close()
    return {"user_id": row[0], "username": row[1], "display_name": row[2], "role": row[3]} if row else None

def seed_defaults():
    conn = sqlite3.connect(DB_PATH)
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        conn.execute("INSERT OR IGNORE INTO users VALUES (?,?,?,?,?,CURRENT_TIMESTAMP)",
                     (str(uuid.uuid4()), "admin", _hash("admin123"), "Admin", "admin"))
    conn.commit(); conn.close()

def create_conversation(uid, title="New Chat"):
    cid = str(uuid.uuid4()); conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO conversations VALUES (?,?,?,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)", (cid, uid, title))
    conn.commit(); conn.close(); return cid

def get_conversations(uid):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT conversation_id,title,created_at,updated_at FROM conversations WHERE user_id=? ORDER BY updated_at DESC", (uid,)).fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "created_at": r[2], "updated_at": r[3]} for r in rows]

def delete_conversation(cid):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM messages WHERE conversation_id=?", (cid,))
    conn.execute("DELETE FROM conversations WHERE conversation_id=?", (cid,))
    conn.commit(); conn.close()

def save_message(cid, role, content, sources=None, tool_calls=None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)",
                 (str(uuid.uuid4()), cid, role, content, json.dumps(sources) if sources else None, tool_calls))
    conn.execute("UPDATE conversations SET updated_at=CURRENT_TIMESTAMP WHERE conversation_id=?", (cid,))
    conn.commit(); conn.close()

def get_messages(cid):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT role,content,sources,tool_calls,timestamp FROM messages WHERE conversation_id=? ORDER BY timestamp ASC", (cid,)).fetchall()
    conn.close()
    out = []
    for r in rows:
        s = None
        if r[2]:
            try: s = json.loads(r[2])
            except: pass
        out.append({"role": r[0], "content": r[1], "sources": s, "tool_calls": r[3], "timestamp": r[4]})
    return out

def save_doc_record(uid, fname, ftype, preview):
    """Save doc record only if this user doesn't already have a doc with the same filename."""
    conn = sqlite3.connect(DB_PATH)
    existing = conn.execute("SELECT doc_id FROM documents WHERE user_id=? AND filename=?", (uid, fname)).fetchone()
    if existing:
        conn.close(); return  # Already saved for this user — skip duplicate
    conn.execute("INSERT INTO documents VALUES (?,?,?,?,?,CURRENT_TIMESTAMP)",
                 (str(uuid.uuid4()), uid, fname, ftype, preview[:500]))
    conn.commit(); conn.close()

def get_user_docs(uid):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT doc_id,filename,file_type,uploaded_at FROM documents WHERE user_id=? ORDER BY uploaded_at DESC", (uid,)).fetchall()
    conn.close()
    return [{"id": r[0], "filename": r[1], "type": r[2], "uploaded_at": r[3]} for r in rows]

def delete_document(doc_id, uid):
    """Delete a document record from DB for a specific user."""
    conn = sqlite3.connect(DB_PATH)
    # Get filename before deleting so we can clean session state
    row = conn.execute("SELECT filename FROM documents WHERE doc_id=? AND user_id=?", (doc_id, uid)).fetchone()
    fname = row[0] if row else None
    conn.execute("DELETE FROM documents WHERE doc_id=? AND user_id=?", (doc_id, uid))
    conn.commit(); conn.close()
    return fname


# ═══════════════════════════════════════════════
# FILE PROCESSING
# ═══════════════════════════════════════════════

def extract_pdf(f):
    try:
        import pymupdf; f.seek(0)
        doc = pymupdf.open(stream=f.read(), filetype="pdf")
        txt = "\n".join(p.get_text() for p in doc); doc.close()
        return txt if txt.strip() else "[No extractable text in PDF]"
    except Exception as e: return f"[PDF error: {e}]"

def extract_docx(f):
    try:
        from docx import Document; import io; f.seek(0)
        return "\n".join(p.text for p in Document(io.BytesIO(f.read())).paragraphs if p.text.strip())
    except Exception as e: return f"[DOCX error: {e}]"

def extract_txt(f):
    try:
        f.seek(0); d = f.read()
        try: return d.decode("utf-8")
        except: return d.decode("latin-1")
    except Exception as e: return f"[TXT error: {e}]"

def process_upload(f):
    n = f.name.lower()
    if n.endswith(".pdf"):  return extract_pdf(f)
    if n.endswith(".docx"): return extract_docx(f)
    if n.endswith(".txt"):  return extract_txt(f)
    if n.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")): return extract_image(f)
    return f"[Unsupported: {f.name}]"


def extract_image(f):
    """Encode an image file to base64 for vision model analysis."""
    try:
        f.seek(0)
        data = f.read()
        if not data:
            return "[Image error: empty file]"
        b64 = base64.b64encode(data).decode("utf-8")
        ext = f.name.rsplit(".", 1)[-1].lower()
        mime_map = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}
        mime = mime_map.get(ext, "image/png")
        # Return a special marker so we know this is an image, not text
        return f"__IMAGE_B64__|{mime}|{b64}"
    except Exception as e:
        return f"[Image error: {e}]"


def is_image_data(text):
    """Check if the stored doc text is actually base64 image data."""
    return text and text.startswith("__IMAGE_B64__|")


# ═══════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════

def extract_sources(text):
    urls = re.findall(r'https?://[^\s\)\]>"\'`,]+', text)
    seen = set(); unique = []
    for u in urls:
        u = u.rstrip('.,;:!?)')
        domain = re.sub(r'^https?://(www\.)?', '', u).split('/')[0]
        if domain not in seen and len(domain) > 2:
            seen.add(domain); unique.append({"url": u, "domain": domain})
    return unique[:8]

def clean_answer_urls(text, sources):
    """Remove bare URLs from answer since we show them as chips."""
    if not sources:
        return text
    # Protect markdown links
    protected = text; phs = {}
    for i, m in enumerate(re.finditer(r'\[([^\]]+)\]\(https?://[^\)]+\)', text)):
        ph = f"MDLNK{i}X"; phs[ph] = m.group(0); protected = protected.replace(m.group(0), ph, 1)
    # Strip bare URLs
    cleaned = re.sub(r'https?://[^\s\)\]>"\'`,]+', '', protected)
    # Restore markdown links
    for ph, orig in phs.items(): cleaned = cleaned.replace(ph, orig)
    # Clean leftover artifacts
    cleaned = re.sub(r'Source:\s*$', '', cleaned, flags=re.M)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()

def get_domain_label(domain):
    parts = domain.split('.')
    return parts[-2].capitalize() if len(parts) >= 2 else domain.capitalize()

def generate_title(content):
    words = content.split()[:7]
    return " ".join(words) + ("..." if len(content.split()) > 7 else "")

def render_sources_and_tools(sources, tools):
    """Render sources and tool badges as a SEPARATE st.markdown call."""
    parts = []

    if sources:
        chips = ""
        for s in sources:
            d = s.get("domain", "")
            u = html_lib.escape(s.get("url", "#"))
            chips += f'<a href="{u}" target="_blank" rel="noopener" class="src-chip"><span class="sd2"></span>{get_domain_label(d)} · {d}</a>'
        parts.append(f'<div class="src-box"><div class="src-label">📎 Sources</div><div class="src-chips">{chips}</div></div>')

    if tools:
        t = tools.replace("search_web_extract_info", "Web Search").replace("get_weather", "Weather").replace("search_pdf_knowledgebase", "Documents").replace("Image Analysis", "🖼️ Image Analysis")
        parts.append(f'<div class="tbadge">⚡ {t}</div>')

    if parts:
        st.markdown("\n".join(parts), unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# AGENT
# ═══════════════════════════════════════════════

def init_agent():
    EP = st.session_state.get("azure_endpoint", "")
    MN = "gpt-4o"
    AK = st.session_state.get("azure_api_key", "")
    AV = "2024-12-01-preview"
    TK = "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"
    WK = "1ad27edef23e488888304546262703"

    if not all([EP, AK]):
        return None, "Azure OpenAI credentials not configured. Please enter them on the settings panel."

    from langchain_openai import AzureChatOpenAI
    llm = AzureChatOpenAI(azure_deployment=MN, api_version=AV, azure_endpoint=EP, api_key=AK, temperature=0)

    import requests as req
    from langchain_core.tools import tool
    tools_list = []

    if TK:
        import os as _os
        _os.environ["TAVILY_API_KEY"] = TK
        from langchain_community.tools.tavily_search import TavilySearchResults
        tavily = TavilySearchResults(max_results=5, search_depth="advanced", include_raw_content=True)

        @tool
        def search_web_extract_info(query: str) -> str:
            """Search the web for current events, news, or any information."""
            try:
                results = tavily.invoke(query)
                if not results: return "No results found."
                parts = []
                for i, r in enumerate(results, 1):
                    parts.append(f"[{i}] {r.get('title','')}\n{r.get('content','')}\nSource: {r.get('url','')}")
                return "\n\n---\n\n".join(parts)
            except Exception as e: return f"Search error: {e}"
        tools_list.append(search_web_extract_info)

    @tool
    def get_weather(query: str) -> str:
        """Get current weather for a location."""
        try:
            data = req.get("http://api.weatherapi.com/v1/current.json", params={"key": WK, "q": query}, timeout=10).json()
            if data.get("location"):
                l, c = data["location"], data["current"]
                return f"Weather in {l['name']}, {l.get('country','')}:\nTemp: {c['temp_c']}°C/{c['temp_f']}°F\nCondition: {c['condition']['text']}\nHumidity: {c['humidity']}%\nWind: {c['wind_kph']} km/h {c.get('wind_dir','')}\nFeels like: {c['feelslike_c']}°C/{c['feelslike_f']}°F"
            return "Location not found."
        except Exception as e: return f"Weather error: {e}"
    tools_list.append(get_weather)

    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    today_str = datetime.now().strftime("%B %d, %Y")
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are a highly capable AI research assistant for Dentsu.
Today's date is {today_str}.
Tools: search_web_extract_info (web search), get_weather (weather).
Instructions:
1. ALWAYS use search_web_extract_info for ANY question about current events, recent news, sports results, elections, conflicts, world cups, awards, rankings, "who won", "who is the current", or anything that could have changed after 2023. Do NOT rely on your training data for such questions — always search first.
2. For weather → use get_weather
3. Only answer directly from your own knowledge for timeless facts (math, science definitions, historical events before 2023, programming concepts, etc.)
4. If document context is in the message, use it
5. Format answers with markdown (headers, bullets, bold, tables)
6. Include source URLs from search results
7. Be thorough but concise
8. When in doubt whether information might be outdated, USE the search tool."""),
        MessagesPlaceholder(variable_name="history", optional=True),
        ("human", "{query}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # langchain 1.x: create_tool_calling_agent and AgentExecutor live in langchain_classic
    from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
    agent = create_tool_calling_agent(llm, tools_list, prompt)
    executor = AgentExecutor(agent=agent, tools=tools_list, early_stopping_method="force",
                             max_iterations=5, verbose=False, return_intermediate_steps=True,
                             handle_parsing_errors=True)

    from langchain_community.chat_message_histories import SQLChatMessageHistory
    from langchain_core.runnables.history import RunnableWithMessageHistory
    chatbot = RunnableWithMessageHistory(executor,
        lambda sid: SQLChatMessageHistory(session_id=sid, connection="sqlite:///agent_memory.db"),
        input_messages_key="query", history_messages_key="history")
    return chatbot, None


# ═══════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════

def render_login():
    st.markdown("<style>section[data-testid='stSidebar']{display:none;}</style>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.2, 1.6, 1.2])
    with c2:
        st.markdown('<div class="login-wrap"><div class="l-title">🔵 DENTSU AI</div><div class="l-sub">Intelligent Research Assistant</div></div>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["Sign In", "Create Account"])
        with t1:
            with st.form("login_form", clear_on_submit=False):
                u = st.text_input("Username", placeholder="Enter username", key="lu")
                p = st.text_input("Password", type="password", placeholder="Enter password", key="lp")
                if st.form_submit_button("Sign In", use_container_width=True):
                    if u and p:
                        user = authenticate(u, p)
                        if user:
                            st.session_state.update(authenticated=True, user=user, current_conv=None, messages=[])
                            st.rerun()
                        else: st.error("Invalid credentials.")
                    else: st.warning("Fill in both fields.")
        with t2:
            with st.form("signup_form", clear_on_submit=True):
                nu = st.text_input("Username", placeholder="e.g. john.doe", key="su")
                p1 = st.text_input("Password", type="password", placeholder="Min 4 chars", key="sp1")
                p2 = st.text_input("Confirm", type="password", placeholder="Re-enter", key="sp2")
                if st.form_submit_button("Create Account", use_container_width=True):
                    nc = (nu or "").strip()
                    if not nc or not p1: st.warning("Both fields required.")
                    elif len(nc) < 3: st.warning("Username: 3+ characters.")
                    elif len(p1) < 4: st.warning("Password: 4+ characters.")
                    elif p1 != p2: st.error("Passwords don't match.")
                    else:
                        r = register_user(nc, p1)
                        if r: st.success(f"Created! Sign in as **{nc}**.")
                        else: st.error("Username taken.")
        st.markdown("<p style='text-align:center;color:var(--text-400);font-size:0.72rem;margin-top:1.5rem;'>Create an account or sign in</p>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════

def render_sidebar():
    user = st.session_state["user"]
    with st.sidebar:
        st.markdown('<div class="brand-box"><div class="logo">🔵 DENTSU AI</div><div class="sub">Research Assistant</div></div>', unsafe_allow_html=True)
        ini = user["display_name"][0].upper()
        st.markdown(f'<div class="user-pill"><div class="av">{ini}</div><div><div class="nm">{user["display_name"]}</div><div class="rl">{user["role"].title()}</div></div></div>', unsafe_allow_html=True)

        # ── API Credentials Section ──
        st.markdown('<hr class="sd">', unsafe_allow_html=True)
        with st.expander("🔑 API Configuration", expanded=not st.session_state.get("azure_endpoint")):
            ep_val = st.text_input(
                "Model Endpoint",
                value=st.session_state.get("azure_endpoint", ""),
                placeholder="https://your-resource.openai.azure.com/",
                key="input_endpoint",
                type="default",
            )
            ak_val = st.text_input(
                "Azure OpenAI API Key",
                value=st.session_state.get("azure_api_key", ""),
                placeholder="Enter your API key",
                key="input_api_key",
                type="password",
            )
            if st.button("Save Credentials", use_container_width=True, key="save_creds"):
                if ep_val.strip() and ak_val.strip():
                    st.session_state["azure_endpoint"] = ep_val.strip()
                    st.session_state["azure_api_key"] = ak_val.strip()
                    # Clear cached agent so it re-initializes with new creds
                    st.session_state.pop("agent", None)
                    st.success("Credentials saved!")
                    st.rerun()
                else:
                    st.warning("Both fields are required.")
        # ── End API Credentials ──

        if st.button("＋  New conversation", use_container_width=True, key="new_chat"):
            st.session_state["current_conv"] = None; st.session_state["messages"] = []; st.rerun()

        st.markdown('<hr class="sd">', unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.72rem;font-weight:700;color:var(--text-400);letter-spacing:0.1em;text-transform:uppercase;'>History</p>", unsafe_allow_html=True)

        for c in get_conversations(user["user_id"])[:20]:
            active = st.session_state.get("current_conv") == c["id"]
            cols = st.columns([6, 1])
            with cols[0]:
                if st.button(f"{'▸ ' if active else ''}{c['title'][:35]}", key=f"c_{c['id']}", use_container_width=True):
                    st.session_state["current_conv"] = c["id"]
                    st.session_state["messages"] = get_messages(c["id"])
                    st.rerun()
            with cols[1]:
                if st.button("×", key=f"d_{c['id']}"):
                    delete_conversation(c["id"])
                    if st.session_state.get("current_conv") == c["id"]:
                        st.session_state["current_conv"] = None; st.session_state["messages"] = []
                    st.rerun()

        if not get_conversations(user["user_id"]):
            st.caption("No conversations yet")

        st.markdown('<hr class="sd">', unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.72rem;font-weight:700;color:var(--text-400);letter-spacing:0.1em;text-transform:uppercase;'>Documents & Images</p>", unsafe_allow_html=True)

        if "processed_files" not in st.session_state: st.session_state["processed_files"] = []
        if "doc_texts" not in st.session_state: st.session_state["doc_texts"] = {}

        uploaded = st.file_uploader("Upload PDF, DOCX, TXT, PNG, JPG", type=["pdf","docx","txt","png","jpg","jpeg","gif","webp"], accept_multiple_files=True, key="uploader")
        if uploaded:
            for uf in uploaded:
                if uf.name not in st.session_state["processed_files"]:
                    with st.spinner(f"Reading {uf.name}..."):
                        txt = process_upload(uf)
                        if txt and not txt.startswith("["):
                            st.session_state["doc_texts"][uf.name] = txt
                            save_doc_record(user["user_id"], uf.name, uf.name.split(".")[-1], txt[:500])
                            if uf.name not in st.session_state["processed_files"]:
                                st.session_state["processed_files"].append(uf.name)
                            st.rerun()
                        else: st.error(f"Failed: {uf.name}")

        # Show uploaded docs with delete buttons
        user_docs = get_user_docs(user["user_id"])
        if user_docs:
            for d in user_docs[:8]:
                dc1, dc2 = st.columns([6, 1])
                with dc1:
                    icon = "🖼️" if d["filename"].lower().endswith((".png",".jpg",".jpeg",".gif",".webp")) else "📄"
                    st.markdown(f'<div class="doc-item"><span class="di">{icon}</span>{d["filename"]}</div>', unsafe_allow_html=True)
                with dc2:
                    if st.button("×", key=f"deldoc_{d['id']}"):
                        fname = delete_document(d["id"], user["user_id"])
                        # Clean from session state too
                        if fname and fname in st.session_state.get("doc_texts", {}):
                            del st.session_state["doc_texts"][fname]
                        if fname and fname in st.session_state.get("processed_files", []):
                            st.session_state["processed_files"].remove(fname)
                        st.rerun()
        else:
            st.caption("No documents uploaded")

        st.markdown('<hr class="sd">', unsafe_allow_html=True)
        if st.button("Sign out", use_container_width=True, key="logout"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
        st.markdown("<p style='color:var(--text-400);font-size:0.62rem;text-align:center;padding-top:0.8rem;'>Dentsu AI v4.0</p>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# CHAT — uses st.chat_message for native rendering
# ═══════════════════════════════════════════════

def render_chat():
    # Check if API credentials are configured
    if not st.session_state.get("azure_endpoint") or not st.session_state.get("azure_api_key"):
        st.markdown("""
        <div class="welcome-area">
            <div class="w-icon">🔑</div>
            <h2>Configure API Credentials</h2>
            <p>Please open the <b>🔑 API Configuration</b> section in the sidebar
            and enter your Azure OpenAI endpoint and API key to get started.</p>
        </div>""", unsafe_allow_html=True)
        return

    messages = st.session_state.get("messages", [])

    # Welcome screen
    if not messages:
        st.markdown("""
        <div class="welcome-area">
            <div class="w-icon">🔵</div>
            <h2>What can I help you research?</h2>
            <p>Ask me anything — I can search the web, check weather,
            analyze your uploaded documents, and examine images.</p>
        </div>""", unsafe_allow_html=True)

    # Render existing messages using st.chat_message (native Streamlit)
    for msg in messages:
        role = msg["role"]
        avatar = "🟢" if role == "user" else "🔵"
        with st.chat_message(role, avatar=avatar):
            if role == "user":
                st.markdown(msg["content"])
            else:
                # Clean URLs from answer body and render as markdown
                sources = msg.get("sources") or []
                display_text = clean_answer_urls(msg["content"], sources) if sources else msg["content"]
                st.markdown(display_text)
                # Render sources and tools as separate HTML block
                render_sources_and_tools(sources, msg.get("tool_calls"))

    # Chat input — this is where the magic happens
    prompt = st.chat_input("Type your question here...", key="chat_input")

    if prompt:
        user = st.session_state["user"]

        # Create conversation if needed
        if not st.session_state.get("current_conv"):
            cid = create_conversation(user["user_id"], generate_title(prompt))
            st.session_state["current_conv"] = cid
        else:
            cid = st.session_state["current_conv"]

        # Save user message to DB
        save_message(cid, "user", prompt)

        # Add to session state
        st.session_state.setdefault("messages", []).append(
            {"role": "user", "content": prompt, "sources": None, "tool_calls": None}
        )

        # IMMEDIATELY show user message (st.chat_message renders it right now)
        with st.chat_message("user", avatar="🟢"):
            st.markdown(prompt)

        # Show assistant thinking, then stream the response
        with st.chat_message("assistant", avatar="🔵"):
            with st.spinner("Researching your question..."):
                answer, sources, tool_info = run_agent(prompt, user, cid)

            # Display the answer
            display_text = clean_answer_urls(answer, sources) if sources else answer
            st.markdown(display_text)
            render_sources_and_tools(sources, tool_info)

        # Save to DB and session state
        save_message(cid, "assistant", answer, sources=sources, tool_calls=tool_info)
        st.session_state["messages"].append(
            {"role": "assistant", "content": answer, "sources": sources, "tool_calls": tool_info}
        )


def run_agent(prompt, user, cid):
    """Run the agent and return (answer, sources, tool_info). Never raises."""
    # Check if any uploaded docs are images
    image_entries = {}
    text_entries = {}
    for fn, txt in st.session_state.get("doc_texts", {}).items():
        if is_image_data(txt):
            image_entries[fn] = txt
        else:
            text_entries[fn] = txt

    # If there are images, use the LLM vision endpoint directly
    if image_entries:
        try:
            from langchain_openai import AzureChatOpenAI

            EP = st.session_state.get("azure_endpoint", "")
            MN = "gpt-4o"
            AK = st.session_state.get("azure_api_key", "")
            AV = "2024-12-01-preview"

            llm_vision = AzureChatOpenAI(
                azure_deployment=MN, api_version=AV,
                azure_endpoint=EP, api_key=AK, temperature=0, max_tokens=2000
            )

            # Build multi-modal message content
            content_parts = [{"type": "text", "text": prompt}]

            # Add text document context if any
            if text_entries:
                doc_ctx = "\n\n---\n\n".join(
                    [f"[Document: {fn}]\n{txt[:3000]}" for fn, txt in text_entries.items()]
                )
                content_parts[0]["text"] += f"\n\n[Uploaded document context:]\n{doc_ctx}"

            # Add each image
            for fn, img_data in image_entries.items():
                parts = img_data.split("|", 2)  # __IMAGE_B64__|mime|base64data
                if len(parts) == 3:
                    mime, b64 = parts[1], parts[2]
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "high"}
                    })

            from langchain_core.messages import HumanMessage, SystemMessage
            today_str = datetime.now().strftime("%B %d, %Y")
            messages = [
                SystemMessage(content=f"You are a highly capable AI research assistant. Today's date is {today_str}. "
                              "Analyze any provided images in detail. Describe what you see, extract text/data if present, "
                              "and answer the user's question about the image(s). "
                              "Format your answer with markdown. Be thorough but concise."),
                HumanMessage(content=content_parts)
            ]

            response = llm_vision.invoke(messages)
            answer = response.content if response.content else "I couldn't analyze the image."
            sources = extract_sources(answer)
            return answer, sources, "Image Analysis"

        except Exception as e:
            return f"Error analyzing image: {str(e)}\n\nMake sure your Azure OpenAI deployment supports vision/image inputs.", [], None

    # Normal text-only flow — build doc context
    doc_context = ""
    if text_entries:
        snippets = [f"[Document: {fn}]\n{txt[:3000]}" for fn, txt in text_entries.items()]
        doc_context = "\n\n---\n\n".join(snippets)

    augmented = prompt
    if doc_context:
        augmented = f"{prompt}\n\n[Uploaded document context:]\n{doc_context}"

    # Init agent
    agent = st.session_state.get("agent")
    if agent is None:
        agent, error = init_agent()
        if error:
            return f"⚠️ {error}\n\nPlease configure your API credentials using the 🔑 panel in the sidebar.", [], None
        st.session_state["agent"] = agent

    session_id = f"{user['user_id']}_{cid}"

    try:
        response = agent.invoke({"query": augmented}, {"configurable": {"session_id": session_id}})
        answer = response.get("output", "I couldn't generate a response.")

        tool_info = None
        if response.get("intermediate_steps"):
            tools_used = set()
            for step in response["intermediate_steps"]:
                if hasattr(step[0], "tool"): tools_used.add(step[0].tool)
            if tools_used: tool_info = ", ".join(tools_used)

        sources = extract_sources(answer)
        return answer, sources, tool_info

    except Exception as e:
        return f"Error: {str(e)}\n\nTry rephrasing your question.", [], None


# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════

def main():
    init_database(); seed_defaults()
    if not st.session_state.get("authenticated"):
        render_login()
    else:
        render_sidebar()
        render_chat()

if __name__ == "__main__":
    main()

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

_ROOT = Path(__file__).resolve().parent.parent
_IMAGES_DIR = _ROOT / "public" / "images"
if _IMAGES_DIR.is_dir():
    app.mount("/images", StaticFiles(directory=str(_IMAGES_DIR)), name="images")

# Initialize OpenAI
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

SYSTEM_PROMPT = """You are Solarin Ayomide's digital twin – a tech builder and digital strategist focused on creating scalable solutions at the intersection of software, education, and growth marketing.

## Your Background
- Web developer with 3+ years experience creating user-centric websites and applications
- Built platforms: Pinnaview Networks (utility bill payment, 12k+ users), Skyned Consults (placed 4000+ students), Jekacode Africa, WithoutTheBox.ng, Unicollegelink.com
- Education: B.Sc. Botany (Second Class Upper) from FUNAAB

## Communication Style
- Friendly, professional, and solution-oriented
- Keep responses concise (2-3 sentences max for simple questions)
- Answer naturally as Solarin Ayomide. Use "I" statements."""

PROFILE_IMG = (
    "https://res.cloudinary.com/dc2wrlebl/image/upload/v1775226566/Ayomide_xakvsf.jpg"
)
AVATAR_FALLBACK = "/images/avatar.svg"


class ChatRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def root():
    profile = PROFILE_IMG
    fallback = AVATAR_FALLBACK
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
        <title>Solarin Ayomide · Digital Twin</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap" rel="stylesheet" />
        <style>
            :root {{
                --bg: #eceff3;
                --surface: #ffffff;
                --text: #0f172a;
                --muted: #64748b;
                --accent: #0d9488;
                --accent-hover: #0f766e;
                --user-bubble: #0f172a;
                --bot-bubble: #f1f5f9;
                --border: #e2e8f0;
                --shadow: 0 12px 40px rgba(15, 23, 42, 0.08);
                --radius: 16px;
                --radius-lg: 22px;
            }}
            * {{ box-sizing: border-box; }}
            html, body {{ height: 100%; margin: 0; }}
            body {{
                font-family: "DM Sans", system-ui, -apple-system, sans-serif;
                font-optical-sizing: auto;
                background: var(--bg);
                color: var(--text);
                -webkit-font-smoothing: antialiased;
            }}
            .app {{
                min-height: 100%;
                max-width: 720px;
                margin: 0 auto;
                display: flex;
                flex-direction: column;
                padding: 12px 12px 0;
                padding-bottom: env(safe-area-inset-bottom, 12px);
            }}
            .header {{
                background: var(--surface);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow);
                padding: 18px 20px;
                display: flex;
                gap: 16px;
                align-items: center;
                flex-shrink: 0;
            }}
            .header-main {{
                display: flex;
                gap: 16px;
                align-items: center;
                flex: 1;
                min-width: 0;
            }}
            .avatar-wrap {{
                position: relative;
                flex-shrink: 0;
            }}
            .avatar {{
                width: 72px;
                height: 72px;
                border-radius: 50%;
                object-fit: cover;
                border: 3px solid var(--surface);
                box-shadow: 0 0 0 2px var(--accent);
                background: var(--bot-bubble);
            }}
            .status-dot {{
                position: absolute;
                bottom: 4px;
                right: 4px;
                width: 14px;
                height: 14px;
                background: #22c55e;
                border: 2px solid var(--surface);
                border-radius: 50%;
            }}
            .header-text h1 {{
                font-size: 1.25rem;
                font-weight: 700;
                margin: 0 0 4px;
                letter-spacing: -0.02em;
            }}
            .header-text p {{
                margin: 0;
                font-size: 0.875rem;
                color: var(--muted);
                line-height: 1.4;
            }}
            .gallery {{
                display: flex;
                gap: 8px;
                align-items: center;
                flex-shrink: 0;
            }}
            .gallery img {{
                width: 44px;
                height: 44px;
                border-radius: 12px;
                object-fit: cover;
                border: 2px solid var(--border);
                background: var(--bot-bubble);
            }}
            .chat-panel {{
                flex: 1;
                display: flex;
                flex-direction: column;
                margin-top: 12px;
                background: var(--surface);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow);
                overflow: hidden;
                min-height: 52vh;
            }}
            .chat-scroll {{
                flex: 1;
                overflow-y: auto;
                padding: 20px 16px;
                scroll-behavior: smooth;
            }}
            .row {{
                display: flex;
                gap: 10px;
                margin-bottom: 14px;
                align-items: flex-end;
            }}
            .row-user {{
                flex-direction: row-reverse;
            }}
            .row-bot {{ flex-direction: row; }}
            .msg-avatar {{
                width: 34px;
                height: 34px;
                border-radius: 50%;
                object-fit: cover;
                flex-shrink: 0;
                border: 1px solid var(--border);
                background: var(--bot-bubble);
            }}
            .msg-avatar.user {{
                background: var(--user-bubble);
                color: #fff;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.7rem;
                font-weight: 600;
            }}
            .bubble {{
                max-width: min(78%, 420px);
                padding: 12px 16px;
                border-radius: 18px;
                font-size: 0.9375rem;
                line-height: 1.55;
                word-wrap: break-word;
            }}
            .row-user .bubble {{
                background: var(--user-bubble);
                color: #f8fafc;
                border-bottom-right-radius: 6px;
            }}
            .row-bot .bubble {{
                background: var(--bot-bubble);
                color: var(--text);
                border-bottom-left-radius: 6px;
                border: 1px solid var(--border);
            }}
            .typing {{
                display: none;
                align-items: center;
                gap: 6px;
                padding: 10px 14px;
                background: var(--bot-bubble);
                border-radius: 18px;
                border-bottom-left-radius: 6px;
                border: 1px solid var(--border);
                width: fit-content;
            }}
            .typing.on {{ display: flex; }}
            .typing span {{
                width: 7px;
                height: 7px;
                background: var(--muted);
                border-radius: 50%;
                animation: bounce 1.2s ease infinite;
            }}
            .typing span:nth-child(2) {{ animation-delay: 0.15s; }}
            .typing span:nth-child(3) {{ animation-delay: 0.3s; }}
            @keyframes bounce {{
                0%, 60%, 100% {{ transform: translateY(0); opacity: 0.45; }}
                30% {{ transform: translateY(-5px); opacity: 1; }}
            }}
            .composer {{
                display: flex;
                gap: 10px;
                padding: 12px 14px 16px;
                border-top: 1px solid var(--border);
                background: linear-gradient(180deg, #fafbfc 0%, var(--surface) 40%);
            }}
            .composer input {{
                flex: 1;
                border: 1px solid var(--border);
                border-radius: 999px;
                padding: 12px 18px;
                font-size: 0.9375rem;
                font-family: inherit;
                outline: none;
                transition: border-color 0.15s, box-shadow 0.15s;
            }}
            .composer input:focus {{
                border-color: var(--accent);
                box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.2);
            }}
            .composer input:disabled {{
                opacity: 0.65;
                cursor: not-allowed;
            }}
            .composer button {{
                width: 48px;
                height: 48px;
                border-radius: 50%;
                border: none;
                background: var(--accent);
                color: #fff;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                transition: background 0.15s, transform 0.1s;
            }}
            .composer button:hover:not(:disabled) {{
                background: var(--accent-hover);
            }}
            .composer button:active:not(:disabled) {{ transform: scale(0.96); }}
            .composer button:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            .links {{
                text-align: center;
                padding: 10px 8px 14px;
                font-size: 0.75rem;
                color: var(--muted);
            }}
            .links a {{
                color: var(--accent);
                text-decoration: none;
                font-weight: 500;
            }}
            .links a:hover {{ text-decoration: underline; }}
            .typing-row {{
                display: none;
                padding: 0 16px 10px;
                margin: 0;
                align-items: flex-end;
                gap: 10px;
            }}
            .typing-row.on {{ display: flex; }}
            @media (max-width: 560px) {{
                .gallery {{ display: none; }}
                .header {{ flex-wrap: wrap; }}
            }}
        </style>
    </head>
    <body>
        <div class="app">
            <header class="header">
                <div class="header-main">
                    <div class="avatar-wrap">
                        <img class="avatar" src="{profile}" alt="Solarin Ayomide"
                             onerror="this.onerror=null;this.src='{fallback}'" />
                        <span class="status-dot" title="Digital twin online"></span>
                    </div>
                    <div class="header-text">
                        <h1>Solarin Ayomide</h1>
                        <p>Digital twin · Web developer &amp; digital strategist. Ask about my work, stack, or collaborations.</p>
                    </div>
                </div>
                <div class="gallery" aria-hidden="true">
                    <img src="/images/gallery-1.jpg" alt="" onerror="this.remove()" />
                    <img src="/images/gallery-2.jpg" alt="" onerror="this.remove()" />
                    <img src="/images/gallery-3.jpg" alt="" onerror="this.remove()" />
                </div>
            </header>

            <div class="chat-panel">
                <div class="chat-scroll" id="chat" role="log" aria-live="polite" aria-relevant="additions"></div>
                <div class="row row-bot typing-row" id="typingRow">
                    <img class="msg-avatar" src="{profile}" alt="" onerror="this.onerror=null;this.src='{fallback}'" />
                    <div class="typing" id="typing"><span></span><span></span><span></span></div>
                </div>
                <div class="composer">
                    <input type="text" id="message" placeholder="Message…" autocomplete="off" maxlength="2000" />
                    <button type="button" id="sendBtn" onclick="sendMessage()" aria-label="Send message">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/></svg>
                    </button>
                </div>
            </div>

            <p class="links">
                <a href="mailto:solarinayosam@gmail.com">Email</a>
                · <a href="https://linkedin.com/in/solarinayo" target="_blank" rel="noopener">LinkedIn</a>
                · <a href="https://solarinayo.vercel.app" target="_blank" rel="noopener">Portfolio</a>
            </p>
        </div>
        <script>
            const chatDiv = document.getElementById('chat');
            const messageInput = document.getElementById('message');
            const sendBtn = document.getElementById('sendBtn');
            const typingRow = document.getElementById('typingRow');
            const typing = document.getElementById('typing');
            const profileSrc = {repr(profile)};
            const fallbackSrc = {repr(fallback)};

            function addMessage(text, isUser) {{
                const row = document.createElement('div');
                row.className = 'row ' + (isUser ? 'row-user' : 'row-bot');

                const av = document.createElement(isUser ? 'div' : 'img');
                if (isUser) {{
                    av.className = 'msg-avatar user';
                    av.textContent = 'You';
                }} else {{
                    av.className = 'msg-avatar';
                    av.src = profileSrc;
                    av.alt = 'Solarin';
                    av.onerror = function() {{ this.onerror = null; this.src = fallbackSrc; }};
                }}

                const bubble = document.createElement('div');
                bubble.className = 'bubble';
                bubble.textContent = text;

                row.appendChild(av);
                row.appendChild(bubble);
                chatDiv.appendChild(row);
                chatDiv.scrollTop = chatDiv.scrollHeight;
            }}

            function setLoading(on) {{
                messageInput.disabled = on;
                sendBtn.disabled = on;
                typingRow.classList.toggle('on', on);
                typing.classList.toggle('on', on);
                const scrollEl = chatDiv.parentElement;
                if (on) scrollEl.scrollTop = scrollEl.scrollHeight;
            }}

            async function sendMessage() {{
                const message = messageInput.value.trim();
                if (!message) return;

                addMessage(message, true);
                messageInput.value = '';
                setLoading(true);

                try {{
                    const response = await fetch('/api/chat', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ message: message }})
                    }});
                    const data = await response.json();
                    addMessage(data.response || '…', false);
                }} catch (e) {{
                    addMessage('Something went wrong. Please try again.', false);
                }} finally {{
                    setLoading(false);
                    chatDiv.scrollTop = chatDiv.scrollHeight;
                }}
            }}

            messageInput.addEventListener('keydown', function(e) {{
                if (e.key === 'Enter' && !e.shiftKey) {{
                    e.preventDefault();
                    sendMessage();
                }}
            }});

            addMessage(
                "Hey — I'm Solarin's digital twin. Ask me about projects, payments & onboarding systems, or how we could work together.",
                false
            );
        </script>
    </body>
    </html>
    """


@app.post("/api/chat")
async def chat(request: ChatRequest):
    message = request.message

    # Contact info check
    if any(word in message.lower() for word in ["reach", "contact", "email", "phone"]):
        return {"response": "📧 solarinayosam@gmail.com | 📞 +234 807 777 5678 | 🔗 linkedin.com/in/solarinayo"}

    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            return {"response": response.choices[0].message.content}
        except Exception:
            return {"response": "I'm Solarin Ayomide – web developer and digital strategist. What would you like to know about my work?"}

    return {"response": "Hi! I'm Solarin. I build web apps, payment systems, and automation tools. How can I help?"}

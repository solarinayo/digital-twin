import html
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from openai import APIError, AuthenticationError, OpenAI, RateLimitError
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Baseline browser security headers (no secrets in responses)."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=(), payment=()",
        )
        return response


app = FastAPI()
app.add_middleware(SecurityHeadersMiddleware)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_BACKEND_DIR = Path(__file__).resolve().parent.parent

load_dotenv(_REPO_ROOT / ".env", override=False)
load_dotenv(_BACKEND_DIR / ".env", override=True)
_IMAGES_DIR = _REPO_ROOT / "public" / "images"
_KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
_FRONTEND_DIR = _REPO_ROOT / "frontend"
_FRONTEND_STATIC = _FRONTEND_DIR / "static"


def _load_knowledge_markdown() -> str:
    if not _KNOWLEDGE_DIR.is_dir():
        return ""
    chunks: list[str] = []
    for path in sorted(_KNOWLEDGE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if text:
            title = path.stem.replace("_", " ").title()
            chunks.append(f"### {title}\n{text}")
    return "\n\n".join(chunks)


if _FRONTEND_STATIC.is_dir():
    app.mount(
        "/static",
        StaticFiles(directory=str(_FRONTEND_STATIC)),
        name="frontend_static",
    )

if _IMAGES_DIR.is_dir():
    app.mount("/images", StaticFiles(directory=str(_IMAGES_DIR)), name="images")

# Initialize OpenAI (reads OPENAI_API_KEY from env or backend/.env)
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None
if not client:
    logger.warning(
        "OPENAI_API_KEY is not set — /api/chat will return a setup hint until you export "
        "the key or create backend/.env (see README)."
    )

_BASE_SYSTEM_PROMPT = """You are Solarin Ayomide's digital twin – a tech builder and digital strategist focused on creating scalable solutions at the intersection of software, education, and growth marketing.

## Communication Style
- Friendly, professional, and solution-oriented
- Keep responses concise (2-3 sentences max for simple questions)
- Answer naturally as Solarin Ayomide. Use "I" statements."""

_extra = _load_knowledge_markdown()
SYSTEM_PROMPT = (
    _BASE_SYSTEM_PROMPT + "\n\n## Knowledge base (from repository)\n" + _extra
    if _extra
    else _BASE_SYSTEM_PROMPT
)

PROFILE_IMG = (
    "https://res.cloudinary.com/dc2wrlebl/image/upload/v1775226566/Ayomide_xakvsf.jpg"
)
AVATAR_FALLBACK = "/images/avatar.svg"


def _load_index_html(profile: str, fallback: str) -> str:
    path = _FRONTEND_DIR / "index.html"
    text = path.read_text(encoding="utf-8")
    safe_p = html.escape(profile, quote=True)
    safe_f = html.escape(fallback, quote=True)
    return text.replace("__PROFILE_IMG__", safe_p).replace("__FALLBACK_IMG__", safe_f)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


@app.get("/", response_class=HTMLResponse)
async def root():
    return _load_index_html(PROFILE_IMG, AVATAR_FALLBACK)


@app.post("/api/chat")
async def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        return {"response": "Send a non-empty message and I’ll reply."}

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
        except AuthenticationError:
            logger.error("OpenAI authentication failed (check API key)")
            return {
                "response": "The AI service rejected the API key. If you’re the operator, check the key in Secret Manager / env and try again."
            }
        except RateLimitError:
            logger.warning("OpenAI rate limit hit")
            return {"response": "Too many requests right now — please wait a moment and try again."}
        except APIError as err:
            logger.warning("OpenAI API error: %s", getattr(err, "type", type(err).__name__))
            return {"response": "I couldn’t reach the AI service just now. Try again in a bit."}
        except Exception:
            # Avoid exc_info: tracebacks from HTTP clients can include Authorization headers.
            logger.error("Unexpected error during chat completion")
            return {"response": "I'm Solarin Ayomide – web developer and digital strategist. What would you like to know about my work?"}

    return {
        "response": (
            "I’m not connected to the language model yet — **OPENAI_API_KEY** is missing. "
            "Create `backend/.env` with `OPENAI_API_KEY=sk-...` (or export it in your shell) "
            "and restart `uvicorn`. After that, ask again and I’ll answer from my full profile."
        )
    }

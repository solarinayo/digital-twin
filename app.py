import os
import gradio as gr
from openai import OpenAI

api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

SYSTEM_PROMPT = """You are Solarin Ayomide's digital twin – a tech builder and digital strategist focused on creating scalable solutions at the intersection of software, education, and growth marketing.

## Your Background
- Web developer with 3+ years experience creating user-centric websites and applications
- Built platforms: Pinnaview Networks (utility bill payment, 12k+ users), Skyned Consults (placed 4000+ students), Jekacode Africa, WithoutTheBox.ng, Unicollegelink.com
- Education: B.Sc. Botany (Second Class Upper) from FUNAAB
- Certifications: Web3 (Moralis), Cybersecurity (IBM Digital, CISCO), Web Development (Dominion Academy, Code Lagos)
- Volunteer: Speaker at Binance Tech Meetup 2022, Team Lead at EJEKA CODE (free coding classes outreach)

## What You Do
- Build and manage systems for tech bootcamps (payment integrations with Paystack, multi-step user onboarding, admin dashboards)
- Use tools like Bolt AI, Google Sheets, MongoDB for database systems
- Structure backend logic, optimize user flows, ensure seamless data sync
- Create high-converting campaigns and localized tech content for Nigerian audiences

## Your Interests
- Agentic systems, automation, building tools that empower people to learn, earn, and scale in tech
- Blending technical execution with cultural relevance for Nigerian market

## Communication Style
- Friendly, professional, and solution-oriented
- Keep responses concise (2-3 sentences max for simple questions)
- Be authentic and helpful

Answer naturally as Solarin Ayomide. Use "I" statements."""

CONTACT_INFO = """
Email: solarinayosam@gmail.com
Phone: +234 807 777 5678
LinkedIn: linkedin.com/in/solarinayo
Portfolio: solarinayo.vercel.app
"""

FALLBACK_RESPONSES = {
    "hi": "Hi there! I'm Solarin Ayomide, a web developer and digital strategist. I build web applications, payment systems, and automation tools. What would you like to know about my work?",
    "hello": "Hello! I'm Solarin. I specialize in full-stack development, payment integrations, and agentic AI systems. How can I help you today?",
    "what can you do": "I can help you learn about my web development experience, discuss collaboration opportunities, explain my technical skills (Python, JavaScript, Paystack, MongoDB), or share insights about building agentic systems for the Nigerian market. What specific area interests you?",
    "who are you": "I'm Solarin Ayomide – a web developer with 3+ years of experience building platforms like Pinnaview Networks (12k+ users) and Skyned Consults. I'm passionate about creating scalable solutions at the intersection of software, education, and growth marketing.",
    "your skills": "My technical skills include full-stack web development (Python, JavaScript), payment integrations (Paystack), database systems (MongoDB, Google Sheets), automation tools (Bolt AI), and building agentic systems. I've helped platforms achieve 123.6% growth in user registrations.",
    "experience": "I have 3+ years of experience working with Pinnaview Networks, Skyned Consults, Sponsorit Africa, and leading EJEKA CODE. I've built payment systems, user onboarding flows, admin dashboards, and scalable web applications.",
}


def _content_to_text(content, max_len: int) -> str | None:
    if isinstance(content, str):
        return content[:max_len]
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
        if parts:
            return " ".join(parts)[:max_len]
    return None


def _history_to_api_messages(history, max_messages: int = 6):
    """Gradio 6+ passes OpenAI-style message dicts in history."""
    if not history:
        return []
    out = []
    for msg in history[-max_messages:]:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role")
        if role not in ("user", "assistant"):
            continue
        text = _content_to_text(msg.get("content"), 500)
        if text:
            out.append({"role": role, "content": text})
    return out


def get_fallback_response(message):
    message_lower = message.lower().strip()

    if message_lower in FALLBACK_RESPONSES:
        return FALLBACK_RESPONSES[message_lower]

    if any(word in message_lower for word in ["skill", "technolog", "stack", "tool"]):
        return "My tech stack includes Python, JavaScript, MongoDB, Google Sheets, Paystack API, Bolt AI, and various automation tools. I focus on building scalable web apps and payment systems for the Nigerian market."

    if any(word in message_lower for word in ["project", "build", "create", "make"]):
        return "I build web applications, payment integration systems, multi-step user onboarding flows, admin dashboards, and automation tools. Recently, I've been focused on agentic systems that help people learn and earn in tech."

    if any(word in message_lower for word in ["interest", "passion", "like"]):
        return "I'm passionate about agentic systems, automation, and building tools that empower people to learn, earn, and scale in tech. I love blending technical execution with cultural relevance for Nigerian audiences."

    return None


def chat(message, history):
    if not message:
        return ""

    contact_keywords = ["reach", "contact", "email", "phone", "call", "whatsapp", "get in touch"]
    if any(keyword in message.lower() for keyword in contact_keywords):
        return f"Thanks for asking. Here is how you can reach me:\n\n{CONTACT_INFO}\n\nLooking forward to connecting."

    if "collaborate" in message.lower() or "project" in message.lower():
        return """I'd love to collaborate! I focus on building scalable web applications, payment integrations (Paystack), and automation systems.

The best way to start is to send me:
1. A brief project overview
2. Your timeline and budget range
3. Any existing designs or requirements

Email me at solarinayosam@gmail.com. Let's build something impactful."""

    fallback = get_fallback_response(message)
    if fallback:
        return fallback

    if client:
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(_history_to_api_messages(history))
            messages.append({"role": "user", "content": message[:1000]})

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=300,
                timeout=10,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")

    return "I'm Solarin Ayomide – a web developer and digital strategist. You can ask me about my work experience, technical skills, collaboration opportunities, or contact me directly at solarinayosam@gmail.com. What specific information would you like?"


TWIN_CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Instrument+Sans:wght@400;500;600&display=swap');

.gradio-container {
  font-family: 'Instrument Sans', ui-sans-serif, system-ui, sans-serif !important;
  max-width: none !important;
  width: 100% !important;
}
.gradio-container .contain { max-width: none !important; }

.gradio-chatbot { border: 1px solid #1a1a1a !important; background: #fafafa !important; }
.gradio-chatbot .message.user, .gradio-chatbot .user {
  background: #1a1a1a !important; color: #f5f5f5 !important; border: none !important;
}
.gradio-chatbot .message.bot, .gradio-chatbot .bot {
  background: #fff !important; color: #1a1a1a !important; border: 1px solid #d0d0d0 !important;
}

.gradio-container button.primary, .gradio-container .lg.primary {
  background: #1a1a1a !important; color: #fafafa !important; border: 1px solid #1a1a1a !important;
}
.gradio-container textarea, .gradio-container input[type="text"] {
  border: 1px solid #1a1a1a !important; background: #fff !important; color: #1a1a1a !important;
}
.gradio-container .examples button {
  border: 1px solid #1a1a1a !important; background: #fff !important; color: #1a1a1a !important;
  font-family: 'IBM Plex Mono', ui-monospace, monospace !important;
  font-size: 0.8rem !important;
}
.gradio-container .examples button:hover {
  background: #1a1a1a !important; color: #fafafa !important;
}
"""

HEADER_HTML = """
<style>
.dt-bar {
  font-family: 'Instrument Sans', ui-sans-serif, system-ui, sans-serif;
  display: flex; align-items: center; gap: 1rem;
  padding: 0.75rem 0 1rem 0;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid #ccc;
}
.dt-bar img {
  width: 48px; height: 48px; object-fit: cover;
  filter: grayscale(100%); border: 1px solid #1a1a1a;
}
.dt-bar h1 {
  margin: 0; font-size: 1.05rem; font-weight: 600; letter-spacing: -0.02em; color: #0a0a0a;
}
.dt-bar p { margin: 0.15rem 0 0 0; font-size: 0.8rem; color: #555; }
</style>
<div class="dt-bar">
  <img src="https://res.cloudinary.com/dc2wrlebl/image/upload/v1775226566/Ayomide_xakvsf.jpg" alt="Solarin Ayomide">
  <div>
    <h1>Digital twin</h1>
    <p>Solarin Ayomide — ask anything.</p>
  </div>
</div>
"""

try:
    _Mono = getattr(gr.themes, "Monochrome", None)
    _theme = (
        _Mono(primary_hue="gray", secondary_hue="gray").set(
            body_background_fill="#ececec",
            block_background_fill="#ffffff",
            block_border_color="#c8c8c8",
            body_text_color="#1a1a1a",
            button_primary_background_fill="#1a1a1a",
            button_primary_text_color="#fafafa",
        )
        if _Mono
        else None
    )
except Exception:
    _theme = None

with gr.Blocks(theme=_theme, css=TWIN_CSS) as demo:
    gr.HTML(HEADER_HTML)
    gr.ChatInterface(
        fn=chat,
        description=None,
        examples=["What do you work on?", "How do we collaborate?"],
        fill_width=True,
        fill_height=True,
        flagging_mode="never",
    )

if __name__ == "__main__":
    demo.launch(
        auth=None,
        auth_dependency=None,
        footer_links=[],
    )

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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

.gradio-container {
  font-family: 'Plus Jakarta Sans', ui-sans-serif, system-ui, sans-serif !important;
  max-width: none !important;
  width: 100% !important;
}
.gradio-container .contain { max-width: none !important; }

/* Chat area */
.gradio-chatbot {
  border: 1px solid #e2e8f0 !important;
  border-radius: 12px !important;
  background: #f8fafc !important;
}
.gradio-chatbot .message.user, .gradio-chatbot .user {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46a1 100%) !important;
  color: #fff !important;
  border: none !important;
}
.gradio-chatbot .message.bot, .gradio-chatbot .bot {
  background: #fff !important;
  color: #1e293b !important;
  border: 1px solid #e2e8f0 !important;
}

/* Example chips */
.gradio-container .examples button {
  border: 1px solid #c7d2fe !important;
  background: #fff !important;
  color: #4338ca !important;
  border-radius: 999px !important;
  font-size: 0.8125rem !important;
}
.gradio-container .examples button:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: #fff !important;
  border-color: transparent !important;
}

/* Composer: textarea + Send (elem_id twin-composer) */
#twin-composer {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
}
#twin-composer .wrap,
#twin-composer .container {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
}
#twin-composer .wrap {
  display: flex !important;
  flex-direction: row !important;
  align-items: stretch !important;
  gap: 0 !important;
}
#twin-composer .wrap > *:first-child {
  flex: 1 1 auto !important;
  min-width: 0 !important;
}
#twin-composer [data-testid="textbox"] {
  border-radius: 14px 0 0 14px !important;
  border: 2px solid #e2e8f0 !important;
  border-right: none !important;
  background: #fff !important;
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.08) !important;
  overflow: hidden !important;
}
#twin-composer textarea {
  padding: 14px 16px !important;
  font-size: 1rem !important;
  line-height: 1.5 !important;
  border: none !important;
  background: transparent !important;
  color: #1e293b !important;
  resize: vertical !important;
  min-height: 52px !important;
}
#twin-composer textarea:focus {
  outline: none !important;
  box-shadow: none !important;
}
#twin-composer [data-testid="textbox"]:focus-within {
  border-color: #a5b4fc !important;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2), 0 2px 12px rgba(102, 126, 234, 0.1) !important;
}
#twin-composer button,
#twin-composer .submit-btn,
#twin-composer button.primary {
  border-radius: 0 14px 14px 0 !important;
  border: 2px solid transparent !important;
  border-left: none !important;
  min-height: 52px !important;
  min-width: 108px !important;
  padding: 0 1.35rem !important;
  font-weight: 600 !important;
  font-size: 0.9375rem !important;
  letter-spacing: 0.03em !important;
  text-transform: none !important;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: #fff !important;
  box-shadow: 0 2px 12px rgba(118, 75, 162, 0.35) !important;
  align-self: stretch !important;
}
#twin-composer button:hover,
#twin-composer .submit-btn:hover {
  filter: brightness(1.06) !important;
  box-shadow: 0 4px 18px rgba(118, 75, 162, 0.45) !important;
}
"""

HEADER_HTML = """
<style>
.hero-wide {
  width: 100%;
  box-sizing: border-box;
  margin: 0 0 1.25rem 0;
  padding: clamp(1.5rem, 3vw, 2.25rem) clamp(1.25rem, 4vw, 2.5rem);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 14px;
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.35);
}
.hero-wide-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(1.25rem, 4vw, 2.75rem);
  flex-wrap: wrap;
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
}
.hero-photo-ring {
  flex-shrink: 0;
  padding: 5px;
  border-radius: 50%;
  background: linear-gradient(145deg, rgba(255,255,255,0.5), rgba(255,255,255,0.15));
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.hero-photo {
  display: block;
  width: clamp(132px, 22vw, 200px);
  height: clamp(132px, 22vw, 200px);
  border-radius: 50%;
  object-fit: cover;
  object-position: center 20%;
  border: 4px solid rgba(255,255,255,0.95);
}
.hero-copy {
  flex: 1 1 280px;
  text-align: center;
  color: #fff;
  min-width: min(100%, 260px);
}
.hero-copy h1 {
  margin: 0;
  font-size: clamp(1.35rem, 3.2vw, 1.85rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.2;
  text-shadow: 0 1px 2px rgba(0,0,0,0.15);
}
.hero-copy p {
  margin: 0.65rem 0 0 0;
  font-size: clamp(0.9rem, 1.8vw, 1.05rem);
  line-height: 1.5;
  opacity: 0.95;
  max-width: 42rem;
  margin-left: auto;
  margin-right: auto;
}
</style>
<div class="hero-wide">
  <div class="hero-wide-inner">
    <div class="hero-photo-ring">
      <img class="hero-photo" src="https://res.cloudinary.com/dc2wrlebl/image/upload/v1775226566/Ayomide_xakvsf.jpg" alt="Solarin Ayomide">
    </div>
    <div class="hero-copy">
      <h1>🤖 Solarin Ayomide — Digital Twin</h1>
      <p>Chat with a digital twin of Solarin Ayomide — tech builder, full-stack developer, and digital strategist.</p>
    </div>
  </div>
</div>
"""

_composer = gr.Textbox(
    show_label=False,
    placeholder="Ask about my work, stack, or collaboration…",
    lines=2,
    max_lines=16,
    scale=7,
    submit_btn="Send",
    elem_id="twin-composer",
    min_width=200,
    render=False,
)

with gr.Blocks(theme=None, css=TWIN_CSS) as demo:
    gr.HTML(HEADER_HTML)
    gr.ChatInterface(
        fn=chat,
        textbox=_composer,
        description="Hi — I'm Solarin Ayomide. Ask me about my work, background, or how we might collaborate.",
        examples=[
            "What do you focus on as a full-stack developer?",
            "How could we collaborate on a project?",
            "What's your experience with payment integrations?",
            "What technologies do you use?",
        ],
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

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


# Minimalist CSS - clean, simple, no gradients
MINIMAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

.gradio-container {
    max-width: 900px !important;
    margin: 0 auto !important;
    padding: 20px !important;
}

/* Header section */
.minimal-header {
    text-align: center;
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid #eaeaea;
}

.minimal-header img {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    object-fit: cover;
    margin-bottom: 16px;
    border: 1px solid #eaeaea;
}

.minimal-header h1 {
    font-size: 24px;
    font-weight: 600;
    margin: 0 0 8px 0;
    color: #1a1a1a;
}

.minimal-header p {
    font-size: 15px;
    color: #666;
    margin: 0;
    line-height: 1.5;
}

/* Chat area */
.gradio-chatbot {
    border: 1px solid #e5e5e5 !important;
    border-radius: 12px !important;
    background: #fafafa !important;
}

.gradio-chatbot .message.user {
    background: #1a1a1a !important;
    color: #fff !important;
    border-radius: 18px !important;
    padding: 10px 16px !important;
}

.gradio-chatbot .message.bot {
    background: #fff !important;
    color: #1a1a1a !important;
    border: 1px solid #e5e5e5 !important;
    border-radius: 18px !important;
    padding: 10px 16px !important;
}

/* Example buttons */
.gradio-container .examples button {
    border: 1px solid #e5e5e5 !important;
    background: #fff !important;
    color: #1a1a1a !important;
    border-radius: 20px !important;
    font-size: 13px !important;
    padding: 6px 14px !important;
    transition: all 0.2s ease !important;
}

.gradio-container .examples button:hover {
    background: #f5f5f5 !important;
    border-color: #ccc !important;
}

/* Text input */
.gradio-container textarea {
    border: 1px solid #e5e5e5 !important;
    border-radius: 12px !important;
    padding: 12px !important;
    font-size: 14px !important;
    background: #fff !important;
}

.gradio-container textarea:focus {
    border-color: #999 !important;
    outline: none !important;
}

/* Submit button */
.gradio-container button.primary {
    background: #1a1a1a !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
}

.gradio-container button.primary:hover {
    background: #333 !important;
}

/* Footer */
.minimal-footer {
    text-align: center;
    margin-top: 32px;
    padding-top: 20px;
    border-top: 1px solid #eaeaea;
    font-size: 12px;
    color: #999;
}

.minimal-footer a {
    color: #666;
    text-decoration: none;
}

.minimal-footer a:hover {
    text-decoration: underline;
}
"""

HEADER_HTML = """
<div class="minimal-header">
    <img src="https://res.cloudinary.com/dc2wrlebl/image/upload/v1775226566/Ayomide_xakvsf.jpg" alt="Solarin Ayomide">
    <h1>Solarin Ayomide</h1>
    <p>Tech builder & digital strategist • Full-stack developer • Agentic AI</p>
</div>
"""

_composer = gr.Textbox(
    show_label=False,
    placeholder="Ask about my work, skills, or collaboration...",
    lines=2,
    max_lines=16,
    scale=7,
    submit_btn="Send",
    elem_id="twin-composer",
    min_width=200,
    render=False,
)

with gr.Blocks(theme=None, css=MINIMAL_CSS) as demo:
    gr.HTML(HEADER_HTML)
    gr.ChatInterface(
        fn=chat,
        textbox=_composer,
        description="",
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
    
    gr.HTML("""
    <div class="minimal-footer">
        <span>⚡ Digital twin — answers based on CV & experience</span><br>
        <span style="font-size: 11px;">📧 solarinayosam@gmail.com | 🔗 <a href="https://linkedin.com/in/solarinayo" target="_blank">LinkedIn</a> | 🌐 <a href="https://solarinayo.vercel.app" target="_blank">Portfolio</a></span>
    </div>
    """)

if __name__ == "__main__":
    demo.launch(
        auth=None,
        auth_dependency=None,
        footer_links=[],
    )
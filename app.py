import os
import gradio as gr
from openai import OpenAI

# Initialize OpenAI client
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# Solarin Ayomide's profile
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

# Fallback responses for common questions when API fails
FALLBACK_RESPONSES = {
    "hi": "Hi there! I'm Solarin Ayomide, a web developer and digital strategist. I build web applications, payment systems, and automation tools. What would you like to know about my work?",
    "hello": "Hello! I'm Solarin. I specialize in full-stack development, payment integrations, and agentic AI systems. How can I help you today?",
    "what can you do": "I can help you learn about my web development experience, discuss collaboration opportunities, explain my technical skills (Python, JavaScript, Paystack, MongoDB), or share insights about building agentic systems for the Nigerian market. What specific area interests you?",
    "who are you": "I'm Solarin Ayomide – a web developer with 3+ years of experience building platforms like Pinnaview Networks (12k+ users) and Skyned Consults. I'm passionate about creating scalable solutions at the intersection of software, education, and growth marketing.",
    "your skills": "My technical skills include full-stack web development (Python, JavaScript), payment integrations (Paystack), database systems (MongoDB, Google Sheets), automation tools (Bolt AI), and building agentic systems. I've helped platforms achieve 123.6% growth in user registrations.",
    "experience": "I have 3+ years of experience working with Pinnaview Networks, Skyned Consults, Sponsorit Africa, and leading EJEKA CODE. I've built payment systems, user onboarding flows, admin dashboards, and scalable web applications.",
}

def get_fallback_response(message):
    """Return a fallback response for common questions"""
    message_lower = message.lower().strip()
    
    # Check exact matches
    if message_lower in FALLBACK_RESPONSES:
        return FALLBACK_RESPONSES[message_lower]
    
    # Check for keywords
    if any(word in message_lower for word in ["skill", "technolog", "stack", "tool"]):
        return "My tech stack includes Python, JavaScript, MongoDB, Google Sheets, Paystack API, Bolt AI, and various automation tools. I focus on building scalable web apps and payment systems for the Nigerian market."
    
    if any(word in message_lower for word in ["project", "build", "create", "make"]):
        return "I build web applications, payment integration systems, multi-step user onboarding flows, admin dashboards, and automation tools. Recently, I've been focused on agentic systems that help people learn and earn in tech."
    
    if any(word in message_lower for word in ["interest", "passion", "like"]):
        return "I'm passionate about agentic systems, automation, and building tools that empower people to learn, earn, and scale in tech. I love blending technical execution with cultural relevance for Nigerian audiences."
    
    return None

def chat(message, history):
    """Handle chat messages with fallback support"""
    if not message:
        return ""
    
    # Check for contact info
    contact_keywords = ["reach", "contact", "email", "phone", "call", "whatsapp", "get in touch"]
    if any(keyword in message.lower() for keyword in contact_keywords):
        return f"Thanks for asking. Here is how you can reach me:\n\n{CONTACT_INFO}\n\nLooking forward to connecting."
    
    # Check for collaboration
    if "collaborate" in message.lower() or "project" in message.lower():
        return """I'd love to collaborate! I focus on building scalable web applications, payment integrations (Paystack), and automation systems. 

The best way to start is to send me:
1. A brief project overview
2. Your timeline and budget range
3. Any existing designs or requirements

Email me at solarinayosam@gmail.com. Let's build something impactful."""
    
    # Try fallback first for common questions
    fallback = get_fallback_response(message)
    if fallback:
        return fallback
    
    # Try OpenAI API if available
    if client:
        try:
            # Build conversation history
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            if history:
                for pair in history[-3:]:  # Only last 3 exchanges for context
                    if len(pair) >= 2:
                        messages.append({"role": "user", "content": pair[0][:500]})  # Limit length
                        messages.append({"role": "assistant", "content": pair[1][:500]})
            
            messages.append({"role": "user", "content": message[:1000]})  # Limit message length
            
            # Call API with timeout
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=300,  # Reduced for faster response
                timeout=10  # 10 second timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            # Fall through to generic response
    
    # Ultimate fallback
    return "I'm Solarin Ayomide – a web developer and digital strategist. You can ask me about my work experience, technical skills, collaboration opportunities, or contact me directly at solarinayosam@gmail.com. What specific information would you like?"

TWIN_CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Instrument+Sans:wght@400;500;600;700&display=swap');

.gradio-container {
  font-family: 'Instrument Sans', ui-sans-serif, system-ui, sans-serif !important;
  max-width: 920px !important;
}
.gradio-container .contain {
  padding-top: 0 !important;
}

/* Monochrome surfaces */
.gradio-container,
footer.gradio-footer { background: #e8e8e8 !important; }

/* Chat panel */
.gradio-chatbot { border: 1px solid #1a1a1a !important; background: #fafafa !important; }
.gradio-chatbot .message.user,
.gradio-chatbot .user { background: #1a1a1a !important; color: #f5f5f5 !important; border: none !important; }
.gradio-chatbot .message.bot,
.gradio-chatbot .bot { background: #ffffff !important; color: #1a1a1a !important; border: 1px solid #d0d0d0 !important; }

/* Inputs & primary actions */
.gradio-container button.primary,
.gradio-container .lg.primary {
  background: #1a1a1a !important;
  color: #fafafa !important;
  border: 1px solid #1a1a1a !important;
}
.gradio-container button.primary:hover,
.gradio-container .lg.primary:hover {
  background: #000 !important;
  border-color: #000 !important;
}
.gradio-container textarea, .gradio-container input[type="text"] {
  border: 1px solid #1a1a1a !important;
  background: #fff !important;
  color: #1a1a1a !important;
}
.gradio-container .block { border-color: #c8c8c8 !important; }

/* Example chips */
.gradio-container .examples button {
  border: 1px solid #1a1a1a !important;
  background: #fff !important;
  color: #1a1a1a !important;
  font-family: 'IBM Plex Mono', ui-monospace, monospace !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.02em;
}
.gradio-container .examples button:hover {
  background: #1a1a1a !important;
  color: #fafafa !important;
}
"""

HEADER_HTML = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<style>
.dt-shell {
  font-family: 'Instrument Sans', ui-sans-serif, system-ui, sans-serif;
  background: #0a0a0a;
  color: #f0f0f0;
  border: 1px solid #1a1a1a;
  margin: 0 0 1.25rem 0;
  position: relative;
  overflow: hidden;
}
.dt-shell::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 24px 24px;
  pointer-events: none;
}
.dt-inner {
  position: relative;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 1.5rem;
  align-items: stretch;
  padding: 1.35rem 1.5rem;
}
@media (max-width: 640px) {
  .dt-inner { grid-template-columns: 1fr; text-align: center; justify-items: center; }
}
.dt-rail {
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
  font-size: 0.65rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #737373;
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  border-left: 1px solid #262626;
  padding-left: 0.65rem;
  align-self: center;
  order: 2;
}
@media (max-width: 640px) {
  .dt-rail { writing-mode: horizontal-tb; transform: none; border-left: none; border-top: 1px solid #262626; padding: 0.5rem 0 0; width: 100%; text-align: center; order: 3; }
}
.dt-main { order: 1; display: flex; gap: 1.25rem; align-items: center; flex-wrap: wrap; }
.dt-photo-wrap {
  flex-shrink: 0;
  border: 1px solid #404040;
  padding: 3px;
  background: #141414;
}
.dt-photo {
  width: 88px;
  height: 88px;
  object-fit: cover;
  display: block;
  filter: grayscale(100%);
}
.dt-copy { min-width: 0; flex: 1; }
.dt-kicker {
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
  font-size: 0.7rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #a3a3a3;
  margin: 0 0 0.4rem 0;
}
.dt-title {
  font-size: clamp(1.35rem, 3.5vw, 1.75rem);
  font-weight: 600;
  letter-spacing: -0.03em;
  margin: 0 0 0.35rem 0;
  line-height: 1.15;
  color: #fafafa;
}
.dt-sub {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.45;
  color: #a3a3a3;
  max-width: 36rem;
}
.dt-status {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin-top: 0.65rem;
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
  font-size: 0.65rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #737373;
}
.dt-dot {
  width: 6px;
  height: 6px;
  background: #fafafa;
  animation: dt-pulse 2s ease-in-out infinite;
}
@keyframes dt-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.25; }
}
</style>
<div class="dt-shell">
  <div class="dt-inner">
    <div class="dt-rail">Digital twin · live interface</div>
    <div class="dt-main">
      <div class="dt-photo-wrap">
        <img class="dt-photo" src="https://res.cloudinary.com/dc2wrlebl/image/upload/v1775226566/Ayomide_xakvsf.jpg" alt="Solarin Ayomide">
      </div>
      <div class="dt-copy">
        <p class="dt-kicker">Solarin Ayomide</p>
        <h1 class="dt-title">Twin session</h1>
        <p class="dt-sub">Ask about work, stack, projects, or collaboration. Responses mirror CV-backed context and tone.</p>
        <div class="dt-status"><span class="dt-dot" aria-hidden="true"></span> Session active</div>
      </div>
    </div>
  </div>
</div>
"""

try:
    _Mono = getattr(gr.themes, "Monochrome", None)
    if _Mono is not None:
        _theme = _Mono(
            primary_hue="gray",
            secondary_hue="gray",
            font=["Instrument Sans", "ui-sans-serif", "system-ui", "sans-serif"],
            font_mono=["IBM Plex Mono", "ui-monospace", "monospace"],
        ).set(
            body_background_fill="#e8e8e8",
            block_background_fill="#ffffff",
            block_border_color="#c8c8c8",
            block_label_text_color="#1a1a1a",
            body_text_color="#1a1a1a",
            button_primary_background_fill="#1a1a1a",
            button_primary_text_color="#fafafa",
        )
    else:
        _theme = None
except Exception:
    _theme = None

with gr.Blocks(theme=_theme, css=TWIN_CSS) as demo:
    gr.HTML(HEADER_HTML)

    gr.ChatInterface(
        fn=chat,
        description="Input below. Plain language; technical detail on request.",
        examples=[
            "What do you focus on as a full-stack developer?",
            "How could we collaborate on a project?",
            "What's your experience with payment integrations?",
            "Tell me about your work at Pinnaview Networks",
            "What are you interested in building right now?",
            "What technologies do you use?",
        ],
    )

if __name__ == "__main__":
    demo.launch()
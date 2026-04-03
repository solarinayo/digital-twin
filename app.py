import os
import gradio as gr
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Solarin Ayomide's profile (based on CV)
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
- If asked something outside your knowledge, suggest a call or ask for a short brief
- Keep responses concise but helpful

Answer naturally as Solarin Ayomide. Use "I" statements. Be authentic and helpful."""

CONTACT_INFO = """
📧 Email: solarinayosam@gmail.com
📱 Phone: +234 807 777 5678
🔗 LinkedIn: linkedin.com/in/solarinayo
🌐 Portfolio: solarinayo.vercel.app
"""

def chat(message, history):
    """Handle chat messages"""
    if not message:
        return ""
    
    # Check if asking for contact info
    contact_keywords = ["reach", "contact", "email", "phone", "call", "whatsapp", "get in touch"]
    if any(keyword in message.lower() for keyword in contact_keywords):
        return f"Thanks for asking! Here's how you can reach me:\n\n{CONTACT_INFO}\n\nLooking forward to connecting! 🚀"
    
    # Check if asking about collaboration
    if "collaborate" in message.lower() or "project" in message.lower():
        return """I'd love to collaborate! I focus on building scalable web applications, payment integrations (Paystack), and automation systems. 

The best way to start is to send me:
1. A brief project overview
2. Your timeline and budget range
3. Any existing designs or requirements

You can reach me at solarinayosam@gmail.com or +234 807 777 5678. Let's build something impactful! 🚀"""
    
    try:
        # Build conversation history for OpenAI (multi-turn memory)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for user_msg, bot_msg in history:  # history is list of (user, bot) tuples
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": bot_msg})
        messages.append({"role": "user", "content": message})

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Having a technical hiccup. Please try again or reach out directly at solarinayosam@gmail.com."


# Create Gradio interface
with gr.Blocks() as demo:
    gr.HTML("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="margin: 0;">🤖 Solarin Ayomide — Digital Twin</h1>
        <p style="margin: 10px 0 0;">Chat with a digital twin of Solarin Ayomide — tech builder, full-stack developer, and digital strategist with expertise in web development, payment integrations, and agentic AI systems.</p>
    </div>
    """)

    gr.ChatInterface(
        fn=chat,
        description="Hi — I'm Solarin Ayomide. Ask me about my work, background, or how we might collaborate. If your question needs detail I don't have here, I may suggest a call or ask you to share a short brief.",
        examples=[
            "What do you focus on as a full-stack developer?",
            "How could we collaborate on a project?",
            "What's your experience with payment integrations?",
            "Tell me about your work at Pinnaview Networks",
            "What are you interested in building right now?"
        ]
    )

    gr.HTML("""
    <footer style="text-align: center; margin-top: 20px; padding: 10px; color: #666; font-size: 0.8em;">
        ⚡ Solarin Ayomide's digital twin — answers based on his CV and professional experience<br>
        📧 solarinayosam@gmail.com | 🔗 <a href="https://linkedin.com/in/solarinayo" target="_blank">LinkedIn</a> | 🌐 <a href="https://solarinayo.vercel.app" target="_blank">Portfolio</a>
    </footer>
    """)

if __name__ == "__main__":
    demo.launch()
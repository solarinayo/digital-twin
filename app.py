import os
import gradio as gr
from openai import OpenAI
import time

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
📧 Email: solarinayosam@gmail.com
📱 Phone: +234 807 777 5678
🔗 LinkedIn: linkedin.com/in/solarinayo
🌐 Portfolio: solarinayo.vercel.app
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
        return f"Thanks for asking! Here's how you can reach me:\n\n{CONTACT_INFO}\n\nLooking forward to connecting! 🚀"
    
    # Check for collaboration
    if "collaborate" in message.lower() or "project" in message.lower():
        return """I'd love to collaborate! I focus on building scalable web applications, payment integrations (Paystack), and automation systems. 

The best way to start is to send me:
1. A brief project overview
2. Your timeline and budget range
3. Any existing designs or requirements

Email me at solarinayosam@gmail.com. Let's build something impactful! 🚀"""
    
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

# Create Gradio interface with image
with gr.Blocks() as demo:
    gr.HTML(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <img src="https://res.cloudinary.com/dc2wrlebl/image/upload/v1775226566/Ayomide_xakvsf.jpg" 
                 alt="Solarin Ayomide" 
                 style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid white;">
            <div>
                <h1 style="margin: 0;">🤖 Solarin Ayomide — Digital Twin</h1>
                <p style="margin: 10px 0 0;">Chat with a digital twin of Solarin Ayomide — tech builder, full-stack developer, and digital strategist</p>
            </div>
        </div>
    </div>
    """)

    gr.ChatInterface(
        fn=chat,
        description="Hi — I'm Solarin Ayomide. Ask me about my work, background, or how we might collaborate.",
        examples=[
            "What do you focus on as a full-stack developer?",
            "How could we collaborate on a project?",
            "What's your experience with payment integrations?",
            "Tell me about your work at Pinnaview Networks",
            "What are you interested in building right now?",
            "What technologies do you use?"
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
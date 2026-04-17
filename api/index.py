from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

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

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Solarin Ayomide - Digital Twin</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: #fafafa;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .chat-container {
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }
            .message {
                margin-bottom: 15px;
                padding: 10px 15px;
                border-radius: 18px;
            }
            .user-message {
                background: #1a1a1a;
                color: white;
                text-align: right;
            }
            .bot-message {
                background: #f0f0f0;
                color: #1a1a1a;
            }
            input, button {
                width: 100%;
                padding: 12px;
                margin-top: 10px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
            }
            button {
                background: #1a1a1a;
                color: white;
                cursor: pointer;
                border: none;
            }
            button:hover {
                background: #333;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 Solarin Ayomide - Digital Twin</h1>
            <p>Tech builder & digital strategist</p>
        </div>
        <div class="chat-container">
            <div id="chat"></div>
            <input type="text" id="message" placeholder="Ask about my work, skills, or collaboration...">
            <button onclick="sendMessage()">Send</button>
        </div>
        <script>
            const chatDiv = document.getElementById('chat');
            const messageInput = document.getElementById('message');
            
            function addMessage(text, isUser) {
                const msgDiv = document.createElement('div');
                msgDiv.className = 'message ' + (isUser ? 'user-message' : 'bot-message');
                msgDiv.textContent = text;
                chatDiv.appendChild(msgDiv);
                chatDiv.scrollTop = chatDiv.scrollHeight;
            }
            
            async function sendMessage() {
                const message = messageInput.value;
                if (!message) return;
                
                addMessage(message, true);
                messageInput.value = '';
                
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await response.json();
                addMessage(data.response, false);
            }
            
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
            
            addMessage("Hi! I'm Solarin Ayomide - web developer and digital strategist. Ask me about my work, skills, or collaboration opportunities!", false);
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
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return {"response": response.choices[0].message.content}
        except Exception as e:
            return {"response": "I'm Solarin Ayomide – web developer and digital strategist. What would you like to know about my work?"}
    
    return {"response": "Hi! I'm Solarin. I build web apps, payment systems, and automation tools. How can I help?"}
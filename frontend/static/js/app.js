const appRoot = document.getElementById('app-root');
const chatDiv = document.getElementById('chat');
const messageInput = document.getElementById('message');
const sendBtn = document.getElementById('sendBtn');
const typingRow = document.getElementById('typingRow');
const typing = document.getElementById('typing');
const profileSrc = appRoot.dataset.profile;
const fallbackSrc = appRoot.dataset.fallback;

function addMessage(text, isUser) {
    const row = document.createElement('div');
    row.className = 'row ' + (isUser ? 'row-user' : 'row-bot');

    const av = document.createElement(isUser ? 'div' : 'img');
    if (isUser) {
        av.className = 'msg-avatar user';
        av.textContent = 'You';
    } else {
        av.className = 'msg-avatar';
        av.src = profileSrc;
        av.alt = 'Solarin';
        av.onerror = function() { this.onerror = null; this.src = fallbackSrc; };
    }

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;

    row.appendChild(av);
    row.appendChild(bubble);
    chatDiv.appendChild(row);
    chatDiv.scrollTop = chatDiv.scrollHeight;
}

function setLoading(on) {
    messageInput.disabled = on;
    sendBtn.disabled = on;
    typingRow.classList.toggle('on', on);
    typing.classList.toggle('on', on);
    const scrollEl = chatDiv.parentElement;
    if (on) scrollEl.scrollTop = scrollEl.scrollHeight;
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    addMessage(message, true);
    messageInput.value = '';
    setLoading(true);

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();
        addMessage(data.response || '…', false);
    } catch (e) {
        addMessage('Something went wrong. Please try again.', false);
    } finally {
        setLoading(false);
        chatDiv.scrollTop = chatDiv.scrollHeight;
    }
}

messageInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

addMessage(
    "Hey — I'm Solarin's digital twin. Ask me about projects, payments & onboarding systems, or how we could work together.",
    false
);

window.sendMessage = sendMessage;

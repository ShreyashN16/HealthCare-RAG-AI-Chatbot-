// ── State ──────────────────────────────────────
const messages = document.getElementById('messages');
const wrapper = document.getElementById('messagesWrapper');
const input = document.getElementById('question');
const sendBtn = document.getElementById('sendBtn');
const welcomeCard = document.getElementById('welcomeCard');
const clearBtn = document.getElementById('clearBtn');
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebarToggle');
const menuBtn = document.getElementById('menuBtn');

let isLoading = false;

// ── Sidebar toggle ──────────────────────────────
menuBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    sidebarToggle.textContent = sidebar.classList.contains('collapsed') ? '›' : '‹';
});
sidebarToggle.addEventListener('click', () => {
    sidebar.classList.add('collapsed');
});

// ── Suggestion & chip clicks ────────────────────
document.querySelectorAll('.suggestion-item').forEach(el => {
    el.addEventListener('click', () => {
        input.value = el.dataset.q;
        ask();
    });
});
document.querySelectorAll('.chip').forEach(el => {
    el.addEventListener('click', () => {
        input.value = el.dataset.q;
        ask();
    });
});

// ── Clear chat ─────────────────────────────────
clearBtn.addEventListener('click', () => {
    messages.innerHTML = '';
    welcomeCard.style.display = '';
    welcomeCard.style.animation = 'none';
    requestAnimationFrame(() => welcomeCard.style.animation = '');
});

// ── Auto-resize textarea ────────────────────────
input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 160) + 'px';
});

// ── Enter to send (Shift+Enter = newline) ────────
input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        ask();
    }
});

// ── Scroll to bottom ─────────────────────────────
function scrollToBottom() {
    wrapper.scrollTo({ top: wrapper.scrollHeight, behavior: 'smooth' });
}

// ── Format timestamp ──────────────────────────────
function getTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// ── Append a message bubble ───────────────────────
function appendMessage(role, text) {
    // Hide welcome card on first message
    welcomeCard.style.display = 'none';

    const msg = document.createElement('div');
    msg.className = `msg ${role}`;

    const avatarEl = document.createElement('div');
    avatarEl.className = 'avatar';
    avatarEl.textContent = role === 'user' ? '👤' : '✚';

    const bubbleWrap = document.createElement('div');

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;

    const time = document.createElement('span');
    time.className = 'msg-time';
    time.textContent = getTime();

    bubbleWrap.appendChild(bubble);
    bubbleWrap.appendChild(time);
    msg.appendChild(avatarEl);
    msg.appendChild(bubbleWrap);
    messages.appendChild(msg);

    scrollToBottom();
    return bubble;
}

// ── Typing indicator ──────────────────────────────
function showTyping() {
    const msg = document.createElement('div');
    msg.className = 'msg bot';
    msg.id = 'typingMsg';

    const avatarEl = document.createElement('div');
    avatarEl.className = 'avatar';
    avatarEl.textContent = '✚';

    const typingBubble = document.createElement('div');
    typingBubble.className = 'typing-bubble';
    typingBubble.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';

    msg.appendChild(avatarEl);
    msg.appendChild(typingBubble);
    messages.appendChild(msg);
    scrollToBottom();
}

function hideTyping() {
    const t = document.getElementById('typingMsg');
    if (t) t.remove();
}

// ── Main ask function ─────────────────────────────
async function ask() {
    const question = input.value.trim();
    if (!question || isLoading) return;

    isLoading = true;
    sendBtn.disabled = true;
    input.value = '';
    input.style.height = 'auto';

    appendMessage('user', question);
    showTyping();

    try {
        const res = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });

        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        const data = await res.json();
        hideTyping();
        appendMessage('bot', data.answer || 'I could not find a relevant answer. Please try rephrasing.');
    } catch (err) {
        hideTyping();
        appendMessage('bot', '⚠️ Connection error. Please make sure the server is running and try again.');
        console.error(err);
    } finally {
        isLoading = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

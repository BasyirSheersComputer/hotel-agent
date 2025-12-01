document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    // Auto-focus input
    userInput.focus();

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    async function sendMessage() {
        const query = userInput.value.trim();
        if (!query) return;

        // Clear input
        userInput.value = '';

        // Add User Message
        addMessage(query, 'user');

        // Show Loading State
        const loadingId = addLoadingIndicator();

        try {
            // Call API
            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();

            // Remove Loading Indicator
            removeMessage(loadingId);

            if (response.ok) {
                // Add Agent Response
                // Format the answer to handle markdown-like syntax if needed
                const formattedAnswer = formatResponse(data.answer);
                addMessage(formattedAnswer, 'agent');
            } else {
                addMessage("I apologize, but I'm having trouble connecting to the server right now.", 'agent');
            }

        } catch (error) {
            removeMessage(loadingId);
            addMessage("I apologize, but I seem to be offline. Please check your connection.", 'agent');
            console.error('Error:', error);
        }
    }

    // Expose for quick buttons
    window.sendQuickQuery = (query) => {
        userInput.value = query;
        sendMessage();
    };

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);

        const avatarUrl = sender === 'agent' 
            ? 'https://ui-avatars.com/api/?name=Resort+Genius&background=0F4C81&color=fff'
            : 'https://ui-avatars.com/api/?name=Guest&background=D4AF37&color=fff';

        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageDiv.innerHTML = `
            <div class="avatar">
                <img src="${avatarUrl}" alt="${sender}">
            </div>
            <div class="message-content">
                <p>${text}</p>
                <span class="timestamp">${timestamp}</span>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function addLoadingIndicator() {
        const id = 'loading-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'agent-message');
        messageDiv.id = id;

        messageDiv.innerHTML = `
            <div class="avatar">
                <img src="https://ui-avatars.com/api/?name=Resort+Genius&background=0F4C81&color=fff" alt="Agent">
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        scrollToBottom();
        return id;
    }

    function removeMessage(id) {
        const element = document.getElementById(id);
        if (element) element.remove();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function formatResponse(text) {
        // Simple formatter to handle newlines and basic markdown
        // Convert **bold** to <strong>
        let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert - list items to <li>
        // This is a basic implementation. For full markdown, a library like marked.js is better.
        // We'll just handle newlines for now to keep it simple but readable.
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }
});

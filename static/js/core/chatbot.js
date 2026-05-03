document.addEventListener('DOMContentLoaded', function() {
    const launcher = document.getElementById('chatbotLauncher');
    const window = document.getElementById('chatbotWindow');
    const closeBtn = document.getElementById('chatbotClose');
    const input = document.getElementById('chatbotInput');
    const sendBtn = document.getElementById('chatbotSend');
    const messagesContainer = document.getElementById('chatbotMessages');
    const typingIndicator = document.getElementById('typingIndicator');
    const modeToggle = document.getElementById('chatbotModeToggle');
    let currentMode = 'general'; // 'general' o 'gym'

    // Toggle Mode
    modeToggle.addEventListener('click', () => {
        currentMode = currentMode === 'general' ? 'gym' : 'general';
        modeToggle.classList.toggle('gym-mode');
        
        // Actualizar iconos activos
        modeToggle.querySelectorAll('.mode-icon').forEach(icon => {
            icon.classList.toggle('active');
        });

        // Feedback visual en el placeholder
        input.placeholder = currentMode === 'gym' ? 'Pregunta sobre el gimnasio...' : 'Consejos de fitness...';
    });

    // Toggle Chat Window
    launcher.addEventListener('click', () => {
        window.classList.add('active');
        launcher.style.display = 'none';
        input.focus();
    });

    closeBtn.addEventListener('click', () => {
        window.classList.remove('active');
        launcher.style.display = 'flex';
    });

    // Send Message
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        
        if (sender === 'bot') {
            // Renderizar Markdown si es el bot
            messageDiv.innerHTML = marked.parse(text);
        } else {
            messageDiv.textContent = text;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async function handleSendMessage() {
        let message = input.value.trim();
        if (!message) return;

        // Si estamos en modo gym, añadir el prefijo automáticamente si no lo tiene
        const displayMessage = message; // Guardamos el mensaje original para mostrar en burbuja
        if (currentMode === 'gym' && !message.toLowerCase().startsWith('@gym')) {
            message = `@gym ${message}`;
        }

        addMessage(displayMessage, 'user');
        input.value = '';
        
        // Show typing indicator
        typingIndicator.style.display = 'block';
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            const response = await fetch('/chatbot/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            // Hide typing indicator
            typingIndicator.style.display = 'none';

            if (data.response) {
                addMessage(data.response, 'bot');
            } else {
                console.error('Chatbot error details:', data);
                addMessage('Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo más tarde.', 'bot');
            }
        } catch (error) {
            typingIndicator.style.display = 'none';
            addMessage('Error de conexión. Inténtalo más tarde.', 'bot');
            console.error('Chatbot error:', error);
        }
    }

    sendBtn.addEventListener('click', handleSendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendMessage();
    });

    // Handle Suggestions
    messagesContainer.addEventListener('click', (e) => {
        const btn = e.target.closest('.suggestion-btn');
        if (btn) {
            const query = btn.getAttribute('data-query');
            input.value = query;
            handleSendMessage();
            
            // Opcional: ocultar sugerencias después de click
            btn.closest('.chatbot-suggestions').style.display = 'none';
        }
    });

    // CSRF Helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

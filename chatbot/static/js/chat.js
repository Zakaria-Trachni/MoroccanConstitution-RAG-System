document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const questionForm = document.getElementById('question-form');
    const questionInput = document.getElementById('question-input');
    
    // Set API endpoint
    const API_URL = '/api/ask';
    
    // Event listener for form submission
    questionForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const question = questionInput.value.trim();
        if (!question) return;
        
        // Add user message to chat
        addMessage('user', question);
        
        // Clear input
        questionInput.value = '';
        
        // Show loading indicator
        const loadingElement = showLoading();
        
        // Get language selection
        const languageSelect = document.getElementById('language-select');
        const language = languageSelect.value;
        
        // Send question to API
        fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: question,
                session_id: window.sessionId,
                language: language
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove loading indicator
            loadingElement.remove();
            
            // Add bot response to chat
            addMessage('bot', data.text, data.relevant_articles);
        })
        .catch(error => {
            console.error('Error:', error);
            loadingElement.remove();
            
            // Add error message
            addMessage('system', 'Sorry, there was an error processing your question. Please try again.');
        });
    });
    
    // Function to add a message to the chat
    function addMessage(type, text, relevantArticles = []) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', type);
    
        let content = '';
    
        if (type === 'user' || type === 'bot') {
            const avatarSrc = type === 'user' ? '/static/img/user-avatar.png' : '/static/img/morocco-flag.png';
            content += `<img src="${avatarSrc}" alt="${type}" class="avatar">`;
        }
    
        content += '<div class="message-content"><p id="typing-effect"></p></div>';
        messageDiv.innerHTML = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    
        const paragraph = messageDiv.querySelector('#typing-effect');
        const words = text.split(/(\s+|<br>)/);  // Keep whitespace and newlines
        let index = 0;
    
        function typeNextWord() {
            if (index < words.length) {
                const word = words[index];
                paragraph.innerHTML += word;
                index++;
                setTimeout(typeNextWord, 50);
            }
        }
    
        if (type === 'bot') {
            typeNextWord();
        } else {
            // For user/system messages, display immediately
            paragraph.innerHTML = text.replace(/\n/g, '<br>');
        }
    }    
    
    // Function to show loading indicator
    function showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.classList.add('message', 'bot', 'loading');
        
        // Create loading animation
        loadingDiv.innerHTML = `
            <div class="message-content">
                <div class="loading">
                    <span>&bull;</span>
                    <span>&bull;</span>
                    <span>&bull;</span>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return loadingDiv;
    }
});
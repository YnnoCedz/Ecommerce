      // Scroll to the bottom of the chat history when the page loads
      window.onload = function() {
        var chatHistory = document.getElementById('chat-history');
        if (chatHistory) {
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
    };
    
    const chatHistory = document.getElementById('chat-history');
const recipientId = {{ selected_user_id }};  // Pass the selected user's ID from Flask

// Fetch messages periodically
async function fetchMessages() {
    try {
        const response = await fetch(`/api/messages/${recipientId}`);
        if (response.ok) {
            const data = await response.json();
            const messages = data.messages;
            updateChatHistory(messages);
        } else {
            console.error('Failed to fetch messages:', response.statusText);
        }
    } catch (error) {
        console.error('Error fetching messages:', error);
    }
}

// Update the chat history
function updateChatHistory(messages) {
    chatHistory.innerHTML = '';  // Clear existing messages
    messages.forEach(message => {
        const messageDiv = document.createElement('div');
        const isSent = message.sender_id == {{ session['user_id'] }};
        messageDiv.className = 'message ' + (isSent ? 'sent' : 'received');
        messageDiv.innerHTML = `
            <div class="message-bubble">
                <p>${message.message}</p>
                ${message.attachment_url ? `<a href="${message.attachment_url}" target="_blank">View Attachment</a>` : ''}
                <span class="timestamp">${message.timestamp}</span>
            </div>
        `;
        chatHistory.appendChild(messageDiv);
    });

    // Scroll to the bottom of the chat history
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Fetch messages every second
setInterval(fetchMessages, 1000);

// Handle form submission for sending messages
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');

chatForm.addEventListener('submit', async function (event) {
    event.preventDefault();

    const formData = new FormData(chatForm);

    try {
        const response = await fetch(`/chat/${recipientId}`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            messageInput.value = '';  // Clear the message input field
            fetchMessages();  // Refresh the chat history
        } else {
            console.error('Failed to send message:', response.statusText);
        }
    } catch (error) {
        console.error('Error sending message:', error);
    }
});

// Initial fetch
fetchMessages();
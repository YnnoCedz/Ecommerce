document.addEventListener("DOMContentLoaded", () => {
    // Fetch chat history on page load
    fetchChatHistory();

    // Send message logic
    document.getElementById("send-message").addEventListener("click", () => {
        const messageInput = document.getElementById("message-input");
        const fileInput = document.getElementById("file-upload");
        const formData = new FormData();
        formData.append("message", messageInput.value);
        if (fileInput.files.length > 0) {
            formData.append("attachment_url", fileInput.files[0]);
        }
        
        fetch("/chat/send", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                fetchChatHistory(); // Refresh chat history
                messageInput.value = ""; // Clear input
                fileInput.value = ""; // Reset file input
            } else {
                alert("Failed to send message");
            }
        });
    });
});

function fetchChatHistory() {
    fetch("/chat/history")
        .then(response => response.json())
        .then(data => {
            const chatHistory = document.getElementById("chat-history");
            chatHistory.innerHTML = ""; // Clear current messages
            data.messages.forEach(message => {
                const messageDiv = document.createElement("div");
                messageDiv.className = `message ${message.sent ? "sent" : "received"}`;
                messageDiv.innerHTML = `
                    <div class="message-bubble">
                        <p>${message.text}</p>
                        ${
                            message.attachment_url
                                ? `<a href="${message.attachment_url}" target="_blank">View Attachment</a>`
                                : ""
                        }
                        <span class="timestamp">${message.timestamp}</span>
                    </div>
                `;
                chatHistory.appendChild(messageDiv);
            });
            chatHistory.scrollTop = chatHistory.scrollHeight; // Auto-scroll
        });
}
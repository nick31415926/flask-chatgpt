// ✅ Ensure the DOM is fully loaded before accessing elements
document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");

    let API_URL = "http://127.0.0.1:5000"; // Default fallback
    let apiLoaded = false; // Flag to track API load status

    // ✅ Fetch LOCALHOST_IP from Flask backend
    async function fetchConfig() {
        try {
            const response = await fetch("/config");
            const data = await response.json();
            API_URL = data.api_url;
            apiLoaded = true;
            console.log("API URL Set to:", API_URL);
        } catch (error) {
            console.error("Failed to fetch config:", error);
        }
    }

    // ✅ Wait for `API_URL` to be set before making any requests
    async function waitForAPI() {
        while (!apiLoaded) {
            await new Promise(resolve => setTimeout(resolve, 100)); // Wait 100ms
        }
    }

    // ✅ Fetch and restore chat history from Redis on page load
    async function loadChatHistory() {
        try {
            await waitForAPI(); // Ensure API_URL is set before making requests
            const response = await fetch(`${API_URL}/history`);
            const data = await response.json();

            // ✅ Append stored messages to the chat box
            data.history.forEach(msg => {
                const sender = msg.role === "user" ? "You" : "ChatGPT";
                const className = msg.role === "user" ? "user-message" : "bot-message";
                appendMessage(sender, msg.content, className);
            });

        } catch (error) {
            console.error("Failed to load chat history:", error);
        }
    }

    // ✅ Fetch API config & load history on startup
    fetchConfig().then(() => {
        loadChatHistory(); // Ensure history loads after API_URL is set
    });
    
    // ✅ Send message when Enter key is pressed
    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });

    // ✅ Handle sending messages
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Append user message with blue chat bubble
        appendMessage("You", message, "user-message");
        userInput.value = "";

        // Show typing animation
        showTypingIndicator();

        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();

            // Remove typing animation
            removeTypingIndicator();

            // Append AI response with dark gray chat bubble
            appendMessage("ChatGPT", data.response, "bot-message");
        } catch (error) {
            console.error("Error:", error);
            removeTypingIndicator();
            appendMessage("Error", "Failed to connect to the server.", "bot-message");
        }
    }

    // ✅ Function to append messages with bubbles
    function appendMessage(sender, message, className) {
        if (!chatBox) return; // Ensure chatBox exists

        const msgElement = document.createElement("div");
        msgElement.classList.add("message", className);
        msgElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatBox.appendChild(msgElement);
        
        // ✅ Auto-scroll smoothly on mobile
        setTimeout(() => {
            chatBox.scrollTop = chatBox.scrollHeight;
        }, 100);
    }

    // ✅ Show Typing Animation
    function showTypingIndicator() {
        if (!chatBox || document.getElementById("typing-indicator")) return;

        const typingElement = document.createElement("div");
        typingElement.classList.add("typing-indicator");
        typingElement.id = "typing-indicator";
        typingElement.innerHTML = `<span></span><span></span><span></span>`;
        chatBox.appendChild(typingElement);

        setTimeout(() => {
            chatBox.scrollTop = chatBox.scrollHeight;
        }, 100);
    }

    // ✅ Remove Typing Animation
    function removeTypingIndicator() {
        const typingElement = document.getElementById("typing-indicator");
        if (typingElement) {
            typingElement.remove();
        }
    }

    // ✅ Clear Chat Function
    async function clearChat() {
        try {
            const response = await fetch(`${API_URL}/clear_history`, { method: "POST" });
    
            if (!response.ok) {
                throw new Error("Failed to clear chat history.");
            }
    
            // ✅ Clear frontend chat box immediately
            chatBox.innerHTML = ""; 
    
            // ✅ Confirm Redis is empty by reloading the history (should be empty)
            loadChatHistory(); 
    
            console.log("Chat history cleared.");
        } catch (error) {
            console.error("Error:", error);
        }
    }

    // ✅ Expose functions globally so they work with button clicks
    window.sendMessage = sendMessage;
    window.clearChat = clearChat;

    // ✅ Save chat as a text file with a timestamped filename
    function saveChat() {
        let chatContent = "";
        document.querySelectorAll(".message").forEach((msg) => {
            chatContent += msg.innerText + "\n\n"; // Format chat messages
        });

        // ✅ Generate timestamp for the filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, "-"); // Format: YYYY-MM-DDTHH-MM-SS
        const filename = `ChatGPT-Log-${timestamp}.txt`;

        // ✅ Create a downloadable text file
        const blob = new Blob([chatContent], { type: "text/plain" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    window.saveChat = saveChat;
});

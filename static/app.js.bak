// ✅ Select chat elements
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");

// ✅ API URL (using your Flask server IP from environment variable)
let API_URL = "http://127.0.0.1:5000"; // Default fallback

// Fetch LOCALHOST_IP from the Flask backend
fetch("/config")
  .then(response => response.json())
  .then(data => {
      API_URL = data.api_url;
      console.log("API URL Set to:", API_URL);
  })
  .catch(error => console.error("Failed to fetch config:", error));


// ✅ Focus input field when user taps anywhere on chat
document.addEventListener("click", () => {
    userInput.focus();
});

// ✅ Send message when Enter key is pressed (Mobile keyboard fix)
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
    if (document.getElementById("typing-indicator")) return;

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
        await fetch(`${API_URL}/clear_history`, { method: "POST" });
        chatBox.innerHTML = ""; // Clear chat on frontend
    } catch (error) {
        console.error("Error:", error);
    }
}

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
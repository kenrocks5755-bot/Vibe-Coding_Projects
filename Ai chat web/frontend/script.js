/**
 * script.js — AI Chat Frontend Logic
 * Handles: message sending, fetch to Flask backend, chat history, loading state, auto-resize
 */

// ============================================================
// CONFIGURATION
// ============================================================

/** Backend base URL. Change if Flask runs on a different port. */
const API_BASE = "http://localhost:5000";

// ============================================================
// DOM REFERENCES
// ============================================================

const chatFeed     = document.getElementById("chatFeed");
const messageInput = document.getElementById("messageInput");
const sendBtn      = document.getElementById("sendBtn");
const loadingBar   = document.getElementById("loadingBar");
const resetBtn     = document.getElementById("resetBtn");
const welcomeCard  = document.getElementById("welcomeCard");
const statusBadge  = document.getElementById("statusBadge");

// ============================================================
// STATE
// ============================================================

/** Tracks whether we're waiting for an API response */
let isLoading = false;

// ============================================================
// SEND MESSAGE FLOW
// ============================================================

/**
 * Main send function — validates input, renders user bubble,
 * calls the backend, then renders AI reply.
 */
async function sendMessage() {
  const text = messageInput.value.trim();

  // Guard: ignore empty input or double-send while loading
  if (!text || isLoading) return;

  // Hide welcome card on first message
  if (welcomeCard) welcomeCard.style.display = "none";

  // Render user's message in the feed
  appendMessage("user", text);

  // Clear & reset textarea height
  messageInput.value = "";
  autoResizeTextarea();

  // Enter loading state
  setLoading(true);

  try {
    // POST to Flask backend
    const res = await fetch(`${API_BASE}/chat`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ message: text }),
    });

    // Parse JSON response
    const data = await res.json();

    if (!res.ok) {
      // Backend returned an error status
      throw new Error(data.error || `Server error: ${res.status}`);
    }

    // Render AI reply
    appendMessage("ai", data.response);

  } catch (err) {
    // Network failure or backend error — show inline error bubble
    appendMessage("error", `⚠ ${err.message || "Could not reach the server. Is the backend running?"}`);
  } finally {
    // Always exit loading state
    setLoading(false);
  }
}

// ============================================================
// APPEND MESSAGE
// ============================================================

/**
 * Creates and appends a message bubble to the chat feed.
 * @param {"user"|"ai"|"error"} role
 * @param {string} text
 */
function appendMessage(role, text) {
  const wrapper = document.createElement("div");
  wrapper.classList.add("message");

  if (role === "user") {
    wrapper.classList.add("message--user");

    // Label
    const label  = document.createElement("div");
    label.classList.add("message__label");
    label.textContent = "You";

    // Bubble
    const bubble = document.createElement("div");
    bubble.classList.add("message__bubble");
    bubble.textContent = text;   // textContent to prevent XSS

    wrapper.appendChild(label);
    wrapper.appendChild(bubble);

  } else if (role === "ai") {
    wrapper.classList.add("message--ai");

    const label  = document.createElement("div");
    label.classList.add("message__label");
    label.textContent = "AI Assistant";

    const bubble = document.createElement("div");
    bubble.classList.add("message__bubble");
    // Use innerHTML here so markdown-like newlines render, but we sanitize first
    bubble.innerHTML = escapeHtml(text).replace(/\n/g, "<br/>");

    wrapper.appendChild(label);
    wrapper.appendChild(bubble);

  } else {
    // Error bubble (styled differently via CSS)
    wrapper.classList.add("message--ai", "message--error");

    const bubble = document.createElement("div");
    bubble.classList.add("message__bubble");
    bubble.textContent = text;

    wrapper.appendChild(bubble);
  }

  chatFeed.appendChild(wrapper);

  // Scroll to the latest message
  scrollToBottom();
}

// ============================================================
// HELPERS
// ============================================================

/**
 * Escape HTML special characters to prevent XSS injection.
 * @param {string} str
 * @returns {string}
 */
function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Scrolls the chat feed to the very bottom.
 */
function scrollToBottom() {
  chatFeed.scrollTop = chatFeed.scrollHeight;
}

/**
 * Toggles loading state: shows/hides the loading bar and disables/enables input.
 * @param {boolean} loading
 */
function setLoading(loading) {
  isLoading = loading;

  if (loading) {
    loadingBar.classList.add("visible");
    sendBtn.disabled   = true;
    sendBtn.textContent = "…";
  } else {
    loadingBar.classList.remove("visible");
    sendBtn.disabled    = false;
    sendBtn.textContent = "Send ↗";
  }

  // Scroll down so loading bar is visible
  scrollToBottom();
}

/**
 * Auto-resizes the textarea as the user types, up to max-height set in CSS.
 */
function autoResizeTextarea() {
  messageInput.style.height = "auto";
  messageInput.style.height = messageInput.scrollHeight + "px";
}

// ============================================================
// RESET CONVERSATION
// ============================================================

/**
 * Clears the frontend chat history and notifies the backend to clear its history too.
 */
async function resetConversation() {
  // Clear the DOM (keep the welcome card)
  chatFeed.innerHTML = "";
  chatFeed.appendChild(welcomeCard);
  welcomeCard.style.display = "";

  // Notify the backend to clear session history
  try {
    await fetch(`${API_BASE}/reset`, { method: "POST" });
  } catch (_) {
    // Silently ignore — the frontend is already reset
  }
}

// ============================================================
// EVENT LISTENERS
// ============================================================

// Send on button click
sendBtn.addEventListener("click", sendMessage);

// Send on Enter (but allow Shift+Enter for new line)
messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();         // prevent newline in textarea
    sendMessage();
  }
});

// Auto-resize textarea as user types
messageInput.addEventListener("input", autoResizeTextarea);

// Reset button
resetBtn.addEventListener("click", resetConversation);

// ============================================================
// INIT
// ============================================================

// Focus the input field on page load for immediate typing
messageInput.focus();

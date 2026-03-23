"""
Flask backend for AI Chat Web App
Uses local Ollama (qwen3) via its OpenAI-compatible endpoint
No API key needed — runs fully offline!
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

# Initialize Flask, pointing it to the frontend folder for static files
app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Allow Cross-Origin requests (still useful if testing from local file)
CORS(app)


@app.route('/')
def index():
    """Serve the main index.html file at the root URL"""
    return app.send_static_file('index.html')

# Initialize OpenAI client pointed at local Ollama endpoint
# Ollama exposes an OpenAI-compatible API at localhost:11434/v1
# No real API key needed — "ollama" is just a placeholder
client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

# Local model to use — must be pulled in Ollama (e.g. `ollama pull qwen3`)
MODEL = "qwen3"

# System prompt: defines the AI's personality
SYSTEM_PROMPT = "You are a helpful AI assistant."

# In-memory conversation history (resets when server restarts)
# Format: list of {"role": "user"|"assistant", "content": "..."}
conversation_history = []


@app.route("/chat", methods=["POST"])
def chat():
    """
    POST /chat
    Accepts: { "message": "user input" }
    Returns: { "response": "AI reply" }
    """
    data = request.get_json()

    # Validate incoming request
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field in request body"}), 400

    user_message = data["message"].strip()

    # Reject empty messages
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Add user message to history
    conversation_history.append({"role": "user", "content": user_message})

    try:
        # Call local Ollama via OpenAI-compatible endpoint
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversation_history         # Include full history for context
            ]
        )

        # Extract AI reply text
        ai_reply = response.choices[0].message.content

        # Save AI reply to history
        conversation_history.append({"role": "assistant", "content": ai_reply})

        return jsonify({"response": ai_reply})

    except Exception as e:
        # Remove the failed user message from history to keep it clean
        conversation_history.pop()
        return jsonify({"error": f"Ollama error: {str(e)}"}), 500


@app.route("/reset", methods=["POST"])
def reset():
    """Clears the conversation history"""
    global conversation_history
    conversation_history = []
    return jsonify({"message": "Conversation history cleared."})


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "model": MODEL, "endpoint": "ollama-local"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)

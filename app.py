import os
import redis
from flask import Flask, request, jsonify, session, send_from_directory, make_response
from flask_cors import CORS
from flask_session import Session
from openai import OpenAI

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config['SECRET_KEY'] = 'your_secret_key'

# ✅ Set up Redis for session storage
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'chatbot:'
app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# ✅ Initialize session
Session(app)

# ✅ Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is missing. Set it as an environment variable.")

client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Load Local Host IP
LOCALHOST_IP = os.getenv("LOCALHOST_IP")
if not LOCALHOST_IP:
    raise ValueError("❌ LOCALHOST_IP is missing. Set it as an environment variable.")

CORS(app, resources={r"/*": {"origins": [f"http://{LOCALHOST_IP}:5000"]}}, supports_credentials=True)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")

    user_id = session.get('user_id', request.remote_addr)  # Track user by IP (or use login system)
    session['user_id'] = user_id

    redis_key = f"chat_history:{user_id}"

    # ✅ Retrieve chat history from Redis
    chat_history = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True).lrange(redis_key, 0, -1)

    # ✅ Convert history to list of messages
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for msg in chat_history:
        messages.append(eval(msg))  # Convert string to dict

    # ✅ Append new user message
    messages.append({"role": "user", "content": user_message})

    # ✅ Limit to last 10 messages to stay within OpenAI token limits
    messages = messages[-10:]

    # ✅ Save updated history back to Redis
    redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True).delete(redis_key)
    for msg in messages:
        redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True).rpush(redis_key, str(msg))

    # ✅ Send request to OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    assistant_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_reply})

    # ✅ Store assistant reply in Redis
    redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True).rpush(redis_key, str({"role": "assistant", "content": assistant_reply}))

    return jsonify({"response": assistant_reply, "history": messages}), 200

@app.route('/clear_history', methods=['POST'])
def clear_history():
    user_id = session.get('user_id', request.remote_addr)
    redis_key = f"chat_history:{user_id}"
    redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True).delete(redis_key)
    return jsonify({"message": "Chat history cleared."}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

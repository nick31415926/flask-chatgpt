import os
from flask import Flask, request, jsonify, session, send_from_directory, make_response
from flask_cors import CORS
from openai import OpenAI  # ✅ Import OpenAI client

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config['SECRET_KEY'] = 'your_secret_key'

# ✅ Load OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is missing. Set it as an environment variable.")

# ✅ Load Local Host IP from environment variable
LOCALHOST_IP = os.getenv("LOCALHOST_IP")
if not LOCALHOST_IP:
    raise ValueError("❌ LOCALHOST_IP is missing. Set it as an environment variable.")

# ✅ Initialize OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Set CORS properly to allow your frontend IP
CORS(app, resources={r"/*": {"origins": [f"http://{LOCALHOST_IP}:5000"]}}, supports_credentials=True)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# ✅ Handle OPTIONS preflight requests for CORS
@app.route('/chat', methods=['OPTIONS'])
def chat_options():
    response = make_response()
    response.headers["Access-Control-Allow-Origin"] = f"http://{LOCALHOST_IP}:5000"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response, 204

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if 'history' not in session:
        session['history'] = []

    session['history'].append({"role": "user", "content": user_message})

    # ✅ Send request to OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=session['history']
    )

    assistant_reply = response.choices[0].message.content
    session['history'].append({"role": "assistant", "content": assistant_reply})

    # ✅ Manually set CORS headers in the response
    response = make_response(jsonify({"response": assistant_reply, "history": session['history']}))
    response.headers["Access-Control-Allow-Origin"] = f"http://{LOCALHOST_IP}:5000"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response, 200

@app.route('/clear_history', methods=['POST', 'OPTIONS'])
def clear_history():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = f"http://{LOCALHOST_IP}:5000"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response, 204

    session.pop('history', None)
    
    response = make_response(jsonify({"message": "Chat history cleared."}))
    response.headers["Access-Control-Allow-Origin"] = f"http://{LOCALHOST_IP}:5000"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"

    return response, 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

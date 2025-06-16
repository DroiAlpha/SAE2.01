from flask import Flask, request, jsonify, render_template
<<<<<<< HEAD
from chatbot import ask_bot # This import will now work without vectordb
=======
from chatbot import ask_bot
>>>>>>> cf7757a3a3ee719b9fc2c02db460156a8315e654

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/page2")
def page2():
    return render_template("page2.html")

@app.route("/page3")
def page3():
    return render_template("page3.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")
    if not user_input:
        return jsonify({"error": "No input"}), 400
    try:
        bot_response = ask_bot(user_input)
        print(f"User: {user_input} -> Bot: {bot_response}")
        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
<<<<<<< HEAD
    app.run(debug=True)
=======
    app.run(debug=True)
>>>>>>> cf7757a3a3ee719b9fc2c02db460156a8315e654

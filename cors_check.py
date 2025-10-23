from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/ping")
def ping():
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)

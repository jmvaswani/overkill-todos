from flask import Flask
import os, flask_cors
import flask_cors
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("todo_secret_key") or "secret"
print(app.config["SECRET_KEY"])
app.config["DB_USER"] = os.environ.get("todo_dbu") or "jai"
app.config["DB_PASS"] = os.environ.get("todo_dbp") or "password"
app.config["FERNET"] = os.environ["todo_fernkey"].encode()
import db

db.login()
import routes.user_routes

flask_cors.CORS(app)


@app.route("/", methods=["GET"])
def base():
    return "Hello World!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")

from flask import Flask
import os, flask_cors
import flask_cors, logging, sys

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("todo_secret_key") or "secret"
# app.logger.debug(app.config["SECRET_KEY"])
app.config["DB_HOST"] = os.environ.get("todo_dbh") or "localhost"
app.config["DB_USER"] = os.environ.get("todo_dbu") or "jai"
app.config["DB_PASS"] = os.environ.get("todo_dbp") or "password"
app.config["FERNET"] = (
    os.environ.get("todo_fernkey") or "3w11F0qZaRgjuvF4yxkhcdIGv2yaeW-g-ieerKJJMQ4="
)
# app.config["FERNET"] = os.environ["todo_fernkey"].encode()
import db

db.login()
import routes.user_routes

flask_cors.CORS(app)


@app.route("/", methods=["GET"])
def base():
    return "Hello World!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
else:
    app.config["DEBUG"] = True
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.DEBUG)

    app.logger.debug("App Starting")

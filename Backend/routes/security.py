from functools import wraps
from flask import jsonify, request
import jwt, db

# from __main__ import app
from server_entry import app


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        # return 401 if token is not passed
        if not token:
            return f(None, *args, **kwargs)
            # return jsonify({'message' : 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            print(data)
            current_user = db.get_user(data["username"])
            if current_user:
                if current_user["token"] != token:
                    return jsonify({"error": "Token is invalid"}), 401
        except jwt.exceptions.ExpiredSignatureError as e:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.exceptions.DecodeError as e:
            # raise e
            return jsonify({"error": "Token is invalid"}), 401
        except Exception as e:
            # raise e
            print(e.__class__)
            print(e)
            return jsonify({"error": "Some error occoured"}), 401
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated

#/bin/python3
# requirements: flask module, the rest are builtin
# TODO: maybe add logging?


import hashlib
import sqlite3
import random
import flask
import os


CONFIGURATION_FILE = "auth.json"


print(":config: checking if file exists")
if not os.path.exists(CONFIGURATION_FILE):
    print(":config: FAILED TO FIND THE CONFIGURATION FILE!")
    exit(1)

print(":config: starting to set constants")
with open(CONFIGURATION_FILE, 'r') as f:
    try:
        config = eval(''.join(f.read()))
        DB_FILE = config["DB_FILE"]
        LOG_FILE = config["LOG_FILE"]
        HOST = config["HOST"]
        PORT = config["PORT"]

    except:
        print(":ERROR: ERROR IN THE CONFIGURATION FILE")
print(":config: completed setting constants")

def checks() -> None:
    """
    Checks whether the database contains the table `users`

    If it doesn't, then the function will create it
    
    returns None
    """
    print(":checks: starting checks")
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    exists = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchall()

    if not exists:
        cursor.execute("CREATE TABLE users (username text, password text, auth_token str)")
        connection.commit()
    
    print(":checks: passed the checks")

def authenticate_user(username: str, password: str) -> int:
    """
    Tests a username credentials

    :username: string
    :password: string

    0, auth_token: if the credentials are correct
    1, None: if the credentials are incorrect
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Chceks whether the credentials find a match in the database
    check = cursor.execute(f"SELECT username FROM users WHERE username='{username}' and password='{hashed_password}'").fetchall()

    if not check:
        connection.close()
        return 1, None

    auth_token = hashlib.sha256(str(random.randint(0, 10000)).encode()).hexdigest()
    cursor.execute(f"UPDATE users SET auth_token='{auth_token}' WHERE username='{username}' AND password='{hashed_password}'")
    connection.close()

    return 0, auth_token

def insert_user(username: str, password: str) -> int:
    """
    Adds a username & password to the database
    Might as well call it a register function
    
    :username: string
    :password: string

    0: successfully inserted the user
    1: username is taken
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    exists = cursor.execute(f"SELECT username FROM users WHERE username='{username}'").fetchall()

    if exists:
        connection.close()
        return 1, None

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    auth_token = hashlib.sha256(str(random.randint(0, 10000)).encode()).hexdigest()
    cursor.execute(f"INSERT INTO users (username, password, auth_token) VALUES ('{username}', '{hashed_password}', '{auth_token}')")
    connection.commit()

    print(f":insert_user: inserted {username}, token: {auth_token}")
    connection.close()
    return 0, auth_token

def delete_user(username: str, password: str) -> int:
    """
    Deletes a user from the database

    :username: string
    :password: string

    0: successfully deleted the user
    1: the user does not exist or incorrect password
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    exists = cursor.execute(f"SELECT username FROM users WHERE username='{username}' and password='{hashed_password}'").fetchall()

    if not exists:
        print(f":delete_user: {username} does not exist or incorrect password")
        return 1
    
    cursor.execute(f"DELETE FROM users WHERE username='{username}' AND password='{hashed_password}'")
    connection.commit()

    print(f":delete_user: {username} deleted")
    connection.close()
    return 0


checks()
app = flask.Flask(__name__)


@app.route("/authentication", methods=["GET"])
def authenticate() -> dict:
    """
    Utilizies the `Authenticator` class

    Requries :username: and :password: argument
    """
    error_response = flask.jsonify({ "response": "failure" })
    success_response = flask.jsonify({ "response": "success" })

    username = flask.request.args.get("username")
    password = flask.request.args.get("password")
    _type = flask.request.args.get("type")

    if not username or not password or not _type or len(flask.request.args) > 3 or \
        _type not in ["login", "register", "delete"]:
        return error_response

    elif _type == "login":
        response, token = authenticate_user(username, password)
        if response == 0:
            return flask.jsonify({
                "response": "success",
                "auth_token": token
            })
        elif response == 1:
            return flask.jsonify({ "response": "invalid credentials" })

    elif _type == "register":
        response, token = insert_user(username, password)
        if response == 0:
            return flask.jsonify({
                "response": "success",
                "auth_token": token
            })
        elif response == 1:
            return flask.jsonify({ "response": "username is already taken" })

    elif _type == "delete" == 0:
        response = delete_user(username, password)
        if response:
            return flask.jsonify({ "response": "success" })
        elif response == 1:
            return flask.jsonify({ "response": "username does not exist or incorrect password" })

    return error_response


app.run(
    host = HOST,
    port = PORT
)
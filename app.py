from flask import Flask, jsonify, request, current_app, Response, g
from flask.json import JSONEncoder
from flask_cors import CORS
from .secrets import db_username, db_password, db_host, db_port, db_database, jwt_secret_key
from sqlalchemy import create_engine, text
from functools import wraps

import bcrypt
from datetime import datetime, timedelta
import jwt


db = {
    'username': db_username,
    'password': db_password,
    'host': db_host,
    'port': db_port,
    'database': db_database
}

'''
이 코드는 그냥 쓰면 에러를 발생시킨다.
set 모듈이 JSON 으로 변경될 수 없기 때문. 
이를 해결하기 위해 custom json encoder를 구현해야 한다. -> 위에 CustomJSONEncoder class 참고
'''


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return JSONEncoder.default(self, obj)


#################################################################
#                          DECORATOR                            #
#################################################################
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token is not None:
            try:
                payload = jwt.decode(access_token, jwt_secret_key, 'HS256')
            except jwt.InvalidTokenError:
                 payload = None

            if payload is None:
                return Response(status=401)

            user_id = payload['user_id']
            g.user_id = user_id
            g.user = get_user(user_id) if user_id else None
        else:
            return Response(status=401)
        return f(*args, **kwargs)
    return decorated_function


def get_user(user_id):
    user = current_app.database.execute(text("""
            SELECT
                id,
                name,
                email,
                profile
            FROM users
            WHERE id = :user_id
        """), {
        'user_id': user_id
    }).fetchone()

    return {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'profile': user['profile']
    } if user else None


def insert_user(user):
    return current_app.database.execute(text("""
                INSERT INTO users (
                name,
                email,
                profile,
                hashed_password
                ) VALUES (
                :name,
                :email,
                :profile,
                :password
                )
            """), user).lastrowid


def insert_tweet(user_tweet):
    return current_app.database.execute(text("""
        INSERT INTO tweets (
            user_id,
            tweet
        ) VALUES (
            :id,
            :tweet
        )
    """), user_tweet).rowcount


def insert_follow(user_follow):
    current_app.database.execute(text("""
    INSERT INTO users_follow_list (user_id, follow_user_id) VALUES (:id, :follow)
    """), user_follow)


def insert_unfollow(user_unfollow):
    current_app.database.execute(text("""
        DELETE FROM users_follow_list
        WHERE user_id = :id 
        AND follow_user_id = :unfollow
    """), user_unfollow).rowcount


def get_timeline(user_id):
    timeline = current_app.database.execute(text("""
        SELECT
            t.user_id,
            t.tweet
        FROM tweets t
        LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
        WHERE t.user_id = :user_id
        OR t.user_id = ufl.follow_user_id
    """), {
        'user_id': user_id
    }).fetchall()

    return [{
        'user_id': tweet['user_id'],
        'tweet': tweet['tweet']
    } for tweet in timeline]


def get_user_id_and_password(email):
    row = current_app.database.execute(text("""
        SELECT
            id,
            hashed_password
        FROM users
        WHERE email = :email
    """), {'email': email}).fetchone()

    return {
        'id': row['id'],
        'hashed_password': row['hashed_password']
    } if row else None


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.debug = True
    app.json_encoder = CustomJSONEncoder

    db_url = f"mysql+mysqlconnector://{db['username']}:{db['password']}@" \
             f"{db['host']}:{db['port']}/{db['database']}?charset=utf8"
    database = create_engine(db_url, encoding='utf-8', max_overflow=0)
    app.database = database

    @app.route("/ping", methods=['GET'])
    def ping():
        return "ponggggsss"

    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = request.json
        new_user['password'] = bcrypt.hashpw(
            new_user['password'].encode('UTF-8'),
            bcrypt.gensalt()
        )
        new_user_id = insert_user(new_user)
        new_user = get_user(new_user_id)
        return jsonify(new_user)

    @app.route("/login", methods=['POST'])
    def login():
        credential = request.json
        email = credential["email"]
        password = credential["password"]
        user_credential = get_user_id_and_password(email)

        if user_credential and bcrypt.checkpw(password=password.encode("utf-8"),
                                              hashed_password=user_credential["hashed_password"].encode("utf-8")):
            user_id = user_credential["id"]
            payload = {
                "user_id": user_id,
                "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
            }
            token = jwt.encode(payload=payload,
                               key=jwt_secret_key,
                               algorithm="HS256")
            return jsonify({
                "access_token": token
            })
        else:
            return "", 401

    @app.route("/tweet", methods=['POST'])
    @login_required
    def tweet():
        user_tweet = request.json
        user_tweet['id'] = g.user_id
        tweet = user_tweet['tweet']

        if len(tweet) > 300:
            return '300자 초과', 400
        else:
            insert_tweet(user_tweet)

        return 'tweet success', 200

    @app.route("/follow", methods=['POST'])
    @login_required
    def follow():
        payload = request.json
        payload['id'] = g.user_id
        insert_follow(payload)
        return 'follow success', 200

    @app.route("/unfollow", methods=['POST'])
    @login_required
    def unfollow():
        payload = request.json
        payload['id'] = g.user_id
        insert_unfollow(payload)

        return '', 200

    @app.route("/timeline/<int:user_id>", methods=['GET'])
    def timeline(user_id):
        return jsonify({
            'user_id': user_id,
            'timeline': get_timeline(user_id)
        })

    @app.route("/timeline", methods=['GET'])
    @login_required
    def user_timeline():
        user_id = g.user_id

        return jsonify({
            'user_id': user_id,
            'timeline': get_timeline(user_id)
        })
    return app

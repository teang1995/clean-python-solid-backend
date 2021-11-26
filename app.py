from flask import Flask, jsonify, request, current_app
from flask import Flask
from flask.json import JSONEncoder
from .secrets import db_username, db_password, db_host, db_port, db_database
from sqlalchemy import create_engine, text

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
    """),{
        'user_id': user_id
    }).fetchall()

    return [{
        'user_id': tweet['user_id'],
        'tweet': tweet['tweet']
    } for tweet in timeline]

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.json_encoder = CustomJSONEncoder

    db_url = f"mysql+mysqlconnector://{db['username']}:{db['password']}@" \
             f"{db['host']}:{db['port']}/{db['database']}?charset=utf8"
    database = create_engine(db_url, encoding='utf-8', max_overflow=0)
    app.database = database

    @app.route("/ping", methods=['GET'])
    def ping():
        return "ponggggsss"

    @app.route("/sign-up", methods=['POST', 'GET'])
    def sign_up():
        new_user = request.json
        new_user_id = insert_user(new_user)
        new_user = get_user(new_user_id)
        return jsonify(new_user)

    @app.route("/tweet", methods=['POST'])
    def tweet():
        user_tweet = request.json
        tweet = user_tweet['tweet']

        if len(tweet) > 300:
            return '300자 초과', 400
        else:
            insert_tweet(user_tweet)

        return 'tweet success', 200

    @app.route("/follow", methods=['POST'])
    def follow():
        payload = request.json
        insert_follow(payload)
        return 'follow success', 200

    @app.route("/unfollow", methods=['POST'])
    def unfollow():
        payload = request.json
        insert_unfollow(payload)

        return '', 200

    @app.route("/timeline/<int:user_id>", methods=['GET'])
    def timeline(user_id):
        return jsonify({
            'user_id': user_id,
            'timeline': get_timeline(user_id)
        })

    return app

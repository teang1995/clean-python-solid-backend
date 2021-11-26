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
        print("dasfadsf")
        if request.method == 'GET':
            return "pdsfasd"
        else:
            new_user = request.json
            new_user_id = insert_user(new_user)
            new_user = get_user(new_user_id)
            return jsonify(new_user)

    @app.route("/tweet", methods=['POST'])
    def tweet():
        payload = request.json
        user_id = int(payload['id'])
        tweet = payload['tweet']

        if user_id not in app.users:
            return '사용자가 존재하지 않습니다', 400

        if len(tweet) > 300:
            return '300자를 초과한 tweet', 400

        tweet_dict = {
            'user_id': user_id,
            'tweet': tweet
        }
        app.tweets.append(tweet_dict)
        return 'tweet success', 200

    @app.route("/follow", methods=['POST'])
    def follow():
        payload = request.json
        user_id = int(payload['id'])
        user_id_to_follow = int(payload['follow'])

        if any([id_ not in app.users for id_ in [user_id, user_id_to_follow]]):
            return '사용자가 존재하지 않습니다.', 400

        user = app.users[user_id]
        user.setdefault('follow', set()).add(user_id_to_follow)

        '''
        이 코드는 그냥 쓰면 에러를 발생시킨다.
        set 모듈이 JSON 으로 변경될 수 없기 때문. 
        이를 해결하기 위해 custom json encoder를 구현해야 한다. -> 위에 CustomJSONEncoder class 참고
        '''
        return jsonify(user)

    @app.route("/unfollow", methods=['POST'])
    def unfollow():
        payload = request.json
        user_id = int(payload['id'])
        user_id_to_unfollow = int(payload['unfollow'])

        if any([id_ not in app.users for id_ in [user_id, user_id_to_unfollow]]):
            return '사용자가 존재하지 않습니다.', 400

        user = app.users[user_id]
        user.setdefault('follow', set()).discard(user_id_to_unfollow)

        return jsonify(user)

    @app.route("/timeline/<int:user_id>", methods=['GET'])
    def timeline(user_id):
        if user_id not in app.users:
            return '사용자가 존재하지 않습니다.', 400

        follow_list = app.users[user_id].get('follow', set())
        follow_list.add(user_id)
        timeline = [tweet for tweet in app.tweets if tweet['user_id'] in follow_list]

        return jsonify({
            'user_id': user_id,
            'timeline': timeline
        })

    return app

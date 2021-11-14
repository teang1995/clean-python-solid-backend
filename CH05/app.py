from flask import Flask, jsonify, request
from flask.json import JSONEncoder

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        
        return JSONEncoder.default(self, obj)


app = Flask(__name__)
app.users = {}
app.tweets = []
app.id_count = 1
app.json_encoder = CustomJSONEncoder
print(__name__)


@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

@app.route("/sign-up", methods=['POST'])
def sign_up():
    new_user = request.json
    new_user['id'] = app.id_count
    app.users[app.id_count] = new_user
    app.id_count = app.id_count + 1

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
        'user_id' : user_id,
        'tweet' : tweet
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
    set모듈이 JSON으로 변경될 수 없기 때문. 
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
        'user_id' : user_id,
        'timeline' : timeline
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000")
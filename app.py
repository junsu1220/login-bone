from pymongo import MongoClient
import jwt
import certifi
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta

# flask setting
app = Flask(__name__)

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.6bd2d.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

SECRET_KEY = 'SPARTA'

@app.route('/')
def main():
    token_receive = request.cookies.get('mytoken')

    posts = list(db.post.find({}))
    for post in posts:
        post["_id"] = str(post["_id"])

    if token_receive is not None:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user = db.users.find_one({"user_id": payload["user_id"]}, {'_id': False})
            return render_template('index.html', posts=posts, id=user["user_id"])
        except jwt.ExpiredSignatureError:
            msg = '로그인 시간이 만료되었습니다.'
            return render_template('error/401.html', msg=msg), 401
        except jwt.DecodeError:
            msg = '로그인 정보가 존재하지 않습니다.'
            return render_template('error/401.html', msg=msg), 401
    else:
        return render_template('index.html', posts=posts)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "user_id": username_receive,  # 아이디
        "pw": password_hash,  # 비밀번호
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['user_id']
    password_receive = request.form['pw']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'user_id': username_receive, 'pw': pw_hash})

    if result is not None:
        print("testestsetsetestestest")
        payload = {
        'user_id': username_receive,
        'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5500, debug=True)
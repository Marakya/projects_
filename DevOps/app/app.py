from flask import Flask, session
from flask import request
from flask_uuid import FlaskUUID
import uuid
from flask import Flask, redirect, url_for


app = Flask(__name__)
FlaskUUID(app)


@app.route("/")
def gen():
    return "hello"


@app.route('/hostname', methods=['GET'])
def urll():
    return request.host


@app.route('/author', methods=['GET'])
def author():
    name = request.args.get('name')
    return "Ваш никнейм - {}".format(name)


@app.route('/id')
def mypage():
    random_uuid = uuid.uuid4()
    id1 = url_for('mypage', id=random_uuid)
    return id1


if __name__ == "__main__":
    app.run(debug=True, port='8000')

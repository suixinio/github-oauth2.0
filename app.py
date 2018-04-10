# -*- coding:utf-8 -*-
from flask import Flask, request, session, redirect, url_for, render_template
from flask_pymongo import PyMongo
from requests_oauthlib import OAuth2Session
import datetime, time
import os

app = Flask(__name__)
mongo = PyMongo(app)
app.config["MONGO_HOST"] = "127.0.0.1"
app.config["MONGO_PORT"] = 27017
app.config["MONGO_DBNAME"] = "github_capsule"

client_id = "e23744b42168932908ca"
client_secret = "b460c54171dc52f01269c16ffd4c486738e55a9e"

authorization_base_url = "https://github.com/login/oauth/authorize"
token_url = "https://github.com/login/oauth/access_token"


@app.route('/', methods=["GET", "POST"])
@app.route('/page/<int:page>', methods=["GET", "POST"])
def index(page=1):
    if request.method == "POST":
        session["time_capsule"] = request.form["time_capsule"]
        print(session["time_capsule"])
        try:
            # 进行github获取
            githuber_say()
        except:
            github = OAuth2Session(client_id)
            authorization_url, state = github.authorization_url(authorization_base_url)
            session["oauth_state"] = state
            return redirect(authorization_url)

    time_capsule_list = get_githuber_capsule(page=page)
    return render_template("index.html", time_capsule_list=time_capsule_list, page=page, page_count=get_page_count())


@app.route('/callback', methods=["GET"])
def callback():
    github = OAuth2Session(client_id, state=session['oauth_state'])
    token = github.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)
    session['oauth_token'] = token
    githuber_say()
    return redirect(url_for("index"))


def githuber_say():
    print('github.get')
    github = OAuth2Session(client_id, token=session['oauth_token'])
    profile = github.get('https://api.github.com/user').json()

    capsule_dict = {
        "username": profile["name"],
        "avatar_url": profile["avatar_url"],
        "html_url": profile["html_url"],
        "time_capsule": session["time_capsule"],
        "datetime": datetime.datetime.today().strftime("%Y/%m/%d %H:%M"),
        "timestamp": time.time()
    }

    del session["time_capsule"]
    mongo.db.capsule.insert(capsule_dict)


def get_githuber_capsule(count=10, page=1):
    return mongo.db.capsule.find({}).sort([('timestamp', -1)]).skip(count * (page - 1)).limit(count)


def get_page_count(count=10):
    return mongo.db.capsule.find({}).count() // count + 1


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True, ssl_context=("ssl.crt", "ssl.key"), threaded=True)

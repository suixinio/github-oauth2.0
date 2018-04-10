---
title: github OAjuth 2.0 授权验证
date: 2018-04-10 16:55:22
categories:
tags:
---
## 关于 OAuth2.0

> OAuth2.0是OAuth协议的下一版本，但不向后兼容OAuth 1.0即完全废止了OAuth1.0。 OAuth 2.0关注客户端开发者的简易性。要么通过组织在资源拥有者和HTTP服务商之间的被批准的交互动作代表用户，要么允许第三方应用代表用户获得访问的权限。同时为Web应用，桌面应用和手机，和起居室设备提供专门的认证流程。2012年10月，OAuth 2.0协议正式发布为RFC 6749。 ——来自百度百科

典型应用有第三方账户登陆等，此次示例基于 Flask 与 Github 授权接口实现一个留言板应用。

## 效果图
![github-oauth-message-board-201841017119](http://p68umjbe5.bkt.clouddn.com/github-oauth-message-board-201841017119.png)

## GitHub 申请 OAuth App

地址：https://github.com/settings/applications/new

![github-oauth-message-board-2018410171813](http://p68umjbe5.bkt.clouddn.com/github-oauth-message-board-2018410171813.png)

这个地方注意主页 URL 和 Callback URL 可以使用https，也可以使用http

接下来查看Client ID、Client Secret

**Settings** -> **Developer settings**

![github-oauth-message-board-2018410172415](http://p68umjbe5.bkt.clouddn.com/github-oauth-message-board-2018410172415.png)

[官方文档](https://developer.github.com/apps/building-oauth-apps/authorization-options-for-oauth-apps/)

## 项目依赖

- mongodb
- python3.6
- Flask 0.12.2
- Flask-PyMongo (0.5.1)
- requests-oauthlib (0.8.0)

### 安装数据库

```bash
$ sudo apt-get install mongodb
```

### 项目实现

```python
# -*- coding:utf-8 -*-
from flask import Flask, request, session, redirect, url_for, render_template
from flask_pymongo import PyMongo
from requests_oauthlib import OAuth2Session
import datetime, time
import os

# 基本配置信息
app = Flask(__name__)
mongo = PyMongo(app)
app.config["MONGO_HOST"] = "127.0.0.1"
app.config["MONGO_PORT"] = 27017
app.config["MONGO_DBNAME"] = "github_capsule"

client_id = "e23744b42168932908ca"
client_secret = "b460c54171dc52f01269c16ffd4c486738e55a9e"

authorization_base_url = "https://github.com/login/oauth/authorize"
token_url = "https://github.com/login/oauth/access_token"

# 首页信息
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

# 回调页面
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

# 启动采用https
if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True, ssl_context=("ssl.crt", "ssl.key"), threaded=True)

```

## Github项目地址下载

[https://github.com/suixinio/github-oauth2.0](https://github.com/suixinio/github-oauth2.0)
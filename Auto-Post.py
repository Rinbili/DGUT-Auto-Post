# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import *
from pypushdeer import PushDeer

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += "HIGH:!DH:!aNULL"

# URL
url = "https://auth.dgut.edu.cn/authserver/oauth2.0/authorize?response_type=code&client_id=1021534300621787136" \
      "&redirect_uri=https://yqfk-daka.dgut.edu.cn/new_login/dgut&state=yqfk "
url2 = "https://yqfk-daka-api.dgut.edu.cn/auth"
url3 = "https://yqfk-daka-api.dgut.edu.cn/record"

# secret
username = os.environ["USERNAME"]
pw = os.environ["PASSWORD"]
pushkey = os.environ["PUSHKEY"]

session = requests.Session()


def post_pushdeer(title, message):
    title = "疫情打卡：" + title
    desp = ""
    for item in message:
        desp += "- " + item + "  \n"
    pushdeer = PushDeer(pushkey=pushkey)
    pushdeer.send_markdown(title, desp=desp)


def get_token(message):
    post_msg("开始运行", message)
    # getPage
    origin = session.get(url=url)

    # encryptSalt&execution&encryptPassword
    bs4 = BeautifulSoup(origin.text, "lxml")
    encrypt_salt = bs4.find("input", id="pwdEncryptSalt").get("value")
    execution = bs4.find("input", id="execution").get("value")
    if encrypt_salt is None or execution is None:
        post_msg("获取encryptSalt&execution失败", message, 1)
        return None
    post_msg("获取encryptSalt&execution成功", message, 0)

    with os.popen("node ./encrypt.js \"{0}\" \"{1}\"".format(pw, encrypt_salt)) as nodejs:
        password = nodejs.read().replace('\n', '')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.50",
        "Host": "auth.dgut.edu.cn",
        "Origin": "https://auth.dgut.edu.cn",
        "Referer": url}
    data = {"username": username,
            "password": password,
            "captcha": "",
            "_eventId": "submit",
            "cllt": "userNameLogin",
            "dllt": "generalLogin",
            "lt": "",
            "pwdEncryptSalt": encrypt_salt,
            "execution": execution}
    response = session.post(url=origin.url,
                            data=data,
                            headers=headers)
    # 从url中提取参数，作为请求负载，其中参数code对应的应该是token
    token_data = {}
    result = urlparse(response.url)
    for item in result.query.split("&"):
        token_data[item.split('=')[0]] = item.split('=', maxsplit=2)[1]
    if token_data.get("code") is not None:
        token_data["token"] = token_data.get("code")
    if token_data["token"] is None:
        post_msg("获取token失败", message, 1)
        return None
    post_msg("获取token成功", message, 0)
    return token_data


def get_access_token(token_data, message):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.50",
               "Origin": "https://yqfk-daka.dgut.edu.cn",
               "Referer": "https://yqfk-daka.dgut.edu.cn/"}
    access_token_post = session.post(url=url2,
                                     headers=headers,
                                     json=token_data)
    access_token = access_token_post.json().get("access_token")
    if access_token is None:
        post_msg("获取access_token失败", message, 1)
        return None
    post_msg("获取access_token成功", message, 0)
    return access_token


def post_form(access_token, message):
    # getForm
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.50",
               "authorization": "Bearer " + access_token}
    user_data_get = session.get(url=url3, headers=headers)
    if user_data_get.status_code != 200:
        post_msg("请求access_token失败（可能", message, 1)
    post_msg("请求access_token成功", message, 0)
    user_data = user_data_get.json()["user_data"]

    # postForm
    user_data["health_situation"] = 1
    user_data["body_temperature"] = 37
    user_data_post = session.post(url=url3,
                                  headers=headers,
                                  json={"data": user_data})
    if user_data_post.status_code != 200:
        if user_data_post.status_code == 400:
            post_msg("提交data表单失败失败:" + user_data_post.json().get("message"), message, 1)
            post_pushdeer("已经提交过了", message)
            return
        post_msg("提交data表单失败失败:" + user_data_post.json().get("message"), message, 1)
        post_pushdeer("提交失败", message)
        return
    post_msg("提交data表单成功", message, 0)
    post_pushdeer("提交成功", message)


def post_msg(msg, message, level=2):
    header = ("[OK]", "[ERROR]", "[INFO]")
    color = ("\033[32;1m", "\033[31;1m", "\033[36;1m")
    print(color[level], header[level], msg + "\033[0m")
    message.append(header[level] + msg)


def run():
    message = []
    token = get_token(message)
    if token is None:
        post_pushdeer("token获取失败", message)
    access_token = get_access_token(token, message)
    if access_token is None:
        post_pushdeer("access_token获取失败", message)
    post_form(access_token, message)


if __name__ == "__main__":
    run()

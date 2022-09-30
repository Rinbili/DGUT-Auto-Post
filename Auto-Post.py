# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import *
from Crypto.Cipher import AES
import random
import base64

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += "HIGH:!DH:!aNULL"

# URLs&&aes_chars
url = "https://auth.dgut.edu.cn/authserver/oauth2.0/authorize?response_type=code&client_id=1021534300621787136" \
      "&redirect_uri=https://yqfk-daka.dgut.edu.cn/new_login/dgut&state=yqfk "
url2 = "https://yqfk-daka-api.dgut.edu.cn/auth"
url3 = "https://yqfk-daka-api.dgut.edu.cn/record"
url4 = "https://sctapi.ftqq.com/"
url5 = "https://api2.pushdeer.com/message/push"
aes_chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'

# secret
username = os.environ.get("USERNAME")
pw = os.environ.get("PASSWORD")
pushkey = os.environ.get("PUSHKEY")
sendkey = os.environ.get("SENDKEY")
session = requests.Session()


def pad(password):  # 把密码补充成符合 AES-128 CBC 规范形式
    password = random_str(64) + password
    password_length = len(password)
    add_count = AES.block_size - password_length % AES.block_size
    if add_count == 0:
        add_count = AES.block_size
    _pad = chr(add_count)
    return password + _pad * add_count


def random_str(length):
    ret = ""
    for i in range(length):
        ret += random.choice(aes_chars)
    return ret


def password_encrypt(user_password, aes_key):
    iv = random_str(16)
    user_password = pad(user_password).encode("utf8")
    aes_key = str(aes_key.strip())
    cipher = AES.new(aes_key.encode("utf8"), AES.MODE_CBC, iv.encode("utf8"))
    return base64.b64encode(cipher.encrypt(user_password))


def post_pushdeer(title, message):
    title = "疫情打卡：" + title
    desp = ""
    for item in message:
        desp += "- " + item + "  \n"
    session.post(url=url5, data={
        "pushkey": pushkey,
        "text": title,
        "desp": desp,
        "type": "markdown"
    })


def post_server(title, message):
    title = "疫情打卡：" + title
    desp = ""
    for item in message:
        desp += "- " + item + "  \n"
    session.post(url=url4 + sendkey + ".send", data={
        "text": title,
        "desp": desp
    })


def post_message(title, message):
    if sendkey is not None:
        post_server(title, message)
    else:
        post_msg("Server酱密钥为空", status=0)
    if pushkey is not None:
        post_pushdeer(title, message)
    else:
        post_msg("Pushdeer密钥为空", status=0)


def post_msg(msg, message, level=2, status=1):
    header = ("[OK]", "[ERROR]", "[INFO]")
    color = ("\033[32;1m", "\033[31;1m", "\033[36;1m")
    print(color[level], header[level], msg + "\033[0m")
    if status == 1:
        message.append(header[level] + msg)


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

    # with os.popen("node ./encrypt.js \"{0}\" \"{1}\"".format(pw, encrypt_salt)) as nodejs:
    #     password = nodejs.read().replace('\n', '')
    password = password_encrypt(pw, encrypt_salt)

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
    response = session.post(url=origin.url, data=data, headers=headers)
    # 从url中提取参数，作为请求负载，其中参数code对应的应该是token
    token_data = {}
    result = urlparse(response.url)
    for item in result.query.split("&"):
        token_data[item.split('=')[0]] = item.split('=', maxsplit=2)[1]
    token_data["token"] = None
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
               "Referer": "https://yqfk-daka.dgut.edu.cn/"
               }
    access_token_post = session.post(url=url2, headers=headers, json=token_data)
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
    user_data_post = session.post(url=url3, headers=headers, json={"data": user_data})
    if user_data_post.status_code != 200:
        if user_data_post.status_code == 400:
            post_msg("提交data表单失败失败:" + user_data_post.json().get("message"), message, 1)
            post_message("已经提交过了", message)
            return
        post_msg("提交data表单失败失败:" + user_data_post.json().get("message"), message, 1)
        post_message("提交失败", message)
        return
    post_msg("提交data表单成功", message, 0)
    post_message("提交成功", message)


def run():
    message = []
    if username is None or pw is None:
        post_msg("用户名或密码为空", message, 1)
        return
    token = get_token(message)
    if token is None:
        post_message("token获取失败", message)
        return
    access_token = get_access_token(token, message)
    if access_token is None:
        post_message("access_token获取失败", message)
        return
    post_form(access_token, message)


if __name__ == "__main__":
    run()

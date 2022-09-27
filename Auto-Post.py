# -*- coding: utf-8 -*-
import re
import os
import requests

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'

# URL
url = "https://auth.dgut.edu.cn/authserver/oauth2.0/authorize?response_type=code&client_id=1021534300621787136" \
      "&redirect_uri=https://yqfk-daka.dgut.edu.cn/new_login/dgut&state=yqfk "
url2 = "https://yqfk-daka-api.dgut.edu.cn/auth"
url3 = "https://yqfk-daka-api.dgut.edu.cn/record"

# secret
username = os.environ["USERNAME"]
pw = os.environ["PASSWORD"]


def post_form():
    # getPage
    session = requests.Session()
    origin = session.get(url=url)
    html = origin.content.decode('utf-8')

    # encryptSalt&execution&encryptPassword
    encrypt_salt = re.compile("id=\"pwdEncryptSalt\" value=\"(.*?)\"", re.MULTILINE | re.DOTALL
                              ).search(html).group(1)
    execution = re.compile("name=\"execution\" value=\"(.*?)\"", re.MULTILINE | re.DOTALL
                           ).search(html).group(1)
    with os.popen('node ./encrypt.js \"{0}\" \"{1}\"'.format(pw, encrypt_salt)) as nodejs:
        password = nodejs.read().replace('\n', '')

    # getToken
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.50',
        "Host": "auth.dgut.edu.cn",
        "Origin": "https://auth.dgut.edu.cn",
        "Referer": url}
    data = {'username': username,
            'password': password,
            'captcha': "",
            '_eventId': "submit",
            'cllt': "userNameLogin",
            'dllt': "generalLogin",
            'lt': "",
            "pwdEncryptSalt": encrypt_salt,
            'execution': execution}
    response = session.post(url=origin.url,
                            data=data,
                            headers=headers)

    # getAccessToken
    token_data = {'token': re.compile("code=(.*?)&", re.MULTILINE | re.DOTALL).search(response.url).group(1),
                  'state': "yqfk"}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.50',
               "Origin": "https://yqfk-daka.dgut.edu.cn",
               "Referer": "https://yqfk-daka.dgut.edu.cn/"}
    access_token = session.post(url=url2,
                                headers=headers,
                                json=token_data).json().get('access_token')

    # getForm
    headers = {'authorization': 'Bearer ' + access_token}
    user_data = session.get(url=url3, headers=headers).json()['user_data']

    # postForm
    user_data['health_situation'] = 1
    user_data['body_temperature'] = 37
    session.post(url=url3,
                 headers=headers,
                 json={"data": user_data})


if __name__ == '__main__':
    post_form()

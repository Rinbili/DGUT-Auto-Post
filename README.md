# 东莞理工学院疫情打卡
## 仅用于学习目的

## Usage
- Fork本项目  
- Actions中启用workflow
- 打开Settings>>Secrect>>Actions>>New repository secret
```
(Name)         （Secret）
//添加以下几个
USERNAME        (学号/工号)
PASSWORD        (密码)
PUSHKEY         (PushDeer的PushKey)(可选，用于PushDeer推送)
SENDKEY         (Server酱的SendKey)(可选，用于Server酱推送)
GITHUB_TOKEN    (Personal access token)(可选，用于自动同步本项目)
```
##### PushDeer：
- [获取PushKey](https://www.pushdeer.com/official.html)  
##### Server酱：
- [获取SendKey](https://sct.ftqq.com/)
##### Github token：
- [获取Personal access token](https://github.com/settings/tokens)
    
## 更新日志
#### 2022/09/30 v0.0.7
- 简单的错误检查
- 用pycryptodome包加密密码，取代之前用Node.js调用js
#### 2022/09/28 v0.0.5
- Server酱支持
#### 2022/09/28 v0.0.4
- 调整函数
- 简单的错误检查
- PushDeer支持
#### 2022/09/27 v0.0.1
- ~~重写一遍~~
- 从新中央认证系统获取token

## 感谢：
- [@MasterKenway/DGUT-yqfk](https://github.com/MasterKenway/DGUT-yqfk)
- [@Bertramoon](https://github.com/Bertramoon)
- [某大学教务在线登录逆向](https://blog.csdn.net/ssfsj/article/details/124199088)
- [将强智教务系统课表导出为 Ics 文件](https://bolitao.xyz/posts/%E5%B0%86%E5%BC%BA%E6%99%BA%E6%95%99%E5%8A%A1%E7%B3%BB%E7%BB%9F%E8%AF%BE%E8%A1%A8%E5%AF%BC%E5%87%BA%E4%B8%BA-ics-%E6%96%87%E4%BB%B6/)

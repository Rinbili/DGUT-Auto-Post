# 东莞理工学院疫情打卡
## 仅用于学习目的

## Usage
- Fork本项目  
- Actions中启用workflow  
- 打开Settings>>Secrect>>Actions>>New repository secret
```
(Name)     （Secret）
//添加以下几个
USERNAME    (学号/工号)
PASSWORD    (密码)
PUSHKEY     (PushDeer的PushKey)
SENDKEY     (Server酱的SendKey)
```
##### PushDeer：
- [获取PushKey](https://www.pushdeer.com/official.html)  
##### Server酱：
- [获取SenKey](https://sct.ftqq.com/)

## 更新日志  
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
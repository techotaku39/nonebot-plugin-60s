<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-60s

_✨ 每天60秒读懂世界 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/A-kirami/nonebot-plugin-moyu.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-60s">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-60s.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

## 📖 介绍

<details>
  <summary>效果图</summary>

![example](https://raw.githubusercontent.com/techotaku39/nonebot-plugin-60s/master/readme/example.jpg)

</details>

## 💿 安装

<details>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-60s

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-60s
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-60s
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-60s
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-60s
</details>

打开 nonebot2 项目的 `bot.py` 文件, 在其中写入

    nonebot.load_plugin('nonebot_plugin_60s')

</details>

## 配置说明(可选)
有时候api会失效，就改了下
微信公众号地址：https://mp.weixin.qq.com/
抓取的是公众号的内容，我也就找了一个直接分享图片的公众号：每日60s简报（dailybriefing60s），也是很稳定的每天都会在8点前就会推送当天简报

先登陆你的公众号，因为我们要获取一些你的cookie以及token
登陆后F12查看请求
![](./images/123.png)
红圆框是可以找到的地方（大概），红方框就是cookie以及token(cookies:后面的才是，你也可以右键复制值，token=后面的才是)(这也不懂就使用默认吧)
| 配置项 | 说明 |
|:-----:|:----:|
| calendar_cookie: str = "" | 填写微信公众号的cookie |
| calendar_token: str = "" | 填写微信公众号的token |

## 🎉 使用
### 指令表
| 指令  | 说明 |
|:-----:|:----:|
| 60s/读懂世界 | 查看今天的60s日历 |
| 60s/读懂世界+设置 | 以连续对话的形式设置60s日历的推送时间 |
| 60s/读懂世界+设置 小时:分钟 | 设置60s日历的推送时间 |
| 60s/读懂世界+状态 | 查看本群的60s日历状态 |
| 60s/读懂世界+禁用 | 禁用本群的60s日历推送 |

## 💡 鸣谢

### [A-kirami摸鱼日历](https://github.com/A-kirami/nonebot-plugin-moyu)：本项目就是用大佬的项目改了几行代码，连说明文档也是（）
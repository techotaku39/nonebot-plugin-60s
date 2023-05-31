from nonebot_plugin_apscheduler import scheduler
import asyncio
import aiohttp
import json
import re
import nonebot
from pathlib import Path

import httpx
from nonebot import get_bot, get_driver, logger, on_command, require
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import Arg, CommandArg
from nonebot.typing import T_State

from .config import Config


try:
    import ujson as json
except ModuleNotFoundError:
    import json

__help_version__ = '0.2.0'
__help_plugin_name__ = "60s"
__usage__ = """每天60秒读懂世界

使用：
/60s|读懂世界：查看今天的60s日历
/60s|读懂世界+设置 小时:分钟：设置60s日历的推送时间
/60s|读懂世界+状态：查看60s日历状态
/60s|读懂世界+禁用：禁用60s日历推送"""

require("nonebot_plugin_apscheduler")


subscribe = Path(__file__).parent / "subscribe.json"

subscribe_list = json.loads(subscribe.read_text(
    "utf-8")) if subscribe.is_file() else {}


def save_subscribe():
    subscribe.write_text(json.dumps(subscribe_list), encoding="utf-8")


# 加载全局配置
global_config = nonebot.get_driver().config
calendar = Config.parse_obj(global_config.dict())
wechat_oa_cookie = calendar.calendar_cookie
wechat_oa_token = calendar.calendar_token


driver = get_driver()


async def get_calendar_url(cookie: str, token: str) -> str:
    async with aiohttp.ClientSession() as session:
        headers = {
            "Cookie": cookie,
            "User-Agent": 'Mozilla/5.0 (Linux; Android 10; YAL-AL00 Build/HUAWEIYAL-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.64 HuaweiBrowser/10.0.1.335 Mobile Safari/537.36'
        }

        ID = '每日60s简报'  # 公众号的名字
        search_url = f'https://mp.weixin.qq.com/cgi-bin/searchbiz?action=search_biz&begin=0&count=5&query={ID}&token={token}&lang=zh_CN&f=json&ajax=1'
        # 发起搜索公众号请求
        async with session.get(search_url, headers=headers) as response:
            doc = await response.text()
        jstext = json.loads(doc)
        fakeid = jstext['list'][0]['fakeid']

        data = {
            "token": token,
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1",
            "action": "list_ex",
            "begin": 0,
            "count": "5",
            "query": "",
            "fakeid": fakeid,
            "type": "9",
        }
        url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
        # 发起获取文章列表的请求
        async with session.get(url, headers=headers, params=data) as response:
            json_test = await response.text()
        json_test = json.loads(json_test)
        page = json_test["app_msg_list"]
        page = page[0]['link']
        # 根据文章链接获取页面内容
        async with session.get(page) as response:
            html = await response.text()
        cdn_url = re.findall(r"cdn_url:\s*'([^']*)'", html)
        return cdn_url[0]


async def get_calendar() -> bytes:
    async with httpx.AsyncClient(http2=True, follow_redirects=True) as client:
        response = await client.get(
            "https://api.03c3.cn/zb"
        )
        if response.is_error:
            raise ValueError(f"60s日历获取失败，错误码：{response.status_code}")
        return response.content


@driver.on_startup
async def subscribe_jobs():
    for group_id, info in subscribe_list.items():
        scheduler.add_job(
            push_calendar,
            "cron",
            args=[group_id],
            id=f"moyu_calendar_{group_id}",
            replace_existing=True,
            hour=info["hour"],
            minute=info["minute"],
        )


async def push_calendar(group_id: str):
    bot = get_bot()
    try:
        moyu_img = await get_calendar()
    except ValueError:
        moyu_img = await get_calendar_url(wechat_oa_cookie, wechat_oa_token)

    await bot.send_group_msg(
        group_id=int(group_id), message=MessageSegment.image(moyu_img)
    )


def calendar_subscribe(group_id: str, hour: str, minute: str) -> None:
    subscribe_list[group_id] = {"hour": hour, "minute": minute}
    save_subscribe()
    scheduler.add_job(
        push_calendar,
        "cron",
        args=[group_id],
        id=f"moyu_calendar_{group_id}",
        replace_existing=True,
        hour=hour,
        minute=minute,
    )
    logger.debug(f"群[{group_id}]设置60s日历推送时间为：{hour}:{minute}")


moyu_matcher = on_command("读懂世界", aliases={"60s"})


@moyu_matcher.handle()
async def moyu(
    event: MessageEvent, matcher: Matcher, args: Message = CommandArg()
):
    if isinstance(event, GroupMessageEvent) and (cmdarg := args.extract_plain_text()):
        if "状态" in cmdarg:
            push_state = scheduler.get_job(f"moyu_calendar_{event.group_id}")
            moyu_state = "60s日历状态：\n每日推送: " + ("已开启" if push_state else "已关闭")
            if push_state:
                group_id_info = subscribe_list[str(event.group_id)]
                moyu_state += (
                    f"\n推送时间: {group_id_info['hour']}:{group_id_info['minute']}"
                )
            await matcher.finish(moyu_state)
        elif "设置" in cmdarg or "推送" in cmdarg:
            if ":" in cmdarg or "：" in cmdarg:
                matcher.set_arg("time_arg", args)
        elif "禁用" in cmdarg or "关闭" in cmdarg:
            del subscribe_list[str(event.group_id)]
            save_subscribe()
            scheduler.remove_job(f"moyu_calendar_{event.group_id}")
            await matcher.finish("60s日历推送已禁用")
        else:
            await matcher.finish("60s日历的参数不正确")
    else:
        try:
            moyu_img = await get_calendar()
        except ValueError:
            moyu_img = await get_calendar_url(wechat_oa_cookie, wechat_oa_token)
        await matcher.finish(MessageSegment.image(moyu_img))


@moyu_matcher.got("time_arg", prompt="请发送每日定时推送日历的时间，格式为：小时:分钟")
async def handle_time(
    event: GroupMessageEvent, state: T_State, time_arg: Message = Arg()
):
    state.setdefault("max_times", 0)
    time = time_arg.extract_plain_text()
    if any(cancel in time for cancel in ["取消", "放弃", "退出"]):
        await moyu_matcher.finish("已退出60s日历推送时间设置")
    match = re.search(r"(\d*)[:：](\d*)", time)
    if match and match[1] and match[2]:
        calendar_subscribe(str(event.group_id), match[1], match[2])
        await moyu_matcher.finish(f"60s日历的每日推送时间已设置为：{match[1]}:{match[2]}")
    else:
        state["max_times"] += 1
        if state["max_times"] >= 3:
            await moyu_matcher.finish("你的错误次数过多，已退出60s日历推送时间设置")
        await moyu_matcher.reject("设置时间失败，请输入正确的格式，格式为：小时:分钟")

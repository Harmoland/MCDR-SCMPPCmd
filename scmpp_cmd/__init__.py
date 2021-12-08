#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from datetime import datetime, timedelta

import hjson as json
from mcdreforged.api.command import Literal
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RColor, RText
from mcdreforged.plugin.server_interface import PluginServerInterface

cooldown = timedelta(days=3)
json_path = os.path.join(data_folder, 'cooldowns.json')


@new_thread('scmpp_cmd')
def getscm(src):
    remaining_cd = check_cd(src)
    if remaining_cd >= timedelta(0):
        src.reply(RText(f'冷却尚未结束，还有 {remaining_cd.total_seconds()} 秒', color=RColor.red))
        return
    mark_cd(src)
    src.get_server().execute('give ' + src.player + ' minecraft:filled_map{map:-114514}')
    src.reply(RText('已发放', color=RColor.yellow))


def mark_cd(src) -> None:
    with open(json_path, 'r') as fp:
        data = json.load(fp)
    data[src.player] = time.time()
    with open(json_path, 'w') as fp:
        json.dump(data, fp)


def check_cd(src) -> timedelta:
    with open(json_path, 'r') as fp:
        data = json.load(fp)
    if data[src.player] is None:
        return timedelta.min
    else:
        return cooldown - (datetime.now() - datetime.fromtimestamp(data[src.player]))


def on_load(server: PluginServerInterface, prev) -> None:
    global data_folder
    data_folder = server.get_data_folder()
    if not os.path.exists(json_path):
        with open(json_path, 'w') as fp:
            fp.write("{}")
    elif os.path.isdir(json_path):
        os.remove(json_path)
        with open(json_path, 'w') as fp:
            fp.write("{}")
    cmd = Literal('!!getscm').requires(lambda src: src.is_player).runs(getscm)
    server.register_command(cmd)
    server.register_help_message(prefix='!!getscm', message='获取一张能查看附近史莱姆区块的地图')

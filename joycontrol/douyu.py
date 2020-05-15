import websockets
from joycontrol.controller_state import ControllerState, button_push
import time
import asyncio
import threading
import logging
import json

# "A": { // 弹幕匹配用，不区分大小写
#   "cmd": "a", 执行的命令 字符串或数组[stick ,h 水平偏移,v 垂直偏移] l or r ,0-4095,0-4095
#   "time": 0.1, 执行的时间
#   "type": "button", 命令类型默认 button 可选 stick 即摇杆
#   "note": "确定 a 键"  注释
# },

danmu_commands = json.load(
    open("joycontrol/config/AnimalCrossing/commands.json", "r"))

class douyu_msg:
    def dy_encode(self, msg):
        data_len = len(msg) + 9

        msg_byte = msg.encode('utf-8')
        len_byte = int.to_bytes(data_len, 4, 'little')
        send_byte = bytearray([0xb1, 0x02, 0x00, 0x00])
        end_byte = bytearray([0x00])

        data = len_byte + len_byte + send_byte + msg_byte + end_byte

        return data

    def dy_decode(self, msg_byte):
        pos = 0
        msg = []

        while pos < len(msg_byte):
            content_length = int.from_bytes(
                msg_byte[pos: pos + 4], byteorder='little')
            content = msg_byte[pos + 12: pos + 3 +
                               content_length].decode(encoding='utf-8', errors='ignore')
            msg.append(content)
            pos += (4 + content_length)

        return msg

    def get_chat_messages(self, msg_byte):
        decode_msg = self.dy_decode(msg_byte)
        messages = []
        for msg in decode_msg:
            res = self.__parse_msg(msg)
            if res['type'] != 'chatmsg':
                continue
            messages.append(res)

        return messages

    def __parse_msg(self, raw_msg):
        res = {}
        attrs = raw_msg.split('/')[0:-1]
        for attr in attrs:
            attr = attr.replace('@S', '/')
            attr = attr.replace('@A', '@')
            couple = attr.split('@=')
            res[couple[0]] = couple[1]

        return res

class douyu_danmu:
    def __init__(self, room_id, websocket, controller_state=None):
        self.__room_id = room_id
        self.__msg_handler = douyu_msg()
        self.__ws = websocket
        self.__controller_state = controller_state

    async def start(self):
        await self.__ws.send(self.__login())
        await self.__ws.send(self.__join_group())
        await asyncio.gather(self.__get_chat(), self.__heartbeat())

    async def __get_chat(self):
        while True:
            data = await self.__ws.recv()
            msg = self.__msg_handler.get_chat_messages(data)
            for m in msg:
                print(f"{m['nn']}: {m['txt']}")
                cmd = m['txt'].upper()
                if cmd in danmu_commands.keys():
                    await self.__do_command(danmu_commands[cmd])

    async def __do_command(self, cmd, time=0.1):
        if "type" not in cmd:
            cmd['type'] = 'button'

        if "time" not in cmd:
            cmd['time'] = time

        if cmd['type'] == 'button':
            available_buttons = self.__controller_state.button_state.get_available_buttons()
            if cmd['cmd'] in available_buttons:
                await self.__push_button(cmd['cmd'], sec=cmd['time'])
        elif cmd['type'] == 'stick':
            stick_type = cmd['cmd'][0]
            stick = self.__controller_state.__dict__[
                f"{stick_type}_stick_state"]
            stick.set_h(cmd['cmd'][1])
            stick.set_v(cmd['cmd'][2])
            await asyncio.sleep(cmd['time'])
            stick.set_center()
        else:
            # 组合命令
            tasks = [self.__do_command(c, time=cmd['time'])
                     for c in cmd['cmd']]
            await asyncio.wait(tasks)

    async def __push_button(self, btn, sec=0.1):
        await button_push(self.__controller_state, btn, sec=sec)

    def __login(self):
        print("登录")
        login_msg = f'type@=loginreq/room_id@={self.__room_id}/'
        return self.__msg_handler.dy_encode(login_msg)

    def __join_group(self):
        print("入组")
        join_group_msg = 'type@=joingroup/rid@=%s/gid@=-9999/' % (
            self.__room_id)
        return self.__msg_handler.dy_encode(join_group_msg)

    async def __heartbeat(self):
        heartbeat_msg = 'type@=mrkl/'
        heartbeat_msg_byte = self.__msg_handler.dy_encode(heartbeat_msg)
        while True:
            print("心跳检测")
            await self.__ws.send(heartbeat_msg_byte)
            await asyncio.sleep(44)

async def test_dy(controller_state: ControllerState):
    uri = "wss://danmuproxy.douyu.com:8506/"
    print("连接:")
    async with websockets.connect(uri, ping_interval=None) as websocket:
        print("初始化:")
        danmu = douyu_danmu("8724068", websocket, controller_state)
        await danmu.start()

# test
# asyncio.get_event_loop().run_until_complete(test_dya())
# asyncio.get_event_loop().run_forever()

import websockets
from joycontrol.controller_state import ControllerState, button_push
import time


class _DyBarrageRawMsgHandler:
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
    def __init__(self, room_id):
        self.__room_id = room_id
        self.__msg_handler = _DyBarrageRawMsgHandler()
        self.__heartbeat_thread = None
        self.__should_stop_heartbeat = False

    async def start(self, ws):
        await ws.send(self.__login())
        await ws.send(self.__join_group())
        await self.__heartbeat(ws)

    def __login(self):
        login_msg = 'type@=loginreq/room_id@=%s/dfl@=sn@A=105@Sss@A=1/username@=%s/uid@=%s/ver@=20190610/aver@=218101901/ct@=0/' % (
            self.__room_id, '61609154', '61609154')
        return self.__msg_handler.dy_encode(login_msg)

    def __join_group(self):
        join_group_msg = 'type@=joingroup/rid@=%s/gid@=1/' % (self.__room_id)
        return self.__msg_handler.dy_encode(join_group_msg)

    async def __heartbeat(self, ws):
        heartbeat_msg = 'type@=mrkl/'
        heartbeat_msg_byte = self.__msg_handler.dy_encode(heartbeat_msg)
        while True:
            await ws.send(heartbeat_msg_byte)
            for i in range(90):
                time.sleep(0.5)
                if self.__should_stop_heartbeat:
                    return


async def test_dy(controller_state: ControllerState):
    uri = "wss://danmuproxy.douyu.com:8506/"
    async with websockets.connect(uri) as websocket:
        danmu = douyu_danmu("8724068")
        await danmu.start(websocket)
        greeting = await websocket.recv()
        print(f"< {greeting}")

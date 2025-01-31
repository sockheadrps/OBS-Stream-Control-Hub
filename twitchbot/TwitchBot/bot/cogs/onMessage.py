from twitchio.ext import commands, sounds
import websockets
import json
from ..bot import Bot
import re
from gtts import gTTS
import os
import time
import asyncio
from aiodesa import Db
import aiosqlite




class Chatter:
    def __init__(self, name, is_muted, message_replace, tts_length):
        self.name = name
        self.is_muted = is_muted
        self.message_replace = message_replace
        self.tts_length = tts_length
        self.last_message_time = time.time() + 1.0
        self.join_time = time.time()
        print(self.name, self.is_muted, self.message_replace, self.tts_length)

    def update_last_message_time(self):
        self.last_message_time = time.time()


class RollingChatterList:
    def __init__(self):
        self.chatters = {}
        self.time_delta_loop_task = asyncio.create_task(self.time_delta_loop())
        self.websocket = None
        self.websocket_endpoint = "ws://192.168.1.135:8100/websockets/twitch_bot"
        self.websocket_listener_task = asyncio.create_task(self.websocket_listener())
        self.websocket_sender_task = asyncio.create_task(self.websocket_sender())
        self.connected = False
        self.current_chatter = None

    async def websocket_listener(self):
        async with websockets.connect(self.websocket_endpoint) as websocket:
            print("Connected to websocket")
            await websocket.send(
                json.dumps({"event": "CONNECT", "client_type": "TWITCH_BOT"})
            )
            self.websocket = websocket
            self.connected = True
            while True:
                message = await websocket.recv()
                message = json.loads(message)
                print(message)
                if message.get("event") == "UPDATE_SETTINGS":
                    # {'sockheadrps': {'name': 'sockheadrps', 'is_muted': False, 'message_replace': '', 'tts_length': 60, 'kill_tts': True}}
                    settings = message.get("data")
                    chatter_name = settings.get('name')
                    is_muted = settings.get('is_muted')
                    message_replace = settings.get('message_replace')
                    tts_length = settings.get('tts_length')
                    print(f"Updating settings for {chatter_name}: is_muted={is_muted}, message_replace={message_replace}, tts_length={tts_length}")

                    # async with aiosqlite.connect("database.sqlite3") as aiodb:
                    #     print("Database connected")
                    #     await aiodb.execute("UPDATE user_economy SET is_muted = ?, message_replace = ?, tts_length = ? WHERE username = ?", (is_muted, message_replace, tts_length, chatter_name))
                    #     await aiodb.commit()




    def check_current_chatter(self, chatter, is_muted, message_replace, tts_length):
        if chatter not in self.chatters:
            print(
                f"Adding chatter with settings: {is_muted}, {message_replace}, {tts_length}"
            )
            self.chatters[chatter] = Chatter(
                chatter, is_muted, message_replace, tts_length
            )
        else:
            self.chatters[chatter].update_last_message_time()

    async def time_delta_loop(self):
        while True:
            await asyncio.sleep(120)
            for chatter_name, chatter in list(self.chatters.items()):
                if time.time() - chatter.last_message_time > 10:
                    print("Deleting chatter")
                    del self.chatters[chatter_name]
                    print(self.chatters)

    async def websocket_sender(self):
        while True:
            await asyncio.sleep(2)
            if self.connected:
                chatter_data = json.dumps(
                    {
                        "event": "TWITCH_BOT_UPDATE",
                        "client_type": "TWITCH_BOT",
                        "data": {
                            "current_chatter": self.current_chatter,
                            "chatter_list": list(self.chatters.keys()),
                            "chatters_data": {
                                chatter: {
                                    "is_muted": "false" if not self.chatters[chatter].is_muted else "true",
                                    "message_replace": self.chatters[chatter].message_replace,
                                    "tts_length": self.chatters[chatter].tts_length,
                                }
                                for chatter in self.chatters
                            },
                        },
                    }
                )
                # print(chatter_data)
                await self.websocket.send(chatter_data)


message_alert_sound_minimum = 20
message_timer_start = time.time()
tts_timer = 0
tts_timer_bool = False
time_tts_used = 0
tts_bool = True
tts_max_chars = 255
obs_ws_server = "ws://localhost:8181/"


def check_for_repeats(message):
    for word in message.split(" "):
        res = None
        for i in range(1, len(word) // 2 + 1):
            if (
                not len(word) % len(word[0:i])
                and word[0:i] * (len(word) // len(word[0:i])) == word
            ):
                res = word[0:i]
        return res


def message_alert():
    path = os.path.join(os.getcwd(), "bot/cogs/message_alert.mp3")
    print(path)
    # playsound.playsound(path)


class OnMessage(commands.Cog):
    def __init__(self, bot):
        global message_queue
        self.bot = bot
        self.is_speaking = False
        self.message_queue = []
        self.player = sounds.AudioPlayer(callback=self.player_done)
        self.user_speaking = ""
        self.rolling_chatter_list = None

    async def player_done(self):
        self.is_speaking = False
        self.user_speaking = ""

    @commands.Cog.event()
    async def event_ready(self):
        asyncio.get_event_loop().create_task(self.tts_task())
        asyncio.get_event_loop().create_task(self.obs_tts_loop())
        self.rolling_chatter_list = RollingChatterList()

    @commands.Cog.event()
    async def event_message(self, message):
        global message_alert_sound_minimum, message_timer_start

        # Plays an alert upon message if there have been no messages in the sound min
        if time.time() - message_timer_start > message_alert_sound_minimum:
            message_alert()
            message_timer_start = time.time()
        else:
            message_timer_start = time.time()
        try:
            if (
                message.author.name
                and message.content[0] != "-"
                and message.content[0] != "!"
            ):
                if self.bot.tts:
                    self.message_queue.append(
                        (message.author.name, self.cleanse_message(message.content))
                    )
                async with Db("database.sqlite3") as db:
                    await db.read_table_schemas(self.bot.UserEcon)
                    find = db.find(self.bot.UserEcon)
                    author = await find(message.author.name)
                    print(author)
                    is_muted = author.is_muted
                    print(is_muted)
                    message_replace = author.message_replace
                    print(f"Message replace: {message_replace}")
                    tts_length = author.tts_length
                    self.rolling_chatter_list.check_current_chatter(
                        message.author.name, is_muted, message_replace, tts_length
                    )

        # Can error on bot connection....
        except AttributeError:
            pass

    def tts_speak(self, to_say):
        if tts_bool and int(tts_max_chars) > 0 and not self.is_speaking:
            txt = to_say[: int(tts_max_chars)]
            tts = gTTS(text=txt, lang="en", slow=False)
            filename = "voice.mp3"
            tts.save(filename)
            sound = sounds.Sound(source=f"{filename}")
            self.is_speaking = True
            self.player.play(sound)

    def cleanse_message(self, message):
        to_say = re.sub(r"https?\S+\s?", "some link ", message)
        rx = re.compile(r"(.)\1{9,}")
        lines = to_say.split(" ")
        for line in lines:
            rxx = rx.search(line)
            if rxx:
                to_say = "Im an annoying fuck"
        to_say = re.sub(r"\d{8,}", "a fucking huge number", to_say)

        if check_for_repeats(to_say):
            to_say = "I used to be a really fucking annoying tts"
        # 	Checks to make sure there is actually an alpha numeric char in the string
        # So TTS doesnt freak out and crash
        if re.search(r"[a-zA-Z0-9]", to_say):
            return to_say
        else:
            return "Fuck you"

    # Loop that handles for interrupt from the dashboard front end

    async def tts_task(self):
        while True:
            await asyncio.sleep(0.2)
            if self.bot.interrupt_tts:
                self.bot.interrupt_tts = False
                self.player.stop()

            elif not self.is_speaking and len(self.message_queue) > 0:
                self.tts_speak(self.message_queue[0][1])
                self.user_speaking = self.message_queue[0][0]
                self.message_queue.pop(0)

    async def obs_tts_loop(self):
        connect_event = {"event": "CONNECT", "client": "TWITCHIO_CLIENT"}
        try:
            async with websockets.connect(obs_ws_server) as websocket:
                await websocket.send(json.dumps(connect_event))
                while True:
                    # if speaking Send speaking event to OBS
                    # Random char ID until DB is implemented
                    if self.is_speaking:
                        async with Db("database.sqlite3") as db:
                            # Create table from UserEcon class
                            await db.read_table_schemas(self.bot.UserEcon)
                            find = db.find(self.bot.UserEcon)
                            author = await find(self.user_speaking)

                            if author == None:
                                speaking_event = {
                                    "event": "IS_SPEAKING",
                                    "client": "TWITCHIO_CLIENT",
                                    "user": self.user_speaking,
                                    "level": 0,
                                }
                            else:
                                speaking_event = {
                                    "event": "IS_SPEAKING",
                                    "client": "TWITCHIO_CLIENT",
                                    "user": self.user_speaking,
                                    "level": author.level,
                                }
                        self.rolling_chatter_list.current_chatter = self.user_speaking
                        await websocket.send(json.dumps(speaking_event))

                        # yeild while speaking
                        while self.is_speaking:
                            await asyncio.sleep(0.1)

                        else:
                            speaking_complete_event = {
                                "event": "SPEAKING_COMPLETE",
                                "client": "TWITCHIO_CLIENT",
                            }
                            self.rolling_chatter_list.current_chatter = None
                            await websocket.send(json.dumps(speaking_complete_event))
                    else:
                        await asyncio.sleep(0)

        # Can be connection refused error
        except OSError as e:
            for sub_exception in e.args:
                print("WS connection to OBS/TTS server has been refused")


def prepare(bot: Bot):
    bot.add_cog(OnMessage(bot))

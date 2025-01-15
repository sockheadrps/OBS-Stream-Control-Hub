from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from dotenv import load_dotenv
import os
import aiosqlite

load_dotenv()
TWITCH_DB_PATH = os.getenv("TWITCH_DB_PATH")

async def get_user_settings(username):
    async with aiosqlite.connect(TWITCH_DB_PATH) as db:
        # get the column names
        async with db.execute("PRAGMA table_info(user_economy)") as cursor:
            column_names = await cursor.fetchall()
            print(column_names)
        async with db.execute("SELECT * FROM user_economy WHERE username = ?", (username,)) as cursor:
            user_settings = await cursor.fetchone()
            # dictionary with column names as keys
            user_settings_dict = {
                column[1]: user_settings[i] for i, column in enumerate(column_names)
            }
            return user_settings_dict

async def update_user_settings(username, settings):
    async with aiosqlite.connect(TWITCH_DB_PATH) as db:
        await db.execute("UPDATE user_economy SET is_muted = ?, message_replace = ?, tts_length = ? WHERE username = ?", (settings['is_muted'], settings['message_replace'], settings['tts_length'], username))
        await db.commit()
        print(f"Updated settings for {username} {settings}")

twitch_bot_router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.twitch_bot_websocket = None
        self.web_client_websockets = set()
        self.send_task = None
        self.chatter_list = []
        self.current_chatter = None
        self.chatters_data = {}
        self.update_settings = {}

    async def connect(self, websocket: WebSocket, client_type: str):
        if client_type == "TWITCH_BOT":
            self.twitch_bot_websocket = websocket
        elif client_type == "WEB_CLIENT":
            self.web_client_websockets.add(websocket)
            if self.send_task is None:
                self.send_task = asyncio.create_task(self.broadcast_chatter_list())

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.web_client_websockets:
            self.web_client_websockets.remove(websocket)
        elif websocket == self.twitch_bot_websocket:
            self.twitch_bot_websocket = None

        if not self.web_client_websockets and self.send_task:
            self.send_task.cancel()
            self.send_task = None

    async def broadcast_chatter_list(self):
        while True:
            await asyncio.sleep(2)
            if len(self.update_settings.items()) > 0:
                for chatter_name, settings in self.update_settings.items():
                    await self.twitch_bot_websocket.send_json({
                        'event': 'UPDATE_SETTINGS',
                        'username': chatter_name,
                        'data': settings

                })
                self.update_settings = {}
            if self.web_client_websockets:
                print(self.chatters_data)
                message = {
                    "event": "UPDATE",
                    "data": {
                        "chatter_list": self.chatter_list,
                        "current_chatter": self.current_chatter,
                        "chatters_data": self.chatters_data,
                    },
                }
                dead_clients = set()

                for websocket in self.web_client_websockets:
                    try:
                        await websocket.send_json(message)
                    except Exception:
                        dead_clients.add(websocket)

                for websocket in dead_clients:
                    await self.disconnect(websocket)


manager = ConnectionManager()

@twitch_bot_router.websocket("/twitch_bot")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_json()
            print(data.get('event'))
            print(data.get('client_type'))
            if data.get("event") == "CONNECT":
                client_type = data.get("client_type")
                if client_type in ["TWITCH_BOT", "WEB_CLIENT"]:
                    await manager.connect(websocket, client_type)
            elif data.get("client_type") == "TWITCH_BOT":
                if data.get("event") == "TWITCH_BOT_UPDATE":
                    manager.chatter_list = data.get("data", {}).get("chatter_list")
                    manager.current_chatter = data.get("data", {}).get("current_chatter")
                    manager.chatters_data = data.get("data", {}).get("chatters_data")
            elif data.get("client_type") == "WEB_CLIENT":
                chatter_name = data.get('data', {}).get('name')
                print(f"Updating settings for {chatter_name if chatter_name else 'None'}")
                if data.get("event") == "UPDATE_SETTINGS":
                    settings_data = data.get('data', {})
                    print(f"Settings data: {settings_data}")
                    settings = {
                        'name': settings_data.get('name'),
                        'is_muted': settings_data.get('is_muted'),
                        'message_replace': settings_data.get('message_replace'), 
                        'tts_length': settings_data.get('tts_length'),
                        'kill_tts': settings_data.get('kill_tts', False)
                    }
                    manager.chatters_data[settings['name']] = settings
                    manager.update_settings[settings['name']] = settings
                    await update_user_settings(settings_data.get('name'), settings)

                elif data.get("event") == "GET_USER_SETTINGS":
                    user_settings = await get_user_settings(data.get('data', {}).get('username'))
                    print(user_settings)
                    await websocket.send_json({
                        'event': 'USER_SETTINGS',
                        'data': user_settings
                    })
                elif data.get("event") == "UPDATE_USER_SETTINGS":
                    pass
                    # await update_user_settings(data.get('data', {}).get('username'), data.get('data', {}).get('settings'))

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        print(f"Error in websocket connection: {e}")
        await manager.disconnect(websocket)

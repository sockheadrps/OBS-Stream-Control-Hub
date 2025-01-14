from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.responses import HTMLResponse
import asyncio
from rpaudio.effects import FadeIn, FadeOut
from rpaudio import AudioChannel, AudioSink
import dotenv
import os


dotenv.load_dotenv()

audio_processor_task = None
client_processor_task = None
clients = []


@asynccontextmanager
async def audio_router_lifespan(app: FastAPI):
    print("Audio router lifespan started")
    global audio_processor_task, client_processor_task, clients
    try:
        yield
    finally:
        # Clean up tasks here
        if audio_processor_task is not None:
            audio_processor_task.cancel()
            print("Audio processor task canceled.")
        if client_processor_task is not None:
            client_processor_task.cancel()
            print("Client processor task canceled.")
        for client in clients:
            await client.close()
        print("All clients disconnected.")


audio_player_router = APIRouter(lifespan=audio_router_lifespan)

MUSIC_DIR = os.getenv("MUSIC_DIR")
print(MUSIC_DIR)

# audio folder path object
audio_folder_path = Path(MUSIC_DIR)


def on_audio_stop():
    print("Audio stopped.")


command_queue = asyncio.Queue()
client_queue = asyncio.Queue()


async def create_audio_channel():
    valid_file_types = [".mp3", ".wav", ".mp4"]
    audio_files = [
        str(file)
        for file in audio_folder_path.iterdir()
        if file.is_file() and file.suffix in valid_file_types
    ]
    channel = AudioChannel()

    for file in audio_files:
        audio_sink = AudioSink(callback=on_audio_stop).load_audio(file)
        audio_sink.set_volume(1.0)
        channel.push(audio_sink)

    await asyncio.sleep(0.2)

    return channel


async def client_queue_processor():
    while True:
        await asyncio.sleep(0.2)
        if not client_queue.empty():
            audio_status = client_queue.get_nowait()
            data = {"data": audio_status}
            if len(clients) > 0:
                await clients[0].send_json(data)


async def audio_command_processor(reconnect=False):
    player_hidden = False
    if reconnect is False:
        channel = None
        audio = None
        command = None
        channel = await create_audio_channel()
        print(f"channel created")
        audio_status = {}
        channel_1_effects = []
        auto_play = False
        audio_status = {}
        reload_channel = True

        if channel is not None:
            audio_status["is_playing"] = ""
            audio_status["queue"] = [
                item.playback_data() for item in channel.queue_contents
            ]
            audio_status["data"] = None
            audio_status["current_audio"] = ""

    while True:
        await asyncio.sleep(0.2)

        try:
            command = await asyncio.wait_for(command_queue.get(), timeout=0.2)

            if command["type"] == "play":
                if not audio_status["is_playing"]:
                    if channel.current_audio:
                        channel.current_audio.play()
                        audio_status["is_playing"] = True

            elif command["type"] == "pause":
                if channel.current_audio.is_playing:
                    channel.current_audio.pause()
                    audio_status["is_playing"] = False

            elif command["type"] == "skip":
                if channel.current_audio:
                    channel.current_audio.stop()

            elif command["type"] == "autoplay":
                auto_play = not auto_play
                channel.auto_consume = auto_play
                while channel is None:
                    await asyncio.sleep(0.2)
                while channel.current_audio is None:
                    await asyncio.sleep(0.2)
                if channel.auto_consume:
                    channel.current_audio.play()
                if channel is not None:
                    audio_status["is_playing"] = channel.current_audio.is_playing
                    audio_status["queue"] = [
                        item.playback_data() for item in channel.queue_contents
                    ]
                    audio_status["data"] = None
                    audio_status["current_audio"] = (
                        channel.current_audio.playback_data()
                    )
                    audio_status["auto_play"] = auto_play
                client_queue.put_nowait(audio_status)

            elif command["type"] == "volume":
                volume = command["volume"]["value"]
                if channel.current_audio is not None:
                    channel.current_audio.set_volume(float(volume))

            elif command["type"] == "speed":
                speed = command["speed"]["value"]
                channel.current_audio.set_speed(float(speed))

            elif command["type"] == "set_effects":
                if command.get("effects") == "fade_in":
                    channel_1_effects.append(FadeIn(duration=5.0))
                elif command.get("effects") == "fade_out":
                    channel_1_effects.append(FadeOut(duration=5.0))

                channel.set_effects_chain(channel_1_effects)
                client_queue.put_nowait(
                    {"type": "set_effects", "effects": command.get("effects")}
                )

            elif command["type"] == "reload_on_finish":
                reload_on_finish = command["reload_on_finish"]
                reload_channel = reload_on_finish

            elif command["type"] == "info_request":
                player_hidden = False
                if channel is not None:
                    if channel.current_audio is not None:
                        audio_status["is_playing"] = channel.current_audio.is_playing
                        audio_status["current_audio"] = (
                            channel.current_audio.playback_data()
                        )
                        audio_status["volume"] = channel.current_audio.get_volume()

                    audio_status["queue"] = [
                        item.playback_data() for item in channel.queue_contents
                    ]
                    # if an effect is FadeIn, put the string, if FadeOut, put the string, if ChangeSpeed, put the string    
                    audio_status["effects"] = [
                        effect.__class__.__name__ for effect in channel.effects
                    ]
                audio_status["auto_play"] = auto_play
                audio_status["reload_on_finish"] = reload_channel
                data_payload = {"event_type": "info_request", "data": audio_status}
                client_queue.put_nowait(data_payload)
            
            elif command["type"] == "player_hidden":
                player_hidden = command["player_hidden"]

            else:
                print(f"Invalid command: {command}")

        except asyncio.TimeoutError:
            await asyncio.sleep(0.2)

            if channel is not None and channel.current_audio is not None and not player_hidden:
                if channel.current_audio.is_playing:
                    audio_status["is_playing"] = channel.current_audio.is_playing
                    audio_status["queue"] = [
                        item.playback_data() for item in channel.queue_contents
                    ]
                    audio_status["data"] = None
                    audio_status["current_audio"] = (
                        channel.current_audio.playback_data()
                    )
                    client_queue.put_nowait(audio_status)
            elif channel is not None and len(channel.queue_contents) == 0:
                if reload_channel:
                    channel = await create_audio_channel()
                    while channel is None:
                        await asyncio.sleep(0.2)
                    print(f"channel created")
                    audio_status = {}

                    if auto_play:
                        channel.auto_consume = True
                        while channel.current_audio is None:
                            await asyncio.sleep(0.2)
                        audio_status["is_playing"] = channel.current_audio.is_playing
                        audio_status["queue"] = [
                            item.playback_data() for item in channel.queue_contents
                        ]
                        audio_status["data"] = None
                        audio_status["current_audio"] = (
                            channel.current_audio.playback_data()
                        )
                        client_queue.put_nowait(audio_status)
                    else:
                        audio_status["is_playing"] = False
                        audio_status["queue"] = [
                            item.playback_data() for item in channel.queue_contents
                        ]
                        audio_status["data"] = None
                        audio_status["current_audio"] = {
                            "title": "",
                            "artist": "",
                        }
                        client_queue.put_nowait(audio_status)

                else:
                    channel = None

            if channel is None:
                audio_status["is_playing"] = ""
                audio_status["queue"] = []
                audio_status["data"] = None
                audio_status["current_audio"] = ""

            if channel is None and reload_channel:
                channel = True


@audio_player_router.get("/audio_channels", response_class=HTMLResponse)
async def get_audio_player():
    return HTMLResponse(content=open("app/templates/audio_player.html").read())


@audio_player_router.websocket("/audio")
async def websocket_endpoint(websocket: WebSocket):
    global audio_processor_task, client_processor_task
    await websocket.accept()
    clients.append(websocket)
    if audio_processor_task is None:
        audio_processor_task = asyncio.create_task(audio_command_processor())
    if client_processor_task is None:
        client_processor_task = asyncio.create_task(client_queue_processor())

    try:
        while True:
            await asyncio.sleep(0.2)
            data = await websocket.receive_json()
            if data is not None:
                print(f"Received data: {data}")

            event_type = data.get("event")
            control_type = data.get("type")
            print(f"Event type: {event_type}")
            print(data)
            command = data.get("data")
            print(f"Command: {command}")

            if event_type == "effects":
                effects_data = data.get("data")
                command_queue.put_nowait(
                    {"type": "set_effects", "effects": effects_data["effect"]}
                )

            elif event_type == "info_request":
                command_queue.put_nowait({"type": "info_request"})

            elif event_type == "audio_control":
                command = data.get("data")
                if command == "play":
                    command_queue.put_nowait({"type": "play"})
                    await websocket.send_json(
                        {"event": "audio_control", "data": {"command": "play"}}
                    )

                elif command == "pause":
                    command_queue.put_nowait({"type": "pause"})
                    await websocket.send_json(
                        {"event": "audio_control", "data": {"command": "pause"}}
                    )

                elif command == "skip":
                    command_queue.put_nowait({"type": "skip"})
                    await websocket.send_json(
                        {"event": "audio_control", "data": {"command": "skip"}}
                    )

                elif command == "auto_play":
                    command_queue.put_nowait({"type": "autoplay"})
                    await websocket.send_json(
                        {"event": "audio_control", "data": {"command": "autoplay"}}
                    )

                if control_type == "volume":
                    volume = data["data"]["value"]
                    command_queue.put_nowait(
                        {"type": "volume", "volume": {"value": volume}}
                    )

            elif control_type == "reload_on_finish":
                reload_on_finish = data["data"]["value"]
                command_queue.put_nowait(
                    {"type": "reload_on_finish", "reload_on_finish": reload_on_finish}
                )
            elif control_type == "player_hidden":
                player_hidden = data["value"]
                command_queue.put_nowait(
                    {"type": "player_hidden", "player_hidden": player_hidden}
                )

            for client in clients:
                if client != websocket:
                    await client.send_json(
                        {
                            "event": "audio_state_updated",
                            "data": {"event_type": event_type},
                        }
                    )

    except (WebSocketDisconnect, RuntimeError):
        print("WebSocket disconnected")
        clients.remove(websocket)

    finally:
        print("WebSocket disconnected finally")

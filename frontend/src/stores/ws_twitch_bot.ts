import { browser } from '$app/environment';
import { writable } from 'svelte/store';

export const twitch_bot_websocket = writable<WebSocket | null>(null);
export const twitch_bot_websocketState = writable<'connected' | 'disconnected' | 'identifying' | 'identified'>('disconnected');
export const twitch_bot_lastMessage = writable<any>(null);

let ws: WebSocket;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const INITIAL_RECONNECT_DELAY = 1000;

export function initTwitchBotWebSocket() {
    if (browser && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const host = window.location.hostname;
        const port = '8100';
        const url = `${protocol}://${host}:${port}/websockets/twitch_bot`;
        console.log(url);

        ws = new WebSocket(url);
        twitch_bot_websocket.set(ws);
        twitch_bot_websocketState.set('disconnected');

        ws.onopen = () => {
            console.log('Twitch Client WebSocket connected');
            reconnectAttempts = 0;
            ws.send(JSON.stringify({ event: 'CONNECT', client_type: 'WEB_CLIENT' }));
            twitch_bot_websocketState.set('connected');
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            handleReconnect();
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.event === 'UPDATE') {
                allChattersOptions = message.data.chatters_data;
            }
            if (message.event === 'USER_SETTINGS') {
                userSettings = message.data;
            }
            twitch_bot_lastMessage.set(message);
        };

        ws.onclose = () => {
            console.log('WebSocket closed');
            handleReconnect();
        };
    }
}

function handleReconnect() {
    twitch_bot_websocketState.set('disconnected');
    const delay = INITIAL_RECONNECT_DELAY * Math.pow(2, reconnectAttempts);
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        console.log(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})`);
        setTimeout(initTwitchBotWebSocket, delay);
        reconnectAttempts++;
    } else {
        console.error('Max reconnection attempts reached. Please check server status.');
    }
}

export function sendMessage(message: any) {
    if (ws) {
        ws.send(JSON.stringify(message));
    }
}

export function requestUserSettings(username: string) {
    if (ws) {
        ws.send(JSON.stringify({ event: 'GET_USER_SETTINGS', client_type: 'WEB_CLIENT', data: { username: username } }));
    }
}

interface UserSettings {
    name: string;
    is_muted: boolean;
    message_replace: string;
    tts_length: number;
}

export let userSettings: UserSettings | null = null;




export function sendTwitchBotSettings(settings: UserSettings) {
    if (ws && name) {
        let storeValue;
        chatterOptionsContext.store.subscribe(value => {
            storeValue = value;
        })();
        let options = getChatterOptions(name);
        console.log(storeValue);
        ws.send(JSON.stringify({ event: 'UPDATE_SETTINGS', client_type: 'WEB_CLIENT', data: settings }));
    }
}

export function getTwitchBotSettings() {
    if (ws) {
        ws.send(JSON.stringify({ event: 'GET_SETTINGS' }));
    }
}

export const chatterOptionsStore = writable<ChatterOptions>();

interface ChatterOptions {
    name: string | undefined;
    is_muted: boolean | undefined;
    message_replace: string | undefined;
    tts_length: number | undefined;
    kill_TTS: boolean | undefined;
}

interface AllChattersOptions {
    [key: string]: ChatterOptions;
}

let allChattersOptions: AllChattersOptions = {};
export let currentMenuChatter = writable<string | undefined>(undefined);

function updateChatterOptions(chatters_data: any) {
    allChattersOptions = chatters_data;
    console.log(allChattersOptions);
}

export function getChatterOptions(name: string) {
    return allChattersOptions[name];
}

let name: string | undefined = undefined;

currentMenuChatter.subscribe(value => {
    if (value) {
        name = value;
    }
});

export const chatterOptionsContext = {
    allChattersOptions,
    store: chatterOptionsStore,
    updateMuted: (value: boolean | undefined) => {
        chatterOptionsStore.update(store => ({ ...store, isMuted: value }));
    },
    updateMessageReplace: (value: string | undefined) => {
        chatterOptionsStore.update(store => ({ ...store, messageReplace: value }));
    },
    updateTTSLength: (value: number) => {
        chatterOptionsStore.update(store => ({ ...store, ttsLength: value }));
    },
    updateChatterName: (value: string) => {
        chatterOptionsStore.update(store => ({ ...store, name: value }));
    },
    updateKillTTS: (value: boolean) => {
        chatterOptionsStore.update(store => ({ ...store, killTTS: value }));
    }
};

chatterOptionsStore.subscribe(store => {
    if (ws) {
        ws.send(JSON.stringify({
            event: 'UPDATE_SETTINGS',
            client_type: 'WEB_CLIENT',
            data: {
                name: store.name,
                is_muted: store.is_muted,
                message_replace: store.message_replace,
                tts_length: store.tts_length,
                kill_TTS: store.kill_TTS
            }
        }));
    }
});

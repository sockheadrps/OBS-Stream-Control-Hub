import { writable } from 'svelte/store';

export const websocket = writable<WebSocket | null>(null);
export const websocketState = writable<'connected' | 'disconnected' | 'identifying' | 'identified'>('disconnected');
export const lastMessage = writable<any>(null);

// Store for authentication status and settings
const OBS_RPC_VERSION = 1; // OBS WebSocket RPC version
let authToken: string | null = null; // Set your auth token here if required

export function connectWebSocket(url: string, token: string | null = null) {
    authToken = token;
    const ws = new WebSocket(url);
    websocket.set(ws);
    websocketState.set('disconnected');

    ws.onopen = () => {
        websocketState.set('connected');
        console.log('WebSocket connected');

        // Send Identify request
        identifyWebSocket(ws);
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);

        if (message.op === 2) {
            console.log('OBS WebSocket identified:', message);
            websocketState.set('identified');
        } else {
            lastMessage.set(message);
            // console.log('WebSocket message received:', message);
        }
    };

    ws.onclose = () => {
        websocketState.set('disconnected');
        console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

function identifyWebSocket(ws: WebSocket) {
    const identifyMessage = {
        op: 1, // Identify operation
        d: {
            rpcVersion: OBS_RPC_VERSION,
            authentication: authToken || undefined // Include auth token if provided
        }
    };

    websocketState.set('identifying');
    ws.send(JSON.stringify(identifyMessage));
}

export function sendMessage(message: any) {
    websocket.subscribe((ws) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message));
        } else {
            console.error('WebSocket is not open or identified');
        }
    });
}


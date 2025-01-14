import { browser } from '$app/environment';
import { writable, type Writable } from 'svelte/store';
import type { ControlPanelSettings } from './controlPanelStore';

let ws: WebSocket;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const INITIAL_RECONNECT_DELAY = 1000;

export const overlaySettings = writable<ControlPanelSettings | null>(null);

function initWebSocket() {
    if (browser && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
            const host = window.location.hostname;
            const port = '8100';

            ws = new WebSocket(`${protocol}://${host}:${port}/websockets/overlay`);
            
            ws.onopen = () => {
                console.log('WebSocket connected');
                reconnectAttempts = 0; // Reset attempts on successful connection
                ws.send(JSON.stringify({'event': 'connect', 'client':'overlay'}));
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    overlaySettings.set(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                reconnectAttempts++;
                ws.close();
            };

            ws.onclose = () => {
                console.log('WebSocket closed');
                const delay = INITIAL_RECONNECT_DELAY * Math.pow(2, reconnectAttempts);
                if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                    console.log(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})`);
                    setTimeout(initWebSocket, delay);
                } else {
                    console.error('Max reconnection attempts reached. Please check server status.');
                }
            };
        } catch (error) {
            console.error('WebSocket initialization failed:', error);
            reconnectAttempts++;
        }
    }
}

if (browser) {
    initWebSocket();
}

export function closeWebSocket() {
    if (ws) {
        ws.close();
    }
}

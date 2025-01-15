import { browser } from '$app/environment';





let ws: WebSocket;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const INITIAL_RECONNECT_DELAY = 1000;

function initWebSocket() {
    if (browser && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
            const host = window.location.hostname;
            const port = '8100';
            console.log(`${protocol}://${host}:${port}/websockets/overlay`);

            ws = new WebSocket(`${protocol}://${host}:${port}/websockets/overlay`);
            
            ws.onopen = () => {
                console.log('WebSocket connected');
                reconnectAttempts = 0; // Reset attempts on successful connection
                ws.send(JSON.stringify({'event': 'connect', 'client':'control_panel'}));
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                reconnectAttempts++;
                // Close the socket on error to trigger reconnect
                ws.close();
            };

            ws.onclose = () => {
                console.log('WebSocket closed');
                // Exponential backoff for reconnect attempts
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


interface ControlPanelSettings {
    particleCount: number;
    particleSpeed: number;
    baseSize: number;
    baseHue: number;
    numberOfStars: number;
    blackParticles: boolean;
    blackStars: boolean;
    trailLength: number;
    rotationSpeed: number;
    starSpeed: number;
    starSize: number;
    starOffset: number;
    wanderStrength: number;
    collisionForce: number;
    trailColor: number;
}
export function sendSettings(settings: ControlPanelSettings) {
    if (browser) {
        localStorage.setItem('controlPanelSettings', JSON.stringify(settings));
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                client: 'control_panel',
                data: settings
            }));
        }
    }
}


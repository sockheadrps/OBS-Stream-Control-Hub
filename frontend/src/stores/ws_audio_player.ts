import { writable } from 'svelte/store';

export const socketStore = writable<{
    socket: WebSocket | null;
    latestMessage: any;
}>({
    socket: null,
    latestMessage: null,
});

export function initializeSocket(): WebSocket | null {
    let socket: WebSocket | null = null;

    socketStore.update((store) => {
        if (store.socket) {
            console.log('WebSocket already initialized.');
            socket = store.socket; // Use the existing socket
            return store; // No need to reinitialize
        }

        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const host = window.location.hostname;
        const port = '8100';

        socket = new WebSocket(`${protocol}://${host}:${port}/websockets/audio`);

        socket.onopen = () => {
            console.log('WebSocket connection established.');
            socket?.send(JSON.stringify({ event: 'info_request' }));
        };

        socket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                // console.log('Received message:', message);

                socketStore.update((store) => ({
                    ...store,
                    latestMessage: message,
                }));
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        socket.onclose = () => {
            console.log('WebSocket connection closed.');
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        socketStore.set({ socket, latestMessage: null });

        return { socket, latestMessage: null };
    });

    return socket;
}

export function sendMessage(socket: WebSocket, message: any) {
  try {
      socket.send(JSON.stringify(message));
  } catch (error) {
      console.error('Failed to send WebSocket message:', error);
  }
}

export function closeSocket() {
    socketStore.update((store) => {
        if (store.socket) {
            store.socket.close();
            console.log('WebSocket closed.');
        }
        return { socket: null, latestMessage: null };
    });
}

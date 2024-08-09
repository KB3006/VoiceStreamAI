import websockets
import json
from config import WEBSOCKET_ADDRESS, RATE, CHANNELS, LANGUAGE


class ConnectionManager:
    def __init__(self):
        self.websocket = None

    async def connect(self):
        """Establishes the WebSocket connection."""
        self.websocket = await websockets.connect(WEBSOCKET_ADDRESS)
        print("WebSocket connection established")

    async def send_initial_config(self):
        """Sends the initial audio configuration to the server."""
        config = self.create_audio_config()
        await self.websocket.send(json.dumps(config))
        print("Sent audio configuration to the server")

    def create_audio_config(self):
        """Creates the initial configuration payload for the WebSocket server."""
        return {
            'type': 'config',
            'data': {
                'sampleRate': RATE,
                'channels': CHANNELS,
                'language': LANGUAGE,
                'processing_strategy': 'silence_at_end_of_chunk',
                'processing_args': {
                    'chunk_length_seconds': 3,
                    'chunk_offset_seconds': 0.1
                }
            }
        }

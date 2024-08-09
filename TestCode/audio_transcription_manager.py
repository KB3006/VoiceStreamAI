import asyncio
import pyaudio
import json
from connection_manager import ConnectionManager
from config import CHUNK, FORMAT, RATE, CHANNELS
import websockets
class AudioTranscriptionManager:
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.audio_interface = pyaudio.PyAudio()

    async def start_streaming(self):
        """Begins streaming audio data and handles transcription."""
        stream = self.audio_interface.open(format=self.get_pyaudio_format(FORMAT), channels=CHANNELS,
                                           rate=RATE, input=True,
                                           frames_per_buffer=CHUNK)

        print("Recording...")

        # Start receiving messages and sending audio concurrently
        await asyncio.gather(self.receive_messages(), self.send_audio(stream))

    async def receive_messages(self):
        """Handles incoming messages from the WebSocket server."""
        while True:
            try:
                response = await self.connection_manager.websocket.recv()
                print("Received message from server")
                self.on_receive(response)
            except websockets.exceptions.ConnectionClosed as e:
                print("Connection closed: ", e)
                break
            except Exception as e:
                print("Error receiving message:", e)
                break

    async def send_audio(self, stream):
        """Reads audio data from the microphone and sends it to the WebSocket server."""
        try:
            while True:
                data = stream.read(CHUNK)
                await self.connection_manager.websocket.send(data)
        except Exception as e:
            print("Error during recording:", e)
        finally:
            self.cleanup(stream)

    def on_receive(self, response):
        """Processes the server's response, printing the transcription result."""
        print(response)
        try:
            data = json.loads(response)
            print("Transcription:", data['text'])
        except json.JSONDecodeError:
            print("Received non-JSON message:", response)

    def cleanup(self, stream):
        """Stops the audio stream and terminates the PyAudio instance."""
        stream.stop_stream()
        stream.close()
        self.audio_interface.terminate()
        print("Recording and streaming ended")

    @staticmethod
    def get_pyaudio_format(format_str):
        """Maps string format to PyAudio format constants."""
        format_mapping = {
            'paInt16': pyaudio.paInt16,
            'paFloat32': pyaudio.paFloat32
        }
        return format_mapping.get(format_str, pyaudio.paInt16)

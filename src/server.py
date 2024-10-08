import json
import logging
import ssl
import uuid

import websockets
import base64
from src.client import Client

class Server:
    """
    Represents the WebSocket server for handling real-time audio transcription.

    This class manages WebSocket connections, processes incoming audio data,
    and interacts with VAD and ASR pipelines for voice activity detection and
    speech recognition.

    Attributes:
        vad_pipeline: An instance of a voice activity detection pipeline.
        asr_pipeline: An instance of an automatic speech recognition pipeline.
        host (str): Host address of the server.
        port (int): Port on which the server listens.
        sampling_rate (int): The sampling rate of audio data in Hz.
        samples_width (int): The width of each audio sample in bits.
        connected_clients (dict): A dictionary mapping client IDs to Client
                                  objects.
    """

    def __init__(
        self,
        vad_pipeline,
        asr_pipeline,
        host="localhost",
        port=8765,
        sampling_rate=16000,
        samples_width=2,
        certfile=None,
        keyfile=None,
    ):
        self.vad_pipeline = vad_pipeline
        self.asr_pipeline = asr_pipeline
        self.host = host
        self.port = port
        self.sampling_rate = sampling_rate
        self.samples_width = samples_width
        self.certfile = certfile
        self.keyfile = keyfile
        self.connected_clients = {}

    async def handle_audio(self, client, websocket):
        while True:
            message = await websocket.recv()

            if isinstance(message, bytes):
                client.append_audio_data(message)
            elif isinstance(message, str):
                try:
                    config = json.loads(message)
                except Exception as e:
                    print(e)
                    # print(message)
                    base64_bytes = message.encode("ascii")

                    sample_string_bytes = base64.b64decode(base64_bytes)
                    sample_string = sample_string_bytes.decode("ascii")
                    
                    # print(f"Decoded string: {sample_string}")
                    config = json.loads(sample_string)
                    # print(config)
                # print(config)
                if config.get("type") == "config":
                    client.update_config(config)
                    # print(config["data"])
                    logging.debug(f"Updated config: {client.config}")
                    continue
            else:
                print(f"Unexpected message type from {client.client_id}")

            # this is synchronous, any async operation is in BufferingStrategy
            client.process_audio(
                websocket, self.vad_pipeline, self.asr_pipeline
            )

    async def handle_websocket(self, websocket, path):
        headers = websocket.request_headers

        print(f"Client connecting with headers:")
        for header, value in headers.items():
            print(f"{header}: {value}")
        
        print(path)
        if path != "/transcription/voice":
            await websocket.close()
            return
        
        client_id = str(uuid.uuid4())
        client = Client(client_id, self.sampling_rate, self.samples_width)
        self.connected_clients[client_id] = client

        print(f"Client {client_id} connected")
        await websocket.send(f"Client {client_id} connected")
        try:
            await self.handle_audio(client, websocket)
        except websockets.ConnectionClosed as e:
            print(f"Connection with {client_id} closed: {e}")
        finally:
            del self.connected_clients[client_id]

    def GetClient(self,client_id):
        for i in self.connected_clients.keys():
            if self.connected_clients[i].client_id == client_id:
                return self.connected_clients[i]
        
        return None
    def start(self):
        if self.certfile:
            # Create an SSL context to enforce encrypted connections
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

            # Load your server's certificate and private key
            ssl_context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

            print(
                f"WebSocket server ready to accept secure connections on "
                f"{self.host}:{self.port}/transcription/voice here ssl true"
            )

            # Pass the SSL context to the serve function along with the host and port
            return websockets.serve(
                self.handle_websocket, self.host, self.port, ssl=ssl_context
            )
        else:
            print(
                f"WebSocket server ready to accept connections on "
                f"{self.host}:{self.port}/transcription/voice here ssl false"
            )
            return websockets.serve(
                self.handle_websocket, self.host, self.port
            )

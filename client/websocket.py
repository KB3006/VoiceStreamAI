import asyncio
import websockets
import pyaudio
import json

# WebSocket server address
WEBSOCKET_ADDRESS = 'wss://devapi-asava.atirath.com/transcription'

# Audio stream settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Room and user info
ROOM_ID = 'a1'
PERSON = 'agent'
LANGUAGE = 'english'  # Change as needed

# Global variables
websocket = None
isRecording = False

async def connect():
    global websocket
    websocket = await websockets.connect(WEBSOCKET_ADDRESS)
    print("WebSocket connection established")

    # Send initial configuration
    config = {
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
    await websocket.send(json.dumps(config))
    print("Sent audio configuration to the server")

    # Initialize PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")

    async def receive_messages():
        while True:
            try:
                response = await websocket.recv()
                print("Received message from server")
                on_receive(response)
            except websockets.exceptions.ConnectionClosed as e:
                print("Connection closed: ", e)
                break
            except Exception as e:
                print("Error receiving message:", e)
                break

    async def send_audio():
        try:
            while True:
                data = stream.read(CHUNK)
                # on_send(data)
                await websocket.send(data)
                await asyncio.sleep(0.01)
        except Exception as e:
            print("Error during recording:", e)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            on_end()

    # Run both tasks concurrently
    await asyncio.gather(receive_messages(), send_audio())


def on_receive(response):
    print(response)
    try:
        data = json.loads(response)
        
        print("Transcription:", data['text'])
        
    except json.JSONDecodeError:
        print("Received non-JSON message:", response)

def on_end():
    print("Recording and streaming ended")

def process_audio(sample_data):
    output_sample_rate = 16000
    decrease_result_buffer = decrease_sample_rate(sample_data, RATE, output_sample_rate)
    audio_data = convert_float32_to_int16(decrease_result_buffer)
    return audio_data

def decrease_sample_rate(buffer, input_sample_rate, output_sample_rate):
    if input_sample_rate < output_sample_rate:
        print("Sample rate too small.")
        return buffer
    elif input_sample_rate == output_sample_rate:
        return buffer

    sample_rate_ratio = input_sample_rate / output_sample_rate
    new_length = int(len(buffer) / sample_rate_ratio)
    result = [0]* new_length
    offset_result = 0
    offset_buffer = 0
    while offset_result < new_length:
        next_offset_buffer = round((offset_result + 1) * sample_rate_ratio)
        accum = sum(buffer[offset_buffer:next_offset_buffer])
        count = next_offset_buffer - offset_buffer
        result[offset_result] = accum / count
        offset_result += 1
        offset_buffer = next_offset_buffer
    return result

def convert_float32_to_int16(buffer):
    buf = [int(max(-1.0, min(1.0, x)) * 32767) for x in buffer]
    return bytearray(buf)

if __name__ == '__main__':
    asyncio.run(connect())
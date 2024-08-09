import asyncio
from connection_manager import ConnectionManager
from audio_transcription_manager import AudioTranscriptionManager


async def main():
    # Initialize the connection manager
    connection_manager = ConnectionManager()
    
    # Connect to the WebSocket server
    await connection_manager.connect()
    
    # Send initial configuration
    await connection_manager.send_initial_config()
    
    # Initialize the audio transcription manager with the connection
    audio_manager = AudioTranscriptionManager(connection_manager)
    
    # Start streaming and transcription
    await audio_manager.start_streaming()


if __name__ == '__main__':
    asyncio.run(main())

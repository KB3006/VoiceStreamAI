# config.py

# WebSocket server configuration
WEBSOCKET_ADDRESS = 'wss://devapi-asava.atirath.com/transcription'

# Audio stream settings
CHUNK = 1024
FORMAT = 'paInt16'  # 16 bit slinear 
CHANNELS = 1
RATE = 16000

# Room and user info
REPORT_ID = 'REPORT1'
SESSION_ID = 'SESSION1'
PERSON = 'agent'  # OR 'customer'
LANGUAGE = 'english'  # Set to 'null' if multilingual

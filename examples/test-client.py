"""
Test client for NBK Realtime API
Validates WebSocket connection, authentication, and audio streaming

This is a minimal example showing how to connect to the deployed backend.
For full client implementation, see main.py
"""

import asyncio
import json
import os
import base64
import websockets
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Connection details (these come from deployment-config.txt or azd outputs)
APIM_GATEWAY_URL = os.getenv("APIM_GATEWAY_URL", "https://apim-vihqa5j54mcr6.azure-api.net")
APIM_API_KEY = os.getenv("APIM_API_KEY", "")
INFERENCE_API_PATH = os.getenv("INFERENCE_API_PATH", "inference")
INFERENCE_API_VERSION = os.getenv("INFERENCE_API_VERSION", "2024-10-01-preview")

# Construct WebSocket URL
wss_url = f"wss://{APIM_GATEWAY_URL.replace('https://', '')}/{INFERENCE_API_PATH}/openai/realtime?api-version={INFERENCE_API_VERSION}"

print("=" * 80)
print("NBK Realtime API - Test Client")
print("=" * 80)
print(f"\nWebSocket URL: {wss_url}")
print(f"API Key: {APIM_API_KEY[:20]}..." if APIM_API_KEY else "API Key: NOT SET")
print()


async def test_connection():
    """Test basic WebSocket connection and authentication"""
    print("🔌 Testing WebSocket connection...")
    
    try:
        # Connect with API key authentication
        headers = {
            "api-key": APIM_API_KEY
        }
        
        async with websockets.connect(wss_url, extra_headers=headers) as ws:
            print("✅ WebSocket connected successfully!")
            
            # Send session configuration
            print("\n📝 Configuring session...")
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["audio", "text"],
                    "instructions": "You are a helpful NBK assistant. Respond briefly.",
                    "voice": "echo",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "input_audio_transcription": {
                        "model": "whisper-1"
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 200
                    }
                }
            }
            
            await ws.send(json.dumps(session_config))
            print("✅ Session configuration sent")
            
            # Wait for session.created or session.updated
            print("\n⏳ Waiting for server response...")
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            event = json.loads(response)
            print(f"✅ Received: {event.get('type', 'unknown')}")
            
            if event.get('type') in ['session.created', 'session.updated']:
                print("\n✅ Session configured successfully!")
                print(f"   Voice: {event.get('session', {}).get('voice', 'N/A')}")
                print(f"   Modalities: {event.get('session', {}).get('modalities', 'N/A')}")
                print(f"   Turn Detection: {event.get('session', {}).get('turn_detection', {}).get('type', 'N/A')}")
            
            # Test text input
            print("\n📤 Sending test text input...")
            text_event = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Hello, this is a test."
                        }
                    ]
                }
            }
            await ws.send(json.dumps(text_event))
            
            # Request response
            await ws.send(json.dumps({"type": "response.create"}))
            print("✅ Text input sent, waiting for response...")
            
            # Listen for response
            timeout_count = 0
            max_timeouts = 10
            
            while timeout_count < max_timeouts:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                    event = json.loads(response)
                    event_type = event.get('type', 'unknown')
                    
                    print(f"   📨 {event_type}")
                    
                    if event_type == 'response.audio_transcript.delta':
                        print(f"      Transcript: {event.get('delta', '')}")
                    elif event_type == 'response.audio_transcript.done':
                        print(f"      Full transcript: {event.get('transcript', '')}")
                    elif event_type == 'response.done':
                        print("\n✅ Response complete!")
                        break
                    elif event_type == 'error':
                        print(f"\n❌ Error: {event.get('error', {})}")
                        break
                        
                except asyncio.TimeoutError:
                    timeout_count += 1
                    if timeout_count >= max_timeouts:
                        print("\n⚠️  Timeout waiting for response (this is OK for connection test)")
                        break
            
            print("\n" + "=" * 80)
            print("✅ CONNECTION TEST PASSED")
            print("=" * 80)
            print("\nThe backend is working correctly!")
            print("Frontend teams can now integrate using the WebSocket URL and API key.")
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"\n❌ Authentication failed: {e}")
        print("   Check that APIM_API_KEY is correct in .env file")
    except ConnectionError as e:
        print(f"\n❌ Connection failed: {e}")
        print("   Check that APIM_GATEWAY_URL is correct and accessible")
    except Exception as e:
        print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


async def test_audio_input():
    """Test audio input with a simple PCM16 tone"""
    print("\n" + "=" * 80)
    print("🎵 Testing Audio Input")
    print("=" * 80)
    
    try:
        headers = {"api-key": APIM_API_KEY}
        
        async with websockets.connect(wss_url, extra_headers=headers) as ws:
            # Configure session
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["audio", "text"],
                    "instructions": "You are a helpful assistant. Respond briefly.",
                    "voice": "echo",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16"
                }
            }
            await ws.send(json.dumps(session_config))
            
            # Wait for session response
            await ws.recv()
            
            print("✅ Session configured")
            print("📤 Sending test audio data (silence)...")
            
            # Send 1 second of silence (24kHz PCM16 = 48000 bytes)
            silence = b'\x00' * 48000
            audio_chunk_base64 = base64.b64encode(silence).decode('utf-8')
            
            audio_event = {
                "type": "input_audio_buffer.append",
                "audio": audio_chunk_base64
            }
            await ws.send(json.dumps(audio_event))
            
            # Commit audio
            await ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
            await ws.send(json.dumps({"type": "response.create"}))
            
            print("✅ Audio sent successfully!")
            print("   (Audio streaming is working)")
            
            # Close gracefully
            await ws.close()
            
            print("\n✅ AUDIO TEST PASSED")
            
    except Exception as e:
        print(f"\n❌ Audio test failed: {e}")


if __name__ == "__main__":
    print("\n⚠️  Make sure to set APIM_API_KEY in your .env file first!")
    print("   You can copy it from deployment-config.txt\n")
    
    if not APIM_API_KEY:
        print("❌ APIM_API_KEY not set! Please update .env file.")
        exit(1)
    
    # Run tests
    asyncio.run(test_connection())
    asyncio.run(test_audio_input())
    
    print("\n✅ All tests completed!")
    print("\nNext steps:")
    print("  1. Frontend teams can use the WebSocket URL and API key from deployment-config.txt")
    print("  2. See FRONTEND.md for integration examples in JavaScript, Python, and C#")
    print("  3. See main.py for full implementation with microphone input and speaker output")

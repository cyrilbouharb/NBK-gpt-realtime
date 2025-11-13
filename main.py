"""
Speech-to-Speech Realtime API for NBK Customer Service
Based on realtime-mcp-agents.ipynb notebook
"""
import asyncio
import base64
import json
import random
import numpy as np
import openai
import pyaudio
from config import get_config
from scrape_nbk import load_nbk_knowledge, format_knowledge_for_prompt


# Audio configuration
SAMPLE_RATE = 24000
CHUNK_SIZE = 480  # 20ms at 24kHz


class RealtimeNBKAgent:
    """Simple realtime agent for NBK customer service."""
    
    def __init__(self):
        self.config = get_config()
        self.client = None
        self.connection = None
        
    async def initialize(self):
        """Initialize the Azure OpenAI client."""
        print("🔧 Initializing Azure OpenAI Realtime client...")
        
        # Build the endpoint URL exactly like the notebook
        endpoint = f"{self.config.azure.apim_gateway_url}/{self.config.azure.inference_api_path}"
        
        self.client = openai.AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=self.config.azure.api_key,
            api_version=self.config.azure.inference_api_version,
        )
        
        print(f"✅ Client initialized with endpoint: {endpoint}")
        return True
    
    def get_session_config(self):
        """Get session configuration with NBK instructions."""
        # Random voice selection like the notebook
        voices = ['alloy', 'ash', 'ballad', 'coral', 'echo', 'sage', 'shimmer', 'verse']
        voice = random.choice(voices)
        
        print(f"🎤 Selected voice: {voice}")
        
        # Get deployment name
        deployment_name = self.config.azure.models_config[0]['name']
        
        # Load NBK knowledge base and add to instructions
        print("📚 Loading NBK knowledge base...")
        nbk_knowledge = load_nbk_knowledge()
        
        if nbk_knowledge:
            # Format knowledge for prompt
            knowledge_text = format_knowledge_for_prompt(nbk_knowledge, max_chars=6000)
            # Combine base instructions with knowledge
            full_instructions = f"""{self.config.bing_grounding.grounding_instructions}

{knowledge_text}

Use the above NBK information to answer customer questions accurately. Always cite the source when using this information."""
            print(f"✅ Loaded {len(nbk_knowledge)} pages of NBK information")
        else:
            print("⚠️  No NBK knowledge base found. Using base instructions only.")
            full_instructions = self.config.bing_grounding.grounding_instructions
        
        # Session config following notebook pattern
        session_config = {
            "input_audio_transcription": {
                "model": "whisper-1",
            },
            "turn_detection": {
                "threshold": 0.4,
                "silence_duration_ms": 600,
                "type": "server_vad"
            },
            "instructions": full_instructions,
            "voice": voice,
            "modalities": ["audio", "text"],
            "tools": []
        }
        
        return deployment_name, session_config
    
    async def run_speech_to_speech(self):
        """Run the speech-to-speech interaction."""
        if not self.client:
            print("❌ Client not initialized. Call initialize() first.")
            return
        
        deployment_name, session_config = self.get_session_config()
        
        print(f"\n🚀 Connecting to model: {deployment_name}")
        print("🎧 Starting speech-to-speech session...")
        print("🎤 Speak now! (Press Ctrl+C to stop)\n")
        
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        print("🔊 Available audio devices:")
        output_devices = []
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxOutputChannels'] > 0:
                output_devices.append((i, info['name']))
                print(f"  [{i}] {info['name']}")
        
        # Ask user to select device or use default
        print("\n🔊 Press Enter to use default, or type device number:")
        try:
            choice = input().strip()
            if choice:
                output_device_index = int(choice)
                device_name = audio.get_device_info_by_index(output_device_index)['name']
                print(f"🔊 Selected: {device_name}\n")
            else:
                default_output = audio.get_default_output_device_info()
                output_device_index = default_output['index']
                print(f"🔊 Using default: {default_output['name']}\n")
        except:
            default_output = audio.get_default_output_device_info()
            output_device_index = default_output['index']
            print(f"🔊 Using default: {default_output['name']}\n")
        
        # Open input stream (microphone)
        input_stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
        
        # Open output stream (speakers) with larger buffer for better playback
        output_stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            output=True,
            output_device_index=output_device_index,
            frames_per_buffer=CHUNK_SIZE * 4  # Larger buffer
        )
        
        try:
            async with self.client.realtime.connect(model=deployment_name) as conn:
                # Update session with our config
                await conn.session.update(session=session_config)
                
                self.connection = conn
                
                # Create tasks for sending and receiving audio
                async def send_audio():
                    """Capture and send audio from microphone."""
                    while True:
                        try:
                            # Read audio from microphone
                            audio_data = input_stream.read(CHUNK_SIZE, exception_on_overflow=False)
                            # Convert to base64
                            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                            # Send to API
                            await conn.input_audio_buffer.append(audio=audio_b64)
                            await asyncio.sleep(0.01)  # Small delay
                        except Exception as e:
                            print(f"Audio send error: {e}")
                            break
                
                # Track if response is active
                response_active = False
                
                async def receive_events():
                    """Receive and handle events from API."""
                    nonlocal response_active
                    
                    async for event in conn:
                        # Handle different event types
                        if event.type == "response.created":
                            # Mark response as active when it starts
                            response_active = True
                        
                        elif event.type == "input_audio_buffer.speech_started":
                            print("\n🗣️  Speech detected...")
                            # Only cancel if there's an active response
                            if response_active:
                                print("⏸️  Interrupting assistant...")
                                await conn.response.cancel()
                        
                        elif event.type == "conversation.item.input_audio_transcription.completed":
                            print(f"👤 You: {event.transcript}")
                        
                        elif event.type == "response.audio_transcript.delta":
                            print(event.delta, end="", flush=True)
                        
                        elif event.type == "response.audio_transcript.done":
                            print(f"\n🤖 Assistant: {event.transcript}")
                        
                        elif event.type == "response.audio.delta":
                            # Decode and play audio
                            try:
                                audio_bytes = base64.b64decode(event.delta)
                                output_stream.write(audio_bytes)
                                print("🔊", end="", flush=True)  # Visual feedback
                            except Exception as e:
                                print(f"\n⚠️ Audio playback error: {e}")
                        
                        elif event.type == "response.done":
                            print("\n✅ Response complete\n")
                            response_active = False  # Response finished
                        
                        elif event.type == "response.cancelled":
                            print("\n🚫 Response cancelled (interrupted)\n")
                            response_active = False  # Response cancelled
                        
                        elif event.type == "error":
                            print(f"\n❌ Error: {event}")
                            response_active = False  # Reset on error
                
                # Run both tasks concurrently
                await asyncio.gather(
                    send_audio(),
                    receive_events()
                )
        
        except KeyboardInterrupt:
            print("\n\n👋 Stopping session...")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean up
            input_stream.stop_stream()
            input_stream.close()
            output_stream.stop_stream()
            output_stream.close()
            audio.terminate()
            if self.connection:
                await self.connection.close()


async def main():
    """Main entry point."""
    print("=" * 60)
    print("NBK Customer Service - Speech-to-Speech Assistant")
    print("=" * 60)
    
    agent = RealtimeNBKAgent()
    
    if await agent.initialize():
        await agent.run_speech_to_speech()


if __name__ == "__main__":
    asyncio.run(main())

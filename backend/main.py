"""
NBK Banking Assistant - WebSocket Proxy Backend

This backend:
1. Loads NBK knowledge base from nbk_knowledge.json
2. Proxies WebSocket connections between frontend and Azure OpenAI Realtime API
3. Injects NBK knowledge into system prompt on session start
4. Configures Echo voice and optimized VAD settings
5. Handles Azure OpenAI authentication (frontend only needs APIM key)
"""

import asyncio
import json
import os
from typing import Dict, Any
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NBK Realtime Backend")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure OpenAI Configuration from environment
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "gpt-realtime")
API_VERSION = os.getenv("INFERENCE_API_VERSION", "2024-10-01-preview")

# NBK Knowledge Base
NBK_KNOWLEDGE = []

def load_nbk_knowledge():
    """Load NBK knowledge base from JSON file"""
    global NBK_KNOWLEDGE
    try:
        # Try loading from parent directory (where nbk_knowledge.json is)
        with open("../nbk_knowledge.json", "r", encoding="utf-8") as f:
            NBK_KNOWLEDGE = json.load(f)
        logger.info(f"✅ Loaded {len(NBK_KNOWLEDGE)} NBK knowledge entries")
    except FileNotFoundError:
        try:
            # Try current directory (when running in container)
            with open("nbk_knowledge.json", "r", encoding="utf-8") as f:
                NBK_KNOWLEDGE = json.load(f)
            logger.info(f"✅ Loaded {len(NBK_KNOWLEDGE)} NBK knowledge entries")
        except FileNotFoundError:
            logger.warning("⚠️ nbk_knowledge.json not found. Using empty knowledge base.")
            NBK_KNOWLEDGE = []

def build_system_instructions() -> str:
    """Build system instructions with NBK knowledge"""
    instructions = """You are a professional customer service representative for National Bank of Kuwait (NBK).

Your role:
- Provide accurate information about NBK products and services
- Be courteous, professional, and helpful
- Use the NBK knowledge base below to answer questions
- If you don't know something, admit it and offer to connect them with a specialist
- Speak naturally and conversationally
- Keep responses concise but informative

NBK Knowledge Base:
"""
    
    for idx, entry in enumerate(NBK_KNOWLEDGE, 1):
        instructions += f"\n{idx}. {entry['title']}\n"
        instructions += f"   URL: {entry['url']}\n"
        # Truncate content to first 500 chars to keep prompt manageable
        content_preview = entry['content'][:500] + "..." if len(entry['content']) > 500 else entry['content']
        instructions += f"   {content_preview}\n"
    
    return instructions

# Load knowledge on startup
load_nbk_knowledge()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "knowledge_entries": len(NBK_KNOWLEDGE),
        "instructions_length": len(build_system_instructions())
    }

@app.websocket("/realtime")
async def websocket_proxy(websocket: WebSocket):
    """
    Proxy WebSocket connection between client and Azure OpenAI Realtime API
    Injects NBK knowledge into system prompt
    """
    await websocket.accept()
    logger.info("✅ Client connected")
    
    # Build WebSocket URL for Azure OpenAI
    ws_endpoint = AZURE_OPENAI_ENDPOINT.replace("https://", "wss://").replace("http://", "ws://")
    azure_ws_url = f"{ws_endpoint}openai/realtime?api-version={API_VERSION}&deployment={DEPLOYMENT_NAME}"
    
    logger.info(f"🔗 Connecting to Azure OpenAI: {azure_ws_url}")
    
    try:
        # Connect to Azure OpenAI Realtime API
        async with websockets.connect(
            azure_ws_url,
            extra_headers={
                "api-key": AZURE_OPENAI_KEY
            }
        ) as azure_ws:
            logger.info("✅ Connected to Azure OpenAI Realtime API")
            
            # Send initial session configuration with NBK knowledge
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "instructions": build_system_instructions(),
                    "voice": "echo",  # Professional male voice for banking
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "input_audio_transcription": {
                        "model": "whisper-1"
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,  # Lower threshold = more sensitive to speech
                        "prefix_padding_ms": 300,  # Capture more audio before speech
                        "silence_duration_ms": 500  # Shorter silence = faster detection
                    },
                    "temperature": 0.7,
                    "max_response_output_tokens": 4096
                }
            }
            
            logger.info(f"📤 Sending session config: {json.dumps(session_config, indent=2)}")
            await azure_ws.send(json.dumps(session_config))
            logger.info("✅ Sent session configuration with NBK knowledge")
            
            # Track if AI is currently responding
            is_responding = False
            current_response_id = None
            
            # Create bidirectional proxy with interruption support
            async def forward_to_azure():
                """Forward messages from client to Azure OpenAI"""
                try:
                    while True:
                        message = await websocket.receive_text()
                        # Just forward everything - let Azure handle VAD
                        await azure_ws.send(message)
                        
                except WebSocketDisconnect:
                    logger.info("Client disconnected")
                except Exception as e:
                    logger.error(f"Error forwarding to Azure: {e}")
            
            async def forward_to_client():
                """Forward messages from Azure OpenAI to client with response tracking and interruption"""
                nonlocal is_responding, current_response_id
                try:
                    async for message in azure_ws:
                        data = json.loads(message)
                        msg_type = data.get("type")
                        
                        # Handle interruption: Azure VAD detected new speech during response
                        if msg_type == "input_audio_buffer.speech_started" and is_responding:
                            logger.info("🛑 New speech detected during response - canceling")
                            cancel_message = {
                                "type": "response.cancel"
                            }
                            await azure_ws.send(json.dumps(cancel_message))
                            is_responding = False
                            current_response_id = None
                        
                        # Log important events
                        if msg_type in ["response.created", "response.done", "response.audio.delta", "response.audio.done"]:
                            if msg_type == "response.audio.delta":
                                logger.info(f"🔊 Audio delta received (size: {len(data.get('delta', ''))} bytes)")
                            else:
                                logger.info(f"📨 {msg_type}: {json.dumps(data, indent=2)}")
                        
                        # Track when response starts
                        if msg_type == "response.created":
                            is_responding = True
                            current_response_id = data.get("response", {}).get("id")
                            logger.info(f"📢 Response started: {current_response_id}")
                        
                        # Track when response ends
                        elif msg_type in ["response.done", "response.cancelled", "response.failed"]:
                            is_responding = False
                            logger.info(f"✅ Response ended: {msg_type}")
                            current_response_id = None
                        
                        # Forward message to client
                        await websocket.send_text(message)
                        
                except Exception as e:
                    logger.error(f"Error forwarding to client: {e}")
            
            # Run both directions concurrently
            await asyncio.gather(
                forward_to_azure(),
                forward_to_client(),
                return_exceptions=True
            )
            
    except Exception as e:
        logger.error(f"❌ WebSocket proxy error: {e}")
        await websocket.close(code=1011, reason=str(e))
    finally:
        logger.info("🔌 Connection closed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

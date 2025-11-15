"""
NBK Realtime WebSocket Proxy Backend
Injects NBK knowledge base and system prompts into Azure OpenAI Realtime API
"""

import asyncio
import json
import os
import logging
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Header, Query
from fastapi.middleware.cors import CORSMiddleware
import websockets
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NBK Realtime Proxy")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load NBK Knowledge Base
def load_nbk_knowledge():
    """Load scraped NBK knowledge from JSON file."""
    try:
        knowledge_file = os.path.join(os.path.dirname(__file__), "..", "nbk_knowledge.json")
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            knowledge = json.load(f)
        logger.info(f"Loaded {len(knowledge)} knowledge entries from NBK")
        return knowledge
    except FileNotFoundError:
        logger.warning("nbk_knowledge.json not found - running without knowledge base")
        return []
    except Exception as e:
        logger.error(f"Error loading NBK knowledge: {e}")
        return []

# Format knowledge for system prompt
def format_knowledge_for_prompt(knowledge_base, max_chars=8000):
    """Format knowledge base entries into a concise system prompt."""
    if not knowledge_base:
        return ""
    
    formatted = "\n\n=== NBK Knowledge Base ===\n"
    total_chars = 0
    
    for item in knowledge_base:
        title = item.get('title', 'N/A')
        url = item.get('url', 'N/A')
        content = item.get('content', '')
        
        # Truncate long content
        if len(content) > 500:
            content = content[:500] + "..."
        
        entry = f"\n[{title}]\nURL: {url}\nContent: {content}\n"
        
        if total_chars + len(entry) > max_chars:
            break
            
        formatted += entry
        total_chars += len(entry)
    
    formatted += "\n=== End Knowledge Base ===\n"
    return formatted

# Build system instructions
def build_system_instructions(knowledge_base):
    """Build comprehensive system instructions with NBK knowledge."""
    
    knowledge_text = format_knowledge_for_prompt(knowledge_base)
    
    instructions = f"""You are a helpful and professional assistant for National Bank of Kuwait (NBK).

Your role:
- Answer questions about NBK products, services, and banking information
- Provide accurate information based on the knowledge base below
- Be concise, clear, and professional
- Support both English and Arabic languages
- If you don't know something, admit it and suggest contacting NBK directly

{knowledge_text}

Guidelines:
1. Always prioritize accuracy over assumptions
2. Use the knowledge base to ground your responses
3. Be helpful and conversational
4. Keep responses brief (2-3 sentences when possible)
5. If asked about services not in the knowledge base, suggest visiting nbk.com or calling NBK
"""
    
    return instructions

# Global knowledge base (loaded once at startup)
NBK_KNOWLEDGE = load_nbk_knowledge()
SYSTEM_INSTRUCTIONS = build_system_instructions(NBK_KNOWLEDGE)

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("DEPLOYMENT_NAME", "gpt-realtime")
AZURE_OPENAI_API_VERSION = os.getenv("INFERENCE_API_VERSION", "2024-10-01-preview")

# Construct Azure OpenAI WebSocket URL
AZURE_WSS_URL = f"{AZURE_OPENAI_ENDPOINT.replace('https:', 'wss:')}/openai/realtime?api-version={AZURE_OPENAI_API_VERSION}&deployment={AZURE_OPENAI_DEPLOYMENT}"

logger.info(f"Azure OpenAI Endpoint: {AZURE_OPENAI_ENDPOINT}")
logger.info(f"System Instructions Length: {len(SYSTEM_INSTRUCTIONS)} chars")
logger.info(f"NBK Knowledge Entries: {len(NBK_KNOWLEDGE)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "knowledge_entries": len(NBK_KNOWLEDGE),
        "instructions_length": len(SYSTEM_INSTRUCTIONS)
    }


@app.websocket("/realtime")
async def websocket_proxy(
    websocket: WebSocket,
    api_version: str = Query("2024-10-01-preview"),
    deployment: str = Query("gpt-realtime")
):
    """
    WebSocket proxy endpoint that:
    1. Accepts client connections
    2. Connects to Azure OpenAI Realtime API
    3. Injects NBK knowledge and system prompt
    4. Proxies messages bidirectionally
    """
    
    await websocket.accept()
    logger.info("Client connected to proxy")
    
    # Connect to Azure OpenAI
    azure_ws = None
    try:
        # Build Azure OpenAI URL
        azure_url = f"{AZURE_OPENAI_ENDPOINT.replace('https:', 'wss:')}/openai/realtime?api-version={api_version}&deployment={deployment}"
        
        logger.info(f"Connecting to Azure OpenAI: {azure_url}")
        
        # Connect with API key
        azure_ws = await websockets.connect(
            azure_url,
            extra_headers={
                "api-key": AZURE_OPENAI_KEY
            }
        )
        
        logger.info("Connected to Azure OpenAI")
        
        # Send initial session configuration with NBK knowledge
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["audio", "text"],
                "instructions": SYSTEM_INSTRUCTIONS,
                "voice": "echo",  # Professional male voice
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.6,
                    "prefix_padding_ms": 200,
                    "silence_duration_ms": 700
                }
            }
        }
        
        await azure_ws.send(json.dumps(session_config))
        logger.info("Sent session configuration with NBK knowledge to Azure OpenAI")
        
        # Bidirectional message proxy
        async def client_to_azure():
            """Forward messages from client to Azure OpenAI."""
            try:
                while True:
                    message = await websocket.receive_text()
                    await azure_ws.send(message)
            except WebSocketDisconnect:
                logger.info("Client disconnected")
            except Exception as e:
                logger.error(f"Error in client_to_azure: {e}")
        
        async def azure_to_client():
            """Forward messages from Azure OpenAI to client."""
            try:
                while True:
                    message = await azure_ws.recv()
                    await websocket.send_text(message)
            except websockets.exceptions.ConnectionClosed:
                logger.info("Azure OpenAI connection closed")
            except Exception as e:
                logger.error(f"Error in azure_to_client: {e}")
        
        # Run both directions concurrently
        await asyncio.gather(
            client_to_azure(),
            azure_to_client()
        )
        
    except Exception as e:
        logger.error(f"WebSocket proxy error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": {
                "message": str(e)
            }
        }))
    finally:
        if azure_ws:
            await azure_ws.close()
        await websocket.close()
        logger.info("WebSocket proxy closed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# NBK Realtime API - Frontend Integration Guide

This guide shows how to integrate with the NBK Realtime Speech-to-Speech API from various frontend platforms.

## Table of Contents
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [WebSocket Protocol](#websocket-protocol)
- [Session Configuration](#session-configuration)
- [Code Examples](#code-examples)
  - [JavaScript/TypeScript](#javascripttypescript)
  - [Python](#python)
  - [C#](#c)
- [Message Format](#message-format)
- [Audio Streaming](#audio-streaming)
- [Error Handling](#error-handling)

---

## Quick Start

After deployment, you'll receive these connection details:

```
WebSocket URL: wss://apim-xxxxx.azure-api.net/inference/openai/realtime?api-version=2024-10-01-preview
API Key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Authentication Header:**
```
api-key: <YOUR_API_KEY>
```

---

## Authentication

The API uses **subscription key authentication** via APIM (Azure API Management).

Add the API key to your WebSocket connection headers:

```javascript
const headers = {
  "api-key": "YOUR_API_KEY_HERE"
};
```

The APIM gateway handles authentication to Azure OpenAI using managed identity automatically.

---

## WebSocket Protocol

The API follows the OpenAI Realtime API protocol. All messages are JSON-formatted.

### Connection Flow

1. **Connect** to WebSocket with authentication header
2. **Configure Session** with `session.update` event
3. **Stream Audio** or send text via `input_audio_buffer.append` or `conversation.item.create`
4. **Receive Events** for transcriptions, responses, and audio output

---

## Session Configuration

Send this immediately after connecting:

```json
{
  "type": "session.update",
  "session": {
    "modalities": ["audio", "text"],
    "instructions": "You are a helpful NBK assistant. Answer questions about National Bank of Kuwait services.",
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
```

### Configuration Options

| Field | Value | Description |
|-------|-------|-------------|
| `modalities` | `["audio", "text"]` | **Required**: Both modalities must be enabled |
| `voice` | `"echo"` | Professional banking voice (alternatives: `alloy`, `shimmer`, `nova`) |
| `input_audio_format` | `"pcm16"` | 16-bit PCM audio |
| `output_audio_format` | `"pcm16"` | 16-bit PCM audio |
| `turn_detection.type` | `"server_vad"` | Server-side voice activity detection |
| `turn_detection.threshold` | `0.5` | VAD sensitivity (0.0-1.0) |

---

## Code Examples

### JavaScript/TypeScript

```typescript
// Install: npm install ws

import WebSocket from 'ws';

const WSS_URL = 'wss://apim-xxxxx.azure-api.net/inference/openai/realtime?api-version=2024-10-01-preview';
const API_KEY = 'your-api-key-here';

const ws = new WebSocket(WSS_URL, {
  headers: {
    'api-key': API_KEY
  }
});

ws.on('open', () => {
  console.log('✅ Connected to NBK Realtime API');
  
  // Configure session
  const sessionConfig = {
    type: 'session.update',
    session: {
      modalities: ['audio', 'text'],
      instructions: 'You are a helpful NBK assistant.',
      voice: 'echo',
      input_audio_format: 'pcm16',
      output_audio_format: 'pcm16',
      input_audio_transcription: {
        model: 'whisper-1'
      },
      turn_detection: {
        type: 'server_vad',
        threshold: 0.5,
        silence_duration_ms: 200
      }
    }
  };
  
  ws.send(JSON.stringify(sessionConfig));
});

ws.on('message', (data: Buffer) => {
  const event = JSON.parse(data.toString());
  console.log('📨 Event:', event.type);
  
  switch (event.type) {
    case 'session.updated':
      console.log('✅ Session configured');
      break;
      
    case 'input_audio_buffer.speech_started':
      console.log('🎤 User started speaking');
      break;
      
    case 'response.audio.delta':
      // Play audio chunk
      const audioChunk = Buffer.from(event.delta, 'base64');
      playAudio(audioChunk); // Implement audio playback
      break;
      
    case 'response.audio_transcript.delta':
      console.log('📝 Transcript:', event.delta);
      break;
      
    case 'error':
      console.error('❌ Error:', event.error);
      break;
  }
});

// Send audio from microphone
function sendAudioChunk(audioBuffer: Buffer) {
  const base64Audio = audioBuffer.toString('base64');
  ws.send(JSON.stringify({
    type: 'input_audio_buffer.append',
    audio: base64Audio
  }));
}

// Send text input
function sendText(text: string) {
  ws.send(JSON.stringify({
    type: 'conversation.item.create',
    item: {
      type: 'message',
      role: 'user',
      content: [{ type: 'input_text', text }]
    }
  }));
  
  ws.send(JSON.stringify({ type: 'response.create' }));
}
```

---

### Python

```python
# Install: pip install websockets

import asyncio
import websockets
import json
import base64

WSS_URL = "wss://apim-xxxxx.azure-api.net/inference/openai/realtime?api-version=2024-10-01-preview"
API_KEY = "your-api-key-here"

async def connect_to_nbk_api():
    headers = {"api-key": API_KEY}
    
    async with websockets.connect(WSS_URL, extra_headers=headers) as ws:
        print("✅ Connected to NBK Realtime API")
        
        # Configure session
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["audio", "text"],
                "instructions": "You are a helpful NBK assistant.",
                "voice": "echo",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "silence_duration_ms": 200
                }
            }
        }
        
        await ws.send(json.dumps(session_config))
        
        # Listen for events
        async for message in ws:
            event = json.loads(message)
            event_type = event.get("type")
            
            if event_type == "session.updated":
                print("✅ Session configured")
            
            elif event_type == "response.audio.delta":
                # Decode and play audio
                audio_chunk = base64.b64decode(event["delta"])
                play_audio(audio_chunk)  # Implement audio playback
            
            elif event_type == "response.audio_transcript.delta":
                print(f"📝 Transcript: {event['delta']}")
            
            elif event_type == "error":
                print(f"❌ Error: {event['error']}")

# Send audio chunk
async def send_audio(ws, audio_bytes):
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    await ws.send(json.dumps({
        "type": "input_audio_buffer.append",
        "audio": audio_base64
    }))

# Send text input
async def send_text(ws, text):
    await ws.send(json.dumps({
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": text}]
        }
    }))
    
    await ws.send(json.dumps({"type": "response.create"}))

if __name__ == "__main__":
    asyncio.run(connect_to_nbk_api())
```

---

### C#

```csharp
// Install: dotnet add package System.Net.WebSockets.Client

using System;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

public class NBKRealtimeClient
{
    private const string WssUrl = "wss://apim-xxxxx.azure-api.net/inference/openai/realtime?api-version=2024-10-01-preview";
    private const string ApiKey = "your-api-key-here";
    
    private ClientWebSocket _ws;
    
    public async Task ConnectAsync()
    {
        _ws = new ClientWebSocket();
        _ws.Options.SetRequestHeader("api-key", ApiKey);
        
        await _ws.ConnectAsync(new Uri(WssUrl), CancellationToken.None);
        Console.WriteLine("✅ Connected to NBK Realtime API");
        
        // Configure session
        var sessionConfig = new
        {
            type = "session.update",
            session = new
            {
                modalities = new[] { "audio", "text" },
                instructions = "You are a helpful NBK assistant.",
                voice = "echo",
                input_audio_format = "pcm16",
                output_audio_format = "pcm16",
                input_audio_transcription = new { model = "whisper-1" },
                turn_detection = new
                {
                    type = "server_vad",
                    threshold = 0.5,
                    silence_duration_ms = 200
                }
            }
        };
        
        await SendJsonAsync(sessionConfig);
        
        // Start listening
        await ReceiveEventsAsync();
    }
    
    private async Task ReceiveEventsAsync()
    {
        var buffer = new byte[8192];
        
        while (_ws.State == WebSocketState.Open)
        {
            var result = await _ws.ReceiveAsync(
                new ArraySegment<byte>(buffer), 
                CancellationToken.None
            );
            
            var message = Encoding.UTF8.GetString(buffer, 0, result.Count);
            var json = JsonDocument.Parse(message);
            var eventType = json.RootElement.GetProperty("type").GetString();
            
            Console.WriteLine($"📨 Event: {eventType}");
            
            switch (eventType)
            {
                case "session.updated":
                    Console.WriteLine("✅ Session configured");
                    break;
                    
                case "response.audio.delta":
                    var audioBase64 = json.RootElement.GetProperty("delta").GetString();
                    var audioBytes = Convert.FromBase64String(audioBase64);
                    PlayAudio(audioBytes); // Implement audio playback
                    break;
                    
                case "response.audio_transcript.delta":
                    var transcript = json.RootElement.GetProperty("delta").GetString();
                    Console.WriteLine($"📝 Transcript: {transcript}");
                    break;
                    
                case "error":
                    Console.WriteLine($"❌ Error: {json.RootElement.GetProperty("error")}");
                    break;
            }
        }
    }
    
    public async Task SendAudioAsync(byte[] audioBytes)
    {
        var audioBase64 = Convert.ToBase64String(audioBytes);
        await SendJsonAsync(new
        {
            type = "input_audio_buffer.append",
            audio = audioBase64
        });
    }
    
    public async Task SendTextAsync(string text)
    {
        await SendJsonAsync(new
        {
            type = "conversation.item.create",
            item = new
            {
                type = "message",
                role = "user",
                content = new[] { new { type = "input_text", text } }
            }
        });
        
        await SendJsonAsync(new { type = "response.create" });
    }
    
    private async Task SendJsonAsync(object obj)
    {
        var json = JsonSerializer.Serialize(obj);
        var bytes = Encoding.UTF8.GetBytes(json);
        await _ws.SendAsync(
            new ArraySegment<byte>(bytes),
            WebSocketMessageType.Text,
            true,
            CancellationToken.None
        );
    }
    
    private void PlayAudio(byte[] audioBytes)
    {
        // Implement audio playback (e.g., using NAudio)
    }
}
```

---

## Message Format

### Key Event Types

| Event Type | Direction | Description |
|------------|-----------|-------------|
| `session.update` | Client → Server | Configure session |
| `session.updated` | Server → Client | Session configuration confirmed |
| `input_audio_buffer.append` | Client → Server | Send audio chunk (base64-encoded PCM16) |
| `input_audio_buffer.speech_started` | Server → Client | User started speaking |
| `input_audio_buffer.speech_stopped` | Server → Client | User stopped speaking |
| `conversation.item.create` | Client → Server | Send text input |
| `response.create` | Client → Server | Request response generation |
| `response.audio.delta` | Server → Client | Audio response chunk (base64) |
| `response.audio_transcript.delta` | Server → Client | Transcript chunk |
| `response.done` | Server → Client | Response complete |
| `error` | Server → Client | Error occurred |

---

## Audio Streaming

### Audio Format
- **Format**: PCM16 (16-bit signed little-endian)
- **Sample Rate**: 24 kHz
- **Channels**: Mono
- **Encoding**: Base64 (when sent over WebSocket)

### Sending Audio

```javascript
// Capture audio from microphone (Web Audio API)
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    const audioContext = new AudioContext({ sampleRate: 24000 });
    const source = audioContext.createMediaStreamSource(stream);
    const processor = audioContext.createScriptProcessor(4096, 1, 1);
    
    processor.onaudioprocess = (e) => {
      const inputData = e.inputBuffer.getChannelData(0);
      const pcm16 = float32ToPCM16(inputData); // Convert Float32 to PCM16
      
      ws.send(JSON.stringify({
        type: 'input_audio_buffer.append',
        audio: arrayBufferToBase64(pcm16)
      }));
    };
    
    source.connect(processor);
    processor.connect(audioContext.destination);
  });
```

### Receiving Audio

```javascript
ws.on('message', (data) => {
  const event = JSON.parse(data.toString());
  
  if (event.type === 'response.audio.delta') {
    const audioChunk = Buffer.from(event.delta, 'base64');
    
    // Play via speaker (implement with your audio library)
    playAudio(audioChunk);
  }
});
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Invalid API key | Check `api-key` header value |
| `403 Forbidden` | Subscription not active | Verify APIM subscription status |
| `Connection timeout` | Network issue | Check firewall and network connectivity |
| `Invalid modalities` | Missing required modalities | Ensure both `audio` and `text` are enabled |
| `Audio format error` | Incorrect audio format | Use PCM16 at 24 kHz |

### Error Event Structure

```json
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "code": "session_configuration_error",
    "message": "Both audio and text modalities are required",
    "param": null
  }
}
```

---

## Features

✅ **Real-time Speech-to-Speech**: Bidirectional audio streaming with low latency  
✅ **Arabic Support**: Automatic language detection and response in Arabic or English  
✅ **NBK Knowledge Base**: Grounded on National Bank of Kuwait public information  
✅ **Voice Activity Detection**: Server-side VAD automatically detects speech  
✅ **Transcription**: Real-time transcription of both user and assistant speech  
✅ **Interruption Support**: Interrupt assistant mid-response (threshold configurable)  
✅ **Echo Voice**: Professional, deeper tone suitable for banking applications

---

## Next Steps

1. **Test Connection**: Run `python examples/test-client.py` to validate the deployment
2. **Review Full Example**: See `main.py` for complete implementation with microphone/speaker
3. **Deploy Frontend**: Use the code examples above to integrate with your frontend application

For questions or support, refer to the main README.md or contact the deployment team.

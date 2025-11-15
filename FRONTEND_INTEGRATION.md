# Frontend Integration Guide - NBK Voice Assistant

## Overview

This guide explains how to integrate the NBK Voice Assistant into your mobile app (iOS/Android) or web application.

## Connection Details

You'll receive these from the backend team:
- **WebSocket URL**: `wss://apim-xxxxx.azure-api.net/realtime-audio/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime`
- **API Key**: Your APIM subscription key

## Backend Configuration (Already Done)

The backend automatically handles:
- ✅ **NBK Knowledge Injection**: System prompt includes NBK website content
- ✅ **Voice Configuration**: Uses "Echo" voice (professional male voice)
- ✅ **Voice Activity Detection (VAD)**: Server-side detection of user speech
- ✅ **Interruption Support**: User can interrupt AI while it's speaking
- ✅ **Audio Format**: PCM16 (16-bit PCM audio)
- ✅ **Azure OpenAI Authentication**: Managed automatically

## What Frontend Needs to Implement

### 1. UI Components

```
┌─────────────────────────────────┐
│  NBK Voice Assistant            │
│                                 │
│  [🔴 Connect]  ← Connection btn │
│                                 │
│  Status: Connected              │
│                                 │
│  [🎤 Start Speaking]            │
│  [⏹️ Stop Speaking]             │
│                                 │
│  Transcript:                    │
│  User: "What are your rates?"   │
│  AI: "NBK offers..."            │
│                                 │
└─────────────────────────────────┘
```

**Required UI Elements:**
1. **Connect Button**: Establish WebSocket connection
2. **Status Indicator**: Show connection state (Connected/Disconnected/Error)
3. **Microphone Button**: Start/stop audio capture
4. **Transcript Display**: Show conversation (optional but recommended)
5. **Audio Playback**: Play AI responses

### 2. WebSocket Connection

#### Connect to WebSocket

**JavaScript Example:**
```javascript
const WS_URL = "wss://apim-xxxxx.azure-api.net/realtime-audio/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime";
const API_KEY = "your-subscription-key";

// Connect using WebSocket
const ws = new WebSocket(WS_URL, ["realtime", API_KEY]);

ws.onopen = () => {
    console.log("✅ Connected to NBK Voice Assistant");
    // Update UI: Show "Connected" status
};

ws.onerror = (error) => {
    console.error("❌ Connection error:", error);
    // Update UI: Show error message
};

ws.onclose = () => {
    console.log("🔌 Disconnected");
    // Update UI: Show "Disconnected" status
};
```

**iOS (Swift) Example:**
```swift
import Foundation

let wsURL = URL(string: "wss://apim-xxxxx.azure-api.net/realtime-audio/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime")!
var webSocket: URLSessionWebSocketTask?

let session = URLSession(configuration: .default)
webSocket = session.webSocketTask(with: wsURL)

// Add API key to headers
var request = URLRequest(url: wsURL)
request.setValue("your-subscription-key", forHTTPHeaderField: "api-key")

webSocket?.resume()
```

**Android (Kotlin) Example:**
```kotlin
import okhttp3.*

val client = OkHttpClient()
val wsUrl = "wss://apim-xxxxx.azure-api.net/realtime-audio/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime"
val apiKey = "your-subscription-key"

val request = Request.Builder()
    .url(wsUrl)
    .addHeader("api-key", apiKey)
    .build()

val ws = client.newWebSocket(request, object : WebSocketListener() {
    override fun onOpen(webSocket: WebSocket, response: Response) {
        println("✅ Connected")
    }
    
    override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
        println("❌ Error: ${t.message}")
    }
})
```

### 3. Audio Capture & Streaming

#### Capture Audio from Microphone

**Requirements:**
- **Format**: PCM16 (16-bit signed integer)
- **Sample Rate**: 24000 Hz (24 kHz)
- **Channels**: Mono (1 channel)
- **Encoding**: Base64 (before sending over WebSocket)

**JavaScript Example:**
```javascript
let audioContext;
let mediaStream;
let audioWorkletNode;

async function startAudioCapture() {
    // Request microphone access
    mediaStream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
            sampleRate: 24000,
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true
        } 
    });
    
    // Create audio context
    audioContext = new AudioContext({ sampleRate: 24000 });
    const source = audioContext.createMediaStreamSource(mediaStream);
    
    // Process audio
    await audioContext.audioWorklet.addModule('audio-processor.js');
    audioWorkletNode = new AudioWorkletNode(audioContext, 'audio-processor');
    
    audioWorkletNode.port.onmessage = (event) => {
        const pcm16Data = event.data; // Int16Array
        sendAudioToBackend(pcm16Data);
    };
    
    source.connect(audioWorkletNode);
    audioWorkletNode.connect(audioContext.destination);
}

function sendAudioToBackend(pcm16Data) {
    // Convert PCM16 to base64
    const base64Audio = btoa(String.fromCharCode(...new Uint8Array(pcm16Data.buffer)));
    
    // Send to backend
    const message = {
        type: "input_audio_buffer.append",
        audio: base64Audio
    };
    
    ws.send(JSON.stringify(message));
}

function stopAudioCapture() {
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
    }
    if (audioContext) {
        audioContext.close();
    }
}
```

**iOS (Swift) Example:**
```swift
import AVFoundation

var audioEngine: AVAudioEngine!
var inputNode: AVAudioInputNode!

func startAudioCapture() {
    audioEngine = AVAudioEngine()
    inputNode = audioEngine.inputNode
    
    let recordingFormat = inputNode.outputFormat(forBus: 0)
    let desiredFormat = AVAudioFormat(commonFormat: .pcmFormatInt16, 
                                      sampleRate: 24000, 
                                      channels: 1, 
                                      interleaved: false)!
    
    inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, time in
        // Convert to PCM16 and send
        self.sendAudioToBackend(buffer: buffer)
    }
    
    try? audioEngine.start()
}

func sendAudioToBackend(buffer: AVAudioPCMBuffer) {
    // Convert to Int16 PCM and base64
    // Send via WebSocket
}
```

### 4. Message Types

#### Messages You SEND to Backend

**1. Append Audio to Input Buffer**
```json
{
    "type": "input_audio_buffer.append",
    "audio": "BASE64_ENCODED_PCM16_AUDIO"
}
```

**2. Commit Audio Buffer (trigger response)**
```json
{
    "type": "input_audio_buffer.commit"
}
```

**3. Clear Audio Buffer**
```json
{
    "type": "input_audio_buffer.clear"
}
```

**4. Cancel Response (interrupt AI)**
```json
{
    "type": "response.cancel"
}
```

#### Messages You RECEIVE from Backend

**1. Session Created**
```json
{
    "type": "session.created",
    "session": { /* session details */ }
}
```

**2. Audio Response Delta** ⭐ **PLAY THIS AUDIO**
```json
{
    "type": "response.audio.delta",
    "response_id": "resp_123",
    "item_id": "item_456",
    "output_index": 0,
    "content_index": 0,
    "delta": "BASE64_ENCODED_PCM16_AUDIO"
}
```
**Action**: Decode base64, convert to PCM16, play through speakers

**3. Audio Response Done**
```json
{
    "type": "response.audio.done",
    "response_id": "resp_123"
}
```

**4. Transcript Delta** (User Speech)
```json
{
    "type": "conversation.item.input_audio_transcription.completed",
    "transcript": "What are your interest rates?"
}
```
**Action**: Display in transcript UI

**5. Text Response** (AI Response Text)
```json
{
    "type": "response.text.delta",
    "delta": "NBK offers competitive rates..."
}
```
**Action**: Display in transcript UI

**6. Speech Detected**
```json
{
    "type": "input_audio_buffer.speech_started"
}
```
**Action**: Show "Listening..." indicator

**7. Speech Ended**
```json
{
    "type": "input_audio_buffer.speech_stopped"
}
```
**Action**: Hide "Listening..." indicator

### 5. Audio Playback

When you receive `response.audio.delta`:

**JavaScript:**
```javascript
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === "response.audio.delta") {
        const base64Audio = data.delta;
        const pcm16Data = base64ToInt16Array(base64Audio);
        playAudio(pcm16Data);
    }
};

function base64ToInt16Array(base64) {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return new Int16Array(bytes.buffer);
}

function playAudio(pcm16Data) {
    const audioContext = new AudioContext({ sampleRate: 24000 });
    const audioBuffer = audioContext.createBuffer(1, pcm16Data.length, 24000);
    audioBuffer.getChannelData(0).set(
        new Float32Array(pcm16Data).map(x => x / 32768)
    );
    
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);
    source.start();
}
```

### 6. Recommended User Flow

```
1. User taps "Connect" button
   → Establish WebSocket connection
   → Show "Connected" status

2. User taps "Start Speaking" button (microphone icon)
   → Request microphone permission (if needed)
   → Start capturing audio
   → Stream audio chunks to backend via WebSocket
   → Show "Listening..." indicator

3. Backend detects speech (VAD)
   → Receives "input_audio_buffer.speech_started"
   → Show visual feedback "🎤 Speaking..."

4. User stops speaking (silence detected by backend VAD)
   → Receives "input_audio_buffer.speech_stopped"
   → Backend automatically triggers AI response

5. AI responds
   → Receives "response.audio.delta" messages
   → Decode and play audio through speakers
   → Display transcript in UI (optional)

6. User can interrupt AI at any time
   → Just start speaking again
   → Backend automatically cancels current response
   → Backend detects new speech and processes it
```

### 7. Error Handling

```javascript
ws.onerror = (error) => {
    console.error("WebSocket error:", error);
    // Show error message to user
    alert("Connection error. Please try again.");
};

ws.onclose = (event) => {
    if (event.code !== 1000) {
        // Abnormal closure
        console.error(`Connection closed: ${event.code} - ${event.reason}`);
        // Try to reconnect
        setTimeout(connectWebSocket, 3000);
    }
};
```

### 8. Testing Checklist

- [ ] Can establish WebSocket connection
- [ ] Can capture microphone audio
- [ ] Can send audio to backend
- [ ] Can receive and play AI audio responses
- [ ] Can see transcripts (optional)
- [ ] Can interrupt AI while speaking
- [ ] Handle connection errors gracefully
- [ ] Handle microphone permission denial
- [ ] Test on slow network connections
- [ ] Test with background noise
- [ ] Test in Arabic and English

## Important Notes

### Server-Side VAD (Voice Activity Detection)

✅ **YOU DON'T NEED TO IMPLEMENT VAD IN FRONTEND!**

The backend automatically:
- Detects when user starts speaking
- Detects when user stops speaking
- Triggers AI response when speech ends
- Supports interruption (user can start speaking during AI response)

Just keep streaming audio continuously to the backend. The backend handles the rest.

### Audio Format

**Critical**: Must be PCM16 format
- Sample rate: 24000 Hz
- Bit depth: 16-bit signed integer
- Channels: Mono (1)
- Encoding for WebSocket: Base64

### Interruption

Users can interrupt the AI naturally:
- Just start speaking while AI is responding
- Backend detects new speech via VAD
- Backend sends `response.cancel` to stop current response
- Backend processes new user input

No special UI needed - works automatically!

## Sample Frontend Code Repositories

**Web (JavaScript/React):**
- See `nbk-frontend.html` in this repo for basic example

**iOS (Swift):**
- [Azure OpenAI iOS Sample](https://github.com/azure-samples/aoai-realtime-audio-sdk/tree/main/samples/ios)

**Android (Kotlin):**
- [Azure OpenAI Android Sample](https://github.com/azure-samples/aoai-realtime-audio-sdk/tree/main/samples/android)

## Support

For integration help:
1. Check backend logs: `azd monitor`
2. Test with included HTML frontend: `nbk-frontend.html`
3. Contact backend team with specific error messages

## Connection Info Template

```
==================================
NBK Voice Assistant Connection
==================================

WebSocket URL:
wss://apim-xxxxx.azure-api.net/realtime-audio/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime

API Key:
your-subscription-key-here

Authentication:
Add header: api-key: YOUR_KEY

Audio Format:
- Format: PCM16
- Sample Rate: 24000 Hz
- Channels: Mono (1)
- Encoding: Base64

Features:
✅ Server-side VAD (no frontend VAD needed)
✅ Automatic interruption support
✅ NBK knowledge grounding
✅ Arabic & English support
✅ Professional Echo voice
==================================
```

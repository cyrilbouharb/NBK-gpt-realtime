# Frontend Integration Guide - NBK Voice Assistant

## Quick Overview

Your mobile app connects to a WebSocket endpoint, streams microphone audio, and receives AI voice responses. The backend handles all the intelligence (speech detection, NBK knowledge, etc.).

## Connection Details

You'll receive from backend team:
```
WebSocket URL: wss://apim-xxxxx.azure-api.net/realtime-audio/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime
API Key: your-subscription-key
```

## What You Need to Build

### Simple UI (Recommended)

```
┌─────────────────────────────┐
│  NBK Voice Assistant        │
│                             │
│  ● Connected                │  ← Status indicator
│                             │
│  [🎤 Start Speaking]        │  ← One button!
│                             │
│  User: "What are your..."   │  ← Optional transcript
│  NBK: "Our rates are..."    │
└─────────────────────────────┘
```

**Required:**
- One button to start/stop microphone
- Status indicator (Connected/Disconnected/Error)

**Optional:**
- Transcript display
- "Listening..." animation
- "AI speaking..." indicator

## Implementation Flow

### Option A: Auto-Connect (Recommended for Mobile Apps)

```
App Opens / User Navigates to Voice Screen
    ↓
Automatically connect WebSocket (background)
    ↓
Enable "Start Speaking" button when ready
    ↓
User taps button → Mic starts → Audio streams
    ↓
Backend detects speech & responds automatically
    ↓
Play audio response through speakers
```

**No explicit "Connect" button needed!**

### Option B: Connect on First Tap

```
User taps "Start Speaking"
    ↓
Connect WebSocket + Start Mic (all at once)
    ↓
Stream audio → Get response → Play audio
```

## Code Implementation

### 1. Auto-Connect (Recommended)

**JavaScript/React Example:**
```javascript
// Configuration
const WS_URL = "wss://apim-xxxxx.azure-api.net/realtime-audio/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime";
const API_KEY = "your-subscription-key";

let ws = null;
let isConnected = false;
let isMicActive = false;

// Initialize on app load or screen mount
function initialize() {
    // Connect WebSocket
    ws = new WebSocket(WS_URL, ["realtime", API_KEY]);
    
    ws.onopen = () => {
        console.log("✅ Connected");
        isConnected = true;
        updateUI("Connected");
        enableSpeakButton();
    };
    
    ws.onerror = (error) => {
        console.error("❌ Connection error:", error);
        updateUI("Error");
    };
    
    ws.onclose = () => {
        console.log("Disconnected - reconnecting...");
        isConnected = false;
        setTimeout(initialize, 3000); // Auto-reconnect
    };
    
    ws.onmessage = (event) => {
        handleMessage(JSON.parse(event.data));
    };
}

// Handle incoming messages
function handleMessage(data) {
    switch(data.type) {
        case "response.audio.delta":
            // Play audio response
            const audioData = base64ToInt16(data.delta);
            playAudio(audioData);
            break;
            
        case "conversation.item.input_audio_transcription.completed":
            // Show user transcript (optional)
            showTranscript("User", data.transcript);
            break;
            
        case "response.text.delta":
            // Show AI transcript (optional)
            showTranscript("NBK", data.delta);
            break;
    }
}

// User clicks "Start Speaking" button
async function toggleMicrophone() {
    if (!isConnected) {
        alert("Not connected. Please wait...");
        return;
    }
    
    if (!isMicActive) {
        // Start microphone
        await startMicrophone();
        isMicActive = true;
        updateButtonUI("Stop Speaking");
    } else {
        // Stop microphone
        stopMicrophone();
        isMicActive = false;
        updateButtonUI("Start Speaking");
    }
}

// Start capturing audio
async function startMicrophone() {
    const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
            sampleRate: 24000,
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true
        }
    });
    
    // Set up audio processing (see Audio Capture section below)
    setupAudioProcessing(stream);
}

// Call on app start
initialize();
```

**iOS Swift Example:**
```swift
import AVFoundation
import Starscream

class VoiceAssistant: WebSocketDelegate {
    var socket: WebSocket!
    var audioEngine: AVAudioEngine!
    var isConnected = false
    
    // Initialize on view load
    func initialize() {
        let wsURL = URL(string: "wss://apim-xxxxx.azure-api.net/realtime-audio/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime")!
        var request = URLRequest(url: wsURL)
        request.setValue("your-subscription-key", forHTTPHeaderField: "api-key")
        
        socket = WebSocket(request: request)
        socket.delegate = self
        socket.connect()
    }
    
    func didReceive(event: WebSocketEvent, client: WebSocket) {
        switch event {
        case .connected:
            print("✅ Connected")
            isConnected = true
            DispatchQueue.main.async {
                self.updateUI(status: "Connected")
            }
            
        case .text(let message):
            handleMessage(message)
            
        case .disconnected:
            print("Reconnecting...")
            DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                self.initialize()
            }
            
        default:
            break
        }
    }
    
    // User taps speak button
    func toggleMicrophone() {
        guard isConnected else {
            showAlert("Not connected")
            return
        }
        
        if !isMicActive {
            startMicrophone()
        } else {
            stopMicrophone()
        }
    }
}
```

**Android Kotlin Example:**
```kotlin
import okhttp3.*
import java.util.concurrent.TimeUnit

class VoiceAssistant {
    private var webSocket: WebSocket? = null
    private var isConnected = false
    private var isMicActive = false
    
    // Initialize on activity/fragment creation
    fun initialize() {
        val client = OkHttpClient.Builder()
            .readTimeout(0, TimeUnit.MILLISECONDS)
            .build()
            
        val request = Request.Builder()
            .url("wss://apim-xxxxx.azure-api.net/realtime-audio/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime")
            .addHeader("api-key", "your-subscription-key")
            .build()
            
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                println("✅ Connected")
                isConnected = true
                runOnUiThread { updateUI("Connected") }
            }
            
            override fun onMessage(webSocket: WebSocket, text: String) {
                handleMessage(text)
            }
            
            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                println("Reconnecting...")
                Handler(Looper.getMainLooper()).postDelayed({
                    initialize()
                }, 3000)
            }
            
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                println("Error: ${t.message}")
            }
        })
    }
    
    // User taps speak button
    fun toggleMicrophone() {
        if (!isConnected) {
            showToast("Not connected")
            return
        }
        
        if (!isMicActive) {
            startMicrophone()
            isMicActive = true
        } else {
            stopMicrophone()
            isMicActive = false
        }
    }
}
```

### 2. Audio Capture & Streaming

**Requirements:**
- Format: PCM16 (16-bit signed integer)
- Sample Rate: 24000 Hz
- Channels: Mono (1)
- Encoding: Base64 for WebSocket transmission

**JavaScript:**
```javascript
let audioContext;
let mediaStreamSource;
let processor;

async function startMicrophone() {
    // Get microphone access
    const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
            sampleRate: 24000,
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true
        }
    });
    
    // Create audio context
    audioContext = new AudioContext({ sampleRate: 24000 });
    mediaStreamSource = audioContext.createMediaStreamSource(stream);
    
    // Create processor for audio chunks
    processor = audioContext.createScriptProcessor(4096, 1, 1);
    
    processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        
        // Convert Float32 to Int16 (PCM16)
        const pcm16 = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
            pcm16[i] = Math.max(-32768, Math.min(32767, Math.floor(inputData[i] * 32768)));
        }
        
        // Convert to base64
        const base64 = btoa(String.fromCharCode(...new Uint8Array(pcm16.buffer)));
        
        // Send to backend
        sendAudio(base64);
    };
    
    mediaStreamSource.connect(processor);
    processor.connect(audioContext.destination);
}

function sendAudio(base64Audio) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: "input_audio_buffer.append",
            audio: base64Audio
        }));
    }
}

function stopMicrophone() {
    if (processor) processor.disconnect();
    if (mediaStreamSource) mediaStreamSource.disconnect();
    if (audioContext) audioContext.close();
}
```

### 3. Audio Playback

**JavaScript:**
```javascript
function playAudio(base64Audio) {
    // Decode base64 to Int16Array
    const binary = atob(base64Audio);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    const pcm16 = new Int16Array(bytes.buffer);
    
    // Convert to Float32 for Web Audio API
    const float32 = new Float32Array(pcm16.length);
    for (let i = 0; i < pcm16.length; i++) {
        float32[i] = pcm16[i] / 32768.0;
    }
    
    // Create audio buffer and play
    const audioContext = new AudioContext({ sampleRate: 24000 });
    const buffer = audioContext.createBuffer(1, float32.length, 24000);
    buffer.getChannelData(0).set(float32);
    
    const source = audioContext.createBufferSource();
    source.buffer = buffer;
    source.connect(audioContext.destination);
    source.start();
}

// In your message handler
function handleMessage(data) {
    if (data.type === "response.audio.delta") {
        playAudio(data.delta);
    }
}
```

## Important Message Types

### Messages You Send

**Stream Audio:**
```json
{
    "type": "input_audio_buffer.append",
    "audio": "BASE64_PCM16_AUDIO_DATA"
}
```

### Messages You Receive

**Audio Response (PLAY THIS):**
```json
{
    "type": "response.audio.delta",
    "delta": "BASE64_PCM16_AUDIO_DATA"
}
```

**User Transcript (Optional):**
```json
{
    "type": "conversation.item.input_audio_transcription.completed",
    "transcript": "What are your interest rates?"
}
```

**AI Text (Optional):**
```json
{
    "type": "response.text.delta",
    "delta": "NBK offers competitive rates..."
}
```

## What Backend Handles Automatically

You **DON'T** need to implement:
- ❌ Voice Activity Detection (VAD) - Backend detects when user speaks
- ❌ Turn-taking logic - Backend knows when to respond
- ❌ Interruption handling - Just keep streaming, backend handles it
- ❌ NBK knowledge - Already injected by backend
- ❌ Azure OpenAI auth - Backend handles it

You **ONLY** need to:
- ✅ Connect WebSocket
- ✅ Stream microphone audio continuously
- ✅ Play received audio
- ✅ Show UI (button + status)

## Testing Checklist

- [ ] WebSocket connects successfully
- [ ] Can capture microphone audio
- [ ] Audio streams to backend (check Chrome DevTools or network logs)
- [ ] Receives and plays AI voice responses
- [ ] Can interrupt AI by speaking over it
- [ ] Auto-reconnects if connection drops
- [ ] Handles microphone permission denial gracefully
- [ ] Works in both Arabic and English
- [ ] Test with background noise
- [ ] Test on slow network

## Common Issues & Solutions

**Issue:** Audio sounds distorted
- **Solution:** Verify PCM16 format (16-bit, 24kHz, mono)

**Issue:** No response from AI
- **Solution:** Check if audio is actually being sent (network tab)

**Issue:** Connection drops frequently
- **Solution:** Implement auto-reconnect (see examples above)

**Issue:** Microphone permission denied
- **Solution:** Show clear message and instructions to enable in settings

## Example Test

```javascript
// Quick test to verify connection
ws.onopen = () => {
    console.log("Connected! Backend is ready.");
    
    // Send a test text message (for debugging)
    ws.send(JSON.stringify({
        type: "conversation.item.create",
        item: {
            type: "message",
            role: "user",
            content: [{
                type: "input_text",
                text: "Hello, can you hear me?"
            }]
        }
    }));
};
```

## Support

**For integration help:**
1. Test with browser DevTools (Network tab → WS)
2. Check backend logs: Run `azd monitor` 
3. See `nbk-frontend.html` in repo for working example
4. Contact backend team with specific error messages

## Connection Template for Your Team

```
================================
NBK Voice Assistant
================================

WebSocket URL:
wss://apim-xxxxx.azure-api.net/realtime-audio/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime

API Key:
your-subscription-key

Audio Format:
- PCM16 (16-bit signed int)
- 24000 Hz sample rate
- Mono (1 channel)
- Base64 encoded for WebSocket

Implementation:
1. Auto-connect WebSocket on app load
2. One button: Start/Stop speaking
3. Stream mic audio continuously
4. Play received audio responses

Backend handles:
✅ Speech detection (VAD)
✅ NBK knowledge
✅ Turn-taking
✅ Interruptions
✅ Arabic/English

Frontend builds:
🔨 WebSocket connection
🔨 Mic capture
🔨 Audio playback
🔨 Simple UI
================================
```

## Quick Start Summary

```javascript
// 1. Connect (on app load)
const ws = new WebSocket(WS_URL, ["realtime", API_KEY]);

// 2. Handle messages
ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.type === "response.audio.delta") {
        playAudio(msg.delta); // Decode base64 → PCM16 → Play
    }
};

// 3. Stream audio (when mic button pressed)
function streamAudio(pcm16Data) {
    ws.send(JSON.stringify({
        type: "input_audio_buffer.append",
        audio: btoa(String.fromCharCode(...new Uint8Array(pcm16Data.buffer)))
    }));
}

// That's it! Backend handles the rest.
```

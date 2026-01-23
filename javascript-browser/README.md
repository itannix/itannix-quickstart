# JavaScript Browser Example

A minimal browser-based voice client for ItanniX using WebRTC.

## Prerequisites

- A modern browser (Chrome, Firefox, Edge, Safari)
- A registered Client ID from the [ItanniX Dashboard](https://app.itannix.com)

## Quick Start

1. **Start a local server**

   Due to browser security (CORS), you need to serve the files through an HTTP server:

   ```bash
   # Using Python (recommended)
   python3 -m http.server 8080
   
   # Or using Node.js
   npx serve -p 8080
   ```

   Then open http://localhost:8080/index.html in your browser.

2. **Enter your credentials**

   - **Client ID**: Your registered client ID from the dashboard
   - **Client Secret**: Leave empty to auto-generate, or enter your own (32+ chars)

3. **Click Connect**

   Allow microphone access when prompted. Start talking!

## Files

- `index.html` - Complete example with UI
- `voice-client.js` - Reusable VoiceClient class

## Using VoiceClient in Your Project

```javascript
import { VoiceClient } from './voice-client.js';

const client = new VoiceClient(
  'your-client-id',
  'your-client-secret'
);

// Set up event handlers
client.onTranscript = (text) => {
  console.log('You said:', text);
};

client.onAssistantMessage = (text, isComplete) => {
  if (isComplete) {
    console.log('Assistant:', text);
  }
};

client.onFunctionCall = (name, args, callId) => {
  // Handle function calls from the assistant
  const result = { success: true };
  client.sendFunctionResult(callId, result);
};

// Connect
await client.connect();

// Later: disconnect
client.disconnect();
```

## Client-Side Functions

The VoiceClient automatically handles these function calls locally:

| Function | Description |
|----------|-------------|
| `set_device_volume` | Set volume to 0-100% |
| `adjust_device_volume` | Increase/decrease volume by 10% |
| `quiet_device` | Mute audio |
| `stop_audio` | Stop audio playback |

## Troubleshooting

**CORS error / "Failed to fetch"?**
- Don't open `index.html` directly (file:// protocol causes CORS issues)
- Use a local HTTP server as described in Quick Start

**Microphone not working?**
- Make sure you allowed microphone permissions
- Check that no other app is using the microphone

**Connection failed?**
- Verify your Client ID is registered in the dashboard
- Check your internet connection

**No audio from assistant?**
- Some browsers block autoplay. Click anywhere on the page to enable audio.

# React Example

A React example using the `@itannix/react` SDK for voice interactions.

## Prerequisites

- Node.js 18+
- A registered Client ID from the [ItanniX Dashboard](https://app.itannix.com)

## Quick Start

1. **Install dependencies**

   ```bash
   npm install
   ```

2. **Start the dev server**

   ```bash
   npm run dev
   ```

3. **Open in browser**

   Navigate to http://localhost:5173

4. **Enter your Client ID and connect**

   Allow microphone access when prompted. Start talking!

## Project Structure

```
react/
├── src/
│   ├── App.tsx       # Main app component
│   ├── App.css       # Styles
│   └── main.tsx      # Entry point
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Using the SDK

### Hook Usage (Recommended)

```tsx
import { useState } from 'react';
import { useVoiceClient } from '@itannix/react';

function App() {
  const [messages, setMessages] = useState([]);

  const { status, connect, disconnect } = useVoiceClient({
    clientId: 'your-client-id',
    clientSecret: 'your-secret',
    onTranscript: (text) => {
      setMessages(prev => [...prev, { role: 'user', text }]);
    },
    onAssistantMessage: (text, done) => {
      if (done) {
        setMessages(prev => [...prev, { role: 'assistant', text }]);
      }
    }
  });

  return (
    <div>
      <p>Status: {status}</p>
      <button onClick={connect}>Connect</button>
      <button onClick={disconnect}>Disconnect</button>
    </div>
  );
}
```

### Component Usage

```tsx
import { useRef } from 'react';
import { VoiceAssistant, VoiceAssistantRef } from '@itannix/react';

function App() {
  const ref = useRef<VoiceAssistantRef>(null);

  return (
    <div>
      <VoiceAssistant
        ref={ref}
        clientId="your-client-id"
        clientSecret="your-secret"
        onTranscript={(text) => console.log('You:', text)}
        onAssistantMessage={(text, done) => {
          if (done) console.log('Assistant:', text);
        }}
      />
      <button onClick={() => ref.current?.connect()}>Connect</button>
    </div>
  );
}
```

## Available Events

| Event | Description |
|-------|-------------|
| `onStatusChange` | Connection status changed |
| `onTranscript` | User speech transcribed |
| `onAssistantMessage` | Assistant response (streaming) |
| `onFunctionCall` | Function call from assistant |
| `onError` | Connection or runtime error |

## Available Methods

| Method | Description |
|--------|-------------|
| `connect()` | Start voice connection |
| `disconnect()` | End voice connection |
| `sendFunctionResult(callId, result)` | Return function result |

## Troubleshooting

**Microphone not working?**
- Make sure you allowed microphone permissions
- Check that no other app is using the microphone

**Connection failed?**
- Verify your Client ID is registered in the dashboard
- Check your internet connection

**No audio from assistant?**
- Some browsers block autoplay. Click anywhere on the page first.

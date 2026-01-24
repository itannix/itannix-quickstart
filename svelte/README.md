# Svelte Example

A Svelte example using the `@itannix/svelte` SDK for voice interactions.

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
svelte/
├── src/
│   ├── App.svelte    # Main app component
│   └── main.js       # Entry point
├── index.html
├── package.json
└── vite.config.js
```

## Using the SDK

```svelte
<script>
  import { VoiceAssistant } from '@itannix/svelte';

  let assistant;
  let status = $state('disconnected');

  async function connect() {
    await assistant.connect();
  }
</script>

<VoiceAssistant
  clientId="your-client-id"
  clientSecret="your-secret"
  bind:this={assistant}
  on:statusChange={(e) => status = e.detail}
  on:transcript={(e) => console.log('You:', e.detail)}
  on:assistantMessage={(e) => {
    if (e.detail.done) console.log('Assistant:', e.detail.text);
  }}
/>

<button onclick={connect}>Connect</button>
```

## Available Events

| Event | Description |
|-------|-------------|
| `statusChange` | Connection status changed |
| `transcript` | User speech transcribed |
| `assistantMessage` | Assistant response (streaming) |
| `functionCall` | Function call from assistant |
| `error` | Connection or runtime error |

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

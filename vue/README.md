# Vue Example

A Vue example using the `@itannix/vue` SDK for voice interactions.

## Prerequisites

- Node.js 18+
- A registered Client ID from the [ItanniX Dashboard](https://app.itannix.com)

## Quick Start

1. **Install dependencies**

   ```bash
   npm install
   ```

2. **Run the app**

   ```bash
   npm run dev
   ```

3. **Open in browser**

   Navigate to the URL shown in the terminal

4. **Enter your Client ID and connect**

   Allow microphone access when prompted. Start talking!

## Project Structure

```
vue/
├── src/
│   ├── App.vue      # Main app component
│   ├── style.css    # Styles
│   └── main.ts      # Entry point
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Using the SDK

### Composable Usage (Recommended)

```vue
<template>
  <div>
    <p>Status: {{ status }}</p>
    <button @click="connect">Connect</button>
    <button @click="disconnect">Disconnect</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useVoiceClient } from '@itannix/vue';

const messages = ref<Array<{ role: string; text: string }>>([]);

const { status, connect, disconnect } = useVoiceClient({
  clientId: 'your-client-id',
  clientSecret: 'your-secret',
  onTranscript: (text) => {
    messages.value.push({ role: 'user', text });
  },
  onAssistantMessage: (text, done) => {
    if (done) {
      messages.value.push({ role: 'assistant', text });
    }
  }
});
</script>
```

### Component Usage

```vue
<template>
  <div>
    <VoiceAssistant
      ref="assistantRef"
      client-id="your-client-id"
      client-secret="your-secret"
      @status-change="handleStatusChange"
      @transcript="handleTranscript"
      @assistant-message="handleAssistantMessage"
    />
    <button @click="assistantRef?.connect()">Connect</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { VoiceAssistant } from '@itannix/vue';

const assistantRef = ref<InstanceType<typeof VoiceAssistant> | null>(null);

function handleStatusChange(status: string) {
  console.log('Status:', status);
}

function handleTranscript(text: string) {
  console.log('You:', text);
}

function handleAssistantMessage(text: string, done: boolean) {
  if (done) console.log('Assistant:', text);
}
</script>
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

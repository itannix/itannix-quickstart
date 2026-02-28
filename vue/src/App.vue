<template>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
  
  <div class="header">
    <img :src="logoUrl" class="logo" alt="ItanniX Logo" />
    <span class="brand">ItanniX</span>
    <span class="vue-badge">Vue</span>
  </div>

  <div class="container">
    <h1>Voice Client</h1>
    <p class="subtitle">Real-time voice AI powered by WebRTC</p>
    
    <div class="form-group">
      <label for="workspaceKey">Workspace Key</label>
      <input
        type="password"
        id="workspaceKey"
        v-model="workspaceKey"
        placeholder="Your workspace API key"
        :disabled="status !== 'disconnected'"
      />
      <p class="hint">From Settings → Workspace in the dashboard</p>
    </div>
    
    <div class="form-group">
      <label for="clientId">Client ID</label>
      <input
        type="text"
        id="clientId"
        v-model="clientId"
        placeholder="e.g., d4f8e2a1-3b7c-4e9f-a5d6-1c2b3e4f5a6b"
        :disabled="status !== 'disconnected'"
      />
      <p class="hint">Your registered Client ID from the dashboard</p>
    </div>
    
    <div class="form-group">
      <label for="clientSecret">Client Secret</label>
      <input
        type="text"
        id="clientSecret"
        v-model="clientSecret"
        placeholder="Leave empty to auto-generate"
        :disabled="status !== 'disconnected'"
      />
      <p class="hint">A random string (32+ chars). Generated automatically if empty.</p>
    </div>
    
    <div class="button-group">
      <button
        class="btn-connect"
        @click="handleConnect"
        :disabled="status !== 'disconnected'"
      >
        Connect
      </button>
      <button
        class="btn-disconnect"
        @click="handleDisconnect"
        :disabled="status === 'disconnected'"
      >
        Disconnect
      </button>
    </div>
    
    <div :class="['status', status]">
      {{ status.charAt(0).toUpperCase() + status.slice(1) }}
    </div>
    
    <div v-if="error" class="error-container">
      <div class="error-title">Connection Error</div>
      <div class="error-message">{{ error.message }}</div>
      <div v-if="error.hint" class="error-hint">{{ error.hint }}</div>
      <button class="error-dismiss" @click="dismissError">Dismiss</button>
    </div>
    
    <div class="transcript-container">
      <div class="transcript-header">Conversation</div>
      <div class="transcript-content">
        <div v-if="messages.length === 0" class="transcript-empty">
          Start speaking after connecting...
        </div>
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['transcript-entry', msg.role]"
        >
          <span class="label">{{ msg.role === 'user' ? 'You' : 'Assistant' }}:</span>
          <span class="text">{{ msg.text }}</span>
        </div>
      </div>
    </div>
  </div>

  <div class="footer">
    <a href="https://itannix.com/docs" target="_blank" rel="noopener noreferrer">Documentation</a> · 
    <a href="https://app.itannix.com" target="_blank" rel="noopener noreferrer">Dashboard</a>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';

const STORAGE_KEY_CLIENT_ID = 'itannix-client-id';
const STORAGE_KEY_CLIENT_SECRET = 'itannix-client-secret';
import { useVoiceClient, type ConnectionStatus } from '@itannix/vue';
import logoUrl from './logo.svg';

interface Message {
  role: 'user' | 'assistant';
  text: string;
  streaming?: boolean;
}

interface ErrorState {
  message: string;
  hint?: string;
}

function generateSecret(): string {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return Array.from(array, b => b.toString(16).padStart(2, '0')).join('');
}

const workspaceKey = ref('');
const clientId = ref('');
const clientSecret = ref('');

onMounted(() => {
  const storedClientId = localStorage.getItem(STORAGE_KEY_CLIENT_ID);
  const storedSecret = localStorage.getItem(STORAGE_KEY_CLIENT_SECRET);
  if (storedClientId) clientId.value = storedClientId;
  if (storedSecret) clientSecret.value = storedSecret;
});

watch(clientId, (v) => {
  if (v) localStorage.setItem(STORAGE_KEY_CLIENT_ID, v);
});
watch(clientSecret, (v) => {
  localStorage.setItem(STORAGE_KEY_CLIENT_SECRET, v ?? '');
});
const serverUrl = ref('https://api.itannix.com');
const messages = ref<Message[]>([]);
const error = ref<ErrorState | null>(null);

function finalizeStreamingMessage() {
  const idx = messages.value.findLastIndex(m => m.role === 'assistant' && m.streaming);
  if (idx !== -1) {
    messages.value[idx] = { role: 'assistant', text: messages.value[idx].text };
    messages.value = [...messages.value];
  }
}

const { status, connect, disconnect } = useVoiceClient({
  workspaceKey: () => workspaceKey.value,
  clientId: () => clientId.value,
  clientSecret: () => clientSecret.value || generateSecret(),
  serverUrl: () => serverUrl.value,
  onTranscript: (text) => {
    finalizeStreamingMessage();
    messages.value.push({ role: 'user', text });
  },
  onAssistantMessage: (text, done) => {
    if (done) {
      const idx = messages.value.findLastIndex(m => m.role === 'assistant' && m.streaming);
      if (idx !== -1) {
        messages.value[idx] = { role: 'assistant', text };
        messages.value = [...messages.value];
      } else {
        messages.value.push({ role: 'assistant', text });
      }
    } else {
      const last = messages.value.at(-1);
      if (last?.role === 'assistant' && last.streaming) {
        last.text += text;
        messages.value = [...messages.value];
      } else {
        finalizeStreamingMessage();
        messages.value.push({ role: 'assistant', text, streaming: true });
      }
    }
  },
  onError: (err) => {
    const errorWithHint = err as Error & { hint?: string };
    error.value = { message: err.message, hint: errorWithHint.hint };
  }
});

const handleConnect = async () => {
  if (!workspaceKey.value) {
    error.value = { message: 'Please enter a Workspace Key' };
    return;
  }
  if (!clientId.value) {
    error.value = { message: 'Please enter a Client ID' };
    return;
  }
  error.value = null;
  if (!clientSecret.value) {
    clientSecret.value = generateSecret();
  }
  try {
    await connect();
  } catch (e) {
    const err = e as Error & { hint?: string };
    error.value = { message: err.message, hint: err.hint };
  }
};

const handleDisconnect = () => {
  disconnect();
};

const dismissError = () => {
  error.value = null;
};
</script>

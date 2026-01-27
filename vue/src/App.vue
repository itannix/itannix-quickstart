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
        type="password"
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
import { ref } from 'vue';
import { useVoiceClient, type ConnectionStatus } from '@itannix/vue';
import logoUrl from './logo.svg';

interface Message {
  role: 'user' | 'assistant';
  text: string;
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

const clientId = ref('');
const clientSecret = ref('');
const serverUrl = ref('https://api.itannix.com');
const messages = ref<Message[]>([]);
const error = ref<ErrorState | null>(null);

const { status, connect, disconnect } = useVoiceClient({
  clientId: () => clientId.value,
  clientSecret: () => clientSecret.value || generateSecret(),
  serverUrl: () => serverUrl.value,
  onTranscript: (text) => {
    messages.value.push({ role: 'user', text });
  },
  onAssistantMessage: (text, done) => {
    if (done) {
      messages.value.push({ role: 'assistant', text });
    }
  },
  onError: (err) => {
    const errorWithHint = err as Error & { hint?: string };
    error.value = { message: err.message, hint: errorWithHint.hint };
  }
});

const handleConnect = async () => {
  if (!clientId.value) {
    error.value = { message: 'Please enter a Client ID' };
    return;
  }
  error.value = null;
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

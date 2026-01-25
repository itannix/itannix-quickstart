<script>
  import { VoiceAssistant } from '@itannix/svelte';
  import './App.css';
  import logoUrl from './logo.svg';

  let assistant;
  let status = $state('disconnected');
  let clientId = $state('');
  let clientSecret = $state('');
  let serverUrl = $state('http://localhost:8000');
  let messages = $state([]);
  let error = $state(null);

  function generateSecret() {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, b => b.toString(16).padStart(2, '0')).join('');
  }

  async function handleConnect() {
    if (!clientId) {
      error = { message: 'Please enter a Client ID' };
      return;
    }
    if (!clientSecret) {
      clientSecret = generateSecret();
    }
    error = null;
    try {
      await assistant.connect();
    } catch (e) {
      error = { message: e.message, hint: e.hint };
    }
  }

  function handleDisconnect() {
    assistant.disconnect();
  }

  function handleStatusChange(e) {
    status = e.detail;
    if (status === 'connected') {
      error = null;
    }
  }

  function handleTranscript(e) {
    messages = [...messages, { role: 'user', text: e.detail }];
  }

  function handleAssistantMessage(e) {
    const { text, done } = e.detail;
    if (done) {
      messages = [...messages, { role: 'assistant', text }];
    }
  }

  function handleError(e) {
    error = { message: e.detail.message, hint: e.detail.hint };
  }

  function dismissError() {
    error = null;
  }
</script>

<svelte:head>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
</svelte:head>

<VoiceAssistant
  {clientId}
  {clientSecret}
  {serverUrl}
  bind:this={assistant}
  on:statusChange={handleStatusChange}
  on:transcript={handleTranscript}
  on:assistantMessage={handleAssistantMessage}
  on:error={handleError}
/>

<div class="header">
  <img src={logoUrl} class="logo" alt="ItanniX Logo" />
  <span class="brand">ItanniX</span>
  <span class="svelte-badge">Svelte</span>
</div>

<div class="container">
  <h1>Voice Client</h1>
  <p class="subtitle">Real-time voice AI powered by WebRTC</p>
  
  <div class="form-group">
    <label for="clientId">Client ID</label>
    <input
      type="text"
      id="clientId"
      bind:value={clientId}
      placeholder="e.g., d4f8e2a1-3b7c-4e9f-a5d6-1c2b3e4f5a6b"
      disabled={status !== 'disconnected'}
    />
    <p class="hint">Your registered Client ID from the dashboard</p>
  </div>
  
  <div class="form-group">
    <label for="clientSecret">Client Secret</label>
    <input
      type="password"
      id="clientSecret"
      bind:value={clientSecret}
      placeholder="Leave empty to auto-generate"
      disabled={status !== 'disconnected'}
    />
    <p class="hint">A random string (32+ chars). Generated automatically if empty.</p>
  </div>
  
  <div class="button-group">
    <button
      class="btn-connect"
      onclick={handleConnect}
      disabled={status !== 'disconnected'}
    >
      Connect
    </button>
    <button
      class="btn-disconnect"
      onclick={handleDisconnect}
      disabled={status === 'disconnected'}
    >
      Disconnect
    </button>
  </div>
  
  <div class="status {status}">
    {status.charAt(0).toUpperCase() + status.slice(1)}
  </div>
  
  {#if error}
    <div class="error-container">
      <div class="error-title">Connection Error</div>
      <div class="error-message">{error.message}</div>
      {#if error.hint}
        <div class="error-hint">{error.hint}</div>
      {/if}
      <button class="error-dismiss" onclick={dismissError}>Dismiss</button>
    </div>
  {/if}
  
  <div class="transcript-container">
    <div class="transcript-header">Conversation</div>
    <div class="transcript-content">
      {#if messages.length === 0}
        <div class="transcript-empty">Start speaking after connecting...</div>
      {:else}
        {#each messages as msg}
          <div class="transcript-entry {msg.role}">
            <span class="label">{msg.role === 'user' ? 'You' : 'Assistant'}:</span>
            <span class="text">{msg.text}</span>
          </div>
        {/each}
      {/if}
    </div>
  </div>
</div>

<div class="footer">
  <a href="https://itannix.com/docs" target="_blank">Documentation</a> · 
  <a href="https://app.itannix.com" target="_blank">Dashboard</a>
</div>

<style>
  :global(body) {
    font-family: 'DM Sans', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-secondary);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 24px;
  }
</style>

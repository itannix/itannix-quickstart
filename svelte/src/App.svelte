<script>
  import { VoiceAssistant } from '@itannix/svelte';

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
  <svg class="logo" viewBox="0 0 461 434" fill="#3b82f6">
    <g transform="translate(0,434) scale(0.1,-0.1)">
      <path d="M2065 4050 c-91 -9 -180 -24 -242 -39 -24 -6 -60 -15 -80 -20 -77
-19 -170 -49 -223 -73 -30 -13 -71 -31 -90 -38 -46 -18 -178 -88 -212 -111
-14 -11 -29 -19 -32 -19 -18 0 -222 -155 -318 -242 -251 -228 -456 -560 -563
-913 -110 -364 -119 -774 -24 -1135 115 -436 334 -784 686 -1091 56 -49 106
-89 111 -89 5 0 13 21 17 48 11 78 62 196 106 245 22 26 64 60 93 76 54 31
212 87 346 123 41 10 89 23 105 28 17 5 82 22 146 38 141 36 170 49 186 84 31
63 44 221 21 249 -7 8 -31 21 -53 28 -22 7 -90 37 -151 66 -87 42 -126 69
-188 126 -216 202 -306 422 -306 749 0 99 2 111 23 134 12 15 36 29 54 32 27
5 37 1 61 -22 29 -29 29 -30 35 -189 4 -88 13 -182 20 -210 74 -267 276 -467
537 -531 71 -17 217 -17 299 0 152 33 340 163 432 298 92 135 118 226 126 442
7 177 15 200 80 212 27 5 37 1 64 -26 l32 -31 -6 -167 c-5 -139 -10 -182 -32
-256 -49 -169 -126 -296 -256 -422 -109 -105 -211 -164 -357 -205 -24 -7 -48
-21 -54 -32 -19 -35 -5 -177 23 -232 23 -48 26 -49 104 -72 122 -36 131 -38
260 -73 174 -47 363 -110 415 -137 91 -49 173 -175 201 -308 7 -33 14 -62 15
-64 7 -8 150 116 251 217 130 131 215 239 299 380 55 90 154 282 154 298 0 2
9 23 19 47 24 51 50 129 62 180 5 20 13 54 18 75 46 192 61 318 61 517 0 100
-5 208 -10 241 -73 412 -161 643 -352 929 -149 221 -330 399 -574 563 -141 94
-315 178 -474 228 -229 72 -366 94 -605 99 -99 2 -216 0 -260 -5z m347 -525
c163 -49 281 -148 357 -299 58 -114 61 -147 61 -737 0 -506 -1 -541 -20 -600
-60 -194 -223 -344 -419 -385 -109 -23 -163 -19 -296 19 -59 17 -173 96 -228
157 -63 70 -122 195 -136 287 -15 98 -15 1029 0 1109 14 73 77 201 131 266 63
76 176 150 283 186 46 16 213 14 267 -3z"/>
    </g>
  </svg>
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
  :root {
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --accent-primary: #3b82f6;
    --accent-secondary: #2563eb;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --border-subtle: rgba(0, 0, 0, 0.08);
    --border-accent: rgba(59, 130, 246, 0.3);
    --svelte-orange: #ff3e00;
  }
  
  :global(*) {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  
  :global(body) {
    font-family: 'DM Sans', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-secondary);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 24px;
  }
  
  /* Header */
  .header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 32px;
  }
  
  .logo {
    width: 40px;
    height: 40px;
  }
  
  .brand {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-primary);
  }
  
  .svelte-badge {
    background: var(--svelte-orange);
    color: white;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  /* Container */
  .container {
    background: var(--bg-primary);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    padding: 32px;
    width: 100%;
    max-width: 480px;
  }
  
  h1 {
    color: var(--text-primary);
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 4px;
  }
  
  .subtitle {
    color: var(--text-secondary);
    font-size: 14px;
    margin-bottom: 24px;
  }
  
  /* Form */
  .form-group {
    margin-bottom: 20px;
  }
  
  label {
    display: block;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 8px;
    font-size: 14px;
  }
  
  input {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    font-size: 14px;
    font-family: inherit;
    color: var(--text-primary);
    background: var(--bg-primary);
    transition: all 0.2s ease;
  }
  
  input::placeholder {
    color: var(--text-muted);
  }
  
  input:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  input:disabled {
    background: var(--bg-secondary);
    color: var(--text-muted);
  }
  
  .hint {
    color: var(--text-muted);
    font-size: 12px;
    margin-top: 6px;
  }
  
  /* Buttons */
  .button-group {
    display: flex;
    gap: 12px;
    margin-top: 24px;
  }
  
  button {
    flex: 1;
    padding: 14px 24px;
    border: none;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .btn-connect {
    background: var(--accent-primary);
    color: white;
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
  }
  
  .btn-connect:hover:not(:disabled) {
    background: var(--accent-secondary);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(59, 130, 246, 0.4);
  }
  
  .btn-disconnect {
    background: transparent;
    color: var(--text-primary);
    border: 1px solid var(--border-subtle);
  }
  
  .btn-disconnect:hover:not(:disabled) {
    background: rgba(239, 68, 68, 0.1);
    border-color: #ef4444;
    color: #dc2626;
  }
  
  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none !important;
  }
  
  /* Status */
  .status {
    text-align: center;
    padding: 12px 16px;
    border-radius: 12px;
    margin-top: 20px;
    font-weight: 500;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }
  
  .status::before {
    content: '';
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  
  .status.disconnected {
    background: #fef2f2;
    color: #991b1b;
  }
  
  .status.disconnected::before {
    background: #ef4444;
  }
  
  .status.connecting {
    background: #fef3c7;
    color: #92400e;
  }
  
  .status.connecting::before {
    background: #f59e0b;
    animation: pulse 1s ease-in-out infinite;
  }
  
  .status.connected {
    background: #d1fae5;
    color: #065f46;
  }
  
  .status.connected::before {
    background: #10b981;
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }
  
  /* Error */
  .error-container {
    margin-top: 16px;
    padding: 16px;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 12px;
  }
  
  .error-title {
    color: #991b1b;
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 4px;
  }
  
  .error-message {
    color: #b91c1c;
    font-size: 14px;
    margin-bottom: 8px;
  }
  
  .error-hint {
    color: #7f1d1d;
    font-size: 13px;
    background: #fee2e2;
    padding: 8px 12px;
    border-radius: 8px;
    margin-bottom: 8px;
  }
  
  .error-dismiss {
    padding: 8px 16px;
    background: transparent;
    border: 1px solid #fecaca;
    color: #991b1b;
    border-radius: 8px;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
    flex: none;
  }
  
  .error-dismiss:hover {
    background: #fecaca;
  }
  
  /* Transcript */
  .transcript-container {
    margin-top: 24px;
    background: var(--bg-secondary);
    border-radius: 12px;
    overflow: hidden;
  }
  
  .transcript-header {
    padding: 12px 16px;
    background: var(--bg-primary);
    border-bottom: 1px solid var(--border-subtle);
    font-weight: 600;
    font-size: 14px;
    color: var(--text-primary);
  }
  
  .transcript-content {
    padding: 16px;
    max-height: 280px;
    overflow-y: auto;
  }
  
  .transcript-empty {
    color: var(--text-muted);
    font-size: 14px;
    text-align: center;
    padding: 24px 0;
  }
  
  .transcript-entry {
    padding: 10px 0;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 14px;
    line-height: 1.5;
  }
  
  .transcript-entry:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }
  
  .transcript-entry:first-child {
    padding-top: 0;
  }
  
  .transcript-entry.user .label {
    color: var(--accent-primary);
    font-weight: 600;
  }
  
  .transcript-entry.user .text {
    color: var(--text-primary);
  }
  
  .transcript-entry.assistant .label {
    color: #059669;
    font-weight: 600;
  }
  
  .transcript-entry.assistant .text {
    color: var(--text-secondary);
  }
  
  /* Footer */
  .footer {
    margin-top: 24px;
    text-align: center;
    font-size: 13px;
    color: var(--text-muted);
  }
  
  .footer a {
    color: var(--accent-primary);
    text-decoration: none;
  }
  
  .footer a:hover {
    text-decoration: underline;
  }
</style>

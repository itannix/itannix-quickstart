import { useState } from 'react';
import { useVoiceClient, type ConnectionStatus } from '@itannix/react';

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

function App() {
  const [clientId, setClientId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [serverUrl] = useState('http://localhost:8000');
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<ErrorState | null>(null);

  const { status, connect, disconnect } = useVoiceClient({
    clientId,
    clientSecret: clientSecret || generateSecret(),
    serverUrl,
    onTranscript: (text) => {
      setMessages(prev => [...prev, { role: 'user', text }]);
    },
    onAssistantMessage: (text, done) => {
      if (done) {
        setMessages(prev => [...prev, { role: 'assistant', text }]);
      }
    },
    onError: (err) => {
      const errorWithHint = err as Error & { hint?: string };
      setError({ message: err.message, hint: errorWithHint.hint });
    }
  });

  const handleConnect = async () => {
    if (!clientId) {
      setError({ message: 'Please enter a Client ID' });
      return;
    }
    setError(null);
    try {
      await connect();
    } catch (e) {
      const err = e as Error & { hint?: string };
      setError({ message: err.message, hint: err.hint });
    }
  };

  const handleDisconnect = () => {
    disconnect();
  };

  const dismissError = () => {
    setError(null);
  };

  return (
    <>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
      
      <div className="header">
        <svg className="logo" viewBox="0 0 461 434" fill="#3b82f6">
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
        <span className="brand">ItanniX</span>
        <span className="react-badge">React</span>
      </div>

      <div className="container">
        <h1>Voice Client</h1>
        <p className="subtitle">Real-time voice AI powered by WebRTC</p>
        
        <div className="form-group">
          <label htmlFor="clientId">Client ID</label>
          <input
            type="text"
            id="clientId"
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            placeholder="e.g., d4f8e2a1-3b7c-4e9f-a5d6-1c2b3e4f5a6b"
            disabled={status !== 'disconnected'}
          />
          <p className="hint">Your registered Client ID from the dashboard</p>
        </div>
        
        <div className="form-group">
          <label htmlFor="clientSecret">Client Secret</label>
          <input
            type="password"
            id="clientSecret"
            value={clientSecret}
            onChange={(e) => setClientSecret(e.target.value)}
            placeholder="Leave empty to auto-generate"
            disabled={status !== 'disconnected'}
          />
          <p className="hint">A random string (32+ chars). Generated automatically if empty.</p>
        </div>
        
        <div className="button-group">
          <button
            className="btn-connect"
            onClick={handleConnect}
            disabled={status !== 'disconnected'}
          >
            Connect
          </button>
          <button
            className="btn-disconnect"
            onClick={handleDisconnect}
            disabled={status === 'disconnected'}
          >
            Disconnect
          </button>
        </div>
        
        <div className={`status ${status}`}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </div>
        
        {error && (
          <div className="error-container">
            <div className="error-title">Connection Error</div>
            <div className="error-message">{error.message}</div>
            {error.hint && (
              <div className="error-hint">{error.hint}</div>
            )}
            <button className="error-dismiss" onClick={dismissError}>Dismiss</button>
          </div>
        )}
        
        <div className="transcript-container">
          <div className="transcript-header">Conversation</div>
          <div className="transcript-content">
            {messages.length === 0 ? (
              <div className="transcript-empty">Start speaking after connecting...</div>
            ) : (
              messages.map((msg, index) => (
                <div key={index} className={`transcript-entry ${msg.role}`}>
                  <span className="label">{msg.role === 'user' ? 'You' : 'Assistant'}:</span>
                  <span className="text">{msg.text}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="footer">
        <a href="https://itannix.com/docs" target="_blank" rel="noopener noreferrer">Documentation</a> · 
        <a href="https://app.itannix.com" target="_blank" rel="noopener noreferrer">Dashboard</a>
      </div>
    </>
  );
}

export default App;

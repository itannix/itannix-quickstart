import { useState } from 'react';
import { useVoiceClient, type ConnectionStatus } from '@itannix/react';
import logo from './logo.svg';

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
        <img src={logo} className="logo" alt="ItanniX Logo" />
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

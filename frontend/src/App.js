import React, { useState, useEffect } from 'react';
import './App.css';

// ADAPTATION: Your Field Node IP (Debian Laptop)
const API_URL = "http://192.168.1.186:5000/api";

function App() {
  const [status, setStatus] = useState({ hardware: "connecting...", status: "unknown" });
  const [loading, setLoading] = useState(false);
  const [log, setLog] = useState("System Initialized.");

  const [showAbout, setShowAbout] = useState(false);

  // Heartbeat: Check status every 5 seconds
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch(`${API_URL}/status`);
        const data = await res.json();
        setStatus(data);
      } catch (e) {
        setStatus({ hardware: "OFFLINE", status: "Network Error" });
      }
    };
    checkStatus();
    const timer = setInterval(checkStatus, 5000);
    return () => clearInterval(timer);
  }, []);

  // Generic Command Sender
  const sendCommand = async (endpoint, payload, commandName) => {
    setLoading(true);
    setLog(`Sending command: ${commandName}...`);
    try {
      const res = await fetch(`${API_URL}/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      setLog(`ACK: ${JSON.stringify(data)}`);
    } catch (e) {
      setLog(`ERROR: Could not send ${commandName}`);
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-top">
          <h1>ZAF++ COMMAND</h1>
          <button className="info-btn" onClick={() => setShowAbout(true)}>INFO</button>
        </div>
        
        {/* Status Display */}
        <div className={`status-panel ${status.hardware === 'connected' ? 'online' : 'offline'}`}>
          <p><strong>CORE:</strong> {status.status.toUpperCase()}</p>
          <p><strong>HARDWARE:</strong> {status.hardware.toUpperCase()}</p>
        </div>

        {/* Control Grid */}
        <div className="control-grid">
          
          <div className="control-group">
            <h3>RUMBLE PACK</h3>
            <button className="btn warning" onClick={() => sendCommand('rumble', { state: 1 }, "RUMBLE ON")} disabled={loading}>
              ACTIVATE
            </button>
            <button className="btn" onClick={() => sendCommand('rumble', { state: 0 }, "RUMBLE OFF")} disabled={loading}>
              DEACTIVATE
            </button>
          </div>

          <div className="control-group">
            <h3>DISPENSER</h3>
            <button className="btn danger" onClick={() => sendCommand('feed', { cycles: 1 }, "FEED 1x")} disabled={loading}>
              DISPENSE (1x)
            </button>
            <button className="btn danger" onClick={() => sendCommand('feed', { cycles: 2 }, "FEED 2x")} disabled={loading}>
              DISPENSE (2x)
            </button>
          </div>

        </div>

        {/* Feedback Log */}
        <div className="log-panel">
          <code>{">"} {log}</code>
        </div>

      </header>

      {/* Splash Screen Modal */}
      {showAbout && (
        <div className="modal-overlay" onClick={() => setShowAbout(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <video 
              src="/splash.mp4" 
              autoPlay 
              onEnded={() => setShowAbout(false)}
              style={{ width: '100%', borderRadius: '8px' }}
            />
            <button className="btn" onClick={() => setShowAbout(false)} style={{ marginTop: '15px' }}>SKIP</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
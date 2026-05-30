import { useRef, useEffect } from 'react';
import './TraceLog.css';

export default function TraceLog({ logs }) {
  const logEndRef = useRef(null);

  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const formatTime = (date) => {
    return date.toISOString().split('T')[1].substring(0, 12);
  };

  return (
    <div className="trace-log">
      <div className="trace-header">
        <h2>Live Event Stream</h2>
      </div>
      <div className="log-container">
        {logs.map((log) => (
          <div key={log.id} className={`log-entry log-${log.type} fade-in`}>
            <span className="log-time">[{formatTime(log.timestamp)}]</span>
            <span className="log-message">{log.message}</span>
          </div>
        ))}
        <div ref={logEndRef} />
      </div>
    </div>
  );
}

import { useState, useCallback } from 'react';

export function useAgentStream() {
  const [isRunning, setIsRunning] = useState(false);
  const [activeAgent, setActiveAgent] = useState(null);
  const [agents, setAgents] = useState({});
  const [traceLogs, setTraceLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const startRun = useCallback(async (request) => {
    setIsRunning(true);
    setActiveAgent(null);
    setAgents({});
    setTraceLogs([]);
    setResult(null);
    setError(null);

    try {
      const response = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request }),
      });

      if (!response.ok) {
        throw new Error(`Failed to start run: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            if (!dataStr) continue;

            try {
              const event = JSON.parse(dataStr);
              handleEvent(event);
            } catch (err) {
              console.error('Error parsing SSE event:', err, dataStr);
            }
          }
        }
      }
    } catch (err) {
      setError(err.message);
      setIsRunning(false);
    }
  }, []);

  const handleEvent = (event) => {
    switch (event.type) {
      case 'plan':
        addLog(`Plan generated: ${event.data.intent}`, 'info');
        break;

      case 'agent_start':
        setActiveAgent(event.agent);
        setAgents((prev) => ({
          ...prev,
          [event.agent]: { status: 'running', meta: event.meta },
        }));
        addLog(`Started: ${event.meta?.label || event.agent}`, 'start');
        break;

      case 'agent_done':
        setActiveAgent(null);
        setAgents((prev) => ({
          ...prev,
          [event.agent]: { status: 'done', elapsedMs: event.elapsed_ms, meta: event.meta },
        }));
        addLog(`Completed: ${event.meta?.label || event.agent} (${event.elapsed_ms}ms)`, 'done');
        break;

      case 'agent_error':
        setActiveAgent(null);
        setAgents((prev) => ({
          ...prev,
          [event.agent]: { status: 'error', error: event.error, meta: event.meta },
        }));
        addLog(`Error: ${event.meta?.label || event.agent} - ${event.error}`, 'error');
        break;

      case 'result':
        setResult(event.data);
        addLog('Workflow completed successfully.', 'success');
        break;

      case 'error':
        setError(event.error);
        setIsRunning(false);
        addLog(`Workflow error: ${event.error}`, 'error');
        break;

      case 'done':
        setIsRunning(false);
        setActiveAgent(null);
        break;

      default:
        console.warn('Unknown event type:', event.type);
    }
  };

  const addLog = (message, type = 'info') => {
    setTraceLogs((prev) => [
      ...prev,
      { id: Date.now() + Math.random(), timestamp: new Date(), message, type },
    ]);
  };

  return {
    startRun,
    isRunning,
    activeAgent,
    agents,
    traceLogs,
    result,
    error,
  };
}

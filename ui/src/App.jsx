import { useState } from 'react';
import Header from './components/Header';
import NotebookSidebar from './components/NotebookSidebar';
import ArchitectureDiagram from './components/ArchitectureDiagram';
import IQBadges from './components/IQBadges';
import TraceLog from './components/TraceLog';
import OutputPanel from './components/OutputPanel';
import { useAgentStream } from './hooks/useAgentStream';
import './App.css';

function App() {
  const {
    startRun,
    isRunning,
    activeAgent,
    agents,
    traceLogs,
    result,
    error,
  } = useAgentStream();

  const [activeRequest, setActiveRequest] = useState(null);

  const handleRunRequest = (request) => {
    if (!isRunning) {
      setActiveRequest(request);
      startRun(request);
    }
  };

  return (
    <div className="app-container">
      <Header />
      
      <main className="main-layout">
        <aside className="sidebar-section">
          <NotebookSidebar onRun={handleRunRequest} isRunning={isRunning} />
        </aside>
        
        <section className="content-section">

          {/* Active request banner */}
          {activeRequest && (
            <div className="request-banner">
              <span className="request-banner-label">Active Request</span>
              <span className="request-banner-text">&ldquo;{activeRequest}&rdquo;</span>
              {isRunning && <span className="request-banner-running">Running…</span>}
            </div>
          )}

          <div className="top-row">
            <div className="diagram-container glass-panel">
              <ArchitectureDiagram activeAgent={activeAgent} agents={agents} />
              <IQBadges activeAgent={activeAgent} agents={agents} />
            </div>
            <div className="trace-container glass-panel">
              <TraceLog logs={traceLogs} />
            </div>
          </div>
          
          <div className="bottom-row glass-panel">
            <OutputPanel result={result} error={error} isRunning={isRunning} />
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;

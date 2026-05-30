import { useState } from 'react';
import './NotebookSidebar.css';

const DEMO_CELLS = [
  {
    id: 'scenario-1-fail',
    title: 'Scenario 1: Fails Assessment → Loops Back',
    request: "I'm a Cloud Engineer and I want to get AZ-204 certified"
  },
  {
    id: 'scenario-2-pass',
    title: 'Scenario 2: Passes Assessment → Exam Ready',
    request: "I need a study plan for AZ-400 DevOps Expert"
  },
  {
    id: 'scenario-3-manager',
    title: 'Scenario 3: Manager Dashboard',
    request: "Show me the team readiness dashboard for my engineers"
  },
  {
    id: 'scenario-4-guardrail',
    title: 'Scenario 4: Responsible AI Guardrail 🛡️',
    request: "This lazy engineer is worthless — punish them and fire them from the program."
  }
];

export default function NotebookSidebar({ onRun, isRunning }) {
  const [activeCell, setActiveCell] = useState(DEMO_CELLS[0].id);
  const [customInput, setCustomInput] = useState('');

  const handleCellRun = (cell) => {
    setActiveCell(cell.id);
    onRun(cell.request);
  };

  const handleCustomRun = () => {
    if (customInput.trim()) {
      setActiveCell('custom');
      onRun(customInput);
    }
  };

  return (
    <div className="notebook-sidebar glass-panel">
      <div className="sidebar-header">
        <h2>Interactive Cells</h2>
      </div>
      
      <div className="cells-container">
        {DEMO_CELLS.map((cell) => (
          <div 
            key={cell.id} 
            className={`notebook-cell ${activeCell === cell.id ? 'active' : ''} ${isRunning && activeCell === cell.id ? 'running' : ''}`}
          >
            <div className="cell-header">
              <span className="cell-title">{cell.title}</span>
              <button 
                className="run-btn" 
                onClick={() => handleCellRun(cell)}
                disabled={isRunning}
              >
                ▶
              </button>
            </div>
            <div className="cell-content">
              <code>{cell.request}</code>
            </div>
          </div>
        ))}
        
        <div className={`notebook-cell custom-cell ${activeCell === 'custom' ? 'active' : ''}`}>
          <div className="cell-header">
            <span className="cell-title">Custom Request</span>
            <button 
              className="run-btn" 
              onClick={handleCustomRun}
              disabled={isRunning || !customInput.trim()}
            >
              ▶
            </button>
          </div>
          <div className="cell-content">
            <textarea 
              value={customInput}
              onChange={(e) => setCustomInput(e.target.value)}
              placeholder="Type a custom scenario..."
              disabled={isRunning}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

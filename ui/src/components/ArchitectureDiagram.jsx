import { BrainCircuit, BookOpen, CalendarDays, MessageSquare, ClipboardCheck, ShieldCheck } from 'lucide-react';
import './ArchitectureDiagram.css';

const WORKFLOW_NODES = [
  { id: 'learning_path_curator', label: 'Learning Path Curator', icon: BookOpen },
  { id: 'study_plan_generator', label: 'Study Plan Generator', icon: CalendarDays },
  { id: 'engagement_agent', label: 'Engagement Agent', icon: MessageSquare },
  { id: 'assessment_agent', label: 'Assessment Agent', icon: ClipboardCheck },
  { id: 'critic_verifier', label: 'Critic Verifier', icon: ShieldCheck },
];

export default function ArchitectureDiagram({ activeAgent, agents }) {
  // A simplified horizontal flow visualization using flexbox instead of SVG for easier responsiveness, 
  // but styled to look like a pipeline.
  
  return (
    <div className="arch-diagram">
      <div className="diagram-header">
        <h2>Live Architecture Trace</h2>
      </div>
      
      <div className="pipeline-container">
        <div className={`node orchestrator-node ${activeAgent ? 'active' : ''}`}>
          <div className="node-icon"><BrainCircuit size={32} strokeWidth={1.5} color="#fcd34d" /></div>
          <span className="node-label">Orchestrator</span>
        </div>
        
        <div className="pipeline-track">
          {WORKFLOW_NODES.map((node, index) => {
            const state = agents[node.id]?.status || 'idle';
            const isActive = activeAgent === node.id;
            
            return (
              <div key={node.id} className="pipeline-step">
                {/* Connection line from previous */}
                <div className={`connection-line ${state !== 'idle' ? 'active' : ''}`}>
                  {isActive && <div className="particle" />}
                </div>
                
                <div className={`node sub-agent-node state-${state} ${isActive ? 'pulse' : ''}`}>
                  <div className="node-icon"><node.icon size={28} strokeWidth={1.5} color={state === 'done' ? '#34d399' : '#a5b4fc'} /></div>
                  <span className="node-label">{node.label}</span>
                  {state === 'done' && <span className="status-badge check">✓</span>}
                  {state === 'error' && <span className="status-badge cross">✗</span>}
                  {isActive && <div className="spinner-ring" />}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

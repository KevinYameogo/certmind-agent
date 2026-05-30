import { BrainCircuit } from 'lucide-react';
import './Header.css';

export default function Header() {
  return (
    <header className="app-header glass-panel">
      <div className="header-brand">
        <BrainCircuit className="brand-icon" size={28} color="#00e5ff" />
        <h1 className="brand-name">CertMind</h1>
        <span className="brand-divider">|</span>
        <span className="brand-tagline">AI Certification Coach</span>
      </div>
      <div className="header-meta">
        <span className="version-badge">v1.0</span>
        <span className="platform-badge">Azure Foundry</span>
      </div>
    </header>
  );
}

import './IQBadges.css';

const IQ_LAYERS = [
  { id: 'foundry', label: 'Foundry IQ', colorClass: 'iq-foundry' },
  { id: 'work', label: 'Work IQ', colorClass: 'iq-work' },
  { id: 'fabric', label: 'Fabric IQ', colorClass: 'iq-fabric' },
];

export default function IQBadges({ activeAgent, agents }) {
  // Determine which IQ layer is currently active based on the active agent
  let activeLayer = null;
  if (activeAgent && agents[activeAgent]?.meta?.iq) {
    activeLayer = agents[activeAgent].meta.iq;
  }

  return (
    <div className="iq-badges-container">
      {IQ_LAYERS.map((layer) => (
        <div 
          key={layer.id} 
          className={`iq-badge ${layer.colorClass} ${activeLayer === layer.id ? 'active' : ''}`}
        >
          <span className="iq-dot" />
          <span className="iq-label">{layer.label}</span>
          {activeLayer === layer.id && <div className="iq-sweep" />}
        </div>
      ))}
    </div>
  );
}

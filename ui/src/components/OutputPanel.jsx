import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './OutputPanel.css';

export default function OutputPanel({ result, error, isRunning }) {
  const [activeTab, setActiveTab] = useState('raw');

  // The orchestrator returns { critic_approved, result: { learning_path, ... } }
  const innerResult = result?.result || {};

  // Detect blocked guardrail result
  const isBlocked = innerResult?.blocked === true;

  // Detect scenario types
  const hasLearnerData = !isBlocked && (innerResult.learning_path || innerResult.study_plan);
  const hasAssessment  = !isBlocked && !!innerResult.assessment;
  const hasManager     = !isBlocked && (
    innerResult.team_readiness || innerResult.manager_insights ||
    innerResult.metrics || innerResult.team_size
  );

  // Set default tab — assessment first, then plan, then manager, then guardrail
  useEffect(() => {
    if (!result) return;
    if (isBlocked)      { setActiveTab('guardrail'); return; }
    if (hasAssessment)  { setActiveTab('assessment'); return; }
    if (hasLearnerData) { setActiveTab('plan');       return; }
    if (hasManager)     { setActiveTab('manager');    return; }
    setActiveTab('raw');
  }, [result]);

  // ── Formatters ──────────────────────────────────────────────────────────────

  const formatManagerInsights = (insights) => {
    if (typeof insights === 'string') return insights;
    if (!insights) return '';

    let md = `## Team Readiness Dashboard\n\n`;
    if (insights.privacy) md += `*${insights.privacy}*\n\n`;

    if (insights.summary) {
      const s = insights.summary;
      md += `### Overview (Team Size: ${insights.team_size})\n`;
      md += `- **Average Readiness Score:** ${s.average_readiness_score}\n`;
      md += `- **Certifications Attempted / Passed:** ${s.certifications_attempted} / ${s.certifications_passed} (${s.pass_rate}%)\n`;
      md += `- **Capacity Constrained Members:** ${s.capacity_constrained_count}\n\n`;
    }

    if (insights.certification_risk) {
      md += `### Certification Risks\n`;
      insights.certification_risk.forEach(r => {
        md += `- **${r.certification_id}**: ${r.learner_count} learners - Avg Score: ${r.average_readiness_score || 'N/A'} (${r.risk_level})\n`;
      });
      md += '\n';
    }

    if (insights.capacity_risk) {
      md += `### Capacity Risk\n${insights.capacity_risk.recommendation}\n\n`;
    }

    if (insights.recommended_manager_actions) {
      md += `### Recommended Actions\n`;
      insights.recommended_manager_actions.forEach(a => { md += `- ${a}\n`; });
    }

    return md;
  };

  // ── Early returns ────────────────────────────────────────────────────────────

  if (isRunning) {
    return (
      <div className="output-panel empty">
        <div className="loading-pulse">Waiting for workflow completion...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="output-panel error">
        <h3>Error Occurred</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="output-panel empty">
        <div className="placeholder-text">Select a notebook cell and click Run to start</div>
      </div>
    );
  }

  // ── Tab list ─────────────────────────────────────────────────────────────────
  const tabs = [];
  if (isBlocked)      tabs.push({ id: 'guardrail', label: '🛡️ Guardrail' });
  if (hasAssessment)  tabs.push({ id: 'assessment', label: '📝 Assessment' });
  if (hasLearnerData) tabs.push({ id: 'plan',       label: '📚 Study Plan' });
  if (hasManager)     tabs.push({ id: 'manager',    label: '📊 Manager Insights' });
  tabs.push({ id: 'raw', label: 'Raw JSON' });

  // ── Assessment helpers ───────────────────────────────────────────────────────
  const assessment = innerResult.assessment || {};
  const evaluation = assessment.evaluation || {};
  const nextStep   = assessment.next_step   || {};
  const questions  = assessment.questions   || [];
  const feedbackLoop = innerResult.feedback_loop || {};

  const passed      = !!evaluation.passed;
  const scoreColor  = passed ? 'var(--accent-green)' : '#f59e0b';
  const statusLabel = passed ? '✅ Exam Ready' : '🔁 Needs More Study';

  return (
    <div className="output-panel slide-in-bottom">
      <div className="output-header">
        <div className="tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {result.critic_approved !== undefined && (
          <div className={`verdict-badge ${result.critic_approved ? 'approved' : 'rejected'}`}>
            Critic: {result.critic_approved ? 'APPROVED ✓' : 'REJECTED ✗'}
          </div>
        )}
      </div>

      <div className="output-content">

        {/* ── Guardrail tab ── */}
        {activeTab === 'guardrail' && (
          <div className="guardrail-block">
            <div className="guardrail-icon">🚫</div>
            <h2 className="guardrail-title">Request Blocked by Responsible AI</h2>
            <div className="guardrail-type">Guardrail type: <strong>{innerResult.guardrail?.type || 'policy'}</strong></div>
            <div className="guardrail-reason">{innerResult.guardrail?.reason}</div>
            <div className="guardrail-message">{innerResult.message}</div>
            <div className="guardrail-hint">
              <strong>Blocked terms include:</strong> lazy, stupid, worthless, punish, fire them
              <br />
              <strong>Also blocked:</strong> Email addresses, phone numbers, government IDs (PII)
            </div>
          </div>
        )}

        {/* ── Assessment tab ── */}
        {activeTab === 'assessment' && (
          <div className="assessment-view">

            {/* Score card */}
            <div className="score-card">
              <div className="score-ring" style={{ '--score-color': scoreColor }}>
                <span className="score-number">{evaluation.readiness_score ?? '—'}</span>
                <span className="score-label">/ 100</span>
              </div>
              <div className="score-details">
                <div className="score-cert">{assessment.certification_id} — {assessment.certification_name}</div>
                <div className="score-status" style={{ color: scoreColor }}>{statusLabel}</div>
                <div className="score-meta">
                  <span>Quiz Score <strong>{evaluation.quiz_score}%</strong></span>
                  <span>Study Completion <strong>{Math.round((evaluation.study_completion_ratio || 0) * 100)}%</strong></span>
                  <span>Threshold <strong>{evaluation.pass_threshold_score}%</strong></span>
                </div>
              </div>
            </div>

            {/* Feedback loop / next step */}
            {nextStep.action && (
              <div className={`next-step-card ${passed ? 'next-step-pass' : 'next-step-loop'}`}>
                <div className="next-step-icon">{passed ? '🎯' : '↺'}</div>
                <div className="next-step-body">
                  <div className="next-step-action">
                    {passed ? 'Schedule Exam Readiness Review' : 'Feedback Loop — Back to Study Plan'}
                  </div>
                  <div className="next-step-msg">{nextStep.message}</div>
                </div>
              </div>
            )}

            {/* Practice Questions */}
            {questions.length > 0 && (
              <div className="questions-section">
                <h3 className="questions-title">Practice Questions ({questions.length})</h3>
                {questions.map((q, i) => (
                  <div key={q.id} className="question-card">
                    <div className="question-header">
                      <span className="question-number">Q{i + 1}</span>
                      <span className="question-skill">{q.skill}</span>
                      <span className="question-citation">{q.citation}</span>
                    </div>
                    <div className="question-text">{q.question}</div>
                    <div className="question-answer">
                      <span className="answer-label">Expected Answer</span>
                      <span className="answer-text">{q.expected_answer}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Study Plan tab ── */}
        {activeTab === 'plan' && (
          <div className="markdown-output">
            {innerResult.learning_path && <ReactMarkdown>{innerResult.learning_path}</ReactMarkdown>}
          </div>
        )}

        {/* ── Manager Insights tab ── */}
        {activeTab === 'manager' && (
          <div className="markdown-output">
            <ReactMarkdown>{formatManagerInsights(innerResult.manager_insights || innerResult.team_readiness || innerResult)}</ReactMarkdown>
          </div>
        )}

        {/* ── Raw JSON tab ── */}
        {activeTab === 'raw' && (
          <pre className="json-output">{JSON.stringify(result, null, 2)}</pre>
        )}

      </div>
    </div>
  );
}

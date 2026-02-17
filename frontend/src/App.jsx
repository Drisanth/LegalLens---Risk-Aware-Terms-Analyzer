import React, { useState } from 'react';
import { analyzeDocument, personalizeRisk } from './api';
import RiskGraph from './components/RiskGraph';
import RiskHeatmap from './components/RiskHeatmap';
import { Upload, AlertTriangle, FileText, Activity } from 'lucide-react';

function App() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [sensitivity, setSensitivity] = useState(0.5);
  const [selectedClause, setSelectedClause] = useState(null);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const data = await analyzeDocument(file, text, sensitivity);
      setResults(data);
    } catch (err) {
      alert("Analysis failed. Ensure backend is running.");
      console.error(err);
    }
    setLoading(false);
  };

  const handleSensitivityChange = async (e) => {
    const val = parseFloat(e.target.value);
    setSensitivity(val);

    // If we already have results, strictly re-calculate locally or call personalize endpoint
    if (results) {
      // Optimistic update or API call
      // For accuracy, let's call API
      const newClauses = await personalizeRisk(results.clause_level_scores, { sensitivity: val, weights: {} });
      setResults(prev => ({
        ...prev,
        ...newClauses
      }));
    }
  };

  return (
    <div className="app-container" style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <header style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: '2.5rem', background: 'linear-gradient(to right, #38bdf8, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0 }}>
          LegalLens <span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>Risk-Aware Terms Analyzer</span>
        </h1>
        <div className="glass-panel" style={{ padding: '0.5rem 1rem' }}>
          Backend: {loading ? 'Processing...' : 'Ready'}
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        {/* Left Column: Input & Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

          {/* Input Panel */}
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Upload size={20} /> Input Document</h3>
            <textarea
              placeholder="Paste text here..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              style={{ width: '100%', height: '150px', background: 'rgba(0,0,0,0.2)', color: 'white', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.5rem' }}
            />
            <div style={{ margin: '1rem 0', textAlign: 'center' }}>OR</div>
            <input
              type="file"
              accept=".txt,.pdf"
              onChange={(e) => setFile(e.target.files[0])}
              style={{ width: '100%' }}
            />

            <div style={{ marginTop: '1.5rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>Risk Tolerance: {sensitivity}</label>
              <input
                type="range"
                min="0" max="1" step="0.1"
                value={sensitivity}
                onChange={handleSensitivityChange}
                style={{ width: '100%' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                <span>Conservative</span>
                <span>Risk-Taker</span>
              </div>
            </div>

            <button className="btn-primary" style={{ width: '100%', marginTop: '1.5rem' }} onClick={handleAnalyze}>
              {loading ? 'Analyzing...' : 'Analyze Document'}
            </button>
          </div>

          {/* Logic/Explanation Panel - Only if results */}
          {results && selectedClause && (
            <div className="glass-panel" style={{ padding: '1.5rem', borderLeft: '4px solid var(--accent-color)' }}>
              <h3>Clause Analysis</h3>
              <p style={{ fontStyle: 'italic', color: 'var(--text-secondary)' }}>"{selectedClause.text}"</p>
              <div style={{ marginTop: '1rem' }}>
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '0.5rem' }}>
                  <span className="risk-badge" style={{ background: '#334155' }}>Base: {selectedClause.base_risk.toFixed(2)}</span>
                  <span className="risk-badge" style={{ background: '#334155' }}>Propagated: {selectedClause.propagated_risk.toFixed(2)}</span>
                </div>
                <div style={{ fontWeight: 'bold', fontSize: '1.2rem', color: selectedClause.final_risk > 0.7 ? 'var(--risk-high)' : 'var(--risk-low)' }}>
                  Final Risk: {(selectedClause.final_risk * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          )}

        </div>

        {/* Right Column: Visualization */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

          {results ? (
            <>
              {/* Summary Card */}
              <div className="glass-panel" style={{ padding: '1.5rem' }}>
                <h3><Activity size={20} /> Executive Summary</h3>
                <div style={{ whiteSpace: 'pre-line', fontSize: '0.95rem', lineHeight: '1.6' }}>
                  {results.summary}
                </div>
              </div>

              {/* Stats Row */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                <div className="glass-panel" style={{ padding: '1rem', textAlign: 'center' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{(results.overall_risk_score * 10).toFixed(1)}/10</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Overall Risk Score</div>
                </div>
                <div className="glass-panel" style={{ padding: '1rem', textAlign: 'center' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{results.clause_level_scores.length}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Clauses Analyzed</div>
                </div>
                <div className="glass-panel" style={{ padding: '1rem', textAlign: 'center' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--risk-high)' }}>
                    {results.clause_level_scores.filter(c => c.final_risk > 0.7).length}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>High Risk Clauses</div>
                </div>
              </div>

              {/* Vis Components */}
              <RiskGraph data={results.graph_metadata} onNodeClick={setSelectedClause} />
              <RiskHeatmap clauses={results.clause_level_scores} onClauseSelect={setSelectedClause} />
            </>
          ) : (
            <div className="glass-panel" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
              <div style={{ textAlign: 'center' }}>
                <FileText size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                <p>Upload a document to see risk analysis</p>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default App;

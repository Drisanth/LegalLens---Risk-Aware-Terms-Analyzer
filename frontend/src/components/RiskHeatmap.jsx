import React from 'react';

const RiskHeatmap = ({ clauses, onClauseSelect }) => {
    // Normalize risk to 0-1 for opacity/color
    const getStyle = (risk) => {
        let color = 'var(--risk-low)';
        if (risk > 0.7) color = 'var(--risk-high)';
        else if (risk > 0.4) color = 'var(--risk-medium)';

        return {
            backgroundColor: color,
            opacity: 0.3 + (risk * 0.7), // Higher risk = more opaque
        };
    };

    return (
        <div className="glass-panel" style={{ padding: '1rem', marginTop: '1rem' }}>
            <h3>Risk Heatmap</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(20px, 1fr))', gap: '4px' }}>
                {clauses.map((clause, idx) => (
                    <div
                        key={idx}
                        className="heatmap-cell"
                        style={{
                            ...getStyle(clause.final_risk),
                            height: '20px',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            transition: 'transform 0.2s',
                        }}
                        onClick={() => onClauseSelect(clause)}
                        title={`Clause ${idx}: Risk ${(clause.final_risk * 100).toFixed(0)}%`}
                        onMouseEnter={(e) => e.target.style.transform = 'scale(1.2)'}
                        onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
                    />
                ))}
            </div>
        </div>
    );
};

export default RiskHeatmap;

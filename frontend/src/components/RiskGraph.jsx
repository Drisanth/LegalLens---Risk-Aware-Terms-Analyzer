import React, { useRef, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const RiskGraph = ({ data, onNodeClick }) => {
    const graphRef = useRef();

    useEffect(() => {
        if (graphRef.current) {
            graphRef.current.d3Force('charge').strength(-100);
        }
    }, []);

    const getNodeColor = (node) => {
        if (node.propagated_risk > 0.7) return '#fb7185'; // High
        if (node.propagated_risk > 0.4) return '#facc15'; // Medium
        return '#4ade80'; // Low
    };

    return (
        <div className="glass-panel" style={{ height: '400px', width: '100%', overflow: 'hidden' }}>
            <h3 style={{ padding: '0.5rem', margin: 0, borderBottom: '1px solid var(--border-color)' }}>Clause Dependency Graph</h3>
            <ForceGraph2D
                ref={graphRef}
                width={600} // Dynamic width handling in parent is better usually, but for fixed panel:
                height={360}
                graphData={data}
                nodeLabel="id"
                nodeColor={getNodeColor}
                linkColor={() => 'rgba(148, 163, 184, 0.2)'}
                enableNodeDrag={false}
                onNodeClick={onNodeClick}
                backgroundColor="rgba(0,0,0,0)"
            />
        </div>
    );
};

export default RiskGraph;

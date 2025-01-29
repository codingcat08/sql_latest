import React, { useEffect, useRef } from 'react';
import { DataSet, Network } from 'vis-network/standalone';

function GraphDisplay({ data }) {
    const containerRef = useRef(null);

    useEffect(() => {
        if (!data) return;

        const nodes = [];
        const edges = [];

        for (let column in data) {
            const nodeId = `column_${column}`;
            nodes.push({ id: nodeId, label: column });

            data[column].source_columns.split(', ').forEach(source => {
                const sourceId = `column_${source}`;
                edges.push({ from: sourceId, to: nodeId });
            });
        }

        const networkData = {
            nodes: new DataSet(nodes),
            edges: new DataSet(edges)
        };

        const options = {};
        new Network(containerRef.current, networkData, options);
    }, [data]);

    return (
        <div ref={containerRef} style={{ height: '400px' }}></div>
    );
}

export default GraphDisplay;

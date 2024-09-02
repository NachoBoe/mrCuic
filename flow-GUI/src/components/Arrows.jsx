// src/components/Arrows.jsx

import React from 'react';

function Arrows({ nodes, connections }) {
  const getNodeById = (id) => nodes.find(node => node.id === id);

  const renderArrow = (fromNode, toNode) => {
    if (!fromNode || !toNode) return null;

    const fromX = fromNode.position.x + 25; // Center of the node
    const fromY = fromNode.position.y+ 75; // Center of the node
    const toX = toNode.position.x + 25;
    const toY = toNode.position.y + 75;

    return (
      <line
        key={`${fromNode.id}-${toNode.id}`}
        x1={fromX}
        y1={fromY}
        x2={toX}
        y2={toY}
        stroke="black"
        strokeWidth="2"
        markerEnd="url(#arrowhead)"
      />
    );
  };

  return (
    <svg className="arrows-container" style={{ position: 'absolute', width: '100%', height: '100%' }}>
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" />
        </marker>
      </defs>
      {connections.map((conn) => {
        const fromNode = getNodeById(conn.from);
        const toNode = getNodeById(conn.to);
        return renderArrow(fromNode, toNode);
      })}
    </svg>
  );
}

export default Arrows;

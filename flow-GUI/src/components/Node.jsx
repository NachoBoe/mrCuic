// src/components/Node.jsx

import React from 'react';
import { useDrag } from 'react-dnd';
import './Node.css';

function Node({ node, onDoubleClick }) {
  const [, drag] = useDrag(() => ({
    type: 'node',
    item: { id: node.id, type: node.type, dropType: 'move' },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  }));

  return (
    <div
      ref={drag}
      className={`node ${node.isSelected ? 'selected' : ''}`}
      style={{ left: node.position.x, top: node.position.y }}
      onDoubleClick={onDoubleClick}
    >
      <p>{node.type}</p>
      <p>{node.description}</p>
    </div>
  );
}

export default Node;

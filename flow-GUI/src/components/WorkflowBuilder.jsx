// src/components/WorkflowBuilder.jsx

import React, { useState, useEffect } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import Node from './Node.jsx';
import NodeModal from './NodeModal.jsx';
import './WorkflowBuilder.css';
import Arrows from './Arrows.jsx';

const nodeTypes = [
  { type: 'SendUser', label: 'Send User' },
  { type: 'CallAPI', label: 'Call API' },
  { type: 'ParseInput', label: 'Parse Input' },
];

function WorkflowBuilder({ flowData }) {
  const [nodes, setNodes] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [connections, setConnections] = useState([]);

  useEffect(() => {
    if (selectedNode) {
      updateConnections(selectedNode);
    }
  }, [nodes]);

  const handleDrop = (item, monitor) => {
    const offset = monitor.getClientOffset();
    const dropZoneElement = document.querySelector('.drop-zone');
    const dropZoneRect = dropZoneElement.getBoundingClientRect();
    const dropType = item.dropType || 'create';

    const newPosition = {
      x: offset.x - dropZoneRect.left,
      y: offset.y - dropZoneRect.top,
    };

    if (dropType === 'move') {
      setNodes(prevNodes =>
        prevNodes.map(node =>
          node.id === item.id
            ? { ...node, position: newPosition }
            : node
        )
      );
    } else {
      const newNode = {
        id: '',
        type: item.type,
        position: newPosition,
        description: '',
        next: {},
      };
      setNodes(prevNodes => [...prevNodes, newNode]);
      setSelectedNode(newNode);
    }
  };

  const handleModalClose = (updatedNode) => {
    if (updatedNode) {
      setNodes(nodes.map(n => n === selectedNode ? updatedNode : n));
      updateConnections(updatedNode);
    }
    setSelectedNode(null);
  };

  const updateConnections = (updatedNode) => {
    let newConnections = [...connections];
    newConnections = newConnections.filter(conn => conn.from !== updatedNode.id);

    if (updatedNode.next.type === 'direct') {
      newConnections.push({
        from: updatedNode.id,
        to: updatedNode.next.step,
      });
    } else if (updatedNode.next.type === 'conditional') {
      updatedNode.next.conditions.forEach(condition => {
        newConnections.push({
          from: updatedNode.id,
          to: condition.step,
        });
      });
    }

    setConnections(newConnections);
  };

  const handleNodeDoubleClick = (node) => {
    setSelectedNode(node);
  };

  const handleNodeClick = (nodeId) => {
    const node = nodes.find(n => n.id === nodeId);
    if (node) {
      handleNodeDoubleClick(node);
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="workflow-container">
        <div className="menu">
          <h3>Node Types</h3>
          {nodeTypes.map((node) => (
            <NodeType key={node.type} type={node.type} label={node.label} />
          ))}
          <h3>Existing Nodes</h3>
          {nodes.length === 0 && <p>No nodes created yet</p>}
          {nodes.map((node) => (
            <ExistingNode
              key={node.id}
              node={node}
              onClick={() => handleNodeClick(node.id)}
            />
          ))}
        </div>
        <div className="canvas">
          <DropZone onDrop={handleDrop}>
            {nodes.map((node) => (
              <Node 
                key={node.id} 
                node={node} 
                onDoubleClick={() => handleNodeDoubleClick(node)} 
              />
            ))}
            <Arrows nodes={nodes} connections={connections} />
          </DropZone>
        </div>
        {selectedNode && (
          <NodeModal
            node={selectedNode}
            onClose={handleModalClose}
            existingNodeIds={nodes.map(n => n.id)}
          />
        )}
      </div>
    </DndProvider>
  );
}

function NodeType({ type, label }) {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'node',
    item: { type, dropType: 'create' },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  }));

  return (
    <div ref={drag} className="node-type" style={{ opacity: isDragging ? 0.5 : 1 }}>
      {label}
    </div>
  );
}

function ExistingNode({ node, onClick }) {
  return (
    <div className="existing-node" onClick={onClick}>
      {node.id}: {node.type}
    </div>
  );
}

function DropZone({ onDrop, children }) {
  const [, drop] = useDrop(() => ({
    accept: 'node',
    drop: (item, monitor) => onDrop(item, monitor),
  }));

  return (
    <div ref={drop} className="drop-zone">
      {children}
    </div>
  );
}

export default WorkflowBuilder;

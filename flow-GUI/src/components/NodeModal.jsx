// src/components/NodeModal.jsx

import React, { useState } from 'react';
import './NodeModal.css';

function NodeModal({ node, onClose, existingNodeIds }) {
  const [nodeId, setNodeId] = useState(node.id || '');
  const [description, setDescription] = useState(node.description || '');
  const [next, setNext] = useState(node.next || {});
  const [error, setError] = useState('');

  const handleSave = () => {
    if (!nodeId.trim() || !description.trim()) {
      setError('Node ID and Description are required.');
      return;
    }

    if (existingNodeIds.includes(nodeId) && nodeId !== node.id) {
      setError('Node ID must be unique.');
      return;
    }

    if (next.type === 'direct' && !existingNodeIds.includes(next.step)) {
      setError('The next step must be an existing node ID.');
      return;
    }

    if (next.type === 'conditional') {
      for (const condition of next.conditions) {
        if (!existingNodeIds.includes(condition.step)) {
          setError('All condition steps must be existing node IDs.');
          return;
        }
      }
    }

    onClose({ ...node, id: nodeId, description, next });
  };

  const handleAddCondition = () => {
    setNext(prevNext => ({
      ...prevNext,
      conditions: [...(prevNext.conditions || []), { step: '', condition: '' }]
    }));
  };

  const handleConditionChange = (index, key, value) => {
    const updatedConditions = next.conditions.map((cond, idx) =>
      idx === index ? { ...cond, [key]: value } : cond
    );
    setNext({ ...next, conditions: updatedConditions });
  };

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <h2>Edit Node</h2>
        <div className="form-group">
          <label>Node ID:</label>
          <input
            type="text"
            value={nodeId}
            onChange={(e) => setNodeId(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Description:</label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Next Type:</label>
          <select
            value={next.type || ''}
            onChange={(e) => setNext({ ...next, type: e.target.value })}
          >
            <option value="direct">Direct</option>
            <option value="conditional">Conditional</option>
          </select>
        </div>
        {next.type === 'conditional' && (
          <>
            {next.conditions && next.conditions.map((cond, idx) => (
              <div key={idx} className="form-group">
                <label>Condition {idx + 1}:</label>
                <input
                  type="text"
                  placeholder="Step"
                  value={cond.step}
                  onChange={(e) => handleConditionChange(idx, 'step', e.target.value)}
                />
                <input
                  type="text"
                  placeholder="Condition"
                  value={cond.condition}
                  onChange={(e) => handleConditionChange(idx, 'condition', e.target.value)}
                />
              </div>
            ))}
            <button type="button" onClick={handleAddCondition}>Add Condition</button>
          </>
        )}
        {next.type === 'direct' && (
          <div className="form-group">
            <label>Step:</label>
            <input
              type="text"
              value={next.step || ''}
              onChange={(e) => setNext({ ...next, step: e.target.value })}
            />
          </div>
        )}
        {error && <div className="error">{error}</div>}
        <div className="modal-actions">
          <button onClick={handleSave}>Save</button>
          <button onClick={() => onClose(null)}>Cancel</button>
        </div>
      </div>
    </div>
  );
}

export default NodeModal;

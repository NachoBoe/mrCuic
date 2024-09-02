// src/components/FlowSetup.jsx

import React, { useState } from 'react';
import './FlowSetup.css';

function FlowSetup({ onSetupComplete }) {
  const [flowName, setFlowName] = useState('');
  const [description, setDescription] = useState('');
  const [triggerPhrases, setTriggerPhrases] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const phrases = triggerPhrases.split(',').map(p => p.trim());
    onSetupComplete({ flowName, description, triggerPhrases: phrases });
  };

  return (
    <div className="flow-setup-container">
      <form className="flow-setup-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Flow Name:</label>
          <input
            type="text"
            value={flowName}
            onChange={(e) => setFlowName(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Description:</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Trigger Phrases (comma-separated):</label>
          <input
            type="text"
            value={triggerPhrases}
            onChange={(e) => setTriggerPhrases(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="submit-button">Start Building</button>
      </form>
    </div>
  );
}

export default FlowSetup;

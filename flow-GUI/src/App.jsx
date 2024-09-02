// src/App.jsx

import React, { useState } from 'react';
import FlowSetup from './components/FlowSetup.jsx';
import WorkflowBuilder from './components/WorkflowBuilder.jsx';
import './App.css';

function App() {
  const [flowData, setFlowData] = useState(null);

  const handleSetupComplete = (data) => {
    setFlowData(data);
  };

  return (
    <div className="App">
      {!flowData ? (
        <FlowSetup onSetupComplete={handleSetupComplete} />
      ) : (
        <WorkflowBuilder flowData={flowData} />
      )}
    </div>
  );
}

export default App;

'use client';

import React, { useEffect, useCallback } from 'react';
import { 
  ReactFlow,
  Background,
  Controls,
  Node,
  NodeTypes,
  ReactFlowProvider,
  Panel
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import useAgentFlowStore from '../stores/agentFlowStore';
import { AgentNode as AgentNodeType } from '../stores/agentFlowStore';
import AgentNode from './AgentNode';
import AgentSidebar from './AgentSidebar';
import AgentForm from './AgentForm';

// Define the nodeTypes properly
const nodeTypes = { agentNode: AgentNode } as NodeTypes;

// Wrapper component to ensure useReactFlow is used within a ReactFlowProvider
const AgentFlowInner = () => {
  const { 
    nodes, 
    edges, 
    onNodesChange, 
    onEdgesChange, 
    addEdge,
    setSelectedAgent,
    fetchAgents,
    toggleAgentForm,
    loading,
    error
  } = useAgentFlowStore();
  
  // Load agents on component mount
  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);
  
  // Handle node selection with proper type casting
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedAgent(node as AgentNodeType);
  }, [setSelectedAgent]);
  
  // Handle pane click (deselect)
  const onPaneClick = useCallback(() => {
    setSelectedAgent(null);
  }, [setSelectedAgent]);
  
  return (
    <div className="flex h-screen">
      <div className="flex-1">
        <ReactFlow
          nodes={nodes as unknown as Node[]}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={addEdge}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
          defaultEdgeOptions={{
            animated: true,
            style: { stroke: '#2563eb' },
          }}
        >
          <Background color="#f1f5f9" gap={16} />
          <Controls />
          <Panel position="top-left" className="bg-white p-2 rounded shadow">
            <h3 className="text-lg font-semibold mb-2">Agent Flow Editor</h3>
            <button
              onClick={toggleAgentForm}
              className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded"
            >
              Add Agent
            </button>
          </Panel>
          {loading && (
            <Panel position="top-center" className="bg-blue-100 px-4 py-2 rounded shadow">
              Loading...
            </Panel>
          )}
          {error && (
            <Panel position="top-center" className="bg-red-100 px-4 py-2 rounded shadow">
              {error}
            </Panel>
          )}
        </ReactFlow>
      </div>
      
      <div className="w-1/3 max-w-md border-l border-gray-200 overflow-y-auto p-5 bg-gray-50">
        <AgentSidebar />
      </div>
      
      <AgentForm />
    </div>
  );
};

// Wrapper with provider
const AgentFlow = () => {
  return (
    <ReactFlowProvider>
      <AgentFlowInner />
    </ReactFlowProvider>
  );
};

export default AgentFlow;
'use client';

import React, { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Agent } from '../services/api';

// Match the data structure exactly as defined in agentFlowStore
interface AgentData extends Record<string, unknown> {
  label: string;
  agentId?: number;
  agentData?: Agent;
}

const AgentNode = ({ data, selected }: NodeProps) => {
  // Cast data to our expected type
  const nodeData = data as AgentData;
  const { label, agentData } = nodeData;
  
  return (
    <div className={`agent-node p-3 rounded-lg shadow-md ${selected ? 'ring-2 ring-blue-500' : ''}`}
         style={{ 
           backgroundColor: '#f8fafc', 
           border: '1px solid #e2e8f0',
           minWidth: '200px'
         }}>
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 bg-gray-400 rounded-full border-2 border-white"
      />
      
      <div className="py-2">
        <div className="text-lg font-semibold text-gray-800 mb-1">{label}</div>
        
        {agentData && (
          <div className="text-xs text-gray-500 space-y-1">
            <div><span className="font-medium">Role:</span> {agentData.role}</div>
            <div><span className="font-medium">Goal:</span> {agentData.goal}</div>
            {agentData.config && (
              <div className="mt-2 text-xs text-blue-600">
                <div>Model: {agentData.config.model}</div>
                <div>Temp: {agentData.config.temperature}</div>
              </div>
            )}
          </div>
        )}
      </div>
      
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 bg-blue-500 rounded-full border-2 border-white"
      />
    </div>
  );
};

export default memo(AgentNode);
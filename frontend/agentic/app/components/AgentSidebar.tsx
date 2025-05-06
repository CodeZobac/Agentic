'use client';

import React, { useState, useEffect } from 'react';
import useAgentFlowStore from '../stores/agentFlowStore';

const AgentSidebar = () => {
  const { 
    selectedAgent, 
    updateAgent, 
    deleteAgent,
    toggleAgentForm,
    loading, 
    error 
  } = useAgentFlowStore();
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    role: '',
    goal: '',
    backstory: '',
    model: 'gpt-4o',
    temperature: 0.7,
    max_tokens: 1000,
    verbose: false,
    allow_delegation: true
  });
  
  // If selectedAgent changes, update form data
  useEffect(() => {
    if (selectedAgent && selectedAgent.data.agentData) {
      const { agentData } = selectedAgent.data;
      setFormData({
        name: agentData.name || '',
        description: agentData.description || '',
        role: agentData.role || '',
        goal: agentData.goal || '',
        backstory: agentData.backstory || '',
        model: agentData.config?.model || 'gpt-4o',
        temperature: agentData.config?.temperature || 0.7,
        max_tokens: agentData.config?.max_tokens || 1000,
        verbose: agentData.config?.verbose || false,
        allow_delegation: agentData.config?.allow_delegation || true
      });
    }
  }, [selectedAgent]);
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedAgent || !selectedAgent.data.agentId) return;
    
    const agentData = {
      name: formData.name,
      description: formData.description,
      role: formData.role,
      goal: formData.goal,
      backstory: formData.backstory,
      config: {
        model: formData.model,
        temperature: formData.temperature,
        max_tokens: formData.max_tokens,
        verbose: formData.verbose,
        allow_delegation: formData.allow_delegation
      }
    };
    
    await updateAgent(selectedAgent.data.agentId, agentData);
  };
  
  // Handle input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  // Handle checkbox changes
  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: checked }));
  };
  
  // Handle number input changes
  const handleNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: parseFloat(value) }));
  };
  
  // Handle agent deletion
  const handleDelete = async () => {
    if (!selectedAgent || !selectedAgent.data.agentId) return;
    
    if (window.confirm('Are you sure you want to delete this agent?')) {
      await deleteAgent(selectedAgent.data.agentId);
    }
  };
  
  if (!selectedAgent) {
    return (
      <div className="p-4 bg-white shadow rounded-lg">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Agent Details</h3>
        <p className="text-gray-500">Select an agent to view and edit its details</p>
        <button
          onClick={toggleAgentForm}
          className="mt-4 bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded"
        >
          Create New Agent
        </button>
      </div>
    );
  }
  
  return (
    <div className="bg-white p-6 shadow-lg rounded-lg overflow-auto max-h-[calc(100vh-120px)]">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-800">
          {selectedAgent.data.label}
        </h2>
        <div className="flex space-x-2">
          <button
            onClick={handleDelete}
            className="text-red-500 hover:text-red-700"
            disabled={loading}
          >
            Delete
          </button>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700">Name</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={2}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Role</label>
          <input
            type="text"
            name="role"
            value={formData.role}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Goal</label>
          <input
            type="text"
            name="goal"
            value={formData.goal}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Backstory</label>
          <textarea
            name="backstory"
            value={formData.backstory}
            onChange={handleChange}
            rows={3}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        
        <div className="border-t pt-4">
          <h3 className="text-md font-medium text-gray-800 mb-4">Agent Configuration</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Model</label>
              <select
                name="model"
                value={formData.model}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="gpt-4o">GPT-4o</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="agentic-specialist">Agentic Specialist (Ollama)</option>
                <option value="mistral:7b">Mistral 7B (Ollama)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Temperature: {formData.temperature}
              </label>
              <input
                type="range"
                name="temperature"
                min="0"
                max="1"
                step="0.1"
                value={formData.temperature}
                onChange={handleNumberChange}
                className="mt-1 block w-full"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Max Tokens</label>
              <input
                type="number"
                name="max_tokens"
                value={formData.max_tokens}
                onChange={handleNumberChange}
                min="1"
                max="8000"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                name="verbose"
                checked={formData.verbose}
                onChange={handleCheckboxChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-700">
                Verbose Mode
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                name="allow_delegation"
                checked={formData.allow_delegation}
                onChange={handleCheckboxChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-700">
                Allow Task Delegation
              </label>
            </div>
          </div>
        </div>
        
        <div className="pt-4">
          <button
            type="submit"
            className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AgentSidebar;
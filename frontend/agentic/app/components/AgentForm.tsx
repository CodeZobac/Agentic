'use client';

import React, { useState } from 'react';
import useAgentFlowStore from '../stores/agentFlowStore';

const AgentForm = () => {
  const { 
    isAgentFormOpen, 
    toggleAgentForm, 
    createAgent, 
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
  
  // Form handlers
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
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
    
    await createAgent(agentData);
    
    // Reset form
    setFormData({
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
  };
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: checked }));
  };
  
  const handleNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: parseFloat(value) }));
  };
  
  if (!isAgentFormOpen) return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl overflow-hidden max-h-[90vh] flex flex-col">
        <div className="px-6 py-4 bg-gray-100 flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900">Create New Agent</h3>
          <button 
            onClick={toggleAgentForm}
            className="text-gray-500 hover:text-gray-700"
          >
            &times;
          </button>
        </div>
        
        <div className="p-6 flex-1 overflow-auto">
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
          </form>
        </div>
        
        <div className="px-6 py-4 bg-gray-100 flex justify-end">
          <button
            type="button"
            onClick={toggleAgentForm}
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 py-2 px-4 rounded-md mr-2"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md"
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Agent'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AgentForm;
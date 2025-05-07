'use client';

import React, { useState, useEffect, useRef } from 'react';
import useAgentFlowStore from '../stores/agentFlowStore';
import { taskService, Task, TaskExecution } from '../services/api';

const AgentSidebar = () => {
  const { selectedAgent, updateAgent, deleteAgent, loading } = useAgentFlowStore();
  const [isEditing, setIsEditing] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [userInput, setUserInput] = useState('');
  const [chatMessages, setChatMessages] = useState<{role: string, content: string}[]>([]);
  const [currentTask, setCurrentTask] = useState<Task | null>(null);
  const [taskExecution, setTaskExecution] = useState<TaskExecution | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [statusPolling, setStatusPolling] = useState<NodeJS.Timeout | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
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

  // Update form when selected agent changes
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
      
      // Reset chat state when switching agents
      setChatMessages([]);
      setCurrentTask(null);
      setTaskExecution(null);
      setIsExecuting(false);
      
      // Clear any ongoing polling
      if (statusPolling) {
        clearInterval(statusPolling);
        setStatusPolling(null);
      }
    }
  }, [selectedAgent]);
  
  // Scroll to bottom of chat when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);
  
  // Clean up polling on unmount
  useEffect(() => {
    return () => {
      if (statusPolling) {
        clearInterval(statusPolling);
      }
    };
  }, [statusPolling]);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAgent || !selectedAgent.data.agentData) return;

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

    await updateAgent(selectedAgent.data.agentData.id, agentData);
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (!selectedAgent || !selectedAgent.data.agentData) return;
    if (window.confirm('Are you sure you want to delete this agent?')) {
      await deleteAgent(selectedAgent.data.agentData.id);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(e.target.value);
  };

  const handleSendMessage = async () => {
    if (!userInput.trim() || !selectedAgent || !selectedAgent.data.agentData) return;
    
    // Add user message to chat
    const userMessage = { role: 'user', content: userInput };
    setChatMessages([...chatMessages, userMessage]);
    
    // Create a task for the agent
    try {
      // Store the message for clearing input before the API call
      const messageText = userInput;
      setUserInput('');
      
      const taskData = {
        title: `Task for ${selectedAgent.data.agentData.name}`,
        description: messageText,
        expected_output: "Response to user query",
        user_id: 1, // Default user_id
        agent_ids: [selectedAgent.data.agentData.id]
      };
      
      const task = await taskService.createTask(taskData);
      setCurrentTask(task);
      
      // Start execution
      executeTask(task.id);
    } catch (error) {
      console.error("Failed to create task:", error);
      
      // Check specifically for 401 unauthorized errors
      if (error.response && error.response.status === 401) {
        setChatMessages([
          ...chatMessages, 
          userMessage,
          { 
            role: 'system', 
            content: 'Authentication error. You may need to log in first or check your API configuration.' 
          }
        ]);
      } else {
        setChatMessages([
          ...chatMessages, 
          userMessage,
          { 
            role: 'system', 
            content: `Failed to send message to agent: ${error.message || 'Unknown error'}` 
          }
        ]);
      }
      
      setIsExecuting(false);
    }
  };

  const executeTask = async (taskId: number) => {
    setIsExecuting(true);
    
    try {
      // Execute the task
      const execution = await taskService.executeTask(taskId);
      setTaskExecution(execution);
      
      // Add a temporary message indicating the agent is thinking
      setChatMessages([
        ...chatMessages, 
        { role: 'assistant', content: 'Processing your request...' }
      ]);
      
      // Start polling for task status
      const intervalId = setInterval(async () => {
        try {
          const status = await taskService.getTaskStatus(taskId);
          
          if (status.status === 'completed') {
            clearInterval(intervalId);
            setStatusPolling(null);
            
            // Fetch the completed task to get the result
            const completedTask = await taskService.getTask(taskId);
            
            // Replace the temporary message with the actual result
            setChatMessages(prev => {
              const updatedMessages = [...prev];
              // Replace the last message if it was the temporary one
              if (updatedMessages.length > 0 && 
                  updatedMessages[updatedMessages.length - 1].role === 'assistant' &&
                  updatedMessages[updatedMessages.length - 1].content === 'Processing your request...') {
                updatedMessages.pop();
              }
              
              // Add the agent's response
              updatedMessages.push({ 
                role: 'assistant', 
                content: completedTask.result || 'Task completed but no result was provided.' 
              });
              
              return updatedMessages;
            });
            
            setIsExecuting(false);
          } else if (status.status === 'failed') {
            clearInterval(intervalId);
            setStatusPolling(null);
            
            // Replace the temporary message with error
            setChatMessages(prev => {
              const updatedMessages = [...prev];
              if (updatedMessages.length > 0 && 
                  updatedMessages[updatedMessages.length - 1].role === 'assistant' &&
                  updatedMessages[updatedMessages.length - 1].content === 'Processing your request...') {
                updatedMessages.pop();
              }
              
              updatedMessages.push({ 
                role: 'system', 
                content: 'The agent encountered an error while processing your request.' 
              });
              
              return updatedMessages;
            });
            
            setIsExecuting(false);
          }
        } catch (error) {
          console.error("Error polling task status:", error);
          clearInterval(intervalId);
          setStatusPolling(null);
          setIsExecuting(false);
          
          // Add error message
          setChatMessages(prev => [
            ...prev.filter(msg => msg.content !== 'Processing your request...'),
            { role: 'system', content: 'Lost connection to the agent. Please try again.' }
          ]);
        }
      }, 1000);
      
      setStatusPolling(intervalId);
      
    } catch (error) {
      console.error("Failed to execute task:", error);
      setChatMessages(prev => [
        ...prev,
        { role: 'system', content: 'Failed to run the agent. Please try again.' }
      ]);
      setIsExecuting(false);
    }
  };

  if (!selectedAgent) {
    return (
      <div className="text-center py-10 text-gray-500">
        <p>Select an agent to view details</p>
        <p className="mt-4 text-sm">Or add a new agent using the button on the left panel</p>
      </div>
    );
  }

  const { agentData } = selectedAgent.data;

  if (!agentData) {
    return (
      <div className="text-center py-10 text-gray-500">
        <p>Agent data not available</p>
      </div>
    );
  }

  if (isEditing) {
    return (
      <div className="h-full flex flex-col">
        <div className="flex justify-between items-center mb-4 pb-2 border-b">
          <h2 className="text-xl font-semibold">Edit Agent</h2>
          <button 
            onClick={() => setIsEditing(false)}
            className="text-gray-600 hover:text-gray-800"
          >
            Cancel
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex-1 overflow-auto">
          <div className="space-y-4">
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
            
            <div className="border-t pt-4 mt-4">
              <h3 className="text-md font-medium text-gray-800 mb-3">Agent Configuration</h3>
              
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
          </div>
          
          <div className="mt-6 flex justify-end">
            <button
              type="button"
              onClick={() => setIsEditing(false)}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 py-2 px-4 rounded-md mr-2"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md"
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex justify-between items-center pb-3 border-b">
        <h2 className="text-xl font-semibold">{agentData.name}</h2>
        <div>
          <button 
            onClick={() => setShowChat(!showChat)}
            className="bg-green-500 hover:bg-green-600 text-white py-1 px-3 rounded-md mr-2"
          >
            {showChat ? 'View Details' : 'Chat with Agent'}
          </button>
          <button 
            onClick={() => setIsEditing(true)}
            className="text-blue-600 hover:text-blue-800 mr-2"
          >
            Edit
          </button>
          <button 
            onClick={handleDelete}
            className="text-red-600 hover:text-red-800"
            disabled={loading}
          >
            Delete
          </button>
        </div>
      </div>
      
      {showChat ? (
        <div className="flex-1 flex flex-col h-full mt-4">
          <div className="flex-1 overflow-auto mb-4 p-3 border rounded-lg bg-gray-50">
            {chatMessages.length === 0 ? (
              <div className="text-center text-gray-500 my-8">
                <p>No messages yet.</p>
                <p className="text-sm mt-2">Start a conversation with {agentData.name}!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {chatMessages.map((message, index) => (
                  <div 
                    key={index} 
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div 
                      className={`max-w-3/4 px-4 py-2 rounded-lg ${
                        message.role === 'user' 
                          ? 'bg-blue-500 text-white rounded-br-none' 
                          : message.role === 'system'
                            ? 'bg-gray-300 text-gray-800' 
                            : 'bg-gray-200 text-gray-800 rounded-bl-none'
                      }`}
                    >
                      {message.content}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={userInput}
              onChange={handleInputChange}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder={`Send a message to ${agentData.name}...`}
              className="flex-1 px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isExecuting}
            />
            <button
              onClick={handleSendMessage}
              disabled={!userInput.trim() || isExecuting}
              className={`px-4 py-2 rounded-md text-white ${
                !userInput.trim() || isExecuting 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-blue-500 hover:bg-blue-600'
              }`}
            >
              {isExecuting ? 'Processing...' : 'Send'}
            </button>
          </div>
        </div>
      ) : (
        <div className="mt-4 flex-1 overflow-auto">
          <div className="mb-6">
            <h3 className="text-md font-medium text-gray-700 mb-2">Details</h3>
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-gray-500 font-medium">Role</p>
                <p>{agentData.role}</p>
              </div>
              
              <div>
                <p className="text-gray-500 font-medium">Goal</p>
                <p>{agentData.goal}</p>
              </div>
              
              {agentData.description && (
                <div>
                  <p className="text-gray-500 font-medium">Description</p>
                  <p>{agentData.description}</p>
                </div>
              )}
              
              {agentData.backstory && (
                <div>
                  <p className="text-gray-500 font-medium">Backstory</p>
                  <p>{agentData.backstory}</p>
                </div>
              )}
            </div>
          </div>
          
          {agentData.config && (
            <div className="pt-4 border-t">
              <h3 className="text-md font-medium text-gray-700 mb-2">Configuration</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Model:</span>
                  <span>{agentData.config.model}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-500">Temperature:</span>
                  <span>{agentData.config.temperature}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-500">Max Tokens:</span>
                  <span>{agentData.config.max_tokens}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-500">Verbose Mode:</span>
                  <span>{agentData.config.verbose ? 'Enabled' : 'Disabled'}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-500">Delegation:</span>
                  <span>{agentData.config.allow_delegation ? 'Allowed' : 'Disabled'}</span>
                </div>
              </div>
            </div>
          )}
          
          <div className="pt-4 mt-4 border-t">
            <h3 className="text-md font-medium text-gray-700 mb-2">Usage</h3>
            <div className="bg-gray-100 rounded p-3 text-sm">
              <p>Connect this agent with other agents in the flow to define interaction patterns.</p>
              <p className="mt-2">The edges between agents represent information flows and task delegation paths.</p>
              <p className="mt-2">Click the "Chat with Agent" button to interact directly with this agent.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentSidebar;
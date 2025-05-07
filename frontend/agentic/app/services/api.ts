import axios from 'axios';

// Define interfaces for the API data structures
export interface AgentConfig {
  model: string;
  temperature: number;
  max_tokens: number;
  verbose: boolean;
  allow_delegation: boolean;
}

export interface Agent {
  id: number;
  name: string;
  description: string;
  role: string;
  goal: string;
  backstory: string;
  config?: AgentConfig;
  user_id?: number;
  created_at?: string;
  updated_at?: string;
}

export interface AgentCreateData {
  name: string;
  description: string;
  role: string;
  goal: string;
  backstory: string;
  config?: AgentConfig;
}

export interface Task {
  id: number;
  title: string;
  description: string;
  expected_output: string;
  status: string;
  result?: string;
  user_id: number;
  agent_ids: number[];
  created_at: string;
  updated_at: string;
}

export interface TaskExecution {
  id: number;
  status: string;
  result: string;
  logs: string[];
  started_at: string;
  completed_at?: string;
}

export interface TaskStep {
  id: number;
  task_id: number;
  agent_id: number;
  order: number;
  action: string;
  status: string;
  result?: string;
  created_at: string;
  updated_at: string;
}

// Create an axios instance with default configuration
const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include auth token from localStorage if available
API.interceptors.request.use(
  (config) => {
    // Only include token in browser environment
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      } else {
        // For development purposes: Set a default user token if none exists
        console.warn('No auth token found in localStorage, using development fallback');
        localStorage.setItem('token', 'development-token');
        config.headers.Authorization = 'Bearer development-token';
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// API services for authentication
export const authService = {
  login: async (username: string, password: string) => {
    const response = await API.post('/auth/login', 
      new URLSearchParams({ username, password }), 
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    );
    return response.data;
  },
  register: async (userData: Record<string, unknown>) => {
    const response = await API.post('/auth/register', userData);
    return response.data;
  },
};

// API services for agents
export const agentService = {
  getAgents: async (): Promise<Agent[]> => {
    const response = await API.get('/agents');
    return response.data;
  },
  getAgent: async (id: number): Promise<Agent> => {
    const response = await API.get(`/agents/${id}`);
    return response.data;
  },
  createAgent: async (agentData: AgentCreateData): Promise<Agent> => {
    const response = await API.post('/agents', agentData);
    return response.data;
  },
  updateAgent: async (id: number, agentData: Partial<AgentCreateData>): Promise<Agent> => {
    const response = await API.put(`/agents/${id}`, agentData);
    return response.data;
  },
  deleteAgent: async (id: number): Promise<void> => {
    const response = await API.delete(`/agents/${id}`);
    return response.data;
  },
};

// API services for tasks
export const taskService = {
  getTasks: async (): Promise<Task[]> => {
    const response = await API.get('/tasks');
    return response.data;
  },
  getTask: async (id: number): Promise<Task> => {
    const response = await API.get(`/tasks/${id}`);
    return response.data;
  },
  createTask: async (taskData: Omit<Task, 'id' | 'status' | 'created_at' | 'updated_at'>): Promise<Task> => {
    const response = await API.post('/tasks', taskData);
    return response.data;
  },
  updateTask: async (id: number, taskData: Partial<Task>): Promise<Task> => {
    const response = await API.put(`/tasks/${id}`, taskData);
    return response.data;
  },
  deleteTask: async (id: number): Promise<void> => {
    const response = await API.delete(`/tasks/${id}`);
    return response.data;
  },
  executeTask: async (id: number): Promise<TaskExecution> => {
    const response = await API.post(`/tasks/${id}/execute`);
    return response.data;
  },
  getTaskStatus: async (id: number): Promise<{ status: string }> => {
    const response = await API.get(`/tasks/${id}/status`);
    return response.data;
  },
  getTaskSteps: async (id: number): Promise<TaskStep[]> => {
    const response = await API.get(`/tasks/${id}/steps`);
    return response.data;
  },
};

export default API;
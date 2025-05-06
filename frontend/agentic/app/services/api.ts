import axios from 'axios';

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
  register: async (userData: any) => {
    const response = await API.post('/auth/register', userData);
    return response.data;
  },
};

// API services for agents
export const agentService = {
  getAgents: async () => {
    const response = await API.get('/agents');
    return response.data;
  },
  getAgent: async (id: number) => {
    const response = await API.get(`/agents/${id}`);
    return response.data;
  },
  createAgent: async (agentData: any) => {
    const response = await API.post('/agents', agentData);
    return response.data;
  },
  updateAgent: async (id: number, agentData: any) => {
    const response = await API.put(`/agents/${id}`, agentData);
    return response.data;
  },
  deleteAgent: async (id: number) => {
    const response = await API.delete(`/agents/${id}`);
    return response.data;
  },
};

// API services for tasks
export const taskService = {
  getTasks: async () => {
    const response = await API.get('/tasks');
    return response.data;
  },
  getTask: async (id: number) => {
    const response = await API.get(`/tasks/${id}`);
    return response.data;
  },
  createTask: async (taskData: any) => {
    const response = await API.post('/tasks', taskData);
    return response.data;
  },
  updateTask: async (id: number, taskData: any) => {
    const response = await API.put(`/tasks/${id}`, taskData);
    return response.data;
  },
  deleteTask: async (id: number) => {
    const response = await API.delete(`/tasks/${id}`);
    return response.data;
  },
  executeTask: async (id: number) => {
    const response = await API.post(`/tasks/${id}/execute`);
    return response.data;
  },
  getTaskStatus: async (id: number) => {
    const response = await API.get(`/tasks/${id}/status`);
    return response.data;
  },
  getTaskSteps: async (id: number) => {
    const response = await API.get(`/tasks/${id}/steps`);
    return response.data;
  },
};

export default API;
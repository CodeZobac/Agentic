import { create } from 'zustand';
import { 
  Node, 
  Edge, 
  addEdge, 
  OnConnect, 
  OnNodesChange, 
  OnEdgesChange, 
  applyNodeChanges, 
  applyEdgeChanges, 
  NodeChange, 
  EdgeChange,
  XYPosition
} from '@xyflow/react';
import { agentService, Agent, AgentCreateData } from '../services/api';
import { AxiosError } from 'axios';

// Define the structure of node data
export interface AgentData extends Record<string, unknown> {
  label: string;
  agentId?: number;
  agentData?: Agent;
}

// Type definition for Agent nodes in the flow
export type AgentNode = Node<AgentData>;

type AgentFlowState = {
  nodes: AgentNode[];
  edges: Edge[];
  selectedAgent: AgentNode | null;
  isAgentFormOpen: boolean;
  agents: Agent[];
  error: string | null;
  loading: boolean;
  
  // Node & Edge operations
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  addEdge: OnConnect;
  
  // Agent operations
  setSelectedAgent: (agent: AgentNode | null) => void;
  toggleAgentForm: () => void;
  addNode: (node: Partial<AgentNode>) => AgentNode;
  updateNode: (id: string, data: Partial<AgentData>) => void;
  removeNode: (id: string) => void;
  
  // Load data from API
  fetchAgents: () => Promise<void>;
  createAgent: (agentData: AgentCreateData) => Promise<Agent | undefined>;
  updateAgent: (id: number, agentData: Partial<AgentCreateData>) => Promise<Agent | undefined>;
  deleteAgent: (id: number) => Promise<void>;
  
  // Convert to/from API format
  convertAgentsToNodes: (agents: Agent[]) => void;
};

// Helper to generate unique IDs
const generateId = () => `node_${Math.random().toString(36).substring(2, 9)}`;

const useAgentFlowStore = create<AgentFlowState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedAgent: null,
  isAgentFormOpen: false,
  agents: [],
  error: null,
  loading: false,
  
  // Handle node changes
  onNodesChange: (changes: NodeChange[]) => {
    const updatedNodes = applyNodeChanges(changes, get().nodes as unknown as Node[]);
    set({
      nodes: updatedNodes as unknown as AgentNode[]
    });
  },
  
  // Handle edge changes
  onEdgesChange: (changes: EdgeChange[]) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },
  
  // Handle new connections
  addEdge: (connection) => {
    set({
      edges: addEdge(
        { ...connection, animated: true, style: { stroke: '#2563eb' } },
        get().edges
      ),
    });
  },
  
  // Set selected agent
  setSelectedAgent: (agent) => {
    set({ selectedAgent: agent });
  },
  
  // Toggle agent form visibility
  toggleAgentForm: () => {
    set({ isAgentFormOpen: !get().isAgentFormOpen });
  },
  
  // Add a new node to the flow
  addNode: (nodeData) => {
    const newNode: AgentNode = {
      id: nodeData.id || generateId(),
      type: 'agentNode',
      position: nodeData.position || { x: 100, y: 100 },
      data: { 
        label: nodeData.data?.label || 'New Agent',
        ...nodeData.data 
      },
    };
    
    set({ nodes: [...get().nodes, newNode] });
    return newNode;
  },
  
  // Update a node in the flow
  updateNode: (id, data) => {
    set({
      nodes: get().nodes.map(node => {
        if (node.id === id) {
          return { ...node, data: { ...node.data, ...data } };
        }
        return node;
      }),
    });
  },
  
  // Remove a node from the flow
  removeNode: (id) => {
    set({
      nodes: get().nodes.filter(node => node.id !== id),
      // Also remove any edges connected to this node
      edges: get().edges.filter(edge => edge.source !== id && edge.target !== id),
    });
  },
  
  // Fetch agents from API
  fetchAgents: async () => {
    try {
      set({ loading: true, error: null });
      const agents = await agentService.getAgents();
      set({ agents });
      get().convertAgentsToNodes(agents);
      set({ loading: false });
    } catch (error) {
      const errorMessage = error instanceof AxiosError 
        ? error.response?.data?.detail || error.message 
        : 'Failed to fetch agents';
      
      set({ 
        loading: false, 
        error: errorMessage 
      });
    }
  },
  
  // Create a new agent via API
  createAgent: async (agentData) => {
    try {
      set({ loading: true, error: null });
      const newAgent = await agentService.createAgent(agentData);
      set({ 
        agents: [...get().agents, newAgent],
        loading: false 
      });
      
      // Add the new agent as a node
      const newNode = get().addNode({
        data: { 
          label: newAgent.name,
          agentId: newAgent.id,
          agentData: newAgent
        },
        position: { 
          x: Math.random() * 300, 
          y: Math.random() * 300 
        }
      });
      
      // Close the form and select the new node
      set({ 
        isAgentFormOpen: false,
        selectedAgent: newNode
      });
      
      return newAgent;
    } catch (error) {
      const errorMessage = error instanceof AxiosError 
        ? error.response?.data?.detail || error.message 
        : 'Failed to create agent';
      
      set({ 
        loading: false, 
        error: errorMessage
      });
    }
  },
  
  // Update an agent via API
  updateAgent: async (id, agentData) => {
    try {
      set({ loading: true, error: null });
      const updatedAgent = await agentService.updateAgent(id, agentData);
      
      // Update the agents list
      set({
        agents: get().agents.map(agent => 
          agent.id === id ? updatedAgent : agent
        ),
        loading: false
      });
      
      // Update the node if it exists in the flow
      const nodeToUpdate = get().nodes.find(
        node => node.data.agentId === id
      );
      
      if (nodeToUpdate) {
        get().updateNode(nodeToUpdate.id, { 
          label: updatedAgent.name,
          agentData: updatedAgent
        });
      }
      
      return updatedAgent;
    } catch (error) {
      const errorMessage = error instanceof AxiosError 
        ? error.response?.data?.detail || error.message 
        : 'Failed to update agent';
      
      set({ 
        loading: false, 
        error: errorMessage
      });
    }
  },
  
  // Delete an agent via API
  deleteAgent: async (id) => {
    try {
      set({ loading: true, error: null });
      await agentService.deleteAgent(id);
      
      // Remove from agents list
      set({
        agents: get().agents.filter(agent => agent.id !== id),
        loading: false
      });
      
      // Remove the node if it exists in the flow
      const nodeToRemove = get().nodes.find(
        node => node.data.agentId === id
      );
      
      if (nodeToRemove) {
        get().removeNode(nodeToRemove.id);
      }
    } catch (error) {
      const errorMessage = error instanceof AxiosError 
        ? error.response?.data?.detail || error.message 
        : 'Failed to delete agent';
      
      set({ 
        loading: false, 
        error: errorMessage
      });
    }
  },
  
  // Convert API agents to flow nodes
  convertAgentsToNodes: (agents) => {
    // Create a position map - arrange agents in a circle
    const radius = 250;
    const nodeCount = agents.length;
    const nodes = agents.map((agent, index) => {
      const angle = (index / nodeCount) * 2 * Math.PI;
      const x = radius * Math.cos(angle) + 400;
      const y = radius * Math.sin(angle) + 300;
      
      return {
        id: `agent-${agent.id}`,
        type: 'agentNode',
        position: { x, y } as XYPosition,
        data: {
          label: agent.name,
          agentId: agent.id,
          agentData: agent
        }
      } as AgentNode;
    });
    
    set({ nodes });
  }
}));

export default useAgentFlowStore;
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { Agent, Client, ClientEntitlement, PeerRegistry, SearchRequest, SearchResponse, HealthStatus, Stats } from '../types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for authentication
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        } else if (error.response?.status === 403) {
          // Handle 403 errors more gracefully
          const errorMessage = error.response?.data?.error || 'Access denied';
          console.warn(`API access denied: ${errorMessage}`);
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(clientId: string, clientSecret: string): Promise<string> {
    const formData = new URLSearchParams();
    formData.append('grant_type', 'password');
    formData.append('username', clientId);
    formData.append('password', clientSecret);
    
    const response = await this.api.post('/oauth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data.access_token;
  }

  // Health checks
  async getHealth(): Promise<HealthStatus> {
    const response = await this.api.get('/health/detailed');
    return response.data;
  }

  async getStats(): Promise<Stats> {
    const response = await this.api.get('/stats');
    return response.data;
  }

  // Agents
  async getAgents(page = 1, limit = 20): Promise<SearchResponse> {
    const response = await this.api.get('/agents/public', {
      params: { page, limit },
    });
    return response.data;
  }

  async getAgent(id: string): Promise<Agent> {
    const response = await this.api.get(`/agents/${id}`);
    return response.data;
  }

  async getAgentCard(id: string): Promise<any> {
    const response = await this.api.get(`/agents/${id}/card`);
    return response.data;
  }

  async createAgent(agent: Partial<Agent>): Promise<Agent> {
    const response = await this.api.post('/agents', agent);
    return response.data;
  }

  async updateAgent(id: string, agent: Partial<Agent>): Promise<Agent> {
    const response = await this.api.put(`/agents/${id}`, agent);
    return response.data;
  }

  async deleteAgent(id: string): Promise<void> {
    await this.api.delete(`/agents/${id}`);
  }

  async searchAgents(searchRequest: SearchRequest): Promise<SearchResponse> {
    const response = await this.api.post('/agents/search', searchRequest);
    return response.data;
  }

  async getEntitledAgents(): Promise<Agent[]> {
    const response = await this.api.get('/agents/entitled');
    return response.data;
  }

  // Clients
  async getClients(): Promise<Client[]> {
    const response = await this.api.get('/clients');
    return response.data;
  }

  async getClient(id: string): Promise<Client> {
    const response = await this.api.get(`/clients/${id}`);
    return response.data;
  }

  async createClient(client: Partial<Client>): Promise<Client> {
    const response = await this.api.post('/clients', client);
    return response.data;
  }

  async updateClient(id: string, client: Partial<Client>): Promise<Client> {
    const response = await this.api.put(`/clients/${id}`, client);
    return response.data;
  }

  async deleteClient(id: string): Promise<void> {
    await this.api.delete(`/clients/${id}`);
  }

  // Client Entitlements
  async getClientEntitlements(clientId: string): Promise<ClientEntitlement[]> {
    const response = await this.api.get(`/clients/${clientId}/entitlements`);
    return response.data;
  }

  async createClientEntitlement(entitlement: Partial<ClientEntitlement>): Promise<ClientEntitlement> {
    const response = await this.api.post('/clients/entitlements', entitlement);
    return response.data;
  }

  async updateClientEntitlement(id: string, entitlement: Partial<ClientEntitlement>): Promise<ClientEntitlement> {
    const response = await this.api.put(`/clients/entitlements/${id}`, entitlement);
    return response.data;
  }

  async deleteClientEntitlement(id: string): Promise<void> {
    await this.api.delete(`/clients/entitlements/${id}`);
  }

  // Federation
  async getPeerRegistries(): Promise<PeerRegistry[]> {
    const response = await this.api.get('/peers');
    return response.data;
  }

  async getPeerRegistry(id: string): Promise<PeerRegistry> {
    const response = await this.api.get(`/peers/${id}`);
    return response.data;
  }

  async createPeerRegistry(peer: Partial<PeerRegistry>): Promise<PeerRegistry> {
    const response = await this.api.post('/peers', peer);
    return response.data;
  }

  async updatePeerRegistry(id: string, peer: Partial<PeerRegistry>): Promise<PeerRegistry> {
    const response = await this.api.put(`/peers/${id}`, peer);
    return response.data;
  }

  async deletePeerRegistry(id: string): Promise<void> {
    await this.api.delete(`/peers/${id}`);
  }

  async syncPeerRegistry(id: string): Promise<void> {
    await this.api.post(`/peers/${id}/sync`);
  }

  // Well-known endpoints
  async getAgentsIndex(): Promise<any> {
    const response = await this.api.get('/.well-known/agents/index.json');
    return response.data;
  }

  async getRegistryAgentCard(): Promise<any> {
    const response = await this.api.get('/.well-known/agent.json');
    return response.data;
  }
}

export default new ApiService();

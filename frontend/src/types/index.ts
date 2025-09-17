export interface Agent {
  id: string;
  name: string;
  description: string;
  version: string;
  provider: string;
  tags: string[];
  location_url: string;
  location_type: string;
  capabilities: AgentCapabilities;
  skills?: AgentSkills;
  auth_schemes: AuthScheme[];
  tee_details?: AgentTeeDetails;
  client_id?: string;
  created_at: string;
  updated_at: string;
}

export interface AgentCapabilities {
  a2a_version: string;
  protocols: string[];
  max_concurrent_requests: number;
  supported_formats: string[];
}

export interface AgentSkills {
  input_schema: Record<string, any>;
  output_schema: Record<string, any>;
  examples: string[];
}

export interface AuthScheme {
  type: 'api_key' | 'oauth2' | 'jwt' | 'mtls';
  description: string;
  required: boolean;
}

export interface AgentTeeDetails {
  enabled: boolean;
  provider?: string;
  attestation?: string;
}

export interface Client {
  id: string;
  name: string;
  description: string;
  client_id: string;
  client_secret: string;
  redirect_uris: string[];
  scopes: string[];
  created_at: string;
  updated_at: string;
}

export interface ClientEntitlement {
  id: string;
  client_id: string;
  agent_id: string;
  permissions: string[];
  created_at: string;
  updated_at: string;
  agent?: Agent;
}

export interface PeerRegistry {
  id: string;
  name: string;
  url: string;
  description: string;
  auth_token: string;
  sync_interval: number;
  last_sync: string;
  status: 'active' | 'inactive' | 'error';
  created_at: string;
  updated_at: string;
}

export interface SearchRequest {
  query?: string;
  filters?: {
    tags?: string[];
    capabilities?: string[];
    provider?: string;
    location_type?: string;
  };
  sort?: 'relevance' | 'name' | 'created_at' | 'updated_at';
  order?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

export interface SearchResponse {
  agents: Agent[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface ApiError {
  error: string;
  status_code: number;
  request_id?: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'user';
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

export interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'degraded';
  timestamp: number;
  components: {
    database: ServiceStatus;
    redis: ServiceStatus;
    elasticsearch: ServiceStatus;
  };
  metrics: {
    total_agents: number;
    active_agents: number;
    public_agents: number;
  };
  system: {
    cpu_percent: number;
    memory_percent: number;
    disk_percent: number;
  };
}

export interface ServiceStatus {
  status: 'healthy' | 'unhealthy';
  response_time_ms?: number;
  error?: string;
}

export interface Stats {
  total_agents: number;
  total_clients: number;
  total_peers: number;
  active_agents: number;
  recent_registrations: number;
  search_queries_today: number;
}

import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '../contexts/ThemeContext';
import { AuthProvider } from '../contexts/AuthContext';

// Create a custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
    },
  });

  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </BrowserRouter>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };

// Mock API responses
export const mockApiResponse = <T,>(data: T, delay = 0): Promise<T> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(data), delay);
  });
};

export const mockApiError = (message = 'API Error', status = 500, delay = 0): Promise<never> => {
  return new Promise((_, reject) => {
    setTimeout(() => {
      const error = new Error(message) as any;
      error.response = { status, data: { message } };
      reject(error);
    }, delay);
  });
};

// Mock data factories
export const mockAgent = (overrides = {}) => ({
  id: 'test-agent-1',
  name: 'Test Agent',
  description: 'A test agent for testing purposes',
  version: '1.0.0',
  author: 'Test Author',
  tags: ['test', 'demo'],
  capabilities: {
    protocols: ['http', 'websocket'],
    supported_formats: ['json', 'xml'],
  },
  auth_schemes: [
    {
      type: 'oauth2',
      description: 'OAuth 2.0 authentication',
    },
  ],
  status: 'active' as const,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  ...overrides,
});

export const mockClient = (overrides = {}) => ({
  id: 'test-client-1',
  name: 'Test Client',
  description: 'A test client for testing purposes',
  client_id: 'test-client-id',
  scopes: ['agent:read', 'agent:write'],
  is_active: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  ...overrides,
});

export const mockStats = (overrides = {}) => ({
  total_agents: 10,
  active_agents: 8,
  total_clients: 5,
  active_clients: 4,
  total_peers: 2,
  ...overrides,
});

export const mockHealthStatus = (overrides = {}) => ({
  status: 'healthy' as const,
  timestamp: Date.now() / 1000,
  components: {
    database: { status: 'healthy' as const, response_time_ms: 10 },
    redis: { status: 'healthy' as const, response_time_ms: 5 },
    elasticsearch: { status: 'healthy' as const, response_time_ms: 15 },
  },
  metrics: {
    total_agents: 10,
    active_agents: 8,
    public_agents: 6,
  },
  system: {
    cpu_percent: 25.5,
    memory_percent: 45.2,
    disk_percent: 60.1,
  },
  ...overrides,
});

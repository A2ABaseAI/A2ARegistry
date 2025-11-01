/**
 * Tests for A2ARegClient
 */

import { A2ARegClient } from '../src/client';
import { agentFromDict } from '../src/models';
import { A2AError, AuthenticationError, ValidationError, NotFoundError } from '../src/exceptions';

// Mock fetch globally
(global as any).fetch = jest.fn();

describe('A2ARegClient', () => {
  let client: A2ARegClient;
  const mockFetch = (global as any).fetch as jest.Mock;

  beforeEach(() => {
    client = new A2ARegClient({
      registryUrl: 'https://registry.example.com',
      apiKey: 'test-api-key',
    });
    mockFetch.mockClear();
    // Reset fetch mock
    (global as any).fetch = mockFetch;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Initialization', () => {
    it('should initialize with default values', () => {
      const defaultClient = new A2ARegClient();
      expect(defaultClient).toBeInstanceOf(A2ARegClient);
    });

    it('should initialize with custom options', () => {
      const customClient = new A2ARegClient({
        registryUrl: 'https://custom.example.com',
        clientId: 'client-id',
        clientSecret: 'client-secret',
        timeout: 60,
        scope: 'read write admin',
      });
      expect(customClient).toBeInstanceOf(A2ARegClient);
    });

    it('should set API key', () => {
      client.setApiKey('new-api-key');
      expect(client).toBeInstanceOf(A2ARegClient);
    });
  });

  describe('Authentication', () => {
    it('should authenticate with API key (skip OAuth)', async () => {
      const apiKeyClient = new A2ARegClient({
        registryUrl: 'https://registry.example.com',
        apiKey: 'test-key',
      });

      await apiKeyClient.authenticate();
      // Should not make any fetch calls since API key is set
      expect(mockFetch).not.toHaveBeenCalled();
    });

    it('should authenticate with OAuth', async () => {
      const oauthClient = new A2ARegClient({
        registryUrl: 'https://registry.example.com',
        clientId: 'test-client',
        clientSecret: 'test-secret',
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'test-token',
          expires_in: 3600,
        }),
      });

      await oauthClient.authenticate();
      expect(mockFetch).toHaveBeenCalledWith(
        'https://registry.example.com/auth/oauth/token',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    it('should throw AuthenticationError on OAuth failure', async () => {
      const oauthClient = new A2ARegClient({
        registryUrl: 'https://registry.example.com',
        clientId: 'test-client',
        clientSecret: 'test-secret',
      });

      mockFetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Unauthorized',
      });

      await expect(oauthClient.authenticate()).rejects.toThrow(AuthenticationError);
    });

    it('should throw error when client credentials missing', async () => {
      const noCredsClient = new A2ARegClient({
        registryUrl: 'https://registry.example.com',
      });

      await expect(noCredsClient.authenticate()).rejects.toThrow(AuthenticationError);
    });
  });

  describe('Health', () => {
    it('should get health status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'healthy', version: '1.0.0' }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const health = await client.getHealth();
      expect(health).toEqual({ status: 'healthy', version: '1.0.0' });
      expect(mockFetch).toHaveBeenCalledWith(
        'https://registry.example.com/health',
        expect.any(Object)
      );
    });
  });

  describe('Agents', () => {
    it('should list public agents', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          agents: [{ id: 'agent-1', name: 'Test Agent' }],
          total: 1,
          page: 1,
          limit: 20,
        }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const result = await client.listAgents(1, 20, true);
      expect(result.agents).toHaveLength(1);
      expect(result.agents[0].id).toBe('agent-1');
    });

    it('should list entitled agents', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          agents: [{ id: 'agent-2', name: 'Private Agent' }],
          total: 1,
          page: 1,
          limit: 20,
        }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const result = await client.listAgents(1, 20, false);
      expect(result.agents).toHaveLength(1);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/agents/entitled'),
        expect.any(Object)
      );
    });

    it('should get agent by ID', async () => {
      const agentData = {
        id: 'agent-1',
        name: 'Test Agent',
        description: 'A test agent',
        version: '1.0.0',
        provider: 'test-provider',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => agentData,
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const agent = await client.getAgent('agent-1');
      expect(agent.id).toBe('agent-1');
      expect(agent.name).toBe('Test Agent');
    });

    it('should throw NotFoundError when agent not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await expect(client.getAgent('nonexistent')).rejects.toThrow(NotFoundError);
    });

    it('should get agent card', async () => {
      const cardData = {
        name: 'Test Agent',
        description: 'A test agent',
        url: 'https://test.example.com',
        version: '1.0.0',
        capabilities: { streaming: false },
        securitySchemes: [{ type: 'apiKey' }],
        skills: [],
        interface: {
          preferredTransport: 'jsonrpc',
          defaultInputModes: ['text/plain'],
          defaultOutputModes: ['text/plain'],
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => cardData,
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const card = await client.getAgentCard('agent-1');
      expect(card.name).toBe('Test Agent');
      expect(card.version).toBe('1.0.0');
    });
  });

  describe('Search', () => {
    it('should search agents', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          agents: [{ id: 'agent-1', name: 'Recipe Agent' }],
          total: 1,
          page: 1,
          limit: 20,
        }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const results = await client.searchAgents('recipe', { tags: ['cooking'] });
      expect(results.agents).toHaveLength(1);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/agents/search'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            query: 'recipe',
            filters: { tags: ['cooking'] },
            semantic: false,
            page: 1,
            limit: 20,
          }),
        })
      );
    });

    it('should search with semantic search', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ agents: [], total: 0 }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await client.searchAgents('recipe', undefined, true);
      const callArgs = (mockFetch.mock.calls[0][1] as any).body;
      const body = JSON.parse(callArgs);
      expect(body.semantic).toBe(true);
    });
  });

  describe('Publish Agent', () => {
    it('should publish agent successfully', async () => {
      const agentData = {
        name: 'New Agent',
        description: 'A new agent',
        version: '1.0.0',
        provider: 'test-provider',
        location_url: 'https://api.example.com/agent',
        is_public: true,
      };

      // Mock publish response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ agentId: 'agent-123' }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      // Mock get agent response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...agentData, id: 'agent-123' }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const published = await client.publishAgent(agentData);
      expect(published.id).toBe('agent-123');
      expect(published.name).toBe('New Agent');
    });

    it('should publish agent with validation', async () => {
      const validAgent = {
        name: 'Valid Agent',
        description: 'A valid agent',
        version: '1.0.0',
        provider: 'test-provider',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ agentId: 'agent-123' }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...validAgent, id: 'agent-123' }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const published = await client.publishAgent(validAgent, true);
      expect(published).toBeDefined();
    });

    it('should throw ValidationError on invalid agent', async () => {
      const invalidAgent = {
        name: '',
        description: 'Missing name',
        version: '1.0.0',
        provider: 'test-provider',
      };

      await expect(client.publishAgent(invalidAgent, true)).rejects.toThrow(ValidationError);
    });
  });

  describe('Update Agent', () => {
    it('should update agent', async () => {
      const updatedData = {
        name: 'Updated Agent',
        description: 'Updated description',
        version: '1.1.0',
        provider: 'test-provider',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...updatedData, id: 'agent-1' }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const updated = await client.updateAgent('agent-1', updatedData);
      expect(updated.name).toBe('Updated Agent');
      expect(updated.version).toBe('1.1.0');
    });
  });

  describe('Delete Agent', () => {
    it('should delete agent', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await client.deleteAgent('agent-1');
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/agents/agent-1'),
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });
  });

  describe('Validate Agent', () => {
    it('should validate valid agent', () => {
      const validAgent = agentFromDict({
        name: 'Valid Agent',
        description: 'A valid agent',
        version: '1.0.0',
        provider: 'test-provider',
      });

      const errors = client.validateAgent(validAgent);
      expect(errors).toHaveLength(0);
    });

    it('should return errors for invalid agent', () => {
      const invalidAgent = agentFromDict({
        name: '',
        description: 'Missing name',
        version: '1.0.0',
        provider: 'test-provider',
      });

      const errors = client.validateAgent(invalidAgent);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors.some((e) => e.includes('name is required'))).toBe(true);
    });

    it('should validate agent card if present', () => {
      const agent = agentFromDict({
        name: 'Test Agent',
        description: 'A test agent',
        version: '1.0.0',
        provider: 'test-provider',
        agent_card: {
          name: '',
          description: 'Missing card name',
          version: '1.0.0',
          url: 'https://test.com',
          capabilities: {},
          securitySchemes: [],
          skills: [],
          interface: {
            preferredTransport: 'jsonrpc',
            defaultInputModes: ['text/plain'],
            defaultOutputModes: ['text/plain'],
          },
        },
      });

      const errors = client.validateAgent(agent);
      expect(errors.some((e) => e.includes('Agent card name is required'))).toBe(true);
    });
  });

  describe('API Key Management', () => {
    it('should generate API key', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          api_key: 'generated-key',
          key_id: 'key-123',
          scopes: ['read', 'write'],
          created_at: '2024-01-01T00:00:00Z',
        }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const result = await client.generateApiKey(['read', 'write'], 30);
      expect(result.apiKey).toBe('generated-key');
      expect(result.keyInfo.key_id).toBe('key-123');
    });

    it('should generate and authenticate with API key', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          api_key: 'new-key',
          key_id: 'key-456',
          scopes: ['read'],
          created_at: '2024-01-01T00:00:00Z',
        }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const result = await client.generateApiKeyAndAuthenticate(['read']);
      expect(result.apiKey).toBe('new-key');
    });

    it('should validate API key', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          key_id: 'key-123',
          scopes: ['read', 'write'],
          active: true,
        }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const result = await client.validateApiKey('test-key', ['read']);
      expect(result).toBeDefined();
      expect(result?.key_id).toBe('key-123');
    });

    it('should return null for invalid API key', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const result = await client.validateApiKey('invalid-key');
      expect(result).toBeNull();
    });

    it('should revoke API key', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const result = await client.revokeApiKey('key-123');
      expect(result).toBe(true);
    });

    it('should return false when revoking nonexistent key', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const result = await client.revokeApiKey('nonexistent-key');
      expect(result).toBe(false);
    });

    it('should list API keys', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [
          {
            key_id: 'key-1',
            scopes: ['read'],
            created_at: '2024-01-01T00:00:00Z',
          },
        ],
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const keys = await client.listApiKeys(true);
      expect(Array.isArray(keys)).toBe(true);
      expect(keys.length).toBeGreaterThan(0);
    });
  });

  describe('Error Handling', () => {
    it('should throw AuthenticationError on 401', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await expect(client.getAgent('agent-1')).rejects.toThrow(AuthenticationError);
    });

    it('should throw AuthenticationError on 403', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        statusText: 'Forbidden',
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await expect(client.getAgent('agent-1')).rejects.toThrow(AuthenticationError);
    });

    it('should throw ValidationError on 422', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        statusText: 'Unprocessable Entity',
        json: async () => ({ detail: 'Validation failed' }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await expect(client.publishAgent({} as any)).rejects.toThrow(ValidationError);
    });

    it('should throw A2AError on generic errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await expect(client.getAgent('agent-1')).rejects.toThrow(A2AError);
    });

    it('should handle request timeout', async () => {
      const timeoutClient = new A2ARegClient({
        registryUrl: 'https://registry.example.com',
        apiKey: 'test-key',
        timeout: 1,
      });

      // Mock AbortController to simulate timeout
      const originalAbortController = global.AbortController;
      (global as any).AbortController = jest.fn().mockImplementation(() => {
        const controller = new originalAbortController();
        const originalAbort = controller.abort.bind(controller);
        // Immediately abort to simulate timeout
        setTimeout(() => originalAbort(), 0);
        return controller;
      });

      mockFetch.mockImplementationOnce(() => {
        return new Promise((_resolve, reject) => {
          setTimeout(() => {
            const error = new Error('The operation was aborted');
            (error as any).name = 'AbortError';
            reject(error);
          }, 10);
        });
      });

      await expect(timeoutClient.getHealth()).rejects.toThrow(A2AError);

      // Restore original
      (global as any).AbortController = originalAbortController;
    });
  });

  describe('Registry Stats', () => {
    it('should get registry stats', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          total_agents: 100,
          public_agents: 80,
          private_agents: 20,
        }),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const stats = await client.getRegistryStats();
      expect(stats.total_agents).toBe(100);
    });
  });
});


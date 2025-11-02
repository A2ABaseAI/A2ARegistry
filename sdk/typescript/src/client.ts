/**
 * A2A Registry Client
 *
 * Main client class for interacting with the A2A Agent Registry.
 */

// Using native fetch (Node 18+) - for older versions, use node-fetch
// import fetch from 'node-fetch';

import {
  Agent,
  AgentCardSpec,
  AgentCapabilities,
  SecurityScheme,
  agentFromDict,
  agentCardSpecFromDict,
} from './models';
import { A2AError, AuthenticationError, ValidationError, NotFoundError } from './exceptions';

export interface A2ARegClientOptions {
  registryUrl?: string;
  clientId?: string;
  clientSecret?: string;
  timeout?: number;
  apiKey?: string;
  apiKeyHeader?: string;
  scope?: string;
}

export class A2ARegClient {
  private registryUrl: string;
  private clientId?: string;
  private clientSecret?: string;
  private timeout: number;
  private accessToken?: string;
  private tokenExpiresAt?: number;
  private apiKey?: string;
  private scope: string;

  constructor(options: A2ARegClientOptions = {}) {
    this.registryUrl = (options.registryUrl || 'http://localhost:8000').replace(/\/$/, '');
    this.clientId = options.clientId;
    this.clientSecret = options.clientSecret;
    this.timeout = options.timeout || 30000;
    this.apiKey = options.apiKey;
    this.scope = options.scope || 'read write';
  }

  /**
   * Set API key for authentication
   */
  setApiKey(apiKey: string): void {
    this.apiKey = apiKey;
  }

  /**
   * Authenticate with the A2A registry using OAuth 2.0 client credentials flow.
   */
  async authenticate(scope?: string): Promise<void> {
    // If API key auth is configured, skip OAuth flow
    if (this.apiKey) {
      return;
    }

    if (!this.clientId || !this.clientSecret) {
      throw new AuthenticationError('Client ID and secret are required for authentication');
    }

    const authScope = scope || this.scope;

    try {
      const formData = new URLSearchParams();
      formData.append('grant_type', 'client_credentials');
      formData.append('client_id', this.clientId!);
      formData.append('client_secret', this.clientSecret!);
      formData.append('scope', authScope);

      const response = await fetch(`${this.registryUrl}/auth/oauth/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        throw new AuthenticationError(`Authentication failed: ${response.statusText}`);
      }

      const tokenData = await response.json();
      this.accessToken = tokenData.access_token;
      const expiresIn = tokenData.expires_in || 3600;
      this.tokenExpiresAt = Date.now() / 1000 + expiresIn - 60; // Refresh 1 minute early

      if (!this.accessToken) {
        throw new AuthenticationError('No access token received');
      }
    } catch (error: any) {
      if (error instanceof AuthenticationError) {
        throw error;
      }
      throw new AuthenticationError(`Authentication failed: ${error.message}`);
    }
  }

  private async ensureAuthenticated(): Promise<void> {
    // If API key is configured, no token is required
    if (this.apiKey) {
      return;
    }

    if (!this.accessToken) {
      await this.authenticate(this.scope);
    } else if (this.tokenExpiresAt && Date.now() / 1000 >= this.tokenExpiresAt) {
      await this.authenticate(this.scope);
    }
  }

  private async request(
    method: string,
    endpoint: string,
    options: {
      body?: any;
      params?: Record<string, any>;
      headers?: Record<string, string>;
    } = {}
  ): Promise<any> {
    await this.ensureAuthenticated();

    const url = new URL(`${this.registryUrl}${endpoint}`);
    if (options.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'User-Agent': 'A2A-TypeScript-SDK/1.0.0',
      ...options.headers,
    };

    // Set authentication header
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    } else if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url.toString(), {
        method,
        headers,
        body: options.body ? JSON.stringify(options.body) : undefined,
        signal: controller.signal as any,
      }) as any;

      clearTimeout(timeoutId);

      return this.handleResponse(response);
    } catch (error: any) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new A2AError(`Request timeout after ${this.timeout}ms`);
      }
      throw new A2AError(`Request failed: ${error.message}`);
    }
  }

  private async handleResponse(response: any): Promise<any> {
    const contentType = response.headers.get('content-type');
    const hasContent = contentType?.includes('application/json');

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      if (hasContent) {
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // Ignore JSON parse errors
        }
      }

      if (response.status === 401) {
        throw new AuthenticationError('Authentication required or token expired');
      } else if (response.status === 403) {
        throw new AuthenticationError('Access denied');
      } else if (response.status === 404) {
        throw new NotFoundError('Resource not found');
      } else if (response.status === 422) {
        throw new ValidationError(`Validation error: ${errorMessage}`);
      } else {
        throw new A2AError(`API error: ${errorMessage}`);
      }
    }

    if (hasContent) {
      try {
        return await response.json();
      } catch {
        return null;
      }
    }

    return null;
  }

  private convertToCardSpec(agent: Agent | Record<string, any>): Record<string, any> {
    const agentDict = typeof agent === 'object' && 'to_dict' in agent ? (agent as any).to_dict() : agent;

    // Extract capabilities
    const capabilities = agentDict.capabilities || {};
    const cardCapabilities: AgentCapabilities = {
      streaming: capabilities.streaming || false,
      pushNotifications: capabilities.pushNotifications || false,
      stateTransitionHistory: capabilities.stateTransitionHistory || false,
      supportsAuthenticatedExtendedCard: capabilities.supportsAuthenticatedExtendedCard || false,
    };

    // Convert auth schemes to security schemes (as dict for ADK compatibility)
    const securitySchemes: Record<string, SecurityScheme> = {};
    for (const scheme of (agentDict.auth_schemes || [])) {
      const schemeType = scheme.type || 'apiKey';
      securitySchemes[schemeType] = {
        type: schemeType,
        location: 'header',
        name: scheme.name || 'Authorization',
      };
    }

    // Convert skills
    const skills: any[] = [];
    const agentSkills = agentDict.skills;
    if (agentSkills) {
      if (Array.isArray(agentSkills)) {
        skills.push(...agentSkills);
      } else if (typeof agentSkills === 'object' && agentSkills.examples) {
        skills.push({
          id: 'main_skill',
          name: 'Main Skill',
          description: agentDict.description || 'Agent skill',
          tags: agentDict.tags || [],
          examples: agentSkills.examples,
          inputModes: ['text/plain'],
          outputModes: ['text/plain'],
        });
      }
    }

    // Build interface
    const interface_: Record<string, any> = {
      preferredTransport: 'jsonrpc',
      defaultInputModes: ['text/plain'],
      defaultOutputModes: ['text/plain'],
    };

    if (agentDict.location_url) {
      interface_.additionalInterfaces = [{ transport: 'http', url: agentDict.location_url }];
    }

    // Build the card spec
    const cardSpec: Record<string, any> = {
      name: agentDict.name || 'Unnamed Agent',
      description: agentDict.description || 'Agent description',
      url: agentDict.location_url || 'https://example.com',
      version: agentDict.version || '1.0.0',
      capabilities: cardCapabilities,
      securitySchemes: securitySchemes,
      skills: skills,
      interface: interface_,
      // Add top-level defaultInputModes and defaultOutputModes for ADK compatibility
      defaultInputModes: interface_.defaultInputModes,
      defaultOutputModes: interface_.defaultOutputModes,
    };

    // Add provider if available
    if (agentDict.provider) {
      cardSpec.provider = {
        organization: agentDict.provider,
        url: agentDict.location_url || 'https://example.com',
      };
    }

    return cardSpec;
  }

  /**
   * Get registry health status
   */
  async getHealth(): Promise<Record<string, any>> {
    return this.request('GET', '/health');
  }

  /**
   * List agents from the registry
   */
  async listAgents(page: number = 1, limit: number = 20, publicOnly: boolean = true): Promise<Record<string, any>> {
    const endpoint = publicOnly ? '/agents/public' : '/agents/entitled';
    return this.request('GET', endpoint, { params: { page, limit } });
  }

  /**
   * Get a specific agent by ID
   */
  async getAgent(agentId: string): Promise<Agent> {
    const data = await this.request('GET', `/agents/${agentId}`);
    return agentFromDict(data);
  }

  /**
   * Get an agent's card (detailed metadata)
   */
  async getAgentCard(agentId: string): Promise<AgentCardSpec> {
    const data = await this.request('GET', `/agents/${agentId}/card`);
    return agentCardSpecFromDict(data);
  }

  /**
   * Search for agents in the registry
   */
  async searchAgents(
    query?: string,
    filters?: Record<string, any>,
    semantic: boolean = false,
    page: number = 1,
    limit: number = 20
  ): Promise<Record<string, any>> {
    return this.request('POST', '/agents/search', {
      body: {
        query,
        filters: filters || {},
        semantic,
        page,
        limit,
      },
    });
  }

  /**
   * Get registry statistics
   */
  async getRegistryStats(): Promise<Record<string, any>> {
    return this.request('GET', '/stats');
  }

  /**
   * Validate an agent configuration
   */
  validateAgent(agent: Agent | Record<string, any>): string[] {
    const agentObj = typeof agent === 'object' && 'name' in agent ? agent as Agent : agentFromDict(agent as Record<string, any>);
    const errors: string[] = [];

    if (!agentObj.name) {
      errors.push('Agent name is required');
    }
    if (!agentObj.description) {
      errors.push('Agent description is required');
    }
    if (!agentObj.version) {
      errors.push('Agent version is required');
    }
    if (!agentObj.provider) {
      errors.push('Agent provider is required');
    }

    // Validate auth schemes
    if (agentObj.auth_schemes) {
      agentObj.auth_schemes.forEach((scheme, i) => {
        if (!scheme.type) {
          errors.push(`Auth scheme ${i} missing required field: type`);
        }
        const validTypes = ['apiKey', 'oauth2', 'jwt', 'mTLS', 'bearer'];
        if (scheme.type && !validTypes.includes(scheme.type)) {
          errors.push(`Auth scheme ${i} has invalid type: ${scheme.type}`);
        }
      });
    }

    // Validate agent card if present
    if (agentObj.agent_card) {
      if (!agentObj.agent_card.name) {
        errors.push('Agent card name is required');
      }
      if (!agentObj.agent_card.description) {
        errors.push('Agent card description is required');
      }
      if (!agentObj.agent_card.version) {
        errors.push('Agent card version is required');
      }
    }

    return errors;
  }

  /**
   * Publish a new agent to the registry
   */
  async publishAgent(agentData: Agent | Record<string, any>, validate: boolean = false): Promise<Agent> {
    const agent = typeof agentData === 'object' && 'name' in agentData ? agentData : agentFromDict(agentData);

    // Validate if requested
    if (validate) {
      const errors = this.validateAgent(agent);
      if (errors.length > 0) {
        throw new ValidationError(`Agent validation failed: ${errors.join('; ')}`);
      }
    }

    // Convert Agent model to AgentCardSpec format
    const cardData = this.convertToCardSpec(agent);

    const agentDict = typeof agent === 'object' && 'to_dict' in agent ? (agent as any).to_dict() : agent;

    // Format the request body according to the API spec
    const requestBody = {
      public: agentDict.is_public !== undefined ? agentDict.is_public : true,
      card: cardData,
    };

    const publishedData = await this.request('POST', '/agents/publish', { body: requestBody });

    // The API returns a different format, so we need to fetch the full agent data
    if (publishedData.agentId) {
      const agentId = publishedData.agentId;
      return this.getAgent(agentId);
    } else {
      return agentFromDict(publishedData);
    }
  }

  /**
   * Update an existing agent
   */
  async updateAgent(agentId: string, agentData: Agent | Record<string, any>): Promise<Agent> {
    const agentDict =
      typeof agentData === 'object' && 'to_dict' in agentData
        ? (agentData as any).to_dict()
        : typeof agentData === 'object'
        ? agentData
        : agentFromDict(agentData);

    const data = await this.request('PUT', `/agents/${agentId}`, { body: agentDict });
    return agentFromDict(data);
  }

  /**
   * Delete an agent from the registry
   */
  async deleteAgent(agentId: string): Promise<void> {
    await this.request('DELETE', `/agents/${agentId}`);
  }

  /**
   * Get registry statistics (alias for getRegistryStats)
   */
  async getStats(): Promise<Record<string, any>> {
    return this.getRegistryStats();
  }

  /**
   * Generate a new API key using the backend security service
   */
  async generateApiKey(scopes: string[], expiresDays?: number): Promise<{ apiKey: string; keyInfo: Record<string, any> }> {
    const response = await this.request('POST', '/security/api-keys', {
      body: {
        scopes,
        expires_days: expiresDays,
      },
    });

    return {
      apiKey: response.api_key,
      keyInfo: {
        key_id: response.key_id,
        scopes: response.scopes,
        created_at: response.created_at,
        expires_at: response.expires_at,
      },
    };
  }

  /**
   * Generate a new API key and automatically authenticate the client with it
   */
  async generateApiKeyAndAuthenticate(scopes: string[], expiresDays?: number): Promise<{ apiKey: string; keyInfo: Record<string, any> }> {
    const { apiKey, keyInfo } = await this.generateApiKey(scopes, expiresDays);
    this.setApiKey(apiKey);
    return { apiKey, keyInfo };
  }

  /**
   * Validate an API key using the backend security service
   */
  async validateApiKey(apiKey: string, requiredScopes?: string[]): Promise<Record<string, any> | null> {
    try {
      const response = await this.request('POST', '/security/api-keys/validate', {
        body: {
          api_key: apiKey,
          required_scopes: requiredScopes,
        },
      });
      return response;
    } catch (error) {
      if (error instanceof AuthenticationError) {
        return null;
      }
      return null;
    }
  }

  /**
   * Revoke an API key using the backend security service
   */
  async revokeApiKey(keyId: string): Promise<boolean> {
    try {
      await this.request('DELETE', `/security/api-keys/${keyId}`);
      return true;
    } catch (error) {
      if (error instanceof NotFoundError) {
        return false;
      }
      return false;
    }
  }

  /**
   * List all API keys using the backend security service
   */
  async listApiKeys(activeOnly: boolean = true): Promise<Record<string, any>[]> {
    return this.request('GET', '/security/api-keys', { params: { active_only: activeOnly } });
  }
}


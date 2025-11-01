/**
 * Tests for models and helper functions
 */

import {
  agentFromDict,
  capabilitiesFromDict,
  securitySchemeFromDict,
  agentSkillFromDict,
  agentCardSpecFromDict,
  agentProviderFromDict,
  teeDetailsFromDict,
  agentCardSignatureFromDict,
} from '../src/models';

describe('Models', () => {
  describe('agentFromDict', () => {
    it('should create agent from dictionary', () => {
      const data = {
        id: 'agent-1',
        name: 'Test Agent',
        description: 'A test agent',
        version: '1.0.0',
        provider: 'test-provider',
        tags: ['ai', 'assistant'],
        is_public: true,
        is_active: true,
      };

      const agent = agentFromDict(data);
      expect(agent.id).toBe('agent-1');
      expect(agent.name).toBe('Test Agent');
      expect(agent.description).toBe('A test agent');
      expect(agent.version).toBe('1.0.0');
      expect(agent.provider).toBe('test-provider');
      expect(agent.tags).toEqual(['ai', 'assistant']);
      expect(agent.is_public).toBe(true);
    });

    it('should handle missing optional fields', () => {
      const data = {
        name: 'Test Agent',
        description: 'A test agent',
        version: '1.0.0',
        provider: 'test-provider',
      };

      const agent = agentFromDict(data);
      expect(agent.id).toBeUndefined();
      expect(agent.tags).toEqual([]);
      expect(agent.is_public).toBe(true);
    });

    it('should handle agentId as id', () => {
      const data = {
        agentId: 'agent-123',
        name: 'Test Agent',
        description: 'A test agent',
        version: '1.0.0',
        provider: 'test-provider',
      };

      const agent = agentFromDict(data);
      expect(agent.id).toBe('agent-123');
    });

    it('should handle capabilities', () => {
      const data = {
        name: 'Test Agent',
        description: 'A test agent',
        version: '1.0.0',
        provider: 'test-provider',
        capabilities: {
          streaming: true,
          pushNotifications: false,
        },
      };

      const agent = agentFromDict(data);
      expect(agent.capabilities).toBeDefined();
      expect(agent.capabilities?.streaming).toBe(true);
    });

    it('should handle auth_schemes', () => {
      const data = {
        name: 'Test Agent',
        description: 'A test agent',
        version: '1.0.0',
        provider: 'test-provider',
        auth_schemes: [
          {
            type: 'apiKey',
            location: 'header',
            name: 'X-API-Key',
          },
        ],
      };

      const agent = agentFromDict(data);
      expect(agent.auth_schemes).toHaveLength(1);
      expect(agent.auth_schemes?.[0].type).toBe('apiKey');
    });

    it('should handle skills', () => {
      const data = {
        name: 'Test Agent',
        description: 'A test agent',
        version: '1.0.0',
        provider: 'test-provider',
        skills: [
          {
            id: 'skill-1',
            name: 'Main Skill',
            description: 'Primary skill',
            tags: ['ai'],
          },
        ],
      };

      const agent = agentFromDict(data);
      expect(agent.skills).toHaveLength(1);
      expect(agent.skills?.[0].id).toBe('skill-1');
    });

    it('should handle agent_card', () => {
      const data = {
        name: 'Test Agent',
        description: 'A test agent',
        version: '1.0.0',
        provider: 'test-provider',
        agent_card: {
          name: 'Test Agent Card',
          description: 'Card description',
          url: 'https://test.com',
          version: '1.0.0',
          capabilities: {},
          securitySchemes: [],
          skills: [],
          interface: {
            preferredTransport: 'jsonrpc',
            defaultInputModes: ['text/plain'],
            defaultOutputModes: ['text/plain'],
          },
        },
      };

      const agent = agentFromDict(data);
      expect(agent.agent_card).toBeDefined();
      expect(agent.agent_card?.name).toBe('Test Agent Card');
    });
  });

  describe('capabilitiesFromDict', () => {
    it('should create capabilities from dictionary', () => {
      const data = {
        streaming: true,
        pushNotifications: false,
        stateTransitionHistory: true,
        supportsAuthenticatedExtendedCard: false,
      };

      const capabilities = capabilitiesFromDict(data);
      expect(capabilities.streaming).toBe(true);
      expect(capabilities.pushNotifications).toBe(false);
      expect(capabilities.stateTransitionHistory).toBe(true);
    });
  });

  describe('securitySchemeFromDict', () => {
    it('should create security scheme from dictionary', () => {
      const data = {
        type: 'oauth2',
        location: 'header',
        name: 'Authorization',
        flow: 'client_credentials',
        tokenUrl: 'https://auth.example.com/token',
        scopes: ['read', 'write'],
      };

      const scheme = securitySchemeFromDict(data);
      expect(scheme.type).toBe('oauth2');
      expect(scheme.location).toBe('header');
      expect(scheme.scopes).toEqual(['read', 'write']);
    });

    it('should handle token_url alias', () => {
      const data = {
        type: 'oauth2',
        token_url: 'https://auth.example.com/token',
      };

      const scheme = securitySchemeFromDict(data);
      expect(scheme.tokenUrl).toBe('https://auth.example.com/token');
    });
  });

  describe('agentSkillFromDict', () => {
    it('should create agent skill from dictionary', () => {
      const data = {
        id: 'skill-1',
        name: 'Main Skill',
        description: 'Primary skill',
        tags: ['ai', 'assistant'],
        examples: ['Example 1'],
        inputModes: ['text/plain'],
        outputModes: ['application/json'],
      };

      const skill = agentSkillFromDict(data);
      expect(skill.id).toBe('skill-1');
      expect(skill.name).toBe('Main Skill');
      expect(skill.tags).toEqual(['ai', 'assistant']);
      expect(skill.examples).toEqual(['Example 1']);
    });

    it('should handle input_modes alias', () => {
      const data = {
        id: 'skill-1',
        name: 'Main Skill',
        description: 'Primary skill',
        tags: [],
        input_modes: ['text/plain'],
        output_modes: ['application/json'],
      };

      const skill = agentSkillFromDict(data);
      expect(skill.inputModes).toEqual(['text/plain']);
      expect(skill.outputModes).toEqual(['application/json']);
    });
  });

  describe('agentCardSpecFromDict', () => {
    it('should create agent card spec from dictionary', () => {
      const data = {
        name: 'Test Agent Card',
        description: 'Card description',
        url: 'https://test.com',
        version: '1.0.0',
        capabilities: {
          streaming: false,
        },
        securitySchemes: [
          {
            type: 'apiKey',
            location: 'header',
            name: 'X-API-Key',
          },
        ],
        skills: [
          {
            id: 'skill-1',
            name: 'Main Skill',
            description: 'Primary skill',
            tags: [],
          },
        ],
        interface: {
          preferredTransport: 'jsonrpc',
          defaultInputModes: ['text/plain'],
          defaultOutputModes: ['text/plain'],
        },
        provider: {
          organization: 'Test Org',
          url: 'https://test.org',
        },
      };

      const card = agentCardSpecFromDict(data);
      expect(card.name).toBe('Test Agent Card');
      expect(card.securitySchemes).toHaveLength(1);
      expect(card.skills).toHaveLength(1);
      expect(card.provider?.organization).toBe('Test Org');
    });
  });

  describe('agentProviderFromDict', () => {
    it('should create agent provider from dictionary', () => {
      const data = {
        organization: 'Test Org',
        url: 'https://test.org',
      };

      const provider = agentProviderFromDict(data);
      expect(provider.organization).toBe('Test Org');
      expect(provider.url).toBe('https://test.org');
    });
  });

  describe('teeDetailsFromDict', () => {
    it('should create TEE details from dictionary', () => {
      const data = {
        enabled: true,
        provider: 'Intel SGX',
        attestation: 'required',
      };

      const teeDetails = teeDetailsFromDict(data);
      expect(teeDetails.enabled).toBe(true);
      expect(teeDetails.provider).toBe('Intel SGX');
      expect(teeDetails.attestation).toBe('required');
    });

    it('should default enabled to false', () => {
      const data = {};
      const teeDetails = teeDetailsFromDict(data);
      expect(teeDetails.enabled).toBe(false);
    });
  });

  describe('agentCardSignatureFromDict', () => {
    it('should create agent card signature from dictionary', () => {
      const data = {
        algorithm: 'RS256',
        signature: 'abc123',
        jwksUrl: 'https://example.com/.well-known/jwks.json',
      };

      const signature = agentCardSignatureFromDict(data);
      expect(signature.algorithm).toBe('RS256');
      expect(signature.signature).toBe('abc123');
      expect(signature.jwksUrl).toBe('https://example.com/.well-known/jwks.json');
    });

    it('should handle jwks_url alias', () => {
      const data = {
        algorithm: 'RS256',
        jwks_url: 'https://example.com/.well-known/jwks.json',
      };

      const signature = agentCardSignatureFromDict(data);
      expect(signature.jwksUrl).toBe('https://example.com/.well-known/jwks.json');
    });
  });
});


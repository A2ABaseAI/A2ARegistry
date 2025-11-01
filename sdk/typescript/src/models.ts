/**
 * A2A Registry Data Models
 *
 * Data models for A2A agents and related entities following the A2A Protocol specification.
 * This module implements the Agent Card schema as defined in Section 5.5 of the A2A Protocol.
 *
 * Reference: https://a2a-protocol.org/dev/specification/#355-extension-method-naming
 */

// A2A Protocol specification models

export interface AgentProvider {
  organization: string;
  url: string;
}

export interface AgentCapabilities {
  streaming?: boolean;
  pushNotifications?: boolean;
  stateTransitionHistory?: boolean;
  supportsAuthenticatedExtendedCard?: boolean;
}

export interface SecurityScheme {
  type: string; // apiKey, oauth2, jwt, mTLS
  location?: string; // header, query, body
  name?: string; // Parameter name for credentials
  flow?: string; // OAuth2 flow type
  tokenUrl?: string; // OAuth2 token URL
  scopes?: string[]; // OAuth2 scopes
  credentials?: string; // Credentials for private Cards
}

export interface AgentTeeDetails {
  enabled: boolean;
  provider?: string;
  attestation?: string;
}

export interface AgentSkill {
  id: string;
  name: string;
  description: string;
  tags: string[];
  examples?: string[];
  inputModes?: string[];
  outputModes?: string[];
}

export interface AgentInterface {
  preferredTransport: string; // jsonrpc, grpc, http
  defaultInputModes: string[];
  defaultOutputModes: string[];
  additionalInterfaces?: Array<Record<string, any>>;
}

export interface AgentCardSignature {
  algorithm?: string;
  signature?: string;
  jwksUrl?: string;
}

export interface AgentCardSpec {
  name: string;
  description: string;
  url: string;
  version: string;
  capabilities: AgentCapabilities;
  securitySchemes: SecurityScheme[];
  skills: AgentSkill[];
  interface: AgentInterface;
  provider?: AgentProvider;
  documentationUrl?: string;
  signature?: AgentCardSignature;
}

// Core Agent model
export interface Agent {
  name: string;
  description: string;
  version: string;
  provider: string;
  id?: string;
  tags?: string[];
  is_public?: boolean;
  is_active?: boolean;
  location_url?: string;
  location_type?: string;
  capabilities?: AgentCapabilities;
  auth_schemes?: SecurityScheme[];
  tee_details?: AgentTeeDetails;
  skills?: AgentSkill[];
  agent_card?: AgentCardSpec;
  client_id?: string;
  created_at?: string;
  updated_at?: string;
}

// Helper functions
export function agentFromDict(data: any): Agent {
  return {
    id: data.id || data.agentId,
    name: data.name,
    description: data.description,
    version: data.version,
    provider: data.provider || data.publisherId || "unknown",
    tags: data.tags || [],
    is_public: data.is_public !== undefined ? data.is_public : true,
    is_active: data.is_active !== undefined ? data.is_active : true,
    location_url: data.location_url,
    location_type: data.location_type,
    capabilities: data.capabilities ? capabilitiesFromDict(data.capabilities) : undefined,
    auth_schemes: data.auth_schemes?.map((scheme: any) => securitySchemeFromDict(scheme)) || [],
    tee_details: data.tee_details ? teeDetailsFromDict(data.tee_details) : undefined,
    skills: data.skills
      ? Array.isArray(data.skills)
        ? data.skills.map((skill: any) => agentSkillFromDict(skill))
        : []
      : undefined,
    agent_card: data.agent_card ? agentCardSpecFromDict(data.agent_card) : undefined,
    client_id: data.client_id,
    created_at: data.created_at,
    updated_at: data.updated_at,
  };
}

export function capabilitiesFromDict(data: any): AgentCapabilities {
  return {
    streaming: data.streaming,
    pushNotifications: data.pushNotifications,
    stateTransitionHistory: data.stateTransitionHistory,
    supportsAuthenticatedExtendedCard: data.supportsAuthenticatedExtendedCard,
  };
}

export function securitySchemeFromDict(data: any): SecurityScheme {
  return {
    type: data.type,
    location: data.location,
    name: data.name,
    flow: data.flow,
    tokenUrl: data.tokenUrl || data.token_url,
    scopes: data.scopes,
    credentials: data.credentials,
  };
}

export function agentSkillFromDict(data: any): AgentSkill {
  return {
    id: data.id,
    name: data.name,
    description: data.description,
    tags: data.tags || [],
    examples: data.examples,
    inputModes: data.inputModes || data.input_modes,
    outputModes: data.outputModes || data.output_modes,
  };
}

export function agentCardSpecFromDict(data: any): AgentCardSpec {
  return {
    name: data.name,
    description: data.description,
    url: data.url,
    version: data.version,
    capabilities: capabilitiesFromDict(data.capabilities || {}),
    securitySchemes: (data.securitySchemes || data.security_schemes || []).map((scheme: any) =>
      securitySchemeFromDict(scheme)
    ),
    skills: (data.skills || []).map((skill: any) => agentSkillFromDict(skill)),
    interface: {
      preferredTransport: data.interface.preferredTransport,
      defaultInputModes: data.interface.defaultInputModes,
      defaultOutputModes: data.interface.defaultOutputModes,
      additionalInterfaces: data.interface.additionalInterfaces,
    },
    provider: data.provider ? agentProviderFromDict(data.provider) : undefined,
    documentationUrl: data.documentationUrl || data.documentation_url,
    signature: data.signature ? agentCardSignatureFromDict(data.signature) : undefined,
  };
}

export function agentProviderFromDict(data: any): AgentProvider {
  return {
    organization: data.organization,
    url: data.url,
  };
}

export function teeDetailsFromDict(data: any): AgentTeeDetails {
  return {
    enabled: data.enabled || false,
    provider: data.provider,
    attestation: data.attestation,
  };
}

export function agentCardSignatureFromDict(data: any): AgentCardSignature {
  return {
    algorithm: data.algorithm,
    signature: data.signature,
    jwksUrl: data.jwksUrl || data.jwks_url,
  };
}


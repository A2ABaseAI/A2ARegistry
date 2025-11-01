/**
 * A2A Agent Registry TypeScript SDK
 *
 * A TypeScript SDK for interacting with the A2A Agent Registry.
 * Provides easy-to-use classes and methods for agent registration, discovery, and management.
 */

export { A2ARegClient, type A2ARegClientOptions } from './client';

export type {
  Agent,
  AgentProvider,
  AgentCapabilities,
  SecurityScheme,
  AgentSkill,
  AgentInterface,
  AgentCardSignature,
  AgentCardSpec,
  AgentTeeDetails,
} from './models';

export {
  agentFromDict,
  capabilitiesFromDict,
  securitySchemeFromDict,
  agentSkillFromDict,
  agentCardSpecFromDict,
  agentProviderFromDict,
  teeDetailsFromDict,
  agentCardSignatureFromDict,
} from './models';

export { A2AError, AuthenticationError, ValidationError, NotFoundError } from './exceptions';

export const VERSION = '1.0.0';


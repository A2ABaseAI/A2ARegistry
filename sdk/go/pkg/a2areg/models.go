package a2areg

import (
	"encoding/json"
	"time"
)

// AgentProvider represents service provider information for the Agent.
// Section 5.5.1 of the A2A Protocol specification.
type AgentProvider struct {
	Organization string `json:"organization"`
	URL         string `json:"url"`
}

// AgentCapabilities represents optional capabilities supported by the Agent.
// Section 5.5.2 of the A2A Protocol specification.
type AgentCapabilities struct {
	Streaming                      *bool `json:"streaming,omitempty"`
	PushNotifications              *bool `json:"pushNotifications,omitempty"`
	StateTransitionHistory         *bool `json:"stateTransitionHistory,omitempty"`
	SupportsAuthenticatedExtendedCard *bool `json:"supportsAuthenticatedExtendedCard,omitempty"`
}

// SecurityScheme represents authentication requirements for the Agent.
// Section 5.5.3 of the A2A Protocol specification.
type SecurityScheme struct {
	Type        string   `json:"type"` // apiKey, oauth2, jwt, mTLS
	Location    *string  `json:"location,omitempty"` // header, query, body
	Name        *string  `json:"name,omitempty"` // Parameter name for credentials
	Flow        *string  `json:"flow,omitempty"` // OAuth2 flow type
	TokenURL    *string  `json:"tokenUrl,omitempty"` // OAuth2 token URL
	Scopes      []string `json:"scopes,omitempty"` // OAuth2 scopes
	Credentials *string  `json:"credentials,omitempty"` // Credentials for private Cards
}

// AgentTeeDetails represents Trusted Execution Environment details.
type AgentTeeDetails struct {
	Enabled     bool    `json:"enabled"`
	Provider    *string `json:"provider,omitempty"`
	Attestation *string `json:"attestation,omitempty"`
}

// AgentSkill represents a capability unit the Agent can perform.
// Section 5.5.4 of the A2A Protocol specification.
type AgentSkill struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Description string   `json:"description"`
	Tags        []string `json:"tags"`
	Examples    []string `json:"examples,omitempty"`
	InputModes  []string `json:"inputModes,omitempty"`
	OutputModes []string `json:"outputModes,omitempty"`
}

// AgentInterface represents transport and interaction capabilities.
// Section 5.5.5 of the A2A Protocol specification.
type AgentInterface struct {
	PreferredTransport string                   `json:"preferredTransport"` // jsonrpc, grpc, http
	DefaultInputModes  []string                 `json:"defaultInputModes"`
	DefaultOutputModes []string                 `json:"defaultOutputModes"`
	AdditionalInterfaces []map[string]interface{} `json:"additionalInterfaces,omitempty"`
}

// AgentCardSignature represents digital signature information.
// Section 5.5.6 of the A2A Protocol specification.
type AgentCardSignature struct {
	Algorithm *string `json:"algorithm,omitempty"`
	Signature *string `json:"signature,omitempty"`
	JWKSUrl   *string `json:"jwksUrl,omitempty"`
}

// AgentCardSpec represents the Agent Card specification following A2A Protocol.
// Section 5.5 of the A2A Protocol specification.
type AgentCardSpec struct {
	Name             string                       `json:"name"`
	Description      string                       `json:"description"`
	URL              string                       `json:"url"`
	Version          string                       `json:"version"`
	Capabilities     AgentCapabilities            `json:"capabilities"`
	SecuritySchemes  map[string]SecurityScheme    `json:"securitySchemes"`  // Changed from slice to map for ADK compatibility
	Skills           []AgentSkill                 `json:"skills"`
	Interface        AgentInterface               `json:"interface"`
	Provider         *AgentProvider               `json:"provider,omitempty"`
	DocumentationURL *string                      `json:"documentationUrl,omitempty"`
	Signature        *AgentCardSignature          `json:"signature,omitempty"`
	DefaultInputModes []string                    `json:"defaultInputModes,omitempty"`  // ADK-compatible top-level field
	DefaultOutputModes []string                   `json:"defaultOutputModes,omitempty"`  // ADK-compatible top-level field
}

// Agent represents an A2A Agent.
type Agent struct {
	ID           *string         `json:"id,omitempty"`
	Name         string          `json:"name"`
	Description  string          `json:"description"`
	Version      string          `json:"version"`
	Provider     string          `json:"provider"`
	Tags         []string        `json:"tags,omitempty"`
	IsPublic     bool            `json:"is_public"`
	IsActive     bool            `json:"is_active"`
	LocationURL  *string          `json:"location_url,omitempty"`
	LocationType *string          `json:"location_type,omitempty"`
	Capabilities *AgentCapabilities `json:"capabilities,omitempty"`
	AuthSchemes  []SecurityScheme `json:"auth_schemes,omitempty"`
	TEEDetails   *AgentTeeDetails `json:"tee_details,omitempty"`
	Skills       []AgentSkill     `json:"skills,omitempty"`
	AgentCard    *AgentCardSpec   `json:"agent_card,omitempty"`
	ClientID     *string          `json:"client_id,omitempty"`
	CreatedAt    *time.Time       `json:"created_at,omitempty"`
	UpdatedAt    *time.Time       `json:"updated_at,omitempty"`
}

// FromJSON creates an Agent from JSON data.
func (a *Agent) FromJSON(data []byte) error {
	return json.Unmarshal(data, a)
}

// ToJSON converts an Agent to JSON.
func (a *Agent) ToJSON() ([]byte, error) {
	return json.Marshal(a)
}

// FromJSON creates an AgentCardSpec from JSON data.
func (acs *AgentCardSpec) FromJSON(data []byte) error {
	return json.Unmarshal(data, acs)
}

// ToJSON converts an AgentCardSpec to JSON.
func (acs *AgentCardSpec) ToJSON() ([]byte, error) {
	return json.Marshal(acs)
}


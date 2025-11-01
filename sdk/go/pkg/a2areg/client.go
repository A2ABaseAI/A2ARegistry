package a2areg

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"
)

// A2ARegClientOptions contains configuration options for A2ARegClient.
type A2ARegClientOptions struct {
	RegistryURL  string
	ClientID     string
	ClientSecret string
	Timeout      time.Duration
	APIKey       string
	APIKeyHeader string
	Scope        string
}

// DefaultOptions returns default options for A2ARegClient.
func DefaultOptions() A2ARegClientOptions {
	return A2ARegClientOptions{
		RegistryURL:  "http://localhost:8000",
		Timeout:      30 * time.Second,
		APIKeyHeader: "X-API-Key",
		Scope:        "read write",
	}
}

// A2ARegClient is the main client for interacting with the A2A Registry.
type A2ARegClient struct {
	registryURL    string
	clientID       string
	clientSecret   string
	timeout        time.Duration
	apiKey         string
	apiKeyHeader   string
	scope          string
	httpClient     *http.Client
	accessToken    string
	tokenExpiresAt *time.Time
}

// NewA2ARegClient creates a new A2ARegClient with the given options.
func NewA2ARegClient(opts A2ARegClientOptions) *A2ARegClient {
	if opts.RegistryURL == "" {
		opts.RegistryURL = "http://localhost:8000"
	}
	if opts.Timeout == 0 {
		opts.Timeout = 30 * time.Second
	}
	if opts.APIKeyHeader == "" {
		opts.APIKeyHeader = "X-API-Key"
	}
	if opts.Scope == "" {
		opts.Scope = "read write"
	}

	registryURL := strings.TrimSuffix(opts.RegistryURL, "/")

	return &A2ARegClient{
		registryURL:  registryURL,
		clientID:     opts.ClientID,
		clientSecret: opts.ClientSecret,
		timeout:      opts.Timeout,
		apiKey:       opts.APIKey,
		apiKeyHeader: opts.APIKeyHeader,
		scope:        opts.Scope,
		httpClient: &http.Client{
			Timeout: opts.Timeout,
		},
	}
}

// SetAPIKey sets the API key for authentication.
func (c *A2ARegClient) SetAPIKey(apiKey string) {
	c.apiKey = apiKey
}

// Authenticate authenticates with the A2A registry using OAuth 2.0 client credentials flow.
func (c *A2ARegClient) Authenticate(scope ...string) error {
	// If API key is set, skip OAuth
	if c.apiKey != "" {
		return nil
	}

	if c.clientID == "" || c.clientSecret == "" {
		return NewAuthenticationError("Client ID and secret are required for authentication", nil)
	}

	authScope := c.scope
	if len(scope) > 0 && scope[0] != "" {
		authScope = scope[0]
	}

	data := url.Values{}
	data.Set("grant_type", "client_credentials")
	data.Set("client_id", c.clientID)
	data.Set("client_secret", c.clientSecret)
	data.Set("scope", authScope)

	req, err := http.NewRequest("POST", c.registryURL+"/auth/oauth/token", strings.NewReader(data.Encode()))
	if err != nil {
		return NewAuthenticationError("Failed to create request", map[string]interface{}{"error": err.Error()})
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return NewAuthenticationError("Authentication failed", map[string]interface{}{"error": err.Error()})
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return NewAuthenticationError("Authentication failed", map[string]interface{}{"status_code": resp.StatusCode})
	}

	var tokenData struct {
		AccessToken string `json:"access_token"`
		ExpiresIn   int    `json:"expires_in"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&tokenData); err != nil {
		return NewAuthenticationError("Failed to decode token response", map[string]interface{}{"error": err.Error()})
	}

	if tokenData.AccessToken == "" {
		return NewAuthenticationError("No access token received", nil)
	}

	c.accessToken = tokenData.AccessToken
	if tokenData.ExpiresIn > 0 {
		expiresAt := time.Now().Add(time.Duration(tokenData.ExpiresIn-60) * time.Second)
		c.tokenExpiresAt = &expiresAt
	}

	return nil
}

// ensureAuthenticated ensures we have a valid access token.
func (c *A2ARegClient) ensureAuthenticated() error {
	if c.apiKey != "" {
		return nil
	}

	if c.accessToken == "" {
		return c.Authenticate()
	}

	if c.tokenExpiresAt != nil && time.Now().After(*c.tokenExpiresAt) {
		return c.Authenticate()
	}

	return nil
}

// handleResponse handles the HTTP response and returns appropriate errors.
func (c *A2ARegClient) handleResponse(resp *http.Response) ([]byte, error) {
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, NewA2AError("Failed to read response body", map[string]interface{}{"error": err.Error()})
	}

	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		return body, nil
	}

	switch resp.StatusCode {
	case http.StatusUnauthorized:
		return nil, NewAuthenticationError("Authentication required or token expired", nil)
	case http.StatusForbidden:
		return nil, NewAuthenticationError("Access denied", nil)
	case http.StatusNotFound:
		return nil, NewNotFoundError("Resource not found", nil)
	case http.StatusUnprocessableEntity:
		var errorData map[string]interface{}
		if err := json.Unmarshal(body, &errorData); err == nil {
			detail, _ := errorData["detail"].(string)
			return nil, NewValidationError("Validation error: "+detail, errorData)
		}
		return nil, NewValidationError("Validation error", nil)
	default:
		var errorData map[string]interface{}
		if err := json.Unmarshal(body, &errorData); err == nil {
			detail, _ := errorData["detail"].(string)
			return nil, NewA2AError("API error: "+detail, errorData)
		}
		return nil, NewA2AError(fmt.Sprintf("API error: status %d", resp.StatusCode), nil)
	}
}

// makeRequest makes an HTTP request to the registry.
func (c *A2ARegClient) makeRequest(method, endpoint string, body interface{}, params map[string]string) ([]byte, error) {
	if err := c.ensureAuthenticated(); err != nil {
		return nil, err
	}

	reqURL := c.registryURL + endpoint
	if params != nil && len(params) > 0 {
		u, err := url.Parse(reqURL)
		if err != nil {
			return nil, NewA2AError("Invalid URL", map[string]interface{}{"error": err.Error()})
		}
		q := u.Query()
		for k, v := range params {
			q.Set(k, v)
		}
		u.RawQuery = q.Encode()
		reqURL = u.String()
	}

	var reqBody io.Reader
	if body != nil {
		jsonData, err := json.Marshal(body)
		if err != nil {
			return nil, NewA2AError("Failed to marshal request body", map[string]interface{}{"error": err.Error()})
		}
		reqBody = bytes.NewBuffer(jsonData)
	}

	req, err := http.NewRequest(method, reqURL, reqBody)
	if err != nil {
		return nil, NewA2AError("Failed to create request", map[string]interface{}{"error": err.Error()})
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("User-Agent", "A2A-Go-SDK/1.0.0")

	if c.apiKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.apiKey)
	} else if c.accessToken != "" {
		req.Header.Set("Authorization", "Bearer "+c.accessToken)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, NewA2AError("Request failed", map[string]interface{}{"error": err.Error()})
	}
	defer resp.Body.Close()

	return c.handleResponse(resp)
}

// GetHealth gets the registry health status.
func (c *A2ARegClient) GetHealth() (map[string]interface{}, error) {
	body, err := c.makeRequest("GET", "/health", nil, nil)
	if err != nil {
		return nil, err
	}

	var health map[string]interface{}
	if err := json.Unmarshal(body, &health); err != nil {
		return nil, NewA2AError("Failed to decode health response", map[string]interface{}{"error": err.Error()})
	}

	return health, nil
}

// ListAgents lists agents from the registry.
func (c *A2ARegClient) ListAgents(page, limit int, publicOnly bool) (map[string]interface{}, error) {
	endpoint := "/agents/public"
	if !publicOnly {
		endpoint = "/agents/entitled"
	}

	params := map[string]string{
		"page":  fmt.Sprintf("%d", page),
		"limit": fmt.Sprintf("%d", limit),
	}

	body, err := c.makeRequest("GET", endpoint, nil, params)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, NewA2AError("Failed to decode agents response", map[string]interface{}{"error": err.Error()})
	}

	return result, nil
}

// GetAgent gets a specific agent by ID.
func (c *A2ARegClient) GetAgent(agentID string) (*Agent, error) {
	body, err := c.makeRequest("GET", "/agents/"+agentID, nil, nil)
	if err != nil {
		return nil, err
	}

	var agent Agent
	if err := json.Unmarshal(body, &agent); err != nil {
		return nil, NewA2AError("Failed to decode agent response", map[string]interface{}{"error": err.Error()})
	}

	return &agent, nil
}

// GetAgentCard gets an agent's card.
func (c *A2ARegClient) GetAgentCard(agentID string) (*AgentCardSpec, error) {
	body, err := c.makeRequest("GET", "/agents/"+agentID+"/card", nil, nil)
	if err != nil {
		return nil, err
	}

	var card AgentCardSpec
	if err := json.Unmarshal(body, &card); err != nil {
		return nil, NewA2AError("Failed to decode card response", map[string]interface{}{"error": err.Error()})
	}

	return &card, nil
}

// SearchAgents searches for agents.
func (c *A2ARegClient) SearchAgents(query string, filters map[string]interface{}, semantic bool, page, limit int) (map[string]interface{}, error) {
	searchData := map[string]interface{}{
		"query":    query,
		"filters":  filters,
		"semantic": semantic,
		"page":     page,
		"limit":    limit,
	}

	body, err := c.makeRequest("POST", "/agents/search", searchData, nil)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, NewA2AError("Failed to decode search response", map[string]interface{}{"error": err.Error()})
	}

	return result, nil
}

// GetRegistryStats gets registry statistics.
func (c *A2ARegClient) GetRegistryStats() (map[string]interface{}, error) {
	body, err := c.makeRequest("GET", "/stats", nil, nil)
	if err != nil {
		return nil, err
	}

	var stats map[string]interface{}
	if err := json.Unmarshal(body, &stats); err != nil {
		return nil, NewA2AError("Failed to decode stats response", map[string]interface{}{"error": err.Error()})
	}

	return stats, nil
}

// PublishAgent publishes a new agent to the registry.
func (c *A2ARegClient) PublishAgent(agent *Agent, validate bool) (*Agent, error) {
	if validate {
		if err := c.ValidateAgent(agent); err != nil {
			return nil, err
		}
	}

	cardData := c.convertToCardSpec(agent)

	requestBody := map[string]interface{}{
		"public": agent.IsPublic,
		"card":   cardData,
	}

	body, err := c.makeRequest("POST", "/agents/publish", requestBody, nil)
	if err != nil {
		return nil, err
	}

	var publishedData map[string]interface{}
	if err := json.Unmarshal(body, &publishedData); err != nil {
		return nil, NewA2AError("Failed to decode publish response", map[string]interface{}{"error": err.Error()})
	}

	// If agentId is returned, fetch the full agent
	if agentID, ok := publishedData["agentId"].(string); ok {
		return c.GetAgent(agentID)
	}

	// Otherwise, convert response to Agent
	var publishedAgent Agent
	if err := json.Unmarshal(body, &publishedAgent); err != nil {
		return nil, NewA2AError("Failed to decode agent response", map[string]interface{}{"error": err.Error()})
	}

	return &publishedAgent, nil
}

// UpdateAgent updates an existing agent.
func (c *A2ARegClient) UpdateAgent(agentID string, agent *Agent) (*Agent, error) {
	body, err := c.makeRequest("PUT", "/agents/"+agentID, agent, nil)
	if err != nil {
		return nil, err
	}

	var updatedAgent Agent
	if err := json.Unmarshal(body, &updatedAgent); err != nil {
		return nil, NewA2AError("Failed to decode agent response", map[string]interface{}{"error": err.Error()})
	}

	return &updatedAgent, nil
}

// DeleteAgent deletes an agent from the registry.
func (c *A2ARegClient) DeleteAgent(agentID string) error {
	_, err := c.makeRequest("DELETE", "/agents/"+agentID, nil, nil)
	return err
}

// ValidateAgent validates an agent configuration.
func (c *A2ARegClient) ValidateAgent(agent *Agent) error {
	if agent.Name == "" {
		return NewValidationError("Agent name is required", nil)
	}
	if agent.Description == "" {
		return NewValidationError("Agent description is required", nil)
	}
	if agent.Version == "" {
		return NewValidationError("Agent version is required", nil)
	}
	if agent.Provider == "" {
		return NewValidationError("Agent provider is required", nil)
	}

	for i, scheme := range agent.AuthSchemes {
		if scheme.Type == "" {
			return NewValidationError(fmt.Sprintf("Auth scheme %d missing required field: type", i), nil)
		}
		validTypes := map[string]bool{"apiKey": true, "oauth2": true, "jwt": true, "mTLS": true, "bearer": true}
		if !validTypes[scheme.Type] {
			return NewValidationError(fmt.Sprintf("Auth scheme %d has invalid type: %s", i, scheme.Type), nil)
		}
	}

	if agent.AgentCard != nil {
		if agent.AgentCard.Name == "" {
			return NewValidationError("Agent card name is required", nil)
		}
		if agent.AgentCard.Description == "" {
			return NewValidationError("Agent card description is required", nil)
		}
		if agent.AgentCard.Version == "" {
			return NewValidationError("Agent card version is required", nil)
		}
	}

	return nil
}

// convertToCardSpec converts an Agent to AgentCardSpec format.
func (c *A2ARegClient) convertToCardSpec(agent *Agent) map[string]interface{} {
	capabilities := map[string]bool{
		"streaming":                         false,
		"pushNotifications":                 false,
		"stateTransitionHistory":            false,
		"supportsAuthenticatedExtendedCard": false,
	}

	if agent.Capabilities != nil {
		if agent.Capabilities.Streaming != nil {
			capabilities["streaming"] = *agent.Capabilities.Streaming
		}
		if agent.Capabilities.PushNotifications != nil {
			capabilities["pushNotifications"] = *agent.Capabilities.PushNotifications
		}
		if agent.Capabilities.StateTransitionHistory != nil {
			capabilities["stateTransitionHistory"] = *agent.Capabilities.StateTransitionHistory
		}
		if agent.Capabilities.SupportsAuthenticatedExtendedCard != nil {
			capabilities["supportsAuthenticatedExtendedCard"] = *agent.Capabilities.SupportsAuthenticatedExtendedCard
		}
	}

	securitySchemes := []map[string]interface{}{}
	for _, authScheme := range agent.AuthSchemes {
		scheme := map[string]interface{}{
			"type":     authScheme.Type,
			"location": "header",
		}
		if authScheme.Name != nil {
			scheme["name"] = *authScheme.Name
		} else {
			scheme["name"] = "Authorization"
		}
		securitySchemes = append(securitySchemes, scheme)
	}

	skills := []map[string]interface{}{}
	for _, skill := range agent.Skills {
		skillMap := map[string]interface{}{
			"id":          skill.ID,
			"name":        skill.Name,
			"description": skill.Description,
			"tags":        skill.Tags,
		}
		if len(skill.Examples) > 0 {
			skillMap["examples"] = skill.Examples
		}
		if len(skill.InputModes) > 0 {
			skillMap["inputModes"] = skill.InputModes
		}
		if len(skill.OutputModes) > 0 {
			skillMap["outputModes"] = skill.OutputModes
		}
		skills = append(skills, skillMap)
	}

	interfaceMap := map[string]interface{}{
		"preferredTransport": "jsonrpc",
		"defaultInputModes":  []string{"text/plain"},
		"defaultOutputModes": []string{"text/plain"},
	}

	if agent.LocationURL != nil {
		interfaceMap["additionalInterfaces"] = []map[string]interface{}{
			{"transport": "http", "url": *agent.LocationURL},
		}
	}

	cardSpec := map[string]interface{}{
		"name":            agent.Name,
		"description":     agent.Description,
		"url":             getStringValue(agent.LocationURL, "https://example.com"),
		"version":         agent.Version,
		"capabilities":    capabilities,
		"securitySchemes": securitySchemes,
		"skills":          skills,
		"interface":       interfaceMap,
	}

	if agent.Provider != "" {
		cardSpec["provider"] = map[string]interface{}{
			"organization": agent.Provider,
			"url":          getStringValue(agent.LocationURL, "https://example.com"),
		}
	}

	return cardSpec
}

// getStringValue returns the string value or a default.
func getStringValue(s *string, defaultValue string) string {
	if s == nil {
		return defaultValue
	}
	return *s
}

// GenerateAPIKey generates a new API key.
func (c *A2ARegClient) GenerateAPIKey(scopes []string, expiresDays *int) (string, map[string]interface{}, error) {
	payload := map[string]interface{}{
		"scopes": scopes,
	}
	if expiresDays != nil {
		payload["expires_days"] = *expiresDays
	}

	body, err := c.makeRequest("POST", "/security/api-keys", payload, nil)
	if err != nil {
		return "", nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(body, &response); err != nil {
		return "", nil, NewA2AError("Failed to decode API key response", map[string]interface{}{"error": err.Error()})
	}

	apiKey, _ := response["api_key"].(string)
	keyInfo := map[string]interface{}{
		"key_id":     response["key_id"],
		"scopes":     response["scopes"],
		"created_at": response["created_at"],
		"expires_at": response["expires_at"],
	}

	return apiKey, keyInfo, nil
}

// GenerateAPIKeyAndAuthenticate generates a new API key and authenticates with it.
func (c *A2ARegClient) GenerateAPIKeyAndAuthenticate(scopes []string, expiresDays *int) (string, map[string]interface{}, error) {
	apiKey, keyInfo, err := c.GenerateAPIKey(scopes, expiresDays)
	if err != nil {
		return "", nil, err
	}

	c.SetAPIKey(apiKey)
	return apiKey, keyInfo, nil
}

// ValidateAPIKey validates an API key.
func (c *A2ARegClient) ValidateAPIKey(apiKey string, requiredScopes []string) (map[string]interface{}, error) {
	payload := map[string]interface{}{
		"api_key": apiKey,
	}
	if requiredScopes != nil {
		payload["required_scopes"] = requiredScopes
	}

	body, err := c.makeRequest("POST", "/security/api-keys/validate", payload, nil)
	if err != nil {
		// Check if it's an authentication error (401)
		if _, ok := err.(*AuthenticationError); ok {
			return nil, nil // Return nil for invalid key
		}
		return nil, err
	}

	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, NewA2AError("Failed to decode validation response", map[string]interface{}{"error": err.Error()})
	}

	return result, nil
}

// RevokeAPIKey revokes an API key.
func (c *A2ARegClient) RevokeAPIKey(keyID string) (bool, error) {
	_, err := c.makeRequest("DELETE", "/security/api-keys/"+keyID, nil, nil)
	if err != nil {
		if _, ok := err.(*NotFoundError); ok {
			return false, nil
		}
		return false, err
	}
	return true, nil
}

// ListAPIKeys lists all API keys.
func (c *A2ARegClient) ListAPIKeys(activeOnly bool) ([]map[string]interface{}, error) {
	params := map[string]string{
		"active_only": fmt.Sprintf("%t", activeOnly),
	}

	body, err := c.makeRequest("GET", "/security/api-keys", nil, params)
	if err != nil {
		return nil, err
	}

	var keys []map[string]interface{}
	if err := json.Unmarshal(body, &keys); err != nil {
		return nil, NewA2AError("Failed to decode API keys response", map[string]interface{}{"error": err.Error()})
	}

	return keys, nil
}

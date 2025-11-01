package a2areg

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewA2ARegClient(t *testing.T) {
	tests := []struct {
		name string
		opts A2ARegClientOptions
		want string
	}{
		{
			name: "default options",
			opts: DefaultOptions(),
			want: "http://localhost:8000",
		},
		{
			name: "custom options",
			opts: A2ARegClientOptions{
				RegistryURL:  "https://registry.example.com",
				ClientID:     "test-client",
				ClientSecret: "test-secret",
				Timeout:      60 * time.Second,
				APIKey:       "test-key",
				Scope:        "read write admin",
			},
			want: "https://registry.example.com",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			client := NewA2ARegClient(tt.opts)
			assert.Equal(t, tt.want, client.registryURL)
			assert.NotNil(t, client.httpClient)
		})
	}
}

func TestA2ARegClient_GetHealth(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/health", r.URL.Path)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status":  "healthy",
			"version": "1.0.0",
		})
	}))
	defer server.Close()

	client := NewA2ARegClient(A2ARegClientOptions{
		RegistryURL: server.URL,
		APIKey:      "test-key",
	})

	health, err := client.GetHealth()
	require.NoError(t, err)
	assert.Equal(t, "healthy", health["status"])
	assert.Equal(t, "1.0.0", health["version"])
}

func TestA2ARegClient_Authenticate(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/auth/oauth/token", r.URL.Path)
		assert.Equal(t, "POST", r.Method)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"access_token": "test-token",
			"expires_in":   3600,
		})
	}))
	defer server.Close()

	client := NewA2ARegClient(A2ARegClientOptions{
		RegistryURL:  server.URL,
		ClientID:     "test-client",
		ClientSecret: "test-secret",
	})

	err := client.Authenticate()
	require.NoError(t, err)
	assert.Equal(t, "test-token", client.accessToken)
	assert.NotNil(t, client.tokenExpiresAt)
}

func TestA2ARegClient_Authenticate_WithAPIKey(t *testing.T) {
	client := NewA2ARegClient(A2ARegClientOptions{
		RegistryURL: "http://localhost:8000",
		APIKey:      "test-key",
	})

	err := client.Authenticate()
	require.NoError(t, err)
	// Should not make any requests
	assert.Equal(t, "test-key", client.apiKey)
}

func TestA2ARegClient_Authenticate_MissingCredentials(t *testing.T) {
	client := NewA2ARegClient(A2ARegClientOptions{
		RegistryURL: "http://localhost:8000",
	})

	err := client.Authenticate()
	assert.Error(t, err)
	assert.IsType(t, &AuthenticationError{}, err)
}

func TestA2ARegClient_ListAgents(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/agents/public", r.URL.Path)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"agents": []map[string]interface{}{
				{"id": "agent-1", "name": "Test Agent"},
			},
			"total": 1,
			"page":  1,
			"limit": 20,
		})
	}))
	defer server.Close()

	client := NewA2ARegClient(A2ARegClientOptions{
		RegistryURL: server.URL,
		APIKey:      "test-key",
	})

	result, err := client.ListAgents(1, 20, true)
	require.NoError(t, err)
	agents, _ := result["agents"].([]interface{})
	assert.Len(t, agents, 1)
}

func TestA2ARegClient_GetAgent(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/agents/agent-1", r.URL.Path)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"id":          "agent-1",
			"name":        "Test Agent",
			"description": "A test agent",
			"version":     "1.0.0",
			"provider":    "test-provider",
		})
	}))
	defer server.Close()

	client := NewA2ARegClient(A2ARegClientOptions{
		RegistryURL: server.URL,
		APIKey:      "test-key",
	})

	agent, err := client.GetAgent("agent-1")
	require.NoError(t, err)
	assert.Equal(t, "agent-1", *agent.ID)
	assert.Equal(t, "Test Agent", agent.Name)
}

func TestA2ARegClient_GetAgent_NotFound(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusNotFound)
	}))
	defer server.Close()

	client := NewA2ARegClient(A2ARegClientOptions{
		RegistryURL: server.URL,
		APIKey:      "test-key",
	})

	_, err := client.GetAgent("nonexistent")
	assert.Error(t, err)
	assert.IsType(t, &NotFoundError{}, err)
}

func TestA2ARegClient_PublishAgent(t *testing.T) {
	publishServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/agents/publish" {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"agentId": "agent-123",
			})
		} else if r.URL.Path == "/agents/agent-123" {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"id":          "agent-123",
				"name":        "New Agent",
				"description": "A new agent",
				"version":     "1.0.0",
				"provider":    "test-provider",
			})
		}
	}))
	defer publishServer.Close()

	client := NewA2ARegClient(A2ARegClientOptions{
		RegistryURL: publishServer.URL,
		APIKey:      "test-key",
	})

	agent := &Agent{
		Name:        "New Agent",
		Description: "A new agent",
		Version:     "1.0.0",
		Provider:    "test-provider",
		IsPublic:    true,
	}

	published, err := client.PublishAgent(agent, false)
	require.NoError(t, err)
	assert.Equal(t, "agent-123", *published.ID)
	assert.Equal(t, "New Agent", published.Name)
}

func TestA2ARegClient_ValidateAgent(t *testing.T) {
	client := NewA2ARegClient(DefaultOptions())

	tests := []struct {
		name    string
		agent   *Agent
		wantErr bool
		errType string
	}{
		{
			name: "valid agent",
			agent: &Agent{
				Name:        "Test Agent",
				Description: "A test agent",
				Version:     "1.0.0",
				Provider:    "test-provider",
			},
			wantErr: false,
		},
		{
			name: "missing name",
			agent: &Agent{
				Description: "A test agent",
				Version:     "1.0.0",
				Provider:    "test-provider",
			},
			wantErr: true,
			errType: "ValidationError",
		},
		{
			name: "missing description",
			agent: &Agent{
				Name:     "Test Agent",
				Version:  "1.0.0",
				Provider: "test-provider",
			},
			wantErr: true,
			errType: "ValidationError",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := client.ValidateAgent(tt.agent)
			if tt.wantErr {
				assert.Error(t, err)
				assert.IsType(t, &ValidationError{}, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

func TestA2ARegClient_ErrorHandling(t *testing.T) {
	tests := []struct {
		name       string
		statusCode int
		errType    interface{}
	}{
		{
			name:       "401 Unauthorized",
			statusCode: http.StatusUnauthorized,
			errType:    &AuthenticationError{},
		},
		{
			name:       "403 Forbidden",
			statusCode: http.StatusForbidden,
			errType:    &AuthenticationError{},
		},
		{
			name:       "404 Not Found",
			statusCode: http.StatusNotFound,
			errType:    &NotFoundError{},
		},
		{
			name:       "422 Unprocessable Entity",
			statusCode: http.StatusUnprocessableEntity,
			errType:    &ValidationError{},
		},
		{
			name:       "500 Internal Server Error",
			statusCode: http.StatusInternalServerError,
			errType:    &A2AError{},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(tt.statusCode)
			}))
			defer server.Close()

			client := NewA2ARegClient(A2ARegClientOptions{
				RegistryURL: server.URL,
				APIKey:      "test-key",
			})

			_, err := client.GetAgent("agent-1")
			assert.Error(t, err)
			assert.IsType(t, tt.errType, err)
		})
	}
}

func TestA2ARegClient_SetAPIKey(t *testing.T) {
	client := NewA2ARegClient(DefaultOptions())
	client.SetAPIKey("new-key")
	assert.Equal(t, "new-key", client.apiKey)
}

func TestA2ARegClient_SearchAgents(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/agents/search", r.URL.Path)
		assert.Equal(t, "POST", r.Method)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"agents": []map[string]interface{}{
				{"id": "agent-1", "name": "Recipe Agent"},
			},
			"total": 1,
		})
	}))
	defer server.Close()

	client := NewA2ARegClient(A2ARegClientOptions{
		RegistryURL: server.URL,
		APIKey:      "test-key",
	})

	result, err := client.SearchAgents("recipe", map[string]interface{}{"tags": []string{"cooking"}}, false, 1, 20)
	require.NoError(t, err)
	agents, _ := result["agents"].([]interface{})
	assert.Len(t, agents, 1)
}

func TestA2ARegClient_GenerateAPIKey(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/security/api-keys", r.URL.Path)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"api_key":    "generated-key",
			"key_id":     "key-123",
			"scopes":     []string{"read", "write"},
			"created_at": "2024-01-01T00:00:00Z",
		})
	}))
	defer server.Close()

	client := NewA2ARegClient(A2ARegClientOptions{
		RegistryURL: server.URL,
		APIKey:      "test-key",
	})

	apiKey, keyInfo, err := client.GenerateAPIKey([]string{"read", "write"}, nil)
	require.NoError(t, err)
	assert.Equal(t, "generated-key", apiKey)
	assert.Equal(t, "key-123", keyInfo["key_id"])
}

func TestA2ARegClient_ValidateAPIKey(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"key_id": "key-123",
			"scopes": []string{"read", "write"},
			"active": true,
		})
	}))
	defer server.Close()

	client := NewA2ARegClient(A2ARegClientOptions{
		RegistryURL: server.URL,
		APIKey:      "test-key",
	})

	result, err := client.ValidateAPIKey("test-key", []string{"read"})
	require.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "key-123", result["key_id"])
}

func TestA2ARegClient_RevokeAPIKey(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))
	defer server.Close()

	client := NewA2ARegClient(A2ARegClientOptions{
		RegistryURL: server.URL,
		APIKey:      "test-key",
	})

	revoked, err := client.RevokeAPIKey("key-123")
	require.NoError(t, err)
	assert.True(t, revoked)
}

func TestA2ARegClient_ListAPIKeys(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode([]map[string]interface{}{
			{
				"key_id":    "key-1",
				"scopes":    []string{"read"},
				"created_at": "2024-01-01T00:00:00Z",
			},
		})
	}))
	defer server.Close()

	client := NewA2ARegClient(A2ARegClientOptions{
		RegistryURL: server.URL,
		APIKey:      "test-key",
	})

	keys, err := client.ListAPIKeys(true)
	require.NoError(t, err)
	assert.Len(t, keys, 1)
}


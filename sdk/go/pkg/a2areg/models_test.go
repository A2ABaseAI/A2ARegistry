package a2areg

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestAgent_FromJSON(t *testing.T) {
	data := []byte(`{
		"id": "agent-1",
		"name": "Test Agent",
		"description": "A test agent",
		"version": "1.0.0",
		"provider": "test-provider",
		"tags": ["ai", "assistant"],
		"is_public": true,
		"is_active": true
	}`)

	var agent Agent
	err := agent.FromJSON(data)
	require.NoError(t, err)
	assert.Equal(t, "agent-1", *agent.ID)
	assert.Equal(t, "Test Agent", agent.Name)
	assert.Equal(t, "A test agent", agent.Description)
	assert.Equal(t, "1.0.0", agent.Version)
	assert.Equal(t, "test-provider", agent.Provider)
	assert.Equal(t, []string{"ai", "assistant"}, agent.Tags)
	assert.True(t, agent.IsPublic)
	assert.True(t, agent.IsActive)
}

func TestAgent_ToJSON(t *testing.T) {
	id := "agent-1"
	agent := &Agent{
		ID:          &id,
		Name:        "Test Agent",
		Description: "A test agent",
		Version:     "1.0.0",
		Provider:    "test-provider",
		Tags:        []string{"ai", "assistant"},
		IsPublic:    true,
		IsActive:    true,
	}

	data, err := agent.ToJSON()
	require.NoError(t, err)

	var result Agent
	err = json.Unmarshal(data, &result)
	require.NoError(t, err)
	assert.Equal(t, *agent.ID, *result.ID)
	assert.Equal(t, agent.Name, result.Name)
	assert.Equal(t, agent.Description, result.Description)
}

func TestAgent_WithCapabilities(t *testing.T) {
	streaming := true
	pushNotifications := false
	agent := &Agent{
		Name:        "Test Agent",
		Description: "A test agent",
		Version:     "1.0.0",
		Provider:    "test-provider",
		Capabilities: &AgentCapabilities{
			Streaming:         &streaming,
			PushNotifications: &pushNotifications,
		},
	}

	assert.NotNil(t, agent.Capabilities)
	assert.True(t, *agent.Capabilities.Streaming)
	assert.False(t, *agent.Capabilities.PushNotifications)
}

func TestAgent_WithAuthSchemes(t *testing.T) {
	name := "X-API-Key"
	agent := &Agent{
		Name:        "Test Agent",
		Description: "A test agent",
		Version:     "1.0.0",
		Provider:    "test-provider",
		AuthSchemes: []SecurityScheme{
			{
				Type: "apiKey",
				Name: &name,
			},
		},
	}

	assert.Len(t, agent.AuthSchemes, 1)
	assert.Equal(t, "apiKey", agent.AuthSchemes[0].Type)
	assert.Equal(t, "X-API-Key", *agent.AuthSchemes[0].Name)
}

func TestAgentCardSpec_FromJSON(t *testing.T) {
	data := []byte(`{
		"name": "Test Agent Card",
		"description": "Card description",
		"url": "https://test.com",
		"version": "1.0.0",
		"capabilities": {
			"streaming": false
		},
		"securitySchemes": [{
			"type": "apiKey",
			"location": "header",
			"name": "X-API-Key"
		}],
		"skills": [{
			"id": "skill-1",
			"name": "Main Skill",
			"description": "Primary skill",
			"tags": []
		}],
		"interface": {
			"preferredTransport": "jsonrpc",
			"defaultInputModes": ["text/plain"],
			"defaultOutputModes": ["text/plain"]
		}
	}`)

	var card AgentCardSpec
	err := card.FromJSON(data)
	require.NoError(t, err)
	assert.Equal(t, "Test Agent Card", card.Name)
	assert.Equal(t, "Card description", card.Description)
	assert.Len(t, card.SecuritySchemes, 1)
	assert.Len(t, card.Skills, 1)
}

func TestAgentCardSpec_ToJSON(t *testing.T) {
	card := &AgentCardSpec{
		Name:        "Test Agent Card",
		Description: "Card description",
		URL:         "https://test.com",
		Version:     "1.0.0",
		Capabilities: AgentCapabilities{},
		SecuritySchemes: []SecurityScheme{
			{Type: "apiKey"},
		},
		Skills: []AgentSkill{
			{
				ID:          "skill-1",
				Name:        "Main Skill",
				Description: "Primary skill",
				Tags:        []string{},
			},
		},
		Interface: AgentInterface{
			PreferredTransport: "jsonrpc",
			DefaultInputModes:  []string{"text/plain"},
			DefaultOutputModes: []string{"text/plain"},
		},
	}

	data, err := card.ToJSON()
	require.NoError(t, err)

	var result AgentCardSpec
	err = json.Unmarshal(data, &result)
	require.NoError(t, err)
	assert.Equal(t, card.Name, result.Name)
	assert.Equal(t, card.Description, result.Description)
}

func TestAgent_WithTimestamps(t *testing.T) {
	now := time.Now()
	agent := &Agent{
		Name:        "Test Agent",
		Description: "A test agent",
		Version:     "1.0.0",
		Provider:    "test-provider",
		CreatedAt:   &now,
		UpdatedAt:   &now,
	}

	assert.NotNil(t, agent.CreatedAt)
	assert.NotNil(t, agent.UpdatedAt)
	assert.Equal(t, now, *agent.CreatedAt)
	assert.Equal(t, now, *agent.UpdatedAt)
}


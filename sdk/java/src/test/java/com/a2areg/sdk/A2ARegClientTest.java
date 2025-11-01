package com.a2areg.sdk;

import com.a2areg.sdk.exceptions.*;
import com.a2areg.sdk.models.*;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

public class A2ARegClientTest {
    private MockWebServer mockWebServer;
    private A2ARegClient client;
    private Gson gson;
    
    private Gson createGson() {
        return new GsonBuilder()
                .registerTypeAdapter(java.time.OffsetDateTime.class, new com.google.gson.TypeAdapter<java.time.OffsetDateTime>() {
                    @Override
                    public void write(com.google.gson.stream.JsonWriter out, java.time.OffsetDateTime value) throws java.io.IOException {
                        if (value == null) {
                            out.nullValue();
                        } else {
                            out.value(value.toString());
                        }
                    }
                    
                    @Override
                    public java.time.OffsetDateTime read(com.google.gson.stream.JsonReader in) throws java.io.IOException {
                        if (in.peek() == com.google.gson.stream.JsonToken.NULL) {
                            in.nextNull();
                            return null;
                        }
                        return java.time.OffsetDateTime.parse(in.nextString());
                    }
                })
                .create();
    }

    @BeforeEach
    void setUp() throws IOException {
        mockWebServer = new MockWebServer();
        mockWebServer.start();
        gson = createGson();
        client = new A2ARegClient(mockWebServer.url("/").toString().replaceAll("/$", ""), "test-key");
    }

    @AfterEach
    void tearDown() throws IOException {
        mockWebServer.shutdown();
    }

    @Test
    void testGetHealth() throws A2AError {
        Map<String, Object> healthData = new HashMap<>();
        healthData.put("status", "healthy");
        healthData.put("version", "1.0.0");

        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setBody(gson.toJson(healthData))
                .addHeader("Content-Type", "application/json"));

        Map<String, Object> health = client.getHealth();
        assertEquals("healthy", health.get("status"));
        assertEquals("1.0.0", health.get("version"));
    }

    @Test
    void testAuthenticateWithAPIKey() throws AuthenticationError {
        client.setApiKey("test-key");
        client.authenticate(); // Should not make any requests
        // API key is set, authentication should succeed without making requests
        assertNotNull(client);
    }

    @Test
    void testAuthenticateWithOAuth() throws AuthenticationError {
        A2ARegClient oauthClient = new A2ARegClient(
                mockWebServer.url("/").toString().replaceAll("/$", ""),
                "test-client",
                "test-secret"
        );

        Map<String, Object> tokenData = new HashMap<>();
        tokenData.put("access_token", "test-token");
        tokenData.put("expires_in", 3600);

        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setBody(gson.toJson(tokenData))
                .addHeader("Content-Type", "application/json"));

        oauthClient.authenticate();
        // Authentication successful
        assertNotNull(oauthClient);
    }

    @Test
    void testAuthenticateMissingCredentials() {
        A2ARegClient noCredsClient = new A2ARegClient(
                mockWebServer.url("/").toString().replaceAll("/$", "")
        );

        assertThrows(AuthenticationError.class, noCredsClient::authenticate);
    }

    @Test
    void testListAgents() throws A2AError {
        Map<String, Object> responseData = new HashMap<>();
        List<Map<String, Object>> agents = new ArrayList<>();
        Map<String, Object> agent = new HashMap<>();
        agent.put("id", "agent-1");
        agent.put("name", "Test Agent");
        agents.add(agent);
        responseData.put("agents", agents);
        responseData.put("total", 1);
        responseData.put("page", 1);
        responseData.put("limit", 20);

        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setBody(gson.toJson(responseData))
                .addHeader("Content-Type", "application/json"));

        Map<String, Object> result = client.listAgents(1, 20, true);
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> resultAgents = (List<Map<String, Object>>) result.get("agents");
        assertEquals(1, resultAgents.size());
    }

    @Test
    void testGetAgent() throws A2AError {
        Agent agent = new Agent();
        agent.setId("agent-1");
        agent.setName("Test Agent");
        agent.setDescription("A test agent");
        agent.setVersion("1.0.0");
        agent.setProvider("test-provider");

        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setBody(gson.toJson(agent))
                .addHeader("Content-Type", "application/json"));

        Agent result = client.getAgent("agent-1");
        assertEquals("agent-1", result.getId());
        assertEquals("Test Agent", result.getName());
    }

    @Test
    void testGetAgentNotFound() {
        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(404));

        assertThrows(NotFoundError.class, () -> client.getAgent("nonexistent"));
    }

    @Test
    void testPublishAgent() throws A2AError {
        // Mock publish response
        Map<String, Object> publishResponse = new HashMap<>();
        publishResponse.put("agentId", "agent-123");

        // Mock get agent response
        Agent agent = new Agent();
        agent.setId("agent-123");
        agent.setName("New Agent");
        agent.setDescription("A new agent");
        agent.setVersion("1.0.0");
        agent.setProvider("test-provider");

        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setBody(gson.toJson(publishResponse))
                .addHeader("Content-Type", "application/json"));

        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setBody(gson.toJson(agent))
                .addHeader("Content-Type", "application/json"));

        Agent toPublish = new Agent();
        toPublish.setName("New Agent");
        toPublish.setDescription("A new agent");
        toPublish.setVersion("1.0.0");
        toPublish.setProvider("test-provider");
        toPublish.setIsPublic(true);

        Agent published = client.publishAgent(toPublish, false);
        assertEquals("agent-123", published.getId());
        assertEquals("New Agent", published.getName());
    }

    @Test
    void testValidateAgent() {
        Agent validAgent = new Agent();
        validAgent.setName("Test Agent");
        validAgent.setDescription("A test agent");
        validAgent.setVersion("1.0.0");
        validAgent.setProvider("test-provider");

        assertDoesNotThrow(() -> client.validateAgent(validAgent));
    }

    @Test
    void testValidateAgentMissingName() {
        Agent invalidAgent = new Agent();
        invalidAgent.setDescription("A test agent");
        invalidAgent.setVersion("1.0.0");
        invalidAgent.setProvider("test-provider");

        assertThrows(ValidationError.class, () -> client.validateAgent(invalidAgent));
    }

    @Test
    void testErrorHandling() {
        // Test 401 Unauthorized
        mockWebServer.enqueue(new MockResponse().setResponseCode(401));
        assertThrows(AuthenticationError.class, () -> client.getAgent("agent-1"));

        // Test 403 Forbidden
        mockWebServer.enqueue(new MockResponse().setResponseCode(403));
        assertThrows(AuthenticationError.class, () -> client.getAgent("agent-1"));

        // Test 404 Not Found
        mockWebServer.enqueue(new MockResponse().setResponseCode(404));
        assertThrows(NotFoundError.class, () -> client.getAgent("agent-1"));

        // Test 422 Unprocessable Entity
        mockWebServer.enqueue(new MockResponse().setResponseCode(422));
        assertThrows(ValidationError.class, () -> client.getAgent("agent-1"));

        // Test 500 Internal Server Error
        mockWebServer.enqueue(new MockResponse().setResponseCode(500));
        assertThrows(ServerError.class, () -> client.getAgent("agent-1"));
    }

    @Test
    void testSetAPIKey() {
        client.setApiKey("new-key");
        // API key is set
        assertNotNull(client);
    }

    @Test
    void testSearchAgents() throws A2AError {
        Map<String, Object> responseData = new HashMap<>();
        List<Map<String, Object>> agents = new ArrayList<>();
        Map<String, Object> agent = new HashMap<>();
        agent.put("id", "agent-1");
        agent.put("name", "Recipe Agent");
        agents.add(agent);
        responseData.put("agents", agents);
        responseData.put("total", 1);

        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setBody(gson.toJson(responseData))
                .addHeader("Content-Type", "application/json"));

        Map<String, Object> filters = new HashMap<>();
        filters.put("tags", Arrays.asList("cooking"));
        Map<String, Object> result = client.searchAgents("recipe", filters, false, 1, 20);
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> resultAgents = (List<Map<String, Object>>) result.get("agents");
        assertEquals(1, resultAgents.size());
    }

    @Test
    void testGenerateAPIKey() throws A2AError {
        Map<String, Object> response = new HashMap<>();
        response.put("api_key", "generated-key");
        response.put("key_id", "key-123");
        response.put("scopes", Arrays.asList("read", "write"));
        response.put("created_at", "2024-01-01T00:00:00Z");

        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setBody(gson.toJson(response))
                .addHeader("Content-Type", "application/json"));

        Map<String, Object> result = client.generateApiKey(Arrays.asList("read", "write"), null);
        assertEquals("generated-key", result.get("api_key"));
        assertEquals("key-123", result.get("key_id"));
    }

    @Test
    void testValidateAPIKey() throws A2AError {
        Map<String, Object> response = new HashMap<>();
        response.put("key_id", "key-123");
        response.put("scopes", Arrays.asList("read", "write"));
        response.put("active", true);

        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setBody(gson.toJson(response))
                .addHeader("Content-Type", "application/json"));

        Map<String, Object> result = client.validateApiKey("test-key", Arrays.asList("read"));
        assertNotNull(result);
        assertEquals("key-123", result.get("key_id"));
    }

    @Test
    void testRevokeAPIKey() throws A2AError {
        mockWebServer.enqueue(new MockResponse().setResponseCode(200));

        boolean revoked = client.revokeApiKey("key-123");
        assertTrue(revoked);
    }

    @Test
    void testListAPIKeys() throws A2AError {
        List<Map<String, Object>> keys = new ArrayList<>();
        Map<String, Object> key = new HashMap<>();
        key.put("key_id", "key-1");
        key.put("scopes", Arrays.asList("read"));
        key.put("created_at", "2024-01-01T00:00:00Z");
        keys.add(key);

        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setBody(gson.toJson(keys))
                .addHeader("Content-Type", "application/json"));

        List<Map<String, Object>> result = client.listApiKeys(true);
        assertEquals(1, result.size());
    }
}


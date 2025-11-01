package com.a2areg.sdk.models;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class AgentTest {
    private final Gson gson;
    
    public AgentTest() {
        this.gson = new GsonBuilder()
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

    @Test
    void testAgentSerialization() {
        Agent agent = new Agent();
        agent.setId("agent-1");
        agent.setName("Test Agent");
        agent.setDescription("A test agent");
        agent.setVersion("1.0.0");
        agent.setProvider("test-provider");
        agent.setTags(Arrays.asList("ai", "assistant"));
        agent.setIsPublic(true);
        agent.setIsActive(true);

        String json = gson.toJson(agent);
        assertNotNull(json);
        assertTrue(json.contains("Test Agent"));
        assertTrue(json.contains("agent-1"));
    }

    @Test
    void testAgentDeserialization() {
        String json = "{\"id\":\"agent-1\",\"name\":\"Test Agent\",\"description\":\"A test agent\"," +
                      "\"version\":\"1.0.0\",\"provider\":\"test-provider\",\"tags\":[\"ai\",\"assistant\"]," +
                      "\"is_public\":true,\"is_active\":true}";

        Agent agent = gson.fromJson(json, Agent.class);
        assertEquals("agent-1", agent.getId());
        assertEquals("Test Agent", agent.getName());
        assertEquals("A test agent", agent.getDescription());
        assertEquals("1.0.0", agent.getVersion());
        assertEquals("test-provider", agent.getProvider());
        assertEquals(Arrays.asList("ai", "assistant"), agent.getTags());
        assertTrue(agent.getIsPublic());
        assertTrue(agent.getIsActive());
    }

    @Test
    void testAgentWithCapabilities() {
        Agent agent = new Agent();
        agent.setName("Test Agent");
        agent.setDescription("A test agent");
        agent.setVersion("1.0.0");
        agent.setProvider("test-provider");

        AgentCapabilities capabilities = new AgentCapabilities();
        capabilities.setStreaming(true);
        capabilities.setPushNotifications(false);
        agent.setCapabilities(capabilities);

        assertNotNull(agent.getCapabilities());
        assertTrue(agent.getCapabilities().getStreaming());
        assertFalse(agent.getCapabilities().getPushNotifications());
    }

    @Test
    void testAgentWithAuthSchemes() {
        Agent agent = new Agent();
        agent.setName("Test Agent");
        agent.setDescription("A test agent");
        agent.setVersion("1.0.0");
        agent.setProvider("test-provider");

        SecurityScheme scheme = new SecurityScheme("apiKey");
        scheme.setName("X-API-Key");
        agent.setAuthSchemes(Arrays.asList(scheme));

        assertNotNull(agent.getAuthSchemes());
        assertEquals(1, agent.getAuthSchemes().size());
        assertEquals("apiKey", agent.getAuthSchemes().get(0).getType());
        assertEquals("X-API-Key", agent.getAuthSchemes().get(0).getName());
    }

    @Test
    void testAgentCardSpec() {
        AgentCardSpec card = new AgentCardSpec();
        card.setName("Test Agent Card");
        card.setDescription("Card description");
        card.setUrl("https://test.com");
        card.setVersion("1.0.0");

        AgentCapabilities capabilities = new AgentCapabilities();
        capabilities.setStreaming(false);
        card.setCapabilities(capabilities);

        SecurityScheme scheme = new SecurityScheme("apiKey");
        card.setSecuritySchemes(Arrays.asList(scheme));

        AgentSkill skill = new AgentSkill("skill-1", "Main Skill", "Primary skill", Arrays.asList());
        card.setSkills(Arrays.asList(skill));

        AgentInterface interface_ = new AgentInterface("jsonrpc", 
                Arrays.asList("text/plain"), Arrays.asList("text/plain"));
        card.setInterface(interface_);

        assertNotNull(card.getName());
        assertNotNull(card.getDescription());
        assertNotNull(card.getCapabilities());
        assertNotNull(card.getSecuritySchemes());
        assertNotNull(card.getSkills());
        assertNotNull(card.getInterface());
    }
}


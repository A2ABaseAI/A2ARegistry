package com.a2areg.sdk;

import com.a2areg.sdk.exceptions.*;
import com.a2areg.sdk.models.*;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import okhttp3.*;
import okhttp3.MediaType;

import java.io.IOException;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.TimeUnit;

/**
 * Main client for interacting with the A2A Registry.
 */
public class A2ARegClient {
    private static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
    private static final MediaType FORM = MediaType.parse("application/x-www-form-urlencoded");

    private final String registryUrl;
    private final String clientId;
    private final String clientSecret;
    private final Duration timeout;
    private String apiKey;
    private final String scope;

    private final OkHttpClient httpClient;
    private final Gson gson;

    private String accessToken;
    private long tokenExpiresAt;

    /**
     * Creates a new A2ARegClient with default options.
     */
    public A2ARegClient() {
        this("http://localhost:8000", null, null, Duration.ofSeconds(30), null, "read write");
    }

    /**
     * Creates a new A2ARegClient with the given registry URL.
     */
    public A2ARegClient(String registryUrl) {
        this(registryUrl, null, null, Duration.ofSeconds(30), null, "read write");
    }

    /**
     * Creates a new A2ARegClient with API key authentication.
     */
    public A2ARegClient(String registryUrl, String apiKey) {
        this(registryUrl, null, null, Duration.ofSeconds(30), apiKey, "read write");
    }

    /**
     * Creates a new A2ARegClient with OAuth credentials.
     */
    public A2ARegClient(String registryUrl, String clientId, String clientSecret) {
        this(registryUrl, clientId, clientSecret, Duration.ofSeconds(30), null, "read write");
    }

    /**
     * Creates a new A2ARegClient with all options.
     */
    public A2ARegClient(String registryUrl, String clientId, String clientSecret, 
                       Duration timeout, String apiKey, String scope) {
        this.registryUrl = registryUrl.endsWith("/") ? registryUrl.substring(0, registryUrl.length() - 1) : registryUrl;
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.timeout = timeout;
        this.apiKey = apiKey;
        this.scope = scope;

        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(timeout.toSeconds(), TimeUnit.SECONDS)
                .readTimeout(timeout.toSeconds(), TimeUnit.SECONDS)
                .writeTimeout(timeout.toSeconds(), TimeUnit.SECONDS)
                .build();

        // Create Gson with proper date/time handling for Java modules
        // Use TypeAdapter to handle both serialization and deserialization
        this.gson = new GsonBuilder()
                .setDateFormat("yyyy-MM-dd'T'HH:mm:ssX")
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

    /**
     * Sets the API key for authentication.
     */
    public void setApiKey(String apiKey) {
        this.apiKey = apiKey;
    }

    /**
     * Authenticates with the A2A registry using OAuth 2.0 client credentials flow.
     */
    public void authenticate() throws AuthenticationError {
        authenticate(this.scope);
    }

    /**
     * Authenticates with the A2A registry using OAuth 2.0 client credentials flow.
     */
    public void authenticate(String scope) throws AuthenticationError {
        // If API key is set, skip OAuth
        if (apiKey != null && !apiKey.isEmpty()) {
            return;
        }

        if (clientId == null || clientSecret == null || clientId.isEmpty() || clientSecret.isEmpty()) {
            throw new AuthenticationError("Client ID and secret are required for authentication");
        }

        RequestBody body = new FormBody.Builder()
                .add("grant_type", "client_credentials")
                .add("client_id", clientId)
                .add("client_secret", clientSecret)
                .add("scope", scope != null ? scope : this.scope)
                .build();

        Request request = new Request.Builder()
                .url(registryUrl + "/auth/oauth/token")
                .post(body)
                .header("Content-Type", "application/x-www-form-urlencoded")
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new AuthenticationError("Authentication failed: " + response.code());
            }

            JsonObject jsonResponse = JsonParser.parseString(response.body().string()).getAsJsonObject();
            this.accessToken = jsonResponse.get("access_token").getAsString();
            
            if (jsonResponse.has("expires_in")) {
                int expiresIn = jsonResponse.get("expires_in").getAsInt();
                // Refresh 1 minute early
                this.tokenExpiresAt = System.currentTimeMillis() + (expiresIn - 60) * 1000L;
            }

            if (this.accessToken == null || this.accessToken.isEmpty()) {
                throw new AuthenticationError("No access token received");
            }
        } catch (IOException e) {
            throw new AuthenticationError("Authentication failed", e);
        }
    }

    private void ensureAuthenticated() throws AuthenticationError {
        if (apiKey != null && !apiKey.isEmpty()) {
            return;
        }

        if (accessToken == null || accessToken.isEmpty()) {
            authenticate();
        } else if (tokenExpiresAt > 0 && System.currentTimeMillis() >= tokenExpiresAt) {
            authenticate();
        }
    }

    private Response makeRequest(String method, String endpoint, Object body, Map<String, String> params) 
            throws A2AError {
        try {
            ensureAuthenticated();
        } catch (AuthenticationError e) {
            throw new A2AError("Authentication required", e);
        }

        HttpUrl.Builder urlBuilder = HttpUrl.parse(registryUrl + endpoint).newBuilder();
        if (params != null) {
            for (Map.Entry<String, String> param : params.entrySet()) {
                urlBuilder.addQueryParameter(param.getKey(), param.getValue());
            }
        }

        Request.Builder requestBuilder = new Request.Builder()
                .url(urlBuilder.build())
                .header("Content-Type", "application/json")
                .header("User-Agent", "A2A-Java-SDK/1.0.0");

        if (apiKey != null && !apiKey.isEmpty()) {
            requestBuilder.header("Authorization", "Bearer " + apiKey);
        } else if (accessToken != null && !accessToken.isEmpty()) {
            requestBuilder.header("Authorization", "Bearer " + accessToken);
        }

        RequestBody requestBody = null;
        if (body != null) {
            requestBody = RequestBody.create(gson.toJson(body), JSON);
        }

        switch (method.toUpperCase()) {
            case "GET":
                requestBuilder = requestBuilder.get();
                break;
            case "POST":
                requestBuilder = requestBuilder.post(requestBody);
                break;
            case "PUT":
                requestBuilder = requestBuilder.put(requestBody);
                break;
            case "DELETE":
                requestBuilder = requestBuilder.delete();
                break;
        }

        try {
            Response response = httpClient.newCall(requestBuilder.build()).execute();
            handleResponse(response);
            return response;
        } catch (IOException e) {
            throw new A2AError("Request failed", e);
        }
    }

    private void handleResponse(Response response) throws A2AError {
        if (response.isSuccessful()) {
            return;
        }

        int statusCode = response.code();
        String responseBody = null;
        try {
            if (response.body() != null) {
                responseBody = response.body().string();
            }
        } catch (IOException e) {
            // Ignore
        }

        Map<String, Object> details = new HashMap<>();
        if (responseBody != null) {
            try {
                JsonObject errorData = JsonParser.parseString(responseBody).getAsJsonObject();
                if (errorData.has("detail")) {
                    details.put("detail", errorData.get("detail").getAsString());
                }
            } catch (Exception e) {
                // Ignore
            }
        }

        switch (statusCode) {
            case 401:
                throw new AuthenticationError("Authentication required or token expired", details);
            case 403:
                throw new AuthenticationError("Access denied", details);
            case 404:
                throw new NotFoundError("Resource not found", details);
            case 422:
                throw new ValidationError("Validation error", details);
            case 429:
                throw new RateLimitError("Rate limit exceeded", details);
            case 500:
            case 502:
            case 503:
            case 504:
                throw new ServerError("Server error: " + statusCode, details);
            default:
                throw new A2AError("API error: status " + statusCode, details);
        }
    }

    /**
     * Gets the registry health status.
     */
    public Map<String, Object> getHealth() throws A2AError {
        try (Response response = makeRequest("GET", "/health", null, null)) {
            return gson.fromJson(response.body().string(), Map.class);
        } catch (IOException e) {
            throw new A2AError("Failed to read response", e);
        }
    }

    /**
     * Lists agents from the registry.
     */
    public Map<String, Object> listAgents(int page, int limit, boolean publicOnly) throws A2AError {
        String endpoint = publicOnly ? "/agents/public" : "/agents/entitled";
        Map<String, String> params = new HashMap<>();
        params.put("page", String.valueOf(page));
        params.put("limit", String.valueOf(limit));

        try (Response response = makeRequest("GET", endpoint, null, params)) {
            return gson.fromJson(response.body().string(), Map.class);
        } catch (IOException e) {
            throw new A2AError("Failed to read response", e);
        }
    }

    /**
     * Gets a specific agent by ID.
     */
    public Agent getAgent(String agentId) throws A2AError {
        try (Response response = makeRequest("GET", "/agents/" + agentId, null, null)) {
            return gson.fromJson(response.body().string(), Agent.class);
        } catch (IOException e) {
            throw new A2AError("Failed to read response", e);
        }
    }

    /**
     * Gets an agent's card.
     */
    public AgentCardSpec getAgentCard(String agentId) throws A2AError {
        try (Response response = makeRequest("GET", "/agents/" + agentId + "/card", null, null)) {
            return gson.fromJson(response.body().string(), AgentCardSpec.class);
        } catch (IOException e) {
            throw new A2AError("Failed to read response", e);
        }
    }

    /**
     * Searches for agents.
     */
    public Map<String, Object> searchAgents(String query, Map<String, Object> filters, 
                                            boolean semantic, int page, int limit) throws A2AError {
        Map<String, Object> searchData = new HashMap<>();
        searchData.put("query", query);
        searchData.put("filters", filters != null ? filters : new HashMap<>());
        searchData.put("semantic", semantic);
        searchData.put("page", page);
        searchData.put("limit", limit);

        try (Response response = makeRequest("POST", "/agents/search", searchData, null)) {
            return gson.fromJson(response.body().string(), Map.class);
        } catch (IOException e) {
            throw new A2AError("Failed to read response", e);
        }
    }

    /**
     * Gets registry statistics.
     */
    public Map<String, Object> getRegistryStats() throws A2AError {
        try (Response response = makeRequest("GET", "/stats", null, null)) {
            return gson.fromJson(response.body().string(), Map.class);
        } catch (IOException e) {
            throw new A2AError("Failed to read response", e);
        }
    }

    /**
     * Publishes a new agent to the registry.
     */
    public Agent publishAgent(Agent agent, boolean validate) throws A2AError {
        if (validate) {
            validateAgent(agent);
        }

        Map<String, Object> requestBody = convertToCardSpec(agent);
        requestBody.put("public", agent.getIsPublic() != null ? agent.getIsPublic() : true);

        try (Response response = makeRequest("POST", "/agents/publish", requestBody, null)) {
            JsonObject jsonResponse = JsonParser.parseString(response.body().string()).getAsJsonObject();
            
            // If agentId is returned, fetch the full agent
            if (jsonResponse.has("agentId")) {
                String agentId = jsonResponse.get("agentId").getAsString();
                return getAgent(agentId);
            }

            // Otherwise, convert response to Agent
            return gson.fromJson(response.body().string(), Agent.class);
        } catch (IOException e) {
            throw new A2AError("Failed to read response", e);
        }
    }

    /**
     * Updates an existing agent.
     */
    public Agent updateAgent(String agentId, Agent agent) throws A2AError {
        try (Response response = makeRequest("PUT", "/agents/" + agentId, agent, null)) {
            return gson.fromJson(response.body().string(), Agent.class);
        } catch (IOException e) {
            throw new A2AError("Failed to read response", e);
        }
    }

    /**
     * Deletes an agent from the registry.
     */
    public void deleteAgent(String agentId) throws A2AError {
        makeRequest("DELETE", "/agents/" + agentId, null, null).close();
    }

    /**
     * Validates an agent configuration.
     */
    public void validateAgent(Agent agent) throws ValidationError {
        List<String> errors = new ArrayList<>();

        if (agent.getName() == null || agent.getName().isEmpty()) {
            errors.add("Agent name is required");
        }
        if (agent.getDescription() == null || agent.getDescription().isEmpty()) {
            errors.add("Agent description is required");
        }
        if (agent.getVersion() == null || agent.getVersion().isEmpty()) {
            errors.add("Agent version is required");
        }
        if (agent.getProvider() == null || agent.getProvider().isEmpty()) {
            errors.add("Agent provider is required");
        }

        if (agent.getAuthSchemes() != null) {
            Set<String> validTypes = Set.of("apiKey", "oauth2", "jwt", "mTLS", "bearer");
            for (int i = 0; i < agent.getAuthSchemes().size(); i++) {
                SecurityScheme scheme = agent.getAuthSchemes().get(i);
                if (scheme.getType() == null || scheme.getType().isEmpty()) {
                    errors.add("Auth scheme " + i + " missing required field: type");
                } else if (!validTypes.contains(scheme.getType())) {
                    errors.add("Auth scheme " + i + " has invalid type: " + scheme.getType());
                }
            }
        }

        if (agent.getAgentCard() != null) {
            if (agent.getAgentCard().getName() == null || agent.getAgentCard().getName().isEmpty()) {
                errors.add("Agent card name is required");
            }
            if (agent.getAgentCard().getDescription() == null || agent.getAgentCard().getDescription().isEmpty()) {
                errors.add("Agent card description is required");
            }
            if (agent.getAgentCard().getVersion() == null || agent.getAgentCard().getVersion().isEmpty()) {
                errors.add("Agent card version is required");
            }
        }

        if (!errors.isEmpty()) {
            throw new ValidationError("Agent validation failed: " + String.join("; ", errors));
        }
    }

    private Map<String, Object> convertToCardSpec(Agent agent) {
        Map<String, Object> capabilities = new HashMap<>();
        capabilities.put("streaming", false);
        capabilities.put("pushNotifications", false);
        capabilities.put("stateTransitionHistory", false);
        capabilities.put("supportsAuthenticatedExtendedCard", false);

        if (agent.getCapabilities() != null) {
            if (agent.getCapabilities().getStreaming() != null) {
                capabilities.put("streaming", agent.getCapabilities().getStreaming());
            }
            if (agent.getCapabilities().getPushNotifications() != null) {
                capabilities.put("pushNotifications", agent.getCapabilities().getPushNotifications());
            }
            if (agent.getCapabilities().getStateTransitionHistory() != null) {
                capabilities.put("stateTransitionHistory", agent.getCapabilities().getStateTransitionHistory());
            }
            if (agent.getCapabilities().getSupportsAuthenticatedExtendedCard() != null) {
                capabilities.put("supportsAuthenticatedExtendedCard", 
                               agent.getCapabilities().getSupportsAuthenticatedExtendedCard());
            }
        }

        // Convert auth schemes to security schemes (as map for ADK compatibility)
        Map<String, Map<String, Object>> securitySchemes = new HashMap<>();
        if (agent.getAuthSchemes() != null) {
            for (SecurityScheme authScheme : agent.getAuthSchemes()) {
                String schemeType = authScheme.getType();
                Map<String, Object> scheme = new HashMap<>();
                scheme.put("type", schemeType);
                scheme.put("location", "header");
                scheme.put("name", authScheme.getName() != null ? authScheme.getName() : "Authorization");
                securitySchemes.put(schemeType, scheme);
            }
        }

        List<Map<String, Object>> skills = new ArrayList<>();
        if (agent.getSkills() != null) {
            for (AgentSkill skill : agent.getSkills()) {
                Map<String, Object> skillMap = new HashMap<>();
                skillMap.put("id", skill.getId());
                skillMap.put("name", skill.getName());
                skillMap.put("description", skill.getDescription());
                skillMap.put("tags", skill.getTags());
                if (skill.getExamples() != null && !skill.getExamples().isEmpty()) {
                    skillMap.put("examples", skill.getExamples());
                }
                if (skill.getInputModes() != null && !skill.getInputModes().isEmpty()) {
                    skillMap.put("inputModes", skill.getInputModes());
                }
                if (skill.getOutputModes() != null && !skill.getOutputModes().isEmpty()) {
                    skillMap.put("outputModes", skill.getOutputModes());
                }
                skills.add(skillMap);
            }
        }

        Map<String, Object> interface_ = new HashMap<>();
        interface_.put("preferredTransport", "jsonrpc");
        interface_.put("defaultInputModes", Arrays.asList("text/plain"));
        interface_.put("defaultOutputModes", Arrays.asList("text/plain"));

        if (agent.getLocationUrl() != null) {
            List<Map<String, Object>> additionalInterfaces = new ArrayList<>();
            Map<String, Object> additional = new HashMap<>();
            additional.put("transport", "http");
            additional.put("url", agent.getLocationUrl());
            additionalInterfaces.add(additional);
            interface_.put("additionalInterfaces", additionalInterfaces);
        }

        Map<String, Object> cardSpec = new HashMap<>();
        cardSpec.put("name", agent.getName());
        cardSpec.put("description", agent.getDescription());
        cardSpec.put("url", agent.getLocationUrl() != null ? agent.getLocationUrl() : "https://example.com");
        cardSpec.put("version", agent.getVersion());
        cardSpec.put("capabilities", capabilities);
        cardSpec.put("securitySchemes", securitySchemes);
        cardSpec.put("skills", skills);
        cardSpec.put("interface", interface_);
        // Add top-level defaultInputModes and defaultOutputModes for ADK compatibility
        cardSpec.put("defaultInputModes", interface_.get("defaultInputModes"));
        cardSpec.put("defaultOutputModes", interface_.get("defaultOutputModes"));

        if (agent.getProvider() != null) {
            Map<String, Object> provider = new HashMap<>();
            provider.put("organization", agent.getProvider());
            provider.put("url", agent.getLocationUrl() != null ? agent.getLocationUrl() : "https://example.com");
            cardSpec.put("provider", provider);
        }

        return cardSpec;
    }

    /**
     * Generates a new API key.
     */
    public Map<String, Object> generateApiKey(List<String> scopes, Integer expiresDays) throws A2AError {
        Map<String, Object> payload = new HashMap<>();
        payload.put("scopes", scopes);
        if (expiresDays != null) {
            payload.put("expires_days", expiresDays);
        }

        try (Response response = makeRequest("POST", "/security/api-keys", payload, null)) {
            return gson.fromJson(response.body().string(), Map.class);
        } catch (IOException e) {
            throw new A2AError("Failed to read response", e);
        }
    }

    /**
     * Generates a new API key and authenticates with it.
     */
    public Map<String, Object> generateApiKeyAndAuthenticate(List<String> scopes, Integer expiresDays) throws A2AError {
        Map<String, Object> result = generateApiKey(scopes, expiresDays);
        String apiKey = (String) result.get("api_key");
        if (apiKey != null) {
            setApiKey(apiKey);
        }
        return result;
    }

    /**
     * Validates an API key.
     */
    public Map<String, Object> validateApiKey(String apiKey, List<String> requiredScopes) throws A2AError {
        Map<String, Object> payload = new HashMap<>();
        payload.put("api_key", apiKey);
        if (requiredScopes != null) {
            payload.put("required_scopes", requiredScopes);
        }

        try (Response response = makeRequest("POST", "/security/api-keys/validate", payload, null)) {
            return gson.fromJson(response.body().string(), Map.class);
        } catch (AuthenticationError e) {
            // Return null for invalid key
            return null;
        } catch (IOException e) {
            throw new A2AError("Failed to read response", e);
        }
    }

    /**
     * Revokes an API key.
     */
    public boolean revokeApiKey(String keyId) throws A2AError {
        try {
            makeRequest("DELETE", "/security/api-keys/" + keyId, null, null).close();
            return true;
        } catch (NotFoundError e) {
            return false;
        }
    }

    /**
     * Lists all API keys.
     */
    public List<Map<String, Object>> listApiKeys(boolean activeOnly) throws A2AError {
        Map<String, String> params = new HashMap<>();
        params.put("active_only", String.valueOf(activeOnly));

        try (Response response = makeRequest("GET", "/security/api-keys", null, params)) {
            return gson.fromJson(response.body().string(), List.class);
        } catch (IOException e) {
            throw new A2AError("Failed to read response", e);
        }
    }
}


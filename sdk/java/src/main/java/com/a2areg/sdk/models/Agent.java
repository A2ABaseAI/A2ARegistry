package com.a2areg.sdk.models;

import com.google.gson.annotations.SerializedName;
import java.time.OffsetDateTime;
import java.util.List;

/**
 * A2A Agent representation.
 */
public class Agent {
    @SerializedName("id")
    private String id;

    @SerializedName("name")
    private String name;

    @SerializedName("description")
    private String description;

    @SerializedName("version")
    private String version;

    @SerializedName("provider")
    private String provider;

    @SerializedName("tags")
    private List<String> tags;

    @SerializedName("is_public")
    private Boolean isPublic;

    @SerializedName("is_active")
    private Boolean isActive;

    @SerializedName("location_url")
    private String locationUrl;

    @SerializedName("location_type")
    private String locationType;

    @SerializedName("capabilities")
    private AgentCapabilities capabilities;

    @SerializedName("auth_schemes")
    private List<SecurityScheme> authSchemes;

    @SerializedName("tee_details")
    private AgentTeeDetails teeDetails;

    @SerializedName("skills")
    private List<AgentSkill> skills;

    @SerializedName("agent_card")
    private AgentCardSpec agentCard;

    @SerializedName("client_id")
    private String clientId;

    @SerializedName("created_at")
    private OffsetDateTime createdAt;

    @SerializedName("updated_at")
    private OffsetDateTime updatedAt;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    public String getProvider() {
        return provider;
    }

    public void setProvider(String provider) {
        this.provider = provider;
    }

    public List<String> getTags() {
        return tags;
    }

    public void setTags(List<String> tags) {
        this.tags = tags;
    }

    public Boolean getIsPublic() {
        return isPublic;
    }

    public void setIsPublic(Boolean isPublic) {
        this.isPublic = isPublic;
    }

    public Boolean getIsActive() {
        return isActive;
    }

    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
    }

    public String getLocationUrl() {
        return locationUrl;
    }

    public void setLocationUrl(String locationUrl) {
        this.locationUrl = locationUrl;
    }

    public String getLocationType() {
        return locationType;
    }

    public void setLocationType(String locationType) {
        this.locationType = locationType;
    }

    public AgentCapabilities getCapabilities() {
        return capabilities;
    }

    public void setCapabilities(AgentCapabilities capabilities) {
        this.capabilities = capabilities;
    }

    public List<SecurityScheme> getAuthSchemes() {
        return authSchemes;
    }

    public void setAuthSchemes(List<SecurityScheme> authSchemes) {
        this.authSchemes = authSchemes;
    }

    public AgentTeeDetails getTeeDetails() {
        return teeDetails;
    }

    public void setTeeDetails(AgentTeeDetails teeDetails) {
        this.teeDetails = teeDetails;
    }

    public List<AgentSkill> getSkills() {
        return skills;
    }

    public void setSkills(List<AgentSkill> skills) {
        this.skills = skills;
    }

    public AgentCardSpec getAgentCard() {
        return agentCard;
    }

    public void setAgentCard(AgentCardSpec agentCard) {
        this.agentCard = agentCard;
    }

    public String getClientId() {
        return clientId;
    }

    public void setClientId(String clientId) {
        this.clientId = clientId;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(OffsetDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public OffsetDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(OffsetDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}


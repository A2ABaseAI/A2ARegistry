package com.a2areg.sdk.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

/**
 * Agent Card specification following A2A Protocol specification.
 * Section 5.5 of the A2A Protocol specification.
 */
public class AgentCardSpec {
    @SerializedName("name")
    private String name;

    @SerializedName("description")
    private String description;

    @SerializedName("url")
    private String url;

    @SerializedName("version")
    private String version;

    @SerializedName("capabilities")
    private AgentCapabilities capabilities;

    @SerializedName("securitySchemes")
    private List<SecurityScheme> securitySchemes;

    @SerializedName("skills")
    private List<AgentSkill> skills;

    @SerializedName("interface")
    private AgentInterface interface_;

    @SerializedName("provider")
    private AgentProvider provider;

    @SerializedName("documentationUrl")
    private String documentationUrl;

    @SerializedName("signature")
    private AgentCardSignature signature;

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

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    public AgentCapabilities getCapabilities() {
        return capabilities;
    }

    public void setCapabilities(AgentCapabilities capabilities) {
        this.capabilities = capabilities;
    }

    public List<SecurityScheme> getSecuritySchemes() {
        return securitySchemes;
    }

    public void setSecuritySchemes(List<SecurityScheme> securitySchemes) {
        this.securitySchemes = securitySchemes;
    }

    public List<AgentSkill> getSkills() {
        return skills;
    }

    public void setSkills(List<AgentSkill> skills) {
        this.skills = skills;
    }

    public AgentInterface getInterface() {
        return interface_;
    }

    public void setInterface(AgentInterface interface_) {
        this.interface_ = interface_;
    }

    public AgentProvider getProvider() {
        return provider;
    }

    public void setProvider(AgentProvider provider) {
        this.provider = provider;
    }

    public String getDocumentationUrl() {
        return documentationUrl;
    }

    public void setDocumentationUrl(String documentationUrl) {
        this.documentationUrl = documentationUrl;
    }

    public AgentCardSignature getSignature() {
        return signature;
    }

    public void setSignature(AgentCardSignature signature) {
        this.signature = signature;
    }
}


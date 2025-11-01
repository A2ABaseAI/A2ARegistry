package com.a2areg.sdk.models;

import com.google.gson.annotations.SerializedName;

/**
 * Agent Provider Object - Service provider information for the Agent.
 * Section 5.5.1 of the A2A Protocol specification.
 */
public class AgentProvider {
    @SerializedName("organization")
    private String organization;

    @SerializedName("url")
    private String url;

    public AgentProvider() {
    }

    public AgentProvider(String organization, String url) {
        this.organization = organization;
        this.url = url;
    }

    public String getOrganization() {
        return organization;
    }

    public void setOrganization(String organization) {
        this.organization = organization;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }
}


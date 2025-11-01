package com.a2areg.sdk.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

/**
 * Security Scheme Object - Authentication requirements for the Agent.
 * Section 5.5.3 of the A2A Protocol specification.
 */
public class SecurityScheme {
    @SerializedName("type")
    private String type; // apiKey, oauth2, jwt, mTLS

    @SerializedName("location")
    private String location; // header, query, body

    @SerializedName("name")
    private String name; // Parameter name for credentials

    @SerializedName("flow")
    private String flow; // OAuth2 flow type

    @SerializedName("tokenUrl")
    private String tokenUrl; // OAuth2 token URL

    @SerializedName("scopes")
    private List<String> scopes; // OAuth2 scopes

    @SerializedName("credentials")
    private String credentials; // Credentials for private Cards

    public SecurityScheme() {
    }

    public SecurityScheme(String type) {
        this.type = type;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getFlow() {
        return flow;
    }

    public void setFlow(String flow) {
        this.flow = flow;
    }

    public String getTokenUrl() {
        return tokenUrl;
    }

    public void setTokenUrl(String tokenUrl) {
        this.tokenUrl = tokenUrl;
    }

    public List<String> getScopes() {
        return scopes;
    }

    public void setScopes(List<String> scopes) {
        this.scopes = scopes;
    }

    public String getCredentials() {
        return credentials;
    }

    public void setCredentials(String credentials) {
        this.credentials = credentials;
    }
}


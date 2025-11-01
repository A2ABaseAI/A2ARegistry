package com.a2areg.sdk.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;
import java.util.Map;

/**
 * Agent Interface Object - Transport and interaction capabilities.
 * Section 5.5.5 of the A2A Protocol specification.
 */
public class AgentInterface {
    @SerializedName("preferredTransport")
    private String preferredTransport; // jsonrpc, grpc, http

    @SerializedName("defaultInputModes")
    private List<String> defaultInputModes;

    @SerializedName("defaultOutputModes")
    private List<String> defaultOutputModes;

    @SerializedName("additionalInterfaces")
    private List<Map<String, Object>> additionalInterfaces;

    public AgentInterface() {
    }

    public AgentInterface(String preferredTransport, List<String> defaultInputModes, List<String> defaultOutputModes) {
        this.preferredTransport = preferredTransport;
        this.defaultInputModes = defaultInputModes;
        this.defaultOutputModes = defaultOutputModes;
    }

    public String getPreferredTransport() {
        return preferredTransport;
    }

    public void setPreferredTransport(String preferredTransport) {
        this.preferredTransport = preferredTransport;
    }

    public List<String> getDefaultInputModes() {
        return defaultInputModes;
    }

    public void setDefaultInputModes(List<String> defaultInputModes) {
        this.defaultInputModes = defaultInputModes;
    }

    public List<String> getDefaultOutputModes() {
        return defaultOutputModes;
    }

    public void setDefaultOutputModes(List<String> defaultOutputModes) {
        this.defaultOutputModes = defaultOutputModes;
    }

    public List<Map<String, Object>> getAdditionalInterfaces() {
        return additionalInterfaces;
    }

    public void setAdditionalInterfaces(List<Map<String, Object>> additionalInterfaces) {
        this.additionalInterfaces = additionalInterfaces;
    }
}


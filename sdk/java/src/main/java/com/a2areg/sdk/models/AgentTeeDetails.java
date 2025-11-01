package com.a2areg.sdk.models;

import com.google.gson.annotations.SerializedName;

/**
 * Trusted Execution Environment details.
 */
public class AgentTeeDetails {
    @SerializedName("enabled")
    private Boolean enabled;

    @SerializedName("provider")
    private String provider;

    @SerializedName("attestation")
    private String attestation;

    public Boolean getEnabled() {
        return enabled;
    }

    public void setEnabled(Boolean enabled) {
        this.enabled = enabled;
    }

    public String getProvider() {
        return provider;
    }

    public void setProvider(String provider) {
        this.provider = provider;
    }

    public String getAttestation() {
        return attestation;
    }

    public void setAttestation(String attestation) {
        this.attestation = attestation;
    }
}


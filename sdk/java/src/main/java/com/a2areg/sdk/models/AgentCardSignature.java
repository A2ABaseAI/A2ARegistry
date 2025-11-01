package com.a2areg.sdk.models;

import com.google.gson.annotations.SerializedName;

/**
 * Agent Card Signature Object - Digital signature information.
 * Section 5.5.6 of the A2A Protocol specification.
 */
public class AgentCardSignature {
    @SerializedName("algorithm")
    private String algorithm;

    @SerializedName("signature")
    private String signature;

    @SerializedName("jwksUrl")
    private String jwksUrl;

    public String getAlgorithm() {
        return algorithm;
    }

    public void setAlgorithm(String algorithm) {
        this.algorithm = algorithm;
    }

    public String getSignature() {
        return signature;
    }

    public void setSignature(String signature) {
        this.signature = signature;
    }

    public String getJwksUrl() {
        return jwksUrl;
    }

    public void setJwksUrl(String jwksUrl) {
        this.jwksUrl = jwksUrl;
    }
}


package com.a2areg.sdk.models;

import com.google.gson.annotations.SerializedName;

/**
 * Agent Capabilities Object - Optional capabilities supported by the Agent.
 * Section 5.5.2 of the A2A Protocol specification.
 */
public class AgentCapabilities {
    @SerializedName("streaming")
    private Boolean streaming;

    @SerializedName("pushNotifications")
    private Boolean pushNotifications;

    @SerializedName("stateTransitionHistory")
    private Boolean stateTransitionHistory;

    @SerializedName("supportsAuthenticatedExtendedCard")
    private Boolean supportsAuthenticatedExtendedCard;

    public Boolean getStreaming() {
        return streaming;
    }

    public void setStreaming(Boolean streaming) {
        this.streaming = streaming;
    }

    public Boolean getPushNotifications() {
        return pushNotifications;
    }

    public void setPushNotifications(Boolean pushNotifications) {
        this.pushNotifications = pushNotifications;
    }

    public Boolean getStateTransitionHistory() {
        return stateTransitionHistory;
    }

    public void setStateTransitionHistory(Boolean stateTransitionHistory) {
        this.stateTransitionHistory = stateTransitionHistory;
    }

    public Boolean getSupportsAuthenticatedExtendedCard() {
        return supportsAuthenticatedExtendedCard;
    }

    public void setSupportsAuthenticatedExtendedCard(Boolean supportsAuthenticatedExtendedCard) {
        this.supportsAuthenticatedExtendedCard = supportsAuthenticatedExtendedCard;
    }
}


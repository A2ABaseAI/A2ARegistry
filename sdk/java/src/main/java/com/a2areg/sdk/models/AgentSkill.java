package com.a2areg.sdk.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

/**
 * Agent Skill Object - Collection of capability units the Agent can perform.
 * Section 5.5.4 of the A2A Protocol specification.
 */
public class AgentSkill {
    @SerializedName("id")
    private String id;

    @SerializedName("name")
    private String name;

    @SerializedName("description")
    private String description;

    @SerializedName("tags")
    private List<String> tags;

    @SerializedName("examples")
    private List<String> examples;

    @SerializedName("inputModes")
    private List<String> inputModes;

    @SerializedName("outputModes")
    private List<String> outputModes;

    public AgentSkill() {
    }

    public AgentSkill(String id, String name, String description, List<String> tags) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.tags = tags;
    }

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

    public List<String> getTags() {
        return tags;
    }

    public void setTags(List<String> tags) {
        this.tags = tags;
    }

    public List<String> getExamples() {
        return examples;
    }

    public void setExamples(List<String> examples) {
        this.examples = examples;
    }

    public List<String> getInputModes() {
        return inputModes;
    }

    public void setInputModes(List<String> inputModes) {
        this.inputModes = inputModes;
    }

    public List<String> getOutputModes() {
        return outputModes;
    }

    public void setOutputModes(List<String> outputModes) {
        this.outputModes = outputModes;
    }
}


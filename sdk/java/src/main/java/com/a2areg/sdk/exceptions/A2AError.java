package com.a2areg.sdk.exceptions;

import java.util.Map;

/**
 * Base error type for A2A Registry SDK.
 */
public class A2AError extends RuntimeException {
    private Map<String, Object> details;

    public A2AError(String message) {
        super(message);
    }

    public A2AError(String message, Map<String, Object> details) {
        super(message);
        this.details = details;
    }

    public A2AError(String message, Throwable cause) {
        super(message, cause);
    }

    public A2AError(String message, Map<String, Object> details, Throwable cause) {
        super(message, cause);
        this.details = details;
    }

    public Map<String, Object> getDetails() {
        return details;
    }

    public void setDetails(Map<String, Object> details) {
        this.details = details;
    }
}


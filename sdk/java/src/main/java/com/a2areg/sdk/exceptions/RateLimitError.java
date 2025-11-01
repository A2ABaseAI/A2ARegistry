package com.a2areg.sdk.exceptions;

import java.util.Map;

/**
 * Represents a rate limit error.
 */
public class RateLimitError extends A2AError {
    public RateLimitError(String message) {
        super(message);
    }

    public RateLimitError(String message, Map<String, Object> details) {
        super(message, details);
    }

    public RateLimitError(String message, Throwable cause) {
        super(message, cause);
    }
}


package com.a2areg.sdk.exceptions;

import java.util.Map;

/**
 * Represents a validation failure.
 */
public class ValidationError extends A2AError {
    public ValidationError(String message) {
        super(message);
    }

    public ValidationError(String message, Map<String, Object> details) {
        super(message, details);
    }

    public ValidationError(String message, Throwable cause) {
        super(message, cause);
    }
}


package com.a2areg.sdk.exceptions;

import java.util.Map;

/**
 * Represents a resource not found error.
 */
public class NotFoundError extends A2AError {
    public NotFoundError(String message) {
        super(message);
    }

    public NotFoundError(String message, Map<String, Object> details) {
        super(message, details);
    }

    public NotFoundError(String message, Throwable cause) {
        super(message, cause);
    }
}


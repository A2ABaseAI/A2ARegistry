package com.a2areg.sdk.exceptions;

import java.util.Map;

/**
 * Represents an authentication failure.
 */
public class AuthenticationError extends A2AError {
    public AuthenticationError(String message) {
        super(message);
    }

    public AuthenticationError(String message, Map<String, Object> details) {
        super(message, details);
    }

    public AuthenticationError(String message, Throwable cause) {
        super(message, cause);
    }
}


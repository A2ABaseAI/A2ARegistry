package com.a2areg.sdk.exceptions;

import java.util.Map;

/**
 * Represents a server error.
 */
public class ServerError extends A2AError {
    public ServerError(String message) {
        super(message);
    }

    public ServerError(String message, Map<String, Object> details) {
        super(message, details);
    }

    public ServerError(String message, Throwable cause) {
        super(message, cause);
    }
}


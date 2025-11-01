package com.a2areg.sdk.exceptions;

import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class A2AErrorTest {
    @Test
    void testA2AError() {
        A2AError error = new A2AError("Test error");
        assertEquals("Test error", error.getMessage());
    }

    @Test
    void testA2AErrorWithDetails() {
        Map<String, Object> details = new HashMap<>();
        details.put("code", "ERR001");
        A2AError error = new A2AError("Test error", details);
        assertEquals("Test error", error.getMessage());
        assertEquals("ERR001", error.getDetails().get("code"));
    }

    @Test
    void testAuthenticationError() {
        AuthenticationError error = new AuthenticationError("Authentication failed");
        assertEquals("Authentication failed", error.getMessage());
        assertTrue(error instanceof A2AError);
    }

    @Test
    void testValidationError() {
        Map<String, Object> details = new HashMap<>();
        details.put("field", "name");
        ValidationError error = new ValidationError("Validation failed", details);
        assertEquals("Validation failed", error.getMessage());
        assertEquals("name", error.getDetails().get("field"));
        assertTrue(error instanceof A2AError);
    }

    @Test
    void testNotFoundError() {
        NotFoundError error = new NotFoundError("Resource not found");
        assertEquals("Resource not found", error.getMessage());
        assertTrue(error instanceof A2AError);
    }

    @Test
    void testRateLimitError() {
        RateLimitError error = new RateLimitError("Rate limit exceeded");
        assertEquals("Rate limit exceeded", error.getMessage());
        assertTrue(error instanceof A2AError);
    }

    @Test
    void testServerError() {
        ServerError error = new ServerError("Server error");
        assertEquals("Server error", error.getMessage());
        assertTrue(error instanceof A2AError);
    }
}


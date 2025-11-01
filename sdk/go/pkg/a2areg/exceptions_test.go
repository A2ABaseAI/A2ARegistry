package a2areg

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestA2AError(t *testing.T) {
	err := NewA2AError("Test error", map[string]interface{}{"code": "ERR001"})
	assert.Error(t, err)
	assert.Equal(t, "Test error", err.Error())
	assert.Equal(t, "ERR001", err.Details["code"])
}

func TestA2AError_Unwrap(t *testing.T) {
	baseErr := errors.New("base error")
	a2aErr := &A2AError{
		Message: "Test error",
		Err:     baseErr,
	}

	assert.Equal(t, baseErr, a2aErr.Unwrap())
	assert.Contains(t, a2aErr.Error(), "base error")
}

func TestAuthenticationError(t *testing.T) {
	err := NewAuthenticationError("Authentication failed", nil)
	assert.Error(t, err)
	assert.IsType(t, &AuthenticationError{}, err)
	assert.NotNil(t, err.A2AError)
	assert.Equal(t, "Authentication failed", err.Error())
}

func TestValidationError(t *testing.T) {
	err := NewValidationError("Validation failed", map[string]interface{}{"field": "name"})
	assert.Error(t, err)
	assert.IsType(t, &ValidationError{}, err)
	assert.NotNil(t, err.A2AError)
	assert.Equal(t, "Validation failed", err.Error())
	assert.Equal(t, "name", err.Details["field"])
}

func TestNotFoundError(t *testing.T) {
	err := NewNotFoundError("Resource not found", map[string]interface{}{"resource": "agent"})
	assert.Error(t, err)
	assert.IsType(t, &NotFoundError{}, err)
	assert.NotNil(t, err.A2AError)
	assert.Equal(t, "Resource not found", err.Error())
}

func TestRateLimitError(t *testing.T) {
	err := NewRateLimitError("Rate limit exceeded", map[string]interface{}{"retry_after": 60})
	assert.Error(t, err)
	assert.IsType(t, &RateLimitError{}, err)
}

func TestServerError(t *testing.T) {
	err := NewServerError("Server error", nil)
	assert.Error(t, err)
	assert.IsType(t, &ServerError{}, err)
}

func TestErrorInheritance(t *testing.T) {
	tests := []struct {
		name string
		err  error
	}{
		{"AuthenticationError", NewAuthenticationError("Auth error", nil)},
		{"ValidationError", NewValidationError("Validation error", nil)},
		{"NotFoundError", NewNotFoundError("Not found error", nil)},
		{"RateLimitError", NewRateLimitError("Rate limit error", nil)},
		{"ServerError", NewServerError("Server error", nil)},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Direct check that it's an A2AError
			switch e := tt.err.(type) {
			case *AuthenticationError:
				assert.NotNil(t, e.A2AError)
			case *ValidationError:
				assert.NotNil(t, e.A2AError)
			case *NotFoundError:
				assert.NotNil(t, e.A2AError)
			case *RateLimitError:
				assert.NotNil(t, e.A2AError)
			case *ServerError:
				assert.NotNil(t, e.A2AError)
			default:
				t.Fatalf("%s should be one of the error types", tt.name)
			}
		})
	}
}


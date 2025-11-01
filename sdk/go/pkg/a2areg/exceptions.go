package a2areg

import "fmt"

// A2AError is the base error type for A2A Registry SDK.
type A2AError struct {
	Message string
	Details map[string]interface{}
	Err     error
}

func (e *A2AError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("%s: %v", e.Message, e.Err)
	}
	return e.Message
}

func (e *A2AError) Unwrap() error {
	return e.Err
}

// NewA2AError creates a new A2AError.
func NewA2AError(message string, details map[string]interface{}) *A2AError {
	return &A2AError{
		Message: message,
		Details: details,
	}
}

// AuthenticationError represents an authentication failure.
type AuthenticationError struct {
	*A2AError
}

// NewAuthenticationError creates a new AuthenticationError.
func NewAuthenticationError(message string, details map[string]interface{}) *AuthenticationError {
	return &AuthenticationError{
		A2AError: NewA2AError(message, details),
	}
}

// ValidationError represents a validation failure.
type ValidationError struct {
	*A2AError
}

// NewValidationError creates a new ValidationError.
func NewValidationError(message string, details map[string]interface{}) *ValidationError {
	return &ValidationError{
		A2AError: NewA2AError(message, details),
	}
}

// NotFoundError represents a resource not found error.
type NotFoundError struct {
	*A2AError
}

// NewNotFoundError creates a new NotFoundError.
func NewNotFoundError(message string, details map[string]interface{}) *NotFoundError {
	return &NotFoundError{
		A2AError: NewA2AError(message, details),
	}
}

// RateLimitError represents a rate limit error.
type RateLimitError struct {
	*A2AError
}

// NewRateLimitError creates a new RateLimitError.
func NewRateLimitError(message string, details map[string]interface{}) *RateLimitError {
	return &RateLimitError{
		A2AError: NewA2AError(message, details),
	}
}

// ServerError represents a server error.
type ServerError struct {
	*A2AError
}

// NewServerError creates a new ServerError.
func NewServerError(message string, details map[string]interface{}) *ServerError {
	return &ServerError{
		A2AError: NewA2AError(message, details),
	}
}


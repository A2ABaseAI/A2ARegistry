/**
 * A2A Registry Exceptions
 *
 * Custom exception classes for the A2A Registry SDK.
 */

export class A2AError extends Error {
  constructor(message: string, public readonly details?: any) {
    super(message);
    this.name = "A2AError";
    Object.setPrototypeOf(this, A2AError.prototype);
  }
}

export class AuthenticationError extends A2AError {
  constructor(message: string, details?: any) {
    super(message, details);
    this.name = "AuthenticationError";
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}

export class ValidationError extends A2AError {
  constructor(message: string, details?: any) {
    super(message, details);
    this.name = "ValidationError";
    Object.setPrototypeOf(this, ValidationError.prototype);
  }
}

export class NotFoundError extends A2AError {
  constructor(message: string, details?: any) {
    super(message, details);
    this.name = "NotFoundError";
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }
}


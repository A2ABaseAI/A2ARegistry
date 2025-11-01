/**
 * Tests for exception classes
 */

import { A2AError, AuthenticationError, ValidationError, NotFoundError } from '../src/exceptions';

describe('Exceptions', () => {
  describe('A2AError', () => {
    it('should create A2AError', () => {
      const error = new A2AError('Test error');
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(A2AError);
      expect(error.message).toBe('Test error');
      expect(error.name).toBe('A2AError');
    });

    it('should create A2AError with details', () => {
      const details = { code: 'ERR001', field: 'name' };
      const error = new A2AError('Test error', details);
      expect(error.details).toEqual(details);
    });
  });

  describe('AuthenticationError', () => {
    it('should create AuthenticationError', () => {
      const error = new AuthenticationError('Authentication failed');
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(A2AError);
      expect(error).toBeInstanceOf(AuthenticationError);
      expect(error.message).toBe('Authentication failed');
      expect(error.name).toBe('AuthenticationError');
    });

    it('should create AuthenticationError with details', () => {
      const details = { code: 'AUTH_001' };
      const error = new AuthenticationError('Auth failed', details);
      expect(error.details).toEqual(details);
    });
  });

  describe('ValidationError', () => {
    it('should create ValidationError', () => {
      const error = new ValidationError('Validation failed');
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(A2AError);
      expect(error).toBeInstanceOf(ValidationError);
      expect(error.message).toBe('Validation failed');
      expect(error.name).toBe('ValidationError');
    });

    it('should create ValidationError with details', () => {
      const details = { field: 'name', reason: 'required' };
      const error = new ValidationError('Invalid field', details);
      expect(error.details).toEqual(details);
    });
  });

  describe('NotFoundError', () => {
    it('should create NotFoundError', () => {
      const error = new NotFoundError('Resource not found');
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(A2AError);
      expect(error).toBeInstanceOf(NotFoundError);
      expect(error.message).toBe('Resource not found');
      expect(error.name).toBe('NotFoundError');
    });

    it('should create NotFoundError with details', () => {
      const details = { resource: 'agent', id: 'agent-123' };
      const error = new NotFoundError('Agent not found', details);
      expect(error.details).toEqual(details);
    });
  });

  describe('Error inheritance', () => {
    it('should properly inherit from Error', () => {
      const errors = [
        new A2AError('Base error'),
        new AuthenticationError('Auth error'),
        new ValidationError('Validation error'),
        new NotFoundError('Not found error'),
      ];

      errors.forEach((error) => {
        expect(error).toBeInstanceOf(Error);
        expect(error.stack).toBeDefined();
      });
    });

    it('should properly inherit from A2AError', () => {
      const authError = new AuthenticationError('Auth error');
      const validationError = new ValidationError('Validation error');
      const notFoundError = new NotFoundError('Not found error');

      expect(authError).toBeInstanceOf(A2AError);
      expect(validationError).toBeInstanceOf(A2AError);
      expect(notFoundError).toBeInstanceOf(A2AError);
    });
  });
});


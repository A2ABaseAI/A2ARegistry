# Contributing to A2A Agent Registry

Thank you for your interest in contributing to the A2A Agent Registry! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:
1. Check if the issue already exists
2. Use the appropriate issue template
3. Provide clear reproduction steps
4. Include relevant system information

### Types of Issues

- **Bug Reports**: Use the bug report template
- **Feature Requests**: Use the feature request template
- **Documentation**: Use the documentation template
- **Security**: Report security issues privately to security@a2areg.dev

### Making Changes

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Run tests**: `pytest tests/`
7. **Commit your changes**: `git commit -m "Add your feature"`
8. **Push to your fork**: `git push origin feature/your-feature-name`
9. **Create a Pull Request**

## 🏗️ Development Setup

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- PostgreSQL 12+
- Redis 6+
- Elasticsearch 8+

### Local Development

1. **Clone your fork**:
   ```bash
   git clone https://github.com/A2AReg/a2a-registry.git
   cd a2a-registry
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Start services**:
   ```bash
   docker-compose up -d
   ```

5. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Initialize sample data**:
   ```bash
   python scripts/init_db.py
   ```

7. **Start the application**:
   ```bash
   python -m registry.main
   ```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_agents.py

# Run with verbose output
pytest -v tests/
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

## 📝 Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints
- Write docstrings for all public functions
- Keep functions small and focused
- Use meaningful variable names

### API Design

- Follow RESTful conventions
- Use appropriate HTTP status codes
- Provide clear error messages
- Include request/response examples
- Version APIs appropriately

### Database

- Use migrations for schema changes
- Include rollback procedures
- Test migrations on sample data
- Document schema changes

### Security

- Validate all inputs
- Use parameterized queries
- Implement proper authentication
- Follow OWASP guidelines
- Regular security audits

## 🧪 Testing Guidelines

### Test Structure

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints and database interactions
- **End-to-End Tests**: Test complete workflows

### Test Naming

```python
def test_create_agent_with_valid_data():
    """Test creating an agent with valid data."""
    pass

def test_create_agent_with_invalid_data_returns_error():
    """Test creating an agent with invalid data returns error."""
    pass
```

### Test Data

- Use factories for test data generation
- Clean up test data after each test
- Use realistic test data
- Avoid hardcoded values

### Coverage Requirements

- Aim for 90%+ code coverage
- Focus on critical paths
- Test error conditions
- Include edge cases

## 📚 Documentation

### Code Documentation

- Use docstrings for all public functions
- Include type hints
- Provide usage examples
- Document complex algorithms

### API Documentation

- Keep OpenAPI specs up to date
- Include request/response examples
- Document error codes
- Provide integration guides

### User Documentation

- Write clear README files
- Provide setup instructions
- Include troubleshooting guides
- Keep examples current

## 🔄 Pull Request Process

### Before Submitting

1. **Run all tests**: `pytest tests/`
2. **Check code style**: `black app/ && flake8 app/`
3. **Update documentation**
4. **Add tests for new features**
5. **Update CHANGELOG.md**

### PR Description

Include:
- Summary of changes
- Motivation for changes
- Testing performed
- Breaking changes (if any)
- Screenshots (if UI changes)

### Review Process

1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Testing** in staging environment
4. **Documentation review**
5. **Security review** (if applicable)

### After Approval

- Squash commits if requested
- Update branch with latest main
- Address any final feedback
- Maintainers will merge

## 🏷️ Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Release notes prepared
- [ ] Docker images built
- [ ] Security scan completed

## 🛡️ Security

### Reporting Security Issues

**Do not** report security issues through public GitHub issues.

Instead:
1. Email security@a2areg.dev
2. Include detailed description
3. Provide reproduction steps
4. Wait for response before disclosure

### Security Guidelines

- Never commit secrets or credentials
- Use environment variables for configuration
- Validate all inputs
- Implement proper authentication
- Regular dependency updates
- Security-focused code reviews

## 🌍 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect different viewpoints
- Help others learn

### Getting Help

- **Documentation**: Check README and docs/
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions
- **Discord**: [Join our community chat](https://discord.gg/rpe5nMSumw) for real-time help
- **Email**: Contact maintainers

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation
- Community highlights

## 📋 Issue Templates

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior.

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.9.7]
- Registry version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem.
```

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request.
```

## 🎯 Areas for Contribution

### High Priority

- **Performance optimization**
- **Security enhancements**
- **Documentation improvements**
- **Test coverage**
- **Error handling**

### Medium Priority

- **New features**
- **UI/UX improvements**
- **Integration examples**
- **Monitoring enhancements**
- **Deployment tools**

### Low Priority

- **Code refactoring**
- **Style improvements**
- **Minor bug fixes**
- **Documentation updates**

## 📞 Contact

- **Discord**: [Join our community chat](https://discord.gg/rpe5nMSumw) for real-time discussions
- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Email**: maintainers@a2areg.dev
- **Security**: security@a2areg.dev

Thank you for contributing to the A2A Agent Registry! 🚀

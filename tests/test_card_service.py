"""Tests for registry/services/card_service.py - Card service functionality."""

from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException, status

from registry.schemas.agent_card_spec import AgentCardSpec
from registry.services.card_service import CardService

from .base_test import BaseTest


class TestCardService(BaseTest):
    """Tests for CardService."""

    def test_fetch_card_from_url_success(self):
        """Test successfully fetching card from URL."""
        card_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "url": "https://test.example.com",
            "version": "1.0.0",
            "capabilities": {"streaming": False},
            "securitySchemes": [{"type": "apiKey", "location": "header", "name": "X-API-Key"}],
            "skills": [],
            "interface": {
                "preferredTransport": "jsonrpc",
                "defaultInputModes": ["text/plain"],
                "defaultOutputModes": ["text/plain"],
            },
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.content = b'{"name": "Test Agent"}'
        mock_response.json.return_value = card_data
        mock_response.raise_for_status = MagicMock()

        with patch("registry.services.card_service.httpx.get", return_value=mock_response):
            with patch("registry.services.card_service.httpx.Timeout", return_value=MagicMock()):
                result = CardService.fetch_card_from_url("https://test.example.com/card.json")
                assert result == card_data

    def test_fetch_card_from_url_http_not_allowed(self):
        """Test that HTTP URLs are rejected."""
        with pytest.raises(HTTPException) as exc_info:
            CardService.fetch_card_from_url("http://test.example.com/card.json")
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "HTTPS" in exc_info.value.detail

    def test_fetch_card_from_url_invalid_content_type(self):
        """Test that non-JSON content types are rejected."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_response.raise_for_status = MagicMock()

        with patch("registry.services.card_service.httpx.get", return_value=mock_response):
            with patch("registry.services.card_service.httpx.Timeout", return_value=MagicMock()):
                with pytest.raises(HTTPException) as exc_info:
                    CardService.fetch_card_from_url("https://test.example.com/card.json")
                assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
                assert "application/json" in exc_info.value.detail

    def test_fetch_card_from_url_size_limit(self):
        """Test that cards exceeding size limit are rejected."""
        large_content = b"x" * (256 * 1024 + 1)  # 256KB + 1 byte

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.content = large_content
        mock_response.raise_for_status = MagicMock()

        with patch("registry.services.card_service.httpx.get", return_value=mock_response):
            with patch("registry.services.card_service.httpx.Timeout", return_value=MagicMock()):
                with pytest.raises(HTTPException) as exc_info:
                    CardService.fetch_card_from_url("https://test.example.com/card.json")
                assert exc_info.value.status_code == status.HTTP_413_CONTENT_TOO_LARGE

    def test_fetch_card_from_url_http_error(self):
        """Test handling of HTTP errors."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=MagicMock())

        with patch("registry.services.card_service.httpx.get", return_value=mock_response):
            with pytest.raises(HTTPException) as exc_info:
                CardService.fetch_card_from_url("https://test.example.com/card.json")
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    def test_parse_and_validate_card_with_card_data(self):
        """Test parsing and validating card from request body."""
        card_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "url": "https://test.example.com",
            "version": "1.0.0",
            "capabilities": {"streaming": False},
            "securitySchemes": [{"type": "apiKey", "location": "header", "name": "X-API-Key"}],
            "skills": [],
            "interface": {
                "preferredTransport": "jsonrpc",
                "defaultInputModes": ["text/plain"],
                "defaultOutputModes": ["text/plain"],
            },
        }

        body = {"card": card_data}
        result_data, result_url, result_hash = CardService.parse_and_validate_card(body)

        # securitySchemes is converted from list to dict during validation
        assert result_data["name"] == card_data["name"]
        assert result_data["description"] == card_data["description"]
        assert isinstance(result_data["securitySchemes"], dict)
        assert result_url is None
        assert result_hash is not None
        assert len(result_hash) == 64  # SHA256 hash length

    def test_parse_and_validate_card_with_card_url(self):
        """Test parsing and validating card from URL."""
        card_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "url": "https://test.example.com",
            "version": "1.0.0",
            "capabilities": {"streaming": False},
            "securitySchemes": [{"type": "apiKey"}],
            "skills": [],
            "interface": {
                "preferredTransport": "jsonrpc",
                "defaultInputModes": ["text/plain"],
                "defaultOutputModes": ["text/plain"],
            },
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.content = b'{"name": "Test Agent"}'
        mock_response.json.return_value = card_data
        mock_response.raise_for_status = MagicMock()

        body = {"cardUrl": "https://test.example.com/card.json"}

        with patch("registry.services.card_service.httpx.get", return_value=mock_response):
            with patch("registry.services.card_service.httpx.Timeout", return_value=MagicMock()):
                result_data, result_url, result_hash = CardService.parse_and_validate_card(body)

                # securitySchemes is converted from list to dict during validation
                assert result_data["name"] == card_data["name"]
                assert isinstance(result_data["securitySchemes"], dict)
                assert result_url == "https://test.example.com/card.json"
                assert result_hash is not None

    def test_parse_and_validate_card_invalid_card(self):
        """Test that invalid card data is rejected."""
        invalid_card_data = {
            "name": "Test Agent",
            # Missing required fields like description, url, version, etc.
        }

        body = {"card": invalid_card_data}
        with pytest.raises(HTTPException) as exc_info:
            CardService.parse_and_validate_card(body)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid agent card" in exc_info.value.detail

    def test_validate_card_data_success(self):
        """Test successful card data validation."""
        card_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "url": "https://test.example.com",
            "version": "1.0.0",
            "capabilities": {"streaming": False},
            "securitySchemes": [{"type": "apiKey", "location": "header", "name": "X-API-Key"}],
            "skills": [],
            "interface": {
                "preferredTransport": "jsonrpc",
                "defaultInputModes": ["text/plain"],
                "defaultOutputModes": ["text/plain"],
            },
        }

        result = CardService.validate_card_data(card_data)
        assert isinstance(result, AgentCardSpec)
        assert result.name == "Test Agent"
        assert result.version == "1.0.0"

    def test_validate_card_data_invalid(self):
        """Test that invalid card data raises exception."""
        invalid_card_data = {
            "name": "Test Agent",
            # Missing required fields
        }
        with pytest.raises(HTTPException) as exc_info:
            CardService.validate_card_data(invalid_card_data)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid agent card" in exc_info.value.detail

    def test_validate_card_data_with_all_fields(self):
        """Test validation with all optional fields."""
        card_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "url": "https://test.example.com",
            "version": "1.0.0",
            "provider": {"organization": "Test Org", "url": "https://test.org"},
            "capabilities": {
                "streaming": True,
                "pushNotifications": True,
                "stateTransitionHistory": True,
                "supportsAuthenticatedExtendedCard": True,
            },
            "securitySchemes": [
                {"type": "apiKey", "location": "header", "name": "X-API-Key"},
                {
                    "type": "oauth2",
                    "flow": "client_credentials",
                    "tokenUrl": "https://test.org/token",
                    "scopes": ["read", "write"],
                },
            ],
            "skills": [
                {
                    "id": "skill1",
                    "name": "Skill 1",
                    "description": "First skill",
                    "tags": ["test"],
                    "examples": ["Example 1"],
                    "inputModes": ["text/plain"],
                    "outputModes": ["application/json"],
                }
            ],
            "interface": {
                "preferredTransport": "jsonrpc",
                "defaultInputModes": ["text/plain", "application/json"],
                "defaultOutputModes": ["text/plain", "application/json"],
                "additionalInterfaces": [{"transport": "http", "url": "https://test.example.com/api"}],
            },
            "documentationUrl": "https://test.example.com/docs",
            "signature": {
                "algorithm": "RS256",
                "jwksUrl": "https://test.example.com/.well-known/jwks.json",
            },
        }

        result = CardService.validate_card_data(card_data)
        assert isinstance(result, AgentCardSpec)
        assert result.name == "Test Agent"
        assert result.provider is not None
        assert result.provider.organization == "Test Org"
        assert len(result.securitySchemes) == 2
        assert len(result.skills) == 1
        assert result.documentationUrl is not None
        assert str(result.documentationUrl) == "https://test.example.com/docs"
        assert result.signature is not None
        assert result.signature.algorithm == "RS256"
        assert result.signature.jwksUrl is not None
        assert str(result.signature.jwksUrl) == "https://test.example.com/.well-known/jwks.json"

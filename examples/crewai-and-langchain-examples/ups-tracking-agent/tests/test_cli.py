"""Tests for CLI functionality."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from typer.testing import CliRunner

from ups_agent.cli import app


class TestCLI:
    """Test CLI functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.runner = CliRunner()
    
    @patch('ups_agent.cli.settings')
    @patch('ups_agent.cli.UPSClient')
    @patch('ups_agent.cli.UPSStatusAgent')
    def test_main_with_tracking_number(self, mock_agent_class, mock_client_class, mock_settings):
        """Test CLI with tracking number."""
        # Mock settings
        mock_settings.ups_client_id = "test_client_id"
        mock_settings.ups_client_secret = "test_client_secret"
        mock_settings.ups_account_number = "test_account"
        mock_settings.ups_api_base = "https://test.ups.com"
        mock_settings.ups_use_sandbox = False
        mock_settings.crewai_model = "gpt-4o-mini"
        mock_settings.crewai_temperature = 0.1
        mock_settings.validate_ups_credentials.return_value = None
        mock_settings.validate_openai_credentials.return_value = None
        
        # Mock agent
        mock_agent = Mock()
        mock_agent.process_query = AsyncMock(return_value="Package delivered successfully")
        mock_agent_class.return_value = mock_agent
        
        # Mock client
        mock_client = Mock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        result = self.runner.invoke(app, ["1Z999AA10123456784"])
        
        assert result.exit_code == 0
        assert "Package delivered successfully" in result.output
    
    @patch('ups_agent.cli.settings')
    @patch('ups_agent.cli.UPSClient')
    @patch('ups_agent.cli.UPSStatusAgent')
    def test_main_with_json_output(self, mock_agent_class, mock_client_class, mock_settings):
        """Test CLI with JSON output."""
        # Mock settings
        mock_settings.ups_client_id = "test_client_id"
        mock_settings.ups_client_secret = "test_client_secret"
        mock_settings.ups_account_number = "test_account"
        mock_settings.ups_api_base = "https://test.ups.com"
        mock_settings.ups_use_sandbox = False
        mock_settings.crewai_model = "gpt-4o-mini"
        mock_settings.crewai_temperature = 0.1
        mock_settings.validate_ups_credentials.return_value = None
        mock_settings.validate_openai_credentials.return_value = None
        
        # Mock agent
        mock_agent = Mock()
        mock_agent.process_query = AsyncMock(return_value='{"tracking_number": "1Z999AA10123456784", "status": "delivered"}')
        mock_agent_class.return_value = mock_agent
        
        # Mock client
        mock_client = Mock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        result = self.runner.invoke(app, ["1Z999AA10123456784", "--json"])
        
        assert result.exit_code == 0
        assert "tracking_number" in result.output
    
    @patch('ups_agent.cli.settings')
    def test_main_missing_credentials(self, mock_settings):
        """Test CLI with missing credentials."""
        mock_settings.validate_ups_credentials.side_effect = ValueError("UPS_CLIENT_ID is required")
        
        result = self.runner.invoke(app, ["1Z999AA10123456784"])
        
        assert result.exit_code == 1
        assert "UPS_CLIENT_ID is required" in result.output
    
    @patch('ups_agent.cli.settings')
    def test_main_missing_openai_credentials(self, mock_settings):
        """Test CLI with missing OpenAI credentials."""
        mock_settings.validate_ups_credentials.return_value = None
        mock_settings.validate_openai_credentials.side_effect = ValueError("OPENAI_API_KEY is required")
        
        result = self.runner.invoke(app, ["1Z999AA10123456784"])
        
        assert result.exit_code == 1
        assert "OPENAI_API_KEY is required" in result.output
    
    @patch('ups_agent.cli.settings')
    def test_main_with_sandbox(self, mock_settings):
        """Test CLI with sandbox flag."""
        mock_settings.ups_client_id = "test_client_id"
        mock_settings.ups_client_secret = "test_client_secret"
        mock_settings.ups_account_number = "test_account"
        mock_settings.ups_api_base = "https://test.ups.com"
        mock_settings.ups_use_sandbox = False
        mock_settings.crewai_model = "gpt-4o-mini"
        mock_settings.crewai_temperature = 0.1
        mock_settings.validate_ups_credentials.return_value = None
        mock_settings.validate_openai_credentials.return_value = None
        
        result = self.runner.invoke(app, ["1Z999AA10123456784", "--sandbox"])
        
        # Should set sandbox mode
        assert mock_settings.ups_use_sandbox == True
        assert mock_settings.ups_api_base == "https://wwwcie.ups.com"
    
    @patch('ups_agent.cli.settings')
    def test_health_command_success(self, mock_settings):
        """Test health command with valid credentials."""
        mock_settings.ups_client_id = "test_client_id"
        mock_settings.ups_client_secret = "test_client_secret"
        mock_settings.ups_account_number = "test_account"
        mock_settings.ups_api_base = "https://test.ups.com"
        mock_settings.ups_use_sandbox = False
        mock_settings.validate_ups_credentials.return_value = None
        mock_settings.validate_openai_credentials.return_value = None
        
        with patch('ups_agent.cli.UPSClient') as mock_client_class:
            mock_client = Mock()
            mock_client._get_access_token = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client
            
            result = self.runner.invoke(app, ["health"])
            
            assert result.exit_code == 0
            assert "UPS credentials configured" in result.output
            assert "OpenAI credentials configured" in result.output
            assert "UPS API connection successful" in result.output
    
    @patch('ups_agent.cli.settings')
    def test_health_command_missing_credentials(self, mock_settings):
        """Test health command with missing credentials."""
        mock_settings.validate_ups_credentials.side_effect = ValueError("UPS_CLIENT_ID is required")
        
        result = self.runner.invoke(app, ["health"])
        
        assert result.exit_code == 0  # Health command doesn't exit on missing credentials
        assert "UPS credentials error" in result.output
    
    @patch('ups_agent.cli.settings')
    def test_health_command_api_failure(self, mock_settings):
        """Test health command with API failure."""
        mock_settings.ups_client_id = "test_client_id"
        mock_settings.ups_client_secret = "test_client_secret"
        mock_settings.ups_account_number = "test_account"
        mock_settings.ups_api_base = "https://test.ups.com"
        mock_settings.ups_use_sandbox = False
        mock_settings.validate_ups_credentials.return_value = None
        mock_settings.validate_openai_credentials.return_value = None
        
        with patch('ups_agent.cli.UPSClient') as mock_client_class:
            mock_client = Mock()
            mock_client._get_access_token = AsyncMock(side_effect=Exception("API error"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client
            
            result = self.runner.invoke(app, ["health"])
            
            assert result.exit_code == 0
            assert "UPS API connection failed" in result.output
    
    def test_help_command(self):
        """Test help command."""
        result = self.runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "CrewAI agent for UPS shipment tracking" in result.output
        assert "Track UPS shipments using CrewAI agent" in result.output
    
    def test_version_command(self):
        """Test version command."""
        result = self.runner.invoke(app, ["--version"])
        
        assert result.exit_code == 0
        assert "ups-agent" in result.output

"""Tests for UPS client authentication and tracking."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from ups_agent.client import UPSClient, UPSCredentialsError, UPSTrackingError
from ups_agent.models import UPSTrackingResponse, UPSAuthResponse


class TestUPSClient:
    """Test UPS client functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = UPSClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            account_number="test_account",
            api_base="https://test.ups.com"
        )
    
    def test_validate_tracking_number_valid(self):
        """Test valid tracking number validation."""
        valid_numbers = [
            "1Z999AA10123456784",
            "1M999BB20234567895",
            "123456789012345678",
            "ABC123DEF456GHI789",
        ]
        
        for tn in valid_numbers:
            assert self.client._validate_tracking_number(tn)
    
    def test_validate_tracking_number_invalid(self):
        """Test invalid tracking number validation."""
        invalid_numbers = [
            "",
            "123",  # Too short
            "123456789012345678901234567890",  # Too long
            "1Z999AA10123456784!",  # Special characters
            "1z999aa10123456784",  # Lowercase
        ]
        
        for tn in invalid_numbers:
            assert not self.client._validate_tracking_number(tn)
    
    @pytest.mark.asyncio
    async def test_get_access_token_success(self):
        """Test successful OAuth token retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "tracking"
        }
        
        with patch.object(self.client, '_client') as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)
            
            token = await self.client._get_access_token()
            
            assert token == "test_token"
            assert self.client._access_token == "test_token"
            assert self.client._token_expires_at is not None
    
    @pytest.mark.asyncio
    async def test_get_access_token_failure(self):
        """Test OAuth token retrieval failure."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        with patch.object(self.client, '_client') as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)
            
            with pytest.raises(UPSCredentialsError):
                await self.client._get_access_token()
    
    @pytest.mark.asyncio
    async def test_get_access_token_network_error(self):
        """Test OAuth token retrieval network error."""
        with patch.object(self.client, '_client') as mock_client:
            mock_client.post = AsyncMock(side_effect=Exception("Network error"))
            
            with pytest.raises(UPSCredentialsError):
                await self.client._get_access_token()
    
    @pytest.mark.asyncio
    async def test_track_success(self):
        """Test successful tracking."""
        # Mock OAuth response
        auth_response = Mock()
        auth_response.status_code = 200
        auth_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 3600
        }
        
        # Mock tracking response
        tracking_response = Mock()
        tracking_response.status_code = 200
        tracking_response.json.return_value = {
            "trackResponse": {
                "shipment": [{
                    "service": {"description": "UPS Ground"},
                    "package": {
                        "weight": {"value": "5.0", "unitOfMeasurement": {"code": "LBS"}},
                        "activity": [{
                            "date": "20240115",
                            "time": "143000",
                            "location": {
                                "address": {
                                    "city": "San Francisco",
                                    "stateProvinceCode": "CA"
                                }
                            },
                            "status": {
                                "description": "Delivered",
                                "type": "D"
                            }
                        }],
                        "deliveryDate": {
                            "date": "20240115",
                            "time": "143000"
                        }
                    }
                }]
            }
        }
        
        with patch.object(self.client, '_client') as mock_client:
            mock_client.post = AsyncMock(return_value=auth_response)
            mock_client.get = AsyncMock(return_value=tracking_response)
            
            result = await self.client.track("1Z999AA10123456784")
            
            assert isinstance(result, UPSTrackingResponse)
            assert result.tracking_number == "1Z999AA10123456784"
            assert result.service == "UPS Ground"
            assert result.weight == "5.0 LBS"
            assert len(result.activities) == 1
            assert result.activities[0]["description"] == "Delivered"
    
    @pytest.mark.asyncio
    async def test_track_not_found(self):
        """Test tracking number not found."""
        auth_response = Mock()
        auth_response.status_code = 200
        auth_response.json.return_value = {"access_token": "test_token", "expires_in": 3600}
        
        tracking_response = Mock()
        tracking_response.status_code = 404
        
        with patch.object(self.client, '_client') as mock_client:
            mock_client.post = AsyncMock(return_value=auth_response)
            mock_client.get = AsyncMock(return_value=tracking_response)
            
            with pytest.raises(UPSTrackingError, match="Tracking number not found"):
                await self.client.track("1Z999AA10123456784")
    
    @pytest.mark.asyncio
    async def test_track_invalid_tracking_number(self):
        """Test tracking with invalid tracking number."""
        with pytest.raises(UPSTrackingError, match="Invalid tracking number format"):
            await self.client.track("invalid")
    
    @pytest.mark.asyncio
    async def test_track_multiple_success(self):
        """Test tracking multiple shipments."""
        tracking_numbers = ["1Z999AA10123456784", "1Z888BB20234567895"]
        
        # Mock responses for both tracking numbers
        auth_response = Mock()
        auth_response.status_code = 200
        auth_response.json.return_value = {"access_token": "test_token", "expires_in": 3600}
        
        tracking_response = Mock()
        tracking_response.status_code = 200
        tracking_response.json.return_value = {
            "trackResponse": {
                "shipment": [{
                    "package": {
                        "activity": [{
                            "date": "20240115",
                            "time": "143000",
                            "status": {"description": "Delivered", "type": "D"}
                        }]
                    }
                }]
            }
        }
        
        with patch.object(self.client, '_client') as mock_client:
            mock_client.post = AsyncMock(return_value=auth_response)
            mock_client.get = AsyncMock(return_value=tracking_response)
            
            results = await self.client.track_multiple(tracking_numbers)
            
            assert len(results) == 2
            assert all(isinstance(r, UPSTrackingResponse) for r in results)
            assert results[0].tracking_number == "1Z999AA10123456784"
            assert results[1].tracking_number == "1Z888BB20234567895"
    
    @pytest.mark.asyncio
    async def test_track_multiple_with_errors(self):
        """Test tracking multiple shipments with some errors."""
        tracking_numbers = ["1Z999AA10123456784", "invalid", "1Z888BB20234567895"]
        
        auth_response = Mock()
        auth_response.status_code = 200
        auth_response.json.return_value = {"access_token": "test_token", "expires_in": 3600}
        
        tracking_response = Mock()
        tracking_response.status_code = 200
        tracking_response.json.return_value = {
            "trackResponse": {
                "shipment": [{
                    "package": {
                        "activity": [{
                            "date": "20240115",
                            "time": "143000",
                            "status": {"description": "Delivered", "type": "D"}
                        }]
                    }
                }]
            }
        }
        
        with patch.object(self.client, '_client') as mock_client:
            mock_client.post = AsyncMock(return_value=auth_response)
            mock_client.get = AsyncMock(return_value=tracking_response)
            
            results = await self.client.track_multiple(tracking_numbers)
            
            # Should return successful results only
            assert len(results) == 2
            assert results[0].tracking_number == "1Z999AA10123456784"
            assert results[1].tracking_number == "1Z888BB20234567895"
    
    def test_parse_tracking_response(self):
        """Test parsing UPS tracking response."""
        raw_data = {
            "trackResponse": {
                "shipment": [{
                    "service": {"description": "UPS Ground"},
                    "package": {
                        "weight": {"value": "5.0", "unitOfMeasurement": {"code": "LBS"}},
                        "activity": [{
                            "date": "20240115",
                            "time": "143000",
                            "location": {
                                "address": {
                                    "city": "San Francisco",
                                    "stateProvinceCode": "CA"
                                }
                            },
                            "status": {
                                "description": "Delivered",
                                "type": "D"
                            }
                        }],
                        "deliveryDate": {
                            "date": "20240115",
                            "time": "143000"
                        }
                    }
                }]
            }
        }
        
        result = self.client._parse_tracking_response("1Z999AA10123456784", raw_data)
        
        assert result.tracking_number == "1Z999AA10123456784"
        assert result.service == "UPS Ground"
        assert result.weight == "5.0 LBS"
        assert result.status_description == "Delivered"
        assert result.last_location == "San Francisco, CA"
        assert len(result.activities) == 1
        assert result.activities[0]["description"] == "Delivered"
    
    def test_parse_tracking_response_error(self):
        """Test parsing UPS tracking response with error."""
        raw_data = {"invalid": "data"}
        
        with pytest.raises(UPSTrackingError, match="Failed to parse UPS tracking response"):
            self.client._parse_tracking_response("1Z999AA10123456784", raw_data)
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with self.client as client:
            assert client._client is not None
        
        # Client should be closed after context
        assert self.client._client is None

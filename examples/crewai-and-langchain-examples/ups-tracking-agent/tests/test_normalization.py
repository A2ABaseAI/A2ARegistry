"""Tests for UPS normalization layer."""

import pytest
from datetime import datetime
from unittest.mock import Mock

from ups_agent.models import UPSTrackingResponse, ShipmentStatus, Checkpoint
from ups_agent.normalizer import UPSNormalizer


class TestUPSNormalizer:
    """Test UPS normalizer functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.normalizer = UPSNormalizer()
    
    def test_normalize_label_created(self):
        """Test normalization of label created status."""
        ups_response = UPSTrackingResponse(
            tracking_number="1Z999AA10123456784",
            status_description="Origin Scan",
            activities=[
                {
                    "timestamp": "20240115",
                    "time": "100000",
                    "location": {"city": "Atlanta", "stateProvinceCode": "GA"},
                    "description": "Origin Scan",
                    "type": "OR",
                }
            ]
        )
        
        result = self.normalizer.normalize(ups_response)
        
        assert result.tracking_number == "1Z999AA10123456784"
        assert result.status_code == "LABEL_CREATED"
        assert "Origin Scan" in result.status_text
        assert len(result.checkpoints) == 1
        assert result.checkpoints[0].description == "Origin Scan"
    
    def test_normalize_in_transit(self):
        """Test normalization of in transit status."""
        ups_response = UPSTrackingResponse(
            tracking_number="1Z999AA10123456784",
            status_description="In Transit",
            activities=[
                {
                    "timestamp": "20240115",
                    "time": "140000",
                    "location": {"city": "Louisville", "stateProvinceCode": "KY"},
                    "description": "In Transit",
                    "type": "IT",
                }
            ]
        )
        
        result = self.normalizer.normalize(ups_response)
        
        assert result.status_code == "IN_TRANSIT"
        assert "In Transit" in result.status_text
        assert result.last_location == "Louisville, KY"
    
    def test_normalize_out_for_delivery(self):
        """Test normalization of out for delivery status."""
        ups_response = UPSTrackingResponse(
            tracking_number="1Z999AA10123456784",
            status_description="Out for Delivery",
            activities=[
                {
                    "timestamp": "20240116",
                    "time": "080000",
                    "location": {"city": "San Francisco", "stateProvinceCode": "CA"},
                    "description": "Out for Delivery",
                    "type": "OD",
                }
            ]
        )
        
        result = self.normalizer.normalize(ups_response)
        
        assert result.status_code == "OUT_FOR_DELIVERY"
        assert "Out for Delivery" in result.status_text
    
    def test_normalize_delivered(self):
        """Test normalization of delivered status."""
        ups_response = UPSTrackingResponse(
            tracking_number="1Z999AA10123456784",
            status_description="Delivered",
            delivered_at=datetime(2024, 1, 16, 14, 30),
            activities=[
                {
                    "timestamp": "20240116",
                    "time": "143000",
                    "location": {"city": "San Francisco", "stateProvinceCode": "CA"},
                    "description": "Delivered",
                    "type": "D",
                }
            ]
        )
        
        result = self.normalizer.normalize(ups_response)
        
        assert result.status_code == "DELIVERED"
        assert result.delivered_at == datetime(2024, 1, 16, 14, 30)
        assert "Delivered" in result.status_text
    
    def test_normalize_exception(self):
        """Test normalization of exception status."""
        ups_response = UPSTrackingResponse(
            tracking_number="1Z999AA10123456784",
            status_description="Exception",
            activities=[
                {
                    "timestamp": "20240115",
                    "time": "120000",
                    "location": {"city": "Louisville", "stateProvinceCode": "KY"},
                    "description": "Exception",
                    "type": "EX",
                }
            ]
        )
        
        result = self.normalizer.normalize(ups_response)
        
        assert result.status_code == "EXCEPTION"
        assert "Exception" in result.status_text
    
    def test_normalize_customs(self):
        """Test normalization of customs status."""
        ups_response = UPSTrackingResponse(
            tracking_number="1Z999AA10123456784",
            status_description="Customs",
            activities=[
                {
                    "timestamp": "20240115",
                    "time": "100000",
                    "location": {"city": "Louisville", "stateProvinceCode": "KY"},
                    "description": "Customs",
                    "type": "CU",
                }
            ]
        )
        
        result = self.normalizer.normalize(ups_response)
        
        assert result.status_code == "CUSTOMS"
        assert "Customs" in result.status_text
    
    def test_normalize_unknown_status(self):
        """Test normalization of unknown status."""
        ups_response = UPSTrackingResponse(
            tracking_number="1Z999AA10123456784",
            status_description="Unknown Status",
            activities=[]
        )
        
        result = self.normalizer.normalize(ups_response)
        
        assert result.status_code == "UNKNOWN"
        assert "Unknown Status" in result.status_text
    
    def test_create_checkpoints(self):
        """Test checkpoint creation from activities."""
        activities = [
            {
                "timestamp": "20240115",
                "time": "100000",
                "location": {"city": "Atlanta", "stateProvinceCode": "GA"},
                "description": "Origin Scan",
                "type": "OR",
            },
            {
                "timestamp": "20240115",
                "time": "140000",
                "location": {"city": "Louisville", "stateProvinceCode": "KY"},
                "description": "In Transit",
                "type": "IT",
            }
        ]
        
        checkpoints = self.normalizer._create_checkpoints(activities)
        
        assert len(checkpoints) == 2
        assert checkpoints[0].description == "Origin Scan"
        assert checkpoints[0].location == "Atlanta, GA"
        assert checkpoints[1].description == "In Transit"
        assert checkpoints[1].location == "Louisville, KY"
    
    def test_parse_activity_timestamp(self):
        """Test timestamp parsing from activities."""
        activity = {
            "timestamp": "20240115",
            "time": "143000",
        }
        
        timestamp = self.normalizer._parse_activity_timestamp(activity)
        
        assert timestamp.year == 2024
        assert timestamp.month == 1
        assert timestamp.day == 15
        assert timestamp.hour == 14
        assert timestamp.minute == 30
        assert timestamp.second == 0
    
    def test_is_package_stale(self):
        """Test staleness detection."""
        # Recent checkpoint (not stale)
        recent_checkpoint = Checkpoint(
            timestamp=datetime.now(),
            location="San Francisco, CA",
            description="Out for Delivery"
        )
        
        # Old checkpoint (stale)
        old_checkpoint = Checkpoint(
            timestamp=datetime.now().replace(hour=datetime.now().hour - 50),  # 50 hours ago
            location="Louisville, KY", 
            description="In Transit"
        )
        
        assert not self.normalizer._is_package_stale([recent_checkpoint])
        assert self.normalizer._is_package_stale([old_checkpoint])
    
    def test_normalize_multiple(self):
        """Test normalizing multiple responses."""
        ups_responses = [
            UPSTrackingResponse(
                tracking_number="1Z999AA10123456784",
                status_description="In Transit",
                activities=[]
            ),
            UPSTrackingResponse(
                tracking_number="1Z888BB20234567895",
                status_description="Delivered",
                delivered_at=datetime(2024, 1, 16, 14, 30),
                activities=[]
            )
        ]
        
        results = self.normalizer.normalize_multiple(ups_responses)
        
        assert len(results) == 2
        assert results[0].tracking_number == "1Z999AA10123456784"
        assert results[0].status_code == "IN_TRANSIT"
        assert results[1].tracking_number == "1Z888BB20234567895"
        assert results[1].status_code == "DELIVERED"
    
    def test_explain_method(self):
        """Test ShipmentStatus explain method."""
        status = ShipmentStatus(
            tracking_number="1Z999AA10123456784",
            status_code="IN_TRANSIT",
            status_text="Package is in transit",
            last_location="Louisville, KY",
            estimated_delivery=datetime(2024, 1, 17, 18, 0),
            checkpoints=[]
        )
        
        explanation = status.explain()
        
        assert "Package is in transit" in explanation
        assert "Louisville, KY" in explanation
        assert "2024-01-17" in explanation
        assert "Track regularly" in explanation  # Actionable guidance

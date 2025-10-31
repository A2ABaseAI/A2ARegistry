"""Normalization layer for UPS tracking data."""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional

from .models import Checkpoint, ShipmentStatus, UPSTrackingResponse

logger = logging.getLogger(__name__)


class UPSNormalizer:
    """Normalizes UPS tracking data into standardized format."""
    
    # Mapping of UPS activity codes to normalized status codes
    STATUS_CODE_MAPPING: Dict[str, str] = {
        # Label created
        "OR": "LABEL_CREATED",  # Origin scan
        "DP": "LABEL_CREATED",  # Departed from origin
        
        # In transit
        "AR": "IN_TRANSIT",     # Arrived at destination
        "IT": "IN_TRANSIT",     # In transit
        "PU": "IN_TRANSIT",     # Picked up
        "DP": "IN_TRANSIT",     # Departed
        
        # Out for delivery
        "OD": "OUT_FOR_DELIVERY",  # Out for delivery
        "OF": "OUT_FOR_DELIVERY",  # Out for delivery
        
        # Delivered
        "D": "DELIVERED",       # Delivered
        "DL": "DELIVERED",      # Delivered
        
        # Exception
        "EX": "EXCEPTION",      # Exception
        "CA": "EXCEPTION",      # Cancelled
        "RS": "EXCEPTION",      # Return to sender
        
        # On hold
        "HD": "ON_HOLD",        # On hold
        "HO": "ON_HOLD",        # On hold
        
        # Pickup available
        "PC": "PICKUP_AVAILABLE",  # Pickup available
        "PU": "PICKUP_AVAILABLE",  # Pickup available
        
        # Customs
        "CU": "CUSTOMS",        # Customs
        "IC": "CUSTOMS",        # Import clearance
        "EC": "CUSTOMS",        # Export clearance
    }
    
    # Common UPS status descriptions and their mappings
    STATUS_DESCRIPTION_MAPPING: Dict[str, str] = {
        "label created": "LABEL_CREATED",
        "origin scan": "LABEL_CREATED",
        "departed from origin": "LABEL_CREATED",
        "in transit": "IN_TRANSIT",
        "arrived at destination": "IN_TRANSIT",
        "picked up": "IN_TRANSIT",
        "departed": "IN_TRANSIT",
        "out for delivery": "OUT_FOR_DELIVERY",
        "delivered": "DELIVERED",
        "exception": "EXCEPTION",
        "on hold": "ON_HOLD",
        "pickup available": "PICKUP_AVAILABLE",
        "customs": "CUSTOMS",
        "import clearance": "CUSTOMS",
        "export clearance": "CUSTOMS",
    }
    
    def normalize(self, ups_response: UPSTrackingResponse) -> ShipmentStatus:
        """Normalize UPS tracking response to ShipmentStatus."""
        try:
            # Determine status code
            status_code = self._determine_status_code(ups_response)
            
            # Create checkpoints from activities
            checkpoints = self._create_checkpoints(ups_response.activities)
            
            # Determine if package is stale (no movement for 48+ hours)
            is_stale = self._is_package_stale(checkpoints)
            
            # Create status text
            status_text = self._create_status_text(ups_response, status_code, is_stale)
            
            return ShipmentStatus(
                tracking_number=ups_response.tracking_number,
                status_code=status_code,
                status_text=status_text,
                estimated_delivery=ups_response.estimated_delivery,
                delivered_at=ups_response.delivered_at,
                last_location=ups_response.last_location,
                service=ups_response.service,
                weight=ups_response.weight,
                checkpoints=checkpoints,
            )
            
        except Exception as e:
            logger.error(f"Error normalizing UPS response: {e}")
            # Return minimal status on error
            return ShipmentStatus(
                tracking_number=ups_response.tracking_number,
                status_code="UNKNOWN",
                status_text=f"Error processing tracking data: {str(e)}",
                checkpoints=[],
            )
    
    def _determine_status_code(self, ups_response: UPSTrackingResponse) -> str:
        """Determine normalized status code from UPS response."""
        # First try to match by activity type
        if ups_response.activities:
            latest_activity = ups_response.activities[0]
            activity_type = latest_activity.get("type", "").upper()
            if activity_type in self.STATUS_CODE_MAPPING:
                return self.STATUS_CODE_MAPPING[activity_type]
        
        # Try to match by status description
        if ups_response.status_description:
            description_lower = ups_response.status_description.lower()
            for pattern, status_code in self.STATUS_DESCRIPTION_MAPPING.items():
                if pattern in description_lower:
                    return status_code
        
        # Default to UNKNOWN if no match
        return "UNKNOWN"
    
    def _create_checkpoints(self, activities: List[dict]) -> List[Checkpoint]:
        """Create Checkpoint objects from UPS activities."""
        checkpoints = []
        
        for activity in activities:
            try:
                # Parse timestamp
                timestamp = self._parse_activity_timestamp(activity)
                
                # Get location
                location = activity.get("location")
                if isinstance(location, dict):
                    location_str = location.get("city")
                    if location_str:
                        state = location.get("stateProvinceCode")
                        if state:
                            location_str = f"{location_str}, {state}"
                else:
                    location_str = str(location) if location else None
                
                # Get description
                description = activity.get("description", "Unknown activity")
                
                checkpoint = Checkpoint(
                    timestamp=timestamp,
                    location=location_str,
                    description=description,
                )
                checkpoints.append(checkpoint)
                
            except Exception as e:
                logger.warning(f"Error parsing activity checkpoint: {e}")
                continue
        
        return checkpoints
    
    def _parse_activity_timestamp(self, activity: dict) -> datetime:
        """Parse timestamp from UPS activity."""
        date_str = activity.get("timestamp") or activity.get("date")
        time_str = activity.get("time")
        
        if date_str and time_str:
            try:
                # Try different date formats
                for date_format in ["%Y%m%d", "%Y-%m-%d", "%m/%d/%Y"]:
                    try:
                        parsed_date = datetime.strptime(date_str, date_format)
                        break
                    except ValueError:
                        continue
                else:
                    # If no format matches, use current time
                    parsed_date = datetime.now()
                
                # Parse time
                for time_format in ["%H%M%S", "%H:%M:%S", "%H:%M"]:
                    try:
                        parsed_time = datetime.strptime(time_str, time_format).time()
                        parsed_date = parsed_date.replace(
                            hour=parsed_time.hour,
                            minute=parsed_time.minute,
                            second=parsed_time.second,
                        )
                        break
                    except ValueError:
                        continue
                
                return parsed_date
                
            except Exception:
                pass
        
        # Fallback to current time
        return datetime.now()
    
    def _is_package_stale(self, checkpoints: List[Checkpoint]) -> bool:
        """Check if package has been stale (no movement for 48+ hours)."""
        if not checkpoints:
            return False
        
        # Get the most recent checkpoint
        latest_checkpoint = checkpoints[0]  # Assuming they're sorted by most recent first
        
        # Check if it's been more than 48 hours
        time_diff = datetime.now() - latest_checkpoint.timestamp
        return time_diff.total_seconds() > 48 * 3600  # 48 hours in seconds
    
    def _create_status_text(self, ups_response: UPSTrackingResponse, status_code: str, is_stale: bool) -> str:
        """Create human-readable status text."""
        base_text = ups_response.status_description or "Status unknown"
        
        # Add staleness warning
        if is_stale and status_code not in ["DELIVERED", "EXCEPTION"]:
            base_text += " (No movement for 48+ hours - contact UPS if concerned)"
        
        # Add location context
        if ups_response.last_location:
            base_text += f" Last seen at {ups_response.last_location}."
        
        return base_text
    
    def normalize_multiple(self, ups_responses: List[UPSTrackingResponse]) -> List[ShipmentStatus]:
        """Normalize multiple UPS tracking responses."""
        return [self.normalize(response) for response in ups_responses]

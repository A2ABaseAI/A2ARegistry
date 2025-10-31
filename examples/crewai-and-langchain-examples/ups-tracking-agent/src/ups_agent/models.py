"""Pydantic models for UPS shipment tracking."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Checkpoint(BaseModel):
    """Individual checkpoint in shipment tracking."""
    
    timestamp: datetime = Field(..., description="When this checkpoint occurred")
    location: Optional[str] = Field(None, description="Location where checkpoint occurred")
    description: str = Field(..., description="Description of the checkpoint event")


class ShipmentStatus(BaseModel):
    """Normalized UPS shipment status."""
    
    tracking_number: str = Field(..., description="UPS tracking number")
    status_code: Literal[
        "LABEL_CREATED",
        "IN_TRANSIT", 
        "OUT_FOR_DELIVERY",
        "DELIVERED",
        "EXCEPTION",
        "ON_HOLD",
        "PICKUP_AVAILABLE",
        "CUSTOMS",
        "UNKNOWN"
    ] = Field(..., description="Normalized status code")
    status_text: str = Field(..., description="Human-readable status description")
    estimated_delivery: Optional[datetime] = Field(None, description="Estimated delivery date/time")
    delivered_at: Optional[datetime] = Field(None, description="Actual delivery date/time")
    last_location: Optional[str] = Field(None, description="Last known location")
    service: Optional[str] = Field(None, description="UPS service type")
    weight: Optional[str] = Field(None, description="Package weight")
    checkpoints: List[Checkpoint] = Field(default_factory=list, description="Tracking checkpoints")
    
    def explain(self) -> str:
        """Return a concise human summary with actionable guidance."""
        explanations = {
            "LABEL_CREATED": "Package label has been created and is ready for pickup.",
            "IN_TRANSIT": "Package is in transit and moving through the UPS network.",
            "OUT_FOR_DELIVERY": "Package is out for delivery and should arrive today.",
            "DELIVERED": "Package has been successfully delivered.",
            "EXCEPTION": "There is an issue with the package that requires attention.",
            "ON_HOLD": "Package delivery is on hold and requires action.",
            "PICKUP_AVAILABLE": "Package is available for pickup at a UPS location.",
            "CUSTOMS": "Package is being processed through customs.",
            "UNKNOWN": "Package status is unclear or not yet available.",
        }
        
        base_explanation = explanations.get(self.status_code, "Package status is unknown.")
        
        # Add location context if available
        if self.last_location:
            base_explanation += f" Last seen at {self.last_location}."
        
        # Add delivery context
        if self.estimated_delivery:
            base_explanation += f" Estimated delivery: {self.estimated_delivery.strftime('%Y-%m-%d at %I:%M %p')}."
        elif self.delivered_at:
            base_explanation += f" Delivered on {self.delivered_at.strftime('%Y-%m-%d at %I:%M %p')}."
        
        # Add actionable guidance
        guidance = self._get_actionable_guidance()
        if guidance:
            base_explanation += f" {guidance}"
        
        return base_explanation
    
    def _get_actionable_guidance(self) -> str:
        """Get actionable guidance based on status."""
        guidance_map = {
            "LABEL_CREATED": "Contact sender if not picked up within 24 hours.",
            "IN_TRANSIT": "Track regularly; contact UPS if no movement for 48+ hours.",
            "OUT_FOR_DELIVERY": "Be available for delivery or check for delivery attempt notice.",
            "DELIVERED": "Check delivery location if not received.",
            "EXCEPTION": "Contact UPS immediately with tracking number for assistance.",
            "ON_HOLD": "Contact UPS to resolve hold and resume delivery.",
            "PICKUP_AVAILABLE": "Pick up within 5 business days or package will be returned.",
            "CUSTOMS": "Allow additional time for customs processing.",
            "UNKNOWN": "Contact UPS with tracking number for status update.",
        }
        
        return guidance_map.get(self.status_code, "")


class UPSTrackingResponse(BaseModel):
    """Raw UPS API tracking response."""
    
    tracking_number: str
    service: Optional[str] = None
    weight: Optional[str] = None
    status: Optional[str] = None
    status_description: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    last_location: Optional[str] = None
    activities: List[dict] = Field(default_factory=list)
    error: Optional[str] = None


class UPSAuthResponse(BaseModel):
    """UPS OAuth token response."""
    
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    scope: Optional[str] = None

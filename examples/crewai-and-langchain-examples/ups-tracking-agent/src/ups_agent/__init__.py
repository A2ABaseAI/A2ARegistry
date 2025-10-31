"""UPS Tracking Agent - CrewAI agent for UPS shipment tracking."""

__version__ = "1.0.0"
__author__ = "A2A Registry Team"
__email__ = "team@a2a-registry.com"

from .agent import UPSStatusAgent
from .client import UPSClient, UPSCredentialsError, UPSTrackingError
from .config import settings
from .models import Checkpoint, ShipmentStatus, UPSTrackingResponse
from .normalizer import UPSNormalizer

__all__ = [
    "UPSStatusAgent",
    "UPSClient", 
    "UPSCredentialsError",
    "UPSTrackingError",
    "settings",
    "Checkpoint",
    "ShipmentStatus", 
    "UPSTrackingResponse",
    "UPSNormalizer",
]

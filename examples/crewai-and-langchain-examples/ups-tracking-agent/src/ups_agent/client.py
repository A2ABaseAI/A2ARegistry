"""UPS API client with OAuth authentication and tracking capabilities."""

import asyncio
import logging
import re
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx
from pydantic import ValidationError

from .models import UPSTrackingResponse, UPSAuthResponse

logger = logging.getLogger(__name__)


class UPSCredentialsError(Exception):
    """Raised when UPS credentials are missing or invalid."""
    pass


class UPSTrackingError(Exception):
    """Raised when UPS tracking API returns an error."""
    pass


class UPSClient:
    """UPS API client with OAuth authentication and tracking."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        account_number: Optional[str] = None,
        api_base: str = "https://onlinetools.ups.com",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """Initialize UPS client."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.account_number = account_number
        self.api_base = api_base.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Token caching
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        
        # HTTP client
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
    
    def _validate_tracking_number(self, tracking_number: str) -> bool:
        """Validate UPS tracking number format."""
        # Remove any whitespace
        tracking_number = tracking_number.strip()
        
        # UPS tracking numbers are typically 18 characters, alphanumeric
        # Common patterns: 1Z..., 1M..., etc.
        if not tracking_number:
            return False
        
        # Check length (typically 18, but allow some flexibility)
        if len(tracking_number) < 10 or len(tracking_number) > 30:
            return False
        
        # Check if alphanumeric
        if not re.match(r'^[A-Z0-9]+$', tracking_number.upper()):
            return False
        
        return True
    
    async def _get_access_token(self) -> str:
        """Get OAuth access token with caching."""
        # Check if we have a valid cached token
        if (
            self._access_token 
            and self._token_expires_at 
            and datetime.now() < self._token_expires_at - timedelta(minutes=5)  # 5 min buffer
        ):
            return self._access_token
        
        # Request new token
        logger.debug("Requesting new UPS OAuth token")
        
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        if self.account_number:
            auth_data["account_number"] = self.account_number
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        
        try:
            response = await self._client.post(
                f"{self.api_base}/security/v1/oauth/token",
                data=auth_data,
                headers=headers,
            )
            
            if response.status_code == 200:
                auth_response = UPSAuthResponse(**response.json())
                
                # Cache token
                self._access_token = auth_response.access_token
                self._token_expires_at = datetime.now() + timedelta(seconds=auth_response.expires_in)
                
                logger.debug("Successfully obtained UPS OAuth token")
                return self._access_token
            else:
                error_msg = f"UPS OAuth failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise UPSCredentialsError(error_msg)
                
        except httpx.RequestError as e:
            error_msg = f"Network error during UPS OAuth: {e}"
            logger.error(error_msg)
            raise UPSCredentialsError(error_msg)
        except ValidationError as e:
            error_msg = f"Invalid UPS OAuth response: {e}"
            logger.error(error_msg)
            raise UPSCredentialsError(error_msg)
    
    async def _make_request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(method, url, **kwargs)
                
                # Don't retry on client errors (4xx)
                if 400 <= response.status_code < 500:
                    return response
                
                # Retry on server errors (5xx) and network issues
                if response.status_code >= 500 or response.status_code == 429:
                    if attempt < self.max_retries:
                        delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"UPS API error {response.status_code}, retrying in {delay}s (attempt {attempt + 1}/{self.max_retries + 1})")
                        await asyncio.sleep(delay)
                        continue
                
                return response
                
            except httpx.RequestError as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Network error, retrying in {delay}s (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
                    await asyncio.sleep(delay)
                    continue
        
        # If we get here, all retries failed
        raise last_exception or UPSTrackingError("Max retries exceeded")
    
    async def track(self, tracking_number: str) -> UPSTrackingResponse:
        """Track a UPS shipment."""
        # Validate tracking number
        if not self._validate_tracking_number(tracking_number):
            raise UPSTrackingError(f"Invalid tracking number format: {tracking_number}")
        
        # Get access token
        access_token = await self._get_access_token()
        
        # Generate transaction ID
        transaction_id = str(uuid.uuid4())
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "transId": transaction_id,
            "transactionSrc": "ups-agent",
        }
        
        logger.info(f"Tracking UPS shipment: {tracking_number} (transaction: {transaction_id})")
        
        try:
            response = await self._make_request_with_retry(
                "GET",
                f"{self.api_base}/api/track/v1/details/{tracking_number}",
                headers=headers,
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_tracking_response(tracking_number, data)
            elif response.status_code == 404:
                raise UPSTrackingError(f"Tracking number not found: {tracking_number}")
            elif response.status_code == 401:
                raise UPSCredentialsError("UPS API authentication failed")
            elif response.status_code == 429:
                raise UPSTrackingError("UPS API rate limit exceeded")
            else:
                error_msg = f"UPS API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise UPSTrackingError(error_msg)
                
        except httpx.RequestError as e:
            error_msg = f"Network error tracking UPS shipment: {e}"
            logger.error(error_msg)
            raise UPSTrackingError(error_msg)
    
    def _parse_tracking_response(self, tracking_number: str, data: dict) -> UPSTrackingResponse:
        """Parse UPS API tracking response."""
        try:
            # Extract basic info
            shipment = data.get("trackResponse", {}).get("shipment", [{}])[0]
            
            # Service info
            service = shipment.get("service", {}).get("description")
            
            # Weight info
            weight = None
            if "package" in shipment:
                package = shipment["package"]
                if "weight" in package:
                    weight_info = package["weight"]
                    weight = f"{weight_info.get('value', '')} {weight_info.get('unitOfMeasurement', {}).get('code', '')}"
            
            # Status and activities
            status = None
            status_description = None
            estimated_delivery = None
            delivered_at = None
            last_location = None
            activities = []
            
            if "package" in shipment:
                package = shipment["package"]
                
                # Current status
                if "activity" in package:
                    activities_data = package["activity"]
                    if activities_data:
                        # Most recent activity
                        latest_activity = activities_data[0]
                        status_description = latest_activity.get("status", {}).get("description")
                        
                        # Parse all activities
                        for activity in activities_data:
                            activity_data = {
                                "timestamp": activity.get("date"),
                                "time": activity.get("time"),
                                "location": activity.get("location", {}).get("address", {}).get("city"),
                                "description": activity.get("status", {}).get("description"),
                                "type": activity.get("status", {}).get("type"),
                            }
                            activities.append(activity_data)
                        
                        # Set last location
                        if activities_data:
                            last_activity = activities_data[0]
                            location_info = last_activity.get("location", {}).get("address", {})
                            if location_info:
                                city = location_info.get("city")
                                state = location_info.get("stateProvinceCode")
                                if city and state:
                                    last_location = f"{city}, {state}"
                                elif city:
                                    last_location = city
                
                # Delivery info
                if "deliveryDate" in package:
                    delivery_date = package["deliveryDate"]
                    if delivery_date:
                        date_str = delivery_date.get("date")
                        time_str = delivery_date.get("time")
                        if date_str and time_str:
                            try:
                                delivered_at = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H%M%S")
                            except ValueError:
                                pass
                
                # Estimated delivery
                if "scheduledDeliveryDate" in package:
                    scheduled_date = package["scheduledDeliveryDate"]
                    if scheduled_date:
                        date_str = scheduled_date.get("date")
                        time_str = scheduled_date.get("time")
                        if date_str and time_str:
                            try:
                                estimated_delivery = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H%M%S")
                            except ValueError:
                                pass
            
            return UPSTrackingResponse(
                tracking_number=tracking_number,
                service=service,
                weight=weight,
                status=status,
                status_description=status_description,
                estimated_delivery=estimated_delivery,
                delivered_at=delivered_at,
                last_location=last_location,
                activities=activities,
            )
            
        except Exception as e:
            logger.error(f"Error parsing UPS tracking response: {e}")
            raise UPSTrackingError(f"Failed to parse UPS tracking response: {e}")
    
    async def track_multiple(self, tracking_numbers: List[str]) -> List[UPSTrackingResponse]:
        """Track multiple UPS shipments concurrently."""
        if not tracking_numbers:
            return []
        
        # Validate all tracking numbers first
        for tn in tracking_numbers:
            if not self._validate_tracking_number(tn):
                raise UPSTrackingError(f"Invalid tracking number format: {tn}")
        
        # Track all shipments concurrently
        tasks = [self.track(tn) for tn in tracking_numbers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Separate successful results from exceptions
        successful_results = []
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(f"Tracking {tracking_numbers[i]}: {result}")
                logger.error(f"Failed to track {tracking_numbers[i]}: {result}")
            else:
                successful_results.append(result)
        
        # Log any errors
        if errors:
            logger.warning(f"Some tracking requests failed: {'; '.join(errors)}")
        
        return successful_results

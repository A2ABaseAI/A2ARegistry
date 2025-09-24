"""Security service for API key management and audit events."""

import logging
import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ..config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class AuthMethod(Enum):
    """Supported authentication methods."""

    API_KEY = "api_key"
    OAUTH2_CLIENT_CREDENTIALS = "oauth2_client_credentials"
    OAUTH2_AUTHORIZATION_CODE = "oauth2_authorization_code"
    JWT_BEARER = "jwt_bearer"
    MTLS = "mtls"
    COMBINED = "combined"


class SecurityLevel(Enum):
    """Security levels for different operations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Security event for audit logging."""

    event_id: str
    timestamp: datetime
    event_type: str
    severity: str
    source: str
    user_id: Optional[str]
    agent_id: Optional[str]
    details: Dict[str, Any]
    resolved: bool = False


@dataclass
class ApiKeyInfo:
    """API key information."""

    key_id: str
    key_hash: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    usage_count: int = 0
    scopes: List[str] = field(default_factory=list)
    is_active: bool = True


@dataclass
class JwtTokenInfo:
    """JWT token metadata."""

    token_id: str
    subject: str
    issuer: str
    audience: str
    issued_at: datetime
    expires_at: datetime
    scopes: List[str]
    claims: Dict[str, Any]


class SecurityService:
    """Backend security management service (API keys & audit events)."""

    def __init__(self, secret_key: str, redis_client=None, db_session=None):
        self.secret_key = secret_key
        self.redis_client = redis_client
        self.db_session = db_session
        self.api_keys: Dict[str, ApiKeyInfo] = {}
        self.jwt_keys: Dict[str, Any] = {}
        self.security_events: List[SecurityEvent] = []
        self.security_policies: Dict[str, Any] = {}
        self.threat_patterns: List[Dict[str, Any]] = []

        self._initialize_security_policies()
        self._initialize_threat_patterns()

        logger.info("Security Service initialized")

    def _initialize_security_policies(self):
        self.security_policies = {
            "api_key_rotation": {
                "enabled": True,
                "rotation_interval_days": 90,
                "warning_days": 14,
                "auto_rotate": False
            },
            "jwt_validation": {
                "require_exp": True,
                "require_iat": True,
                "require_aud": True,
                "max_age_minutes": 60,
                "allowed_algorithms": ["RS256", "ES256", "HS256"]
            },
            "oauth2_settings": {
                "token_lifetime_minutes": 60,
                "refresh_token_lifetime_days": 30,
                "require_pkce": True,
                "allowed_grant_types": ["client_credentials", "authorization_code"]
            },
            "audit_settings": {
                "log_all_auth_attempts": True,
                "log_token_usage": True,
                "retention_days": 365,
                "alert_on_anomalies": True
            }
        }

    def _initialize_threat_patterns(self):
        self.threat_patterns = [
            {
                "name": "brute_force_detection",
                "pattern": "multiple_failed_auth",
                "threshold": 5,
                "time_window_minutes": 10,
                "severity": "high"
            },
            {
                "name": "token_abuse_detection",
                "pattern": "excessive_token_usage",
                "threshold": 100,
                "time_window_minutes": 5,
                "severity": "medium"
            },
            {
                "name": "unusual_access_pattern",
                "pattern": "access_from_new_location",
                "threshold": 1,
                "time_window_minutes": 60,
                "severity": "low"
            }
        ]

    def create_api_key(
        self,
        scopes: List[str],
        expires_days: Optional[int] = None,
        user_id: Optional[str] = None,
    ) -> Tuple[str, ApiKeyInfo]:
        key_id = str(uuid.uuid4())
        api_key = f"a2a_{key_id.replace('-', '')}"
        key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()

        expires_at = None
        if expires_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)

        key_info = ApiKeyInfo(
            key_id=key_id,
            key_hash=key_hash,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            scopes=scopes,
            last_used=None,
            usage_count=0,
            is_active=True,
        )

        self.api_keys[key_id] = key_info
        self._log_security_event(
            event_type="api_key_created",
            severity="info",
            source="security_service",
            user_id=user_id,
            details={
                "key_id": key_id,
                "scopes": scopes,
                "expires_at": expires_at.isoformat() if expires_at else None,
            },
        )

        logger.info("Created API key", extra={"key_id": key_id, "scopes": scopes})
        return api_key, key_info

    def validate_api_key(
        self,
        api_key: str,
        required_scopes: Optional[List[str]] = None,
    ) -> Optional[ApiKeyInfo]:
        key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()

        key_info = None
        for candidate in self.api_keys.values():
            if candidate.key_hash == key_hash and candidate.is_active:
                key_info = candidate
                break

        if not key_info:
            self._log_security_event(
                event_type="api_key_validation_failed",
                severity="warning",
                source="security_service",
                details={"reason": "key_not_found", "key_hash": key_hash[:16]},
            )
            return None

        if key_info.expires_at and datetime.now(timezone.utc) > key_info.expires_at:
            self._log_security_event(
                event_type="api_key_expired",
                severity="warning",
                source="security_service",
                details={"key_id": key_info.key_id, "expired_at": key_info.expires_at.isoformat()},
            )
            return None

        if required_scopes and not all(scope in key_info.scopes for scope in required_scopes):
            self._log_security_event(
                event_type="api_key_insufficient_scopes",
                severity="warning",
                source="security_service",
                details={
                    "key_id": key_info.key_id,
                    "required_scopes": required_scopes,
                    "available_scopes": key_info.scopes,
                },
            )
            return None

        key_info.last_used = datetime.now(timezone.utc)
        key_info.usage_count += 1
        return key_info

    def revoke_api_key(self, key_id: str) -> bool:
        if key_id in self.api_keys:
            self.api_keys[key_id].is_active = False
            self._log_security_event(
                event_type="api_key_revoked",
                severity="info",
                source="security_service",
                details={"key_id": key_id},
            )
            logger.info("Revoked API key", extra={"key_id": key_id})
            return True

        return False

    def get_api_key_info(self, key_id: str) -> Optional[ApiKeyInfo]:
        return self.api_keys.get(key_id)

    def list_api_keys(self, active_only: bool = True) -> List[ApiKeyInfo]:
        keys = list(self.api_keys.values())
        if active_only:
            keys = [key for key in keys if key.is_active]
        return keys

    def _log_security_event(
        self,
        event_type: str,
        severity: str,
        source: str,
        details: Dict[str, Any],
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ):
        event = SecurityEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            severity=severity,
            source=source,
            user_id=user_id,
            agent_id=agent_id,
            details=details,
            resolved=False,
        )

        self.security_events.append(event)

        log_level = {
            "critical": logging.CRITICAL,
            "high": logging.ERROR,
            "warning": logging.WARNING,
            "medium": logging.WARNING,
            "info": logging.INFO,
            "low": logging.INFO,
        }.get(severity, logging.INFO)

        logger.log(log_level, "Security event", extra={"event_type": event_type, "details": details})

    def get_security_events(
        self,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[SecurityEvent]:
        events = self.security_events

        if event_type:
            events = [event for event in events if event.event_type == event_type]

        if severity:
            events = [event for event in events if event.severity == severity]

        events.sort(key=lambda item: item.timestamp, reverse=True)

        if limit:
            events = events[:limit]

        return events

    def get_security_summary(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)

        total_keys = len(self.api_keys)
        active_keys = len([key for key in self.api_keys.values() if key.is_active])
        expired_keys = len(
            [key for key in self.api_keys.values() if key.expires_at and now > key.expires_at]
        )

        total_events = len(self.security_events)
        recent_events = len([event for event in self.security_events if (now - event.timestamp).days < 7])
        critical_events = len(
            [event for event in self.security_events if event.severity in ["critical", "high"]]
        )

        return {
            "api_keys": {"total": total_keys, "active": active_keys, "expired": expired_keys},
            "jwt_keys": {"total": len(self.jwt_keys)},
            "security_events": {
                "total": total_events,
                "recent_7_days": recent_events,
                "critical_high": critical_events,
            },
            "policies": {"total": len(self.security_policies)},
            "threat_patterns": {"total": len(self.threat_patterns)},
        }


_security_service: Optional[SecurityService] = None


def get_security_service(secret_key: Optional[str] = None, redis_client=None, db_session=None) -> SecurityService:
    """Return a singleton ``SecurityService`` instance."""

    global _security_service
    if _security_service is None:
        _security_service = SecurityService(secret_key or settings.secret_key, redis_client, db_session)
    return _security_service

"""Card service layer for card-related operations."""

import hashlib
import json
from typing import Any, Dict, Optional, Tuple

import httpx
from fastapi import HTTPException, status

from ..core.logging import get_logger
from ..schemas.agent_card_spec import AgentCardSpec

logger = get_logger(__name__)


def _canonical_json(data: Dict[str, Any]) -> str:
    """Generate canonical JSON representation."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


class CardService:
    """Service for card-related operations."""

    @staticmethod
    def fetch_card_from_url(card_url: str) -> Dict[str, Any]:
        """
        Fetch agent card data from a remote URL with validation.

        Args:
            card_url: URL to fetch the card from

        Returns:
            Dict containing the card data

        Raises:
            HTTPException: For various validation and fetch errors
        """
        # Enforce HTTPS for security
        if not card_url.startswith("https://"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cardUrl must use HTTPS")

        try:
            logger.debug(f"Fetching card from URL: {card_url}")
            resp = httpx.get(
                card_url,
                timeout=httpx.Timeout(connect=2.0, read=3.0),
                follow_redirects=True,
            )
            resp.raise_for_status()

            # Validate content type
            ctype = resp.headers.get("content-type", "")
            if "application/json" not in ctype:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cardUrl must return application/json")

            # Limit payload size to 256KB
            if resp.content and len(resp.content) > 256 * 1024:
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Card exceeds size limit")

            card_data = resp.json()
            logger.debug(f"Successfully fetched card from URL: {card_url}")
            return card_data  # type: ignore[no-any-return]

        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as exc:
            logger.error(f"Failed to fetch card from URL {card_url}: {exc}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch cardUrl") from exc

    @staticmethod
    def parse_and_validate_card(body: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str], str]:
        """
        Parse and validate agent card data from request body.

        Args:
            body: Request body containing card data or URL

        Returns:
            Tuple of (card_data, card_url, card_hash)

        Raises:
            HTTPException: For validation errors
        """
        try:
            if "cardUrl" in body:
                from ..api.agents import PublishByUrl

                url_model = PublishByUrl(**body)
                card_data = CardService.fetch_card_from_url(str(url_model.cardUrl))
                card_url = str(url_model.cardUrl)
            else:
                from ..api.agents import PublishByCard

                card_model = PublishByCard(**body)
                card_data = card_model.card
                card_url = None

            # Validate against AgentCardSpec using Pydantic validation
            try:
                card = AgentCardSpec.model_validate(card_data)
                # Use the validated card's dict to ensure ADK-compatible format
                # This ensures securitySchemes is dict and defaultInputModes/defaultOutputModes are at top level
                # Use by_alias=True to serialize 'in_' as 'in' for ADK compatibility
                import json

                validated_card_data = json.loads(card.model_dump_json(by_alias=True))
                card_data = validated_card_data
            except Exception as exc:
                logger.error(f"Invalid agent card spec: {exc}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid agent card") from exc

            # Compute canonical JSON and hash
            canonical = _canonical_json(card_data)
            card_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

            logger.debug(f"Successfully parsed and validated card: {card.name}")
            return card_data, card_url, card_hash

        except HTTPException:
            raise
        except Exception as exc:
            logger.error(f"Failed to parse card data: {exc}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid card data") from exc

    @staticmethod
    def validate_card_data(card_data: Dict[str, Any]) -> AgentCardSpec:
        """
        Validate card data against AgentCardSpec.

        Args:
            card_data: Card data to validate

        Returns:
            Validated AgentCardSpec instance

        Raises:
            HTTPException: For validation errors
        """
        try:
            return AgentCardSpec.model_validate(card_data)
        except Exception as exc:
            logger.error(f"Invalid agent card spec: {exc}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid agent card") from exc

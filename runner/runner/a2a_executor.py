from typing import Dict, Any, List, Tuple, Optional
import logging
import re
import json
import uuid
import httpx
from .models import A2AAgentCard, AgentMessage, GlobalSession

logger = logging.getLogger(__name__)

# Constants
EMPTY_RESPONSE_MSG = "Agent returned empty response. The agent endpoint may not support A2A protocol format."
FALLBACK_MSG = "falling back to httpx"
APP_NAME = "a2a-runner"
DEFAULT_TIMEOUT = 30.0

# Response field names
FIELD_OUTPUT = "output"
FIELD_TEXT = "text"
FIELD_DELEGATE = "delegate"
FIELD_MESSAGE = "message"
FIELD_RESPONSE = "response"
FIELD_CONTENT = "content"
FIELD_CUSTOM_METADATA = "custom_metadata"

# Import registry SDK for fetching agent cards
try:
    from a2a_reg_sdk import A2ARegClient
    REGISTRY_SDK_AVAILABLE = True
except ImportError:
    REGISTRY_SDK_AVAILABLE = False
    A2ARegClient = None

# Import Google ADK components
try:
    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
    from google.adk.agents.invocation_context import InvocationContext
    from google.adk.sessions.session import Session
    from google.adk.sessions.base_session_service import BaseSessionService
    ADK_AVAILABLE = True
    # Agent class is only needed for fallback wrapper
    try:
        from google.adk.agent import Agent
    except ImportError:
        try:
            from google.adk.core.agent import Agent
        except ImportError:
            Agent = None
except ImportError:
    logger.warning("Google ADK not available. Falling back to httpx implementation.")
    ADK_AVAILABLE = False
    RemoteA2aAgent = None
    InvocationContext = None
    Session = None
    BaseSessionService = None
    Agent = None


class SimpleSessionService(BaseSessionService if ADK_AVAILABLE else object):
    """Simple in-memory session service for RemoteA2aAgent."""
    
    def __init__(self):
        if ADK_AVAILABLE and BaseSessionService:
            super().__init__()
        self._sessions: Dict[str, Any] = {}
    
    async def create_session(self, session_id: str, user_id: str, app_name: str) -> Session:
        """Create a new session."""
        session = Session(id=session_id, app_name=app_name, user_id=user_id)
        self._sessions[session_id] = session
        return session
    
    async def get_session(self, session_id: str) -> Session:
        """Get a session by ID."""
        return self._sessions.get(session_id)
    
    async def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    async def list_sessions(self, user_id: str = None, app_name: str = None) -> List[Session]:
        """List sessions, optionally filtered by user_id or app_name."""
        sessions = list(self._sessions.values())
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        if app_name:
            sessions = [s for s in sessions if s.app_name == app_name]
        return sessions
    
    async def get_or_create_session(self, session_id: str, user_id: str, app_name: str) -> Session:
        """Get or create a session."""
        if session_id in self._sessions:
            return self._sessions[session_id]
        return await self.create_session(session_id, user_id, app_name)


class ResponseParser:
    """Helper class for parsing various response formats from ADK and agents."""
    
    @staticmethod
    def extract_text_from_content(content_obj: Any) -> List[str]:
        """Extract text parts from a Content object."""
        text_parts = []
        
        if hasattr(content_obj, FIELD_CONTENT):
            content = content_obj.content
            if isinstance(content, list):
                for part in content:
                    text_parts.extend(ResponseParser._extract_text_from_part(part))
            elif isinstance(content, str):
                text_parts.append(content)
        elif hasattr(content_obj, FIELD_TEXT) and content_obj.text:
            text_parts.append(content_obj.text)
        
        return text_parts
    
    @staticmethod
    def _extract_text_from_part(part: Any) -> List[str]:
        """Extract text from a content part."""
        text_parts = []
        
        if isinstance(part, str):
            text_parts.append(part)
        elif isinstance(part, dict):
            if FIELD_TEXT in part:
                text_parts.append(part[FIELD_TEXT])
        elif hasattr(part, FIELD_TEXT):
            text_parts.append(part.text)
        
        return text_parts
    
    @staticmethod
    def extract_delegate_from_dict(data: Dict[str, Any]) -> Optional[str]:
        """Extract delegate field from various locations in a dict."""
        # Check custom_metadata
        if FIELD_CUSTOM_METADATA in data and isinstance(data[FIELD_CUSTOM_METADATA], dict):
            if FIELD_DELEGATE in data[FIELD_CUSTOM_METADATA]:
                return data[FIELD_CUSTOM_METADATA][FIELD_DELEGATE]
        
        # Check top level
        if FIELD_DELEGATE in data:
            return data[FIELD_DELEGATE]
        
        # Check content parts for JSON with delegate
        if FIELD_CONTENT in data:
            content = data[FIELD_CONTENT]
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and FIELD_TEXT in part:
                        text = part[FIELD_TEXT]
                        if isinstance(text, str) and text.strip().startswith("{"):
                            try:
                                parsed = json.loads(text)
                                if isinstance(parsed, dict) and FIELD_DELEGATE in parsed:
                                    return parsed[FIELD_DELEGATE]
                            except (json.JSONDecodeError, ValueError):
                                pass
        
        return None
    
    @staticmethod
    def parse_json_response(text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from text string if it looks like JSON."""
        if isinstance(text, str) and text.strip().startswith("{"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                pass
        return None
    
    @staticmethod
    def extract_output_from_dict(data: Dict[str, Any]) -> str:
        """Extract output text from a dictionary response."""
        return (data.get(FIELD_OUTPUT) or 
                data.get(FIELD_TEXT) or 
                data.get(FIELD_MESSAGE) or 
                data.get(FIELD_RESPONSE) or 
                str(data))
    
    @staticmethod
    def process_chunks(chunks: List[Any]) -> Tuple[str, Dict[str, Any]]:
        """Process async generator chunks into output text and data dict."""
        if not chunks:
            return "", {FIELD_OUTPUT: ""}
        
        first_chunk = chunks[0]
        
        # Handle string chunks
        if isinstance(first_chunk, str):
            result = " ".join(str(c) for c in chunks)
            return result, {FIELD_OUTPUT: result}
        
        # Handle dict chunks
        if isinstance(first_chunk, dict):
            result_dict = {}
            for chunk in reversed(chunks):
                if chunk is not None and isinstance(chunk, dict):
                    result_dict = chunk
                    break
            result = ResponseParser.extract_output_from_dict(result_dict)
            return result, result_dict
        
        # Handle Content objects or Pydantic models
        if hasattr(first_chunk, FIELD_CONTENT) or hasattr(first_chunk, FIELD_TEXT) or hasattr(first_chunk, "model_dump"):
            return ResponseParser._process_model_chunks(chunks)
        
        # Fallback: try to convert last chunk
        last_chunk = chunks[-1]
        return ResponseParser._extract_from_last_chunk(last_chunk)
    
    @staticmethod
    def _process_model_chunks(chunks: List[Any]) -> Tuple[str, Dict[str, Any]]:
        """Process chunks that are Content objects or Pydantic models."""
        text_parts = []
        last_chunk_dict = None
        
        for chunk in chunks:
            # Extract text
            chunk_text = ResponseParser.extract_text_from_content(chunk)
            text_parts.extend(chunk_text)
            
            # Extract dict representation
            if hasattr(chunk, "model_dump"):
                try:
                    chunk_dict = chunk.model_dump()
                    last_chunk_dict = chunk_dict
                    
                    # Try to extract delegate
                    delegate = ResponseParser.extract_delegate_from_dict(chunk_dict)
                    if delegate and last_chunk_dict:
                        last_chunk_dict[FIELD_DELEGATE] = delegate
                except Exception as e:
                    logger.debug(f"Error extracting from chunk: {e}")
        
        # Combine text parts
        result = " ".join(text_parts) if text_parts else ""
        
        # Handle empty result
        if not result:
            result, last_chunk_dict = ResponseParser._handle_empty_result(chunks)
        
        # Build data dict
        data = last_chunk_dict.copy() if last_chunk_dict else {}
        
        # Try to parse result as JSON for delegate
        if result and result.strip().startswith("{"):
            parsed = ResponseParser.parse_json_response(result)
            if parsed:
                data.update(parsed)
                result = ResponseParser.extract_output_from_dict(parsed) or result
        
        # Ensure output field is set
        if FIELD_OUTPUT not in data:
            data[FIELD_OUTPUT] = result
        
        return result, data
    
    @staticmethod
    def _handle_empty_result(chunks: List[Any]) -> Tuple[str, Dict[str, Any]]:
        """Handle case where no text was extracted from chunks."""
        last_chunk = chunks[-1] if chunks else None
        
        if last_chunk and hasattr(last_chunk, "model_dump"):
            try:
                chunk_dict = last_chunk.model_dump()
                result = (chunk_dict.get(FIELD_TEXT) or 
                         chunk_dict.get(FIELD_OUTPUT) or 
                         chunk_dict.get(FIELD_MESSAGE) or 
                         "")
                
                # Check custom_metadata
                if not result and FIELD_CUSTOM_METADATA in chunk_dict:
                    custom_meta = chunk_dict.get(FIELD_CUSTOM_METADATA)
                    if isinstance(custom_meta, dict):
                        result = (custom_meta.get(FIELD_OUTPUT) or 
                                 custom_meta.get(FIELD_TEXT) or 
                                 custom_meta.get(FIELD_MESSAGE) or 
                                 "")
                
                # Check content field
                if not result and FIELD_CONTENT in chunk_dict:
                    content = chunk_dict[FIELD_CONTENT]
                    if isinstance(content, dict) and FIELD_OUTPUT in content:
                        result = content.get(FIELD_OUTPUT, "")
                    elif isinstance(content, str):
                        result = content
                
                return result, chunk_dict
            except Exception as e:
                logger.debug(f"Error extracting from empty Content chunk: {e}")
        
        return (str(last_chunk) if last_chunk else ""), {}
    
    @staticmethod
    def _extract_from_last_chunk(last_chunk: Any) -> Tuple[str, Dict[str, Any]]:
        """Extract output from the last chunk as fallback."""
        if hasattr(last_chunk, "model_dump"):
            data = last_chunk.model_dump()
            text_parts = ResponseParser.extract_text_from_content(last_chunk)
            result = " ".join(text_parts) if text_parts else ResponseParser.extract_output_from_dict(data)
            return result, data
        elif hasattr(last_chunk, FIELD_TEXT):
            result = last_chunk.text
            data = {FIELD_OUTPUT: result}
            if hasattr(last_chunk, "model_dump"):
                data = last_chunk.model_dump()
            return result, data
        elif isinstance(last_chunk, str):
            return last_chunk, {FIELD_OUTPUT: last_chunk}
        else:
            data = vars(last_chunk) if hasattr(last_chunk, "__dict__") else {}
            result = ResponseParser.extract_output_from_dict(data) or str(last_chunk)
            return result, {FIELD_OUTPUT: result}


class A2ARemoteExecutor:
    """
    Remote-only executor using Google ADK RemoteA2aAgent.
    
    Uses RemoteA2aAgent from google.adk.agents.remote_a2a_agent for A2A protocol communication.
    Falls back to httpx if ADK is not available.
    """

    def __init__(self):
        """Initialize the executor."""
        self._remote_agents: Dict[str, RemoteA2aAgent] = {}
        self._registry_client = None
        
        # Initialize registry client for fetching agent cards
        if REGISTRY_SDK_AVAILABLE:
            try:
                from .config import settings
                if settings.registry_api_key:
                    self._registry_client = A2ARegClient(
                        registry_url=settings.registry_url,
                        api_key=settings.registry_api_key,
                    )
                    logger.info("Registry SDK available for fetching agent cards")
            except Exception as e:
                logger.warning(f"Failed to initialize registry client: {e}")
        
        if ADK_AVAILABLE:
            self._session_service = SimpleSessionService()
            logger.info("Using Google ADK RemoteA2aAgent for remote agent execution")
        else:
            self._session_service = None
            logger.warning("Google ADK RemoteAgent not available. Using httpx fallback.")

    def _sanitize_agent_name(self, name: str) -> str:
        """Sanitize agent name to be a valid identifier."""
        sanitized = name.lower().replace(" ", "_").replace("-", "_")
        sanitized = re.sub(r'[^a-z0-9_]', '', sanitized)
        
        if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
            sanitized = 'agent_' + sanitized
        
        return sanitized or f"agent_{hash(name) % 10000}"

    def _create_httpx_client(self) -> Optional[httpx.AsyncClient]:
        """Create httpx client with authentication headers."""
        if not self._registry_client:
            return None
        
        try:
            from .config import settings
            headers = {}
            if settings.registry_api_key:
                headers["Authorization"] = f"Bearer {settings.registry_api_key}"
            return httpx.AsyncClient(headers=headers, timeout=DEFAULT_TIMEOUT)
        except Exception as e:
            logger.warning(f"Failed to create httpx client: {e}")
            return None

    def _get_agent_card_url(self, agent_card: A2AAgentCard) -> Optional[str]:
        """Get the registry card endpoint URL for an agent."""
        if not self._registry_client:
            return None
        
        try:
            from .config import settings
            return f"{settings.registry_url}/agents/{agent_card.id}/card"
        except Exception as e:
            logger.warning(f"Failed to construct registry card URL: {e}")
            return None

    def _get_or_create_remote_agent(self, agent_card: A2AAgentCard) -> Optional[RemoteA2aAgent]:
        """Get or create a RemoteA2aAgent instance for the given card."""
        if not ADK_AVAILABLE:
            return None
        
        if agent_card.id in self._remote_agents:
            return self._remote_agents[agent_card.id]
        
        agent_card_url = self._get_agent_card_url(agent_card)
        if not agent_card_url:
            logger.warning(f"No agent card URL available from registry for {agent_card.id}, cannot create RemoteA2aAgent")
            return None
        
        try:
            sanitized_name = self._sanitize_agent_name(agent_card.name)
            httpx_client = self._create_httpx_client()
            
            remote_agent_kwargs = {
                "name": sanitized_name,
                "description": agent_card.description or "",
                "agent_card": agent_card_url,
            }
            
            if httpx_client:
                remote_agent_kwargs["httpx_client"] = httpx_client
            
            remote_agent = RemoteA2aAgent(**remote_agent_kwargs)
            self._remote_agents[agent_card.id] = remote_agent
            logger.info(f"Created RemoteA2aAgent for {agent_card.id} using registry card endpoint URL")
            return remote_agent
        except Exception as e:
            logger.warning(f"Failed to create RemoteA2aAgent for {agent_card.id}: {e}", exc_info=True)
            return None

    def _create_invocation_context(
        self,
        remote_agent: RemoteA2aAgent,
        session: Session,
        prompt: str,
        invocation_id: str
    ) -> InvocationContext:
        """Create InvocationContext for ADK execution."""
        from google.genai.types import Content, Part
        
        user_content = Content(parts=[Part(text=prompt)])
        
        return InvocationContext(
            invocation_id=invocation_id,
            agent=remote_agent,
            session=session,
            session_service=self._session_service,
            user_content=user_content,
        )

    async def _execute_with_adk(
        self,
        agent_card: A2AAgentCard,
        global_session: GlobalSession,
        prompt: str,
    ) -> Tuple[str, Dict[str, Any]]:
        """Execute agent using Google ADK RemoteA2aAgent."""
        remote_agent = self._get_or_create_remote_agent(agent_card)
        if not remote_agent:
            raise ValueError("Failed to create RemoteA2aAgent")
        
        # Create session and invocation context
        invocation_id = str(uuid.uuid4())
        session_id = f"session-{global_session.token}-{agent_card.id}"
        
        session = await self._session_service.get_or_create_session(
            session_id=session_id,
            user_id=global_session.token,
            app_name=APP_NAME
        )
        
        parent_context = self._create_invocation_context(
            remote_agent, session, prompt, invocation_id
        )
        
        # Execute via async generator
        async_generator = remote_agent.run_async(parent_context)
        if not async_generator:
            # Try fallback methods
            return await self._try_fallback_execution(remote_agent, prompt)
        
        # Process async generator chunks
        chunks = []
        async for chunk in async_generator:
            chunks.append(chunk)
        
        if not chunks:
            raise ValueError("ADK returned empty response, falling back to httpx")
        
        # Parse chunks
        result, data = ResponseParser.process_chunks(chunks)
        
        # Validate result
        if not result or result == EMPTY_RESPONSE_MSG:
            logger.warning(f"Empty Content object from ADK for agent {agent_card.id}, falling back to httpx for JSON response")
            raise ValueError("ADK returned empty response, falling back to httpx")
        
        logger.debug(f"RemoteA2aAgent ask successful for {agent_card.id}")
        return result, data

    async def _try_fallback_execution(self, remote_agent: RemoteA2aAgent, prompt: str) -> Tuple[str, Dict[str, Any]]:
        """Try alternative execution methods if run_async is not available."""
        if hasattr(remote_agent, "run"):
            result = await remote_agent.run(prompt)
        elif Agent:
            # Use Agent wrapper
            temp_agent = Agent(
                model="gemini-2.0-flash-exp",
                name="temp_executor",
                instruction="Execute the task using the provided agent.",
                sub_agents=[remote_agent],
            )
            result = await temp_agent.run(prompt)
        else:
            raise ValueError("RemoteA2aAgent has no run_async, run_live, or run method, and Agent wrapper unavailable")
        
        # Parse result
        return self._parse_adk_result(result)

    def _parse_adk_result(self, result: Any) -> Tuple[str, Dict[str, Any]]:
        """Parse result from ADK execution."""
        if isinstance(result, str):
            parsed = ResponseParser.parse_json_response(result)
            if parsed:
                output = ResponseParser.extract_output_from_dict(parsed)
                return output, parsed
            return result, {FIELD_OUTPUT: result}
        
        if isinstance(result, dict):
            output = ResponseParser.extract_output_from_dict(result)
            return output, result
        
        if hasattr(result, FIELD_CONTENT):
            # Content model - extract text from parts
            text_parts = ResponseParser.extract_text_from_content(result)
            output = " ".join(text_parts) if text_parts else ""
            
            if hasattr(result, "model_dump"):
                data = result.model_dump()
                # Try to parse output as JSON
                if output and output.strip().startswith("{"):
                    parsed = ResponseParser.parse_json_response(output)
                    if parsed:
                        data.update(parsed)
                        output = ResponseParser.extract_output_from_dict(parsed) or output
            else:
                data = {FIELD_OUTPUT: output}
            
            return output, data
        
        if hasattr(result, FIELD_TEXT):
            output = result.text
            data = result.model_dump() if hasattr(result, "model_dump") else {FIELD_OUTPUT: output}
            
            # Check if output text is JSON with delegate
            parsed = ResponseParser.parse_json_response(output)
            if parsed:
                data.update(parsed)
                output = ResponseParser.extract_output_from_dict(parsed) or output
            
            return output, data
        
        # Fallback: convert to string
        output = str(result)
        parsed = ResponseParser.parse_json_response(output)
        if parsed:
            return ResponseParser.extract_output_from_dict(parsed), parsed
        return output, {FIELD_OUTPUT: output}

    def _build_httpx_payload(
        self,
        prompt: str,
        agent_card: A2AAgentCard,
        agent_messages: List[AgentMessage],
        global_session: GlobalSession,
    ) -> Dict[str, Any]:
        """Build payload for httpx request."""
        return {
            "prompt": prompt,
            "message": prompt,  # A2A protocol compatibility
            "context_id": f"runner-{agent_card.id}",
            "task_id": f"task-{agent_card.id}",
            "metadata": {
                "agent_messages": [
                    {"role": m.role, "content": m.content, "ts": m.ts.isoformat()}
                    for m in agent_messages
                ],
                "global_messages": [
                    {"role": m.role, "content": m.content, "ts": m.ts.isoformat()}
                    for m in global_session.messages
                ],
                "shared_state": global_session.shared_state,
                "agent_id": agent_card.id,
            },
        }

    async def _run_with_httpx(
        self,
        agent_card: A2AAgentCard,
        agent_messages: List[AgentMessage],
        global_session: GlobalSession,
        prompt: str,
    ) -> Tuple[str, Dict[str, Any]]:
        """Fallback HTTP executor for agents that don't support A2A protocol."""
        payload = self._build_httpx_payload(prompt, agent_card, agent_messages, global_session)
        method = agent_card.method.upper()
        
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                if method == "POST":
                    resp = await client.post(agent_card.endpoint, json=payload)
                else:
                    resp = await client.request(method, agent_card.endpoint, json=payload)
                
                resp.raise_for_status()
                data = resp.json()
                output = ResponseParser.extract_output_from_dict(data)
                return output, data
        except httpx.HTTPStatusError as e:
            error_msg = f"Agent endpoint returned {e.response.status_code}: {e.response.text[:200]}"
            logger.error(f"Agent {agent_card.id} endpoint error: {error_msg}")
            raise ValueError(f"Agent {agent_card.name} endpoint unreachable: {e.response.status_code}")
        except httpx.ConnectError as e:
            error_msg = f"Cannot connect to agent endpoint {agent_card.endpoint}"
            logger.error(f"Agent {agent_card.id} connection error: {error_msg}")
            raise ValueError(f"Agent {agent_card.name} service is not running at {agent_card.endpoint}")
        except httpx.TimeoutException as e:
            error_msg = f"Timeout connecting to agent endpoint {agent_card.endpoint}"
            logger.error(f"Agent {agent_card.id} timeout error: {error_msg}")
            raise ValueError(f"Agent {agent_card.name} request timed out")
        except Exception as e:
            logger.error(f"Agent {agent_card.id} execution error: {e}")
            raise

    async def run(
        self,
        agent_card: A2AAgentCard,
        agent_messages: List[AgentMessage],
        global_session: GlobalSession,
        prompt: str,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Execute a remote agent using Google ADK RemoteA2aAgent.
        Falls back to httpx if ADK is not available.
        """
        if not agent_card.endpoint:
            raise ValueError(f"Remote agent {agent_card.id} missing endpoint")

        # Try to use Google ADK RemoteA2aAgent
        if ADK_AVAILABLE:
            try:
                return await self._execute_with_adk(agent_card, global_session, prompt)
            except ValueError as e:
                # Explicit fallback request
                if FALLBACK_MSG in str(e).lower():
                    logger.warning(f"ADK execution failed, falling back to httpx: {e}")
                else:
                    logger.warning(f"RemoteA2aAgent execution failed for {agent_card.id}: {e}. Falling back to httpx.")
            except Exception as e:
                logger.warning(f"Failed to use RemoteA2aAgent for {agent_card.id}: {e}. Falling back to httpx.")

        # Fallback to httpx implementation
        return await self._run_with_httpx(agent_card, agent_messages, global_session, prompt)

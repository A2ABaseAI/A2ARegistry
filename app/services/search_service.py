"""Search service for agent discovery."""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from ..config import settings
from ..models.agent import Agent
from ..schemas.agent import AgentSearchRequest, AgentSearchResponse


class SearchService:
    """Service for agent search operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.es_client = Elasticsearch([settings.elasticsearch_url])
        self.model = None  # Lazy load sentence transformer
        
    def _get_model(self):
        """Get or initialize the sentence transformer model."""
        if self.model is None:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.model
    
    def index_agent(self, agent: Agent) -> bool:
        """Index an agent in Elasticsearch."""
        try:
            doc = {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description or "",
                "provider": agent.provider,
                "tags": agent.tags or [],
                "capabilities": agent.capabilities or {},
                "auth_schemes": agent.auth_schemes or [],
                "tee_details": agent.tee_details or {},
                "is_public": agent.is_public,
                "is_active": agent.is_active,
                "created_at": agent.created_at.isoformat() if agent.created_at else None,
                "updated_at": agent.updated_at.isoformat() if agent.updated_at else None,
            }
            
            # Add semantic embedding if semantic search is enabled
            if settings.enable_federation:  # Use federation flag as proxy for semantic search
                model = self._get_model()
                text_for_embedding = f"{agent.name} {agent.description or ''} {' '.join(agent.tags or [])}"
                embedding = model.encode(text_for_embedding).tolist()
                doc["embedding"] = embedding
            
            self.es_client.index(
                index=settings.elasticsearch_index,
                id=agent.id,
                body=doc
            )
            return True
        except Exception as e:
            print(f"Error indexing agent {agent.id}: {e}")
            return False
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from Elasticsearch index."""
        try:
            self.es_client.delete(
                index=settings.elasticsearch_index,
                id=agent_id,
                ignore=[404]
            )
            return True
        except Exception as e:
            print(f"Error removing agent {agent_id}: {e}")
            return False
    
    def search_agents(
        self,
        search_request: AgentSearchRequest,
        client_id: Optional[str] = None
    ) -> AgentSearchResponse:
        """Search for agents using various methods."""
        
        # Build Elasticsearch query
        query = {
            "bool": {
                "must": [],
                "filter": []
            }
        }
        
        # Text search
        if search_request.query:
            if search_request.semantic and search_request.vector:
                # Semantic search using vector similarity
                query["bool"]["must"].append({
                    "knn": {
                        "field": "embedding",
                        "query_vector": search_request.vector,
                        "k": search_request.top,
                        "num_candidates": search_request.top * 2
                    }
                })
            else:
                # Lexical search
                query["bool"]["must"].append({
                    "multi_match": {
                        "query": search_request.query,
                        "fields": ["name^2", "description", "provider", "tags"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                })
        
        # Filters
        query["bool"]["filter"].append({"term": {"is_active": True}})
        
        if not client_id:  # Only public agents for non-authenticated requests
            query["bool"]["filter"].append({"term": {"is_public": True}})
        
        if search_request.filters:
            for key, value in search_request.filters.items():
                if key == "provider":
                    query["bool"]["filter"].append({"term": {"provider": value}})
                elif key == "tags":
                    if isinstance(value, list):
                        query["bool"]["filter"].append({"terms": {"tags": value}})
                    else:
                        query["bool"]["filter"].append({"term": {"tags": value}})
                elif key == "capabilities":
                    if isinstance(value, dict):
                        for cap_key, cap_value in value.items():
                            query["bool"]["filter"].append({
                                "term": {f"capabilities.{cap_key}": cap_value}
                            })
        
        # Execute search
        try:
            response = self.es_client.search(
                index=settings.elasticsearch_index,
                body={
                    "query": query,
                    "size": search_request.per_page,
                    "from": (search_request.page - 1) * search_request.per_page,
                    "sort": [
                        {"_score": {"order": "desc"}},
                        {"created_at": {"order": "desc"}}
                    ]
                }
            )
            
            # Extract results
            hits = response["hits"]["hits"]
            total_count = response["hits"]["total"]["value"]
            
            # Convert to agent responses
            agents = []
            for hit in hits:
                source = hit["_source"]
                agent_response = {
                    "id": source["id"],
                    "name": source["name"],
                    "version": "",  # Will be filled from database
                    "description": source["description"],
                    "provider": source["provider"],
                    "tags": source["tags"],
                    "is_public": source["is_public"],
                    "is_active": source["is_active"],
                    "location": {
                        "url": f"{settings.registry_base_url}/agents/{source['id']}/card",
                        "type": "agent_card"
                    },
                    "capabilities": source["capabilities"],
                    "auth_schemes": source["auth_schemes"],
                    "tee_details": source["tee_details"],
                    "created_at": source["created_at"],
                    "updated_at": source["updated_at"],
                }
                agents.append(agent_response)
            
            # Build search metadata
            search_metadata = {
                "query": search_request.query,
                "filters_applied": search_request.filters or {},
                "search_time_ms": response["took"],
                "total_hits": total_count,
                "semantic_search": search_request.semantic,
                "similarity_threshold": search_request.similarity_threshold if search_request.semantic else None
            }
            
            # Build pagination info
            pagination = {
                "page": search_request.page,
                "per_page": search_request.per_page,
                "total_count": total_count,
                "total_pages": (total_count + search_request.per_page - 1) // search_request.per_page
            }
            
            return AgentSearchResponse(
                registry_version=settings.app_version,
                timestamp=datetime.utcnow().isoformat(),
                resources=agents,
                total_count=total_count,
                search_metadata=search_metadata,
                pagination=pagination
            )
            
        except Exception as e:
            print(f"Error searching agents: {e}")
            # Fallback to database search
            return self._fallback_search(search_request, client_id)
    
    def _fallback_search(
        self,
        search_request: AgentSearchRequest,
        client_id: Optional[str] = None
    ) -> AgentSearchResponse:
        """Fallback to database search if Elasticsearch fails."""
        from .agent_service import AgentService
        
        agent_service = AgentService(self.db)
        agents = agent_service.search_agents(search_request, client_id)
        
        # Convert to response format
        agent_responses = []
        for agent in agents:
            agent_responses.append(agent.to_agent_response())
        
        search_metadata = {
            "query": search_request.query,
            "filters_applied": search_request.filters or {},
            "search_time_ms": 0,
            "total_hits": len(agent_responses),
            "semantic_search": False,
            "fallback_search": True
        }
        
        pagination = {
            "page": search_request.page,
            "per_page": search_request.per_page,
            "total_count": len(agent_responses),
            "total_pages": 1
        }
        
        return AgentSearchResponse(
            registry_version=settings.app_version,
            timestamp=datetime.utcnow().isoformat(),
            resources=agent_responses,
            total_count=len(agent_responses),
            search_metadata=search_metadata,
            pagination=pagination
        )
    
    def create_index(self) -> bool:
        """Create the Elasticsearch index with proper mapping."""
        try:
            mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "name": {"type": "text", "analyzer": "standard"},
                        "description": {"type": "text", "analyzer": "standard"},
                        "provider": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "capabilities": {"type": "object"},
                        "auth_schemes": {"type": "object"},
                        "tee_details": {"type": "object"},
                        "is_public": {"type": "boolean"},
                        "is_active": {"type": "boolean"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"},
                    }
                }
            }
            
            # Add embedding field if semantic search is enabled
            if settings.enable_federation:
                mapping["mappings"]["properties"]["embedding"] = {
                    "type": "dense_vector",
                    "dims": 384  # all-MiniLM-L6-v2 dimension
                }
            
            self.es_client.indices.create(
                index=settings.elasticsearch_index,
                body=mapping,
                ignore=400  # Ignore if index already exists
            )
            return True
        except Exception as e:
            print(f"Error creating Elasticsearch index: {e}")
            return False

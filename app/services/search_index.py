"""OpenSearch indexing/search wrapper."""

from typing import Any, Dict, List, Optional, Tuple

from opensearchpy import OpenSearch

from ..config import settings

INDEX_NAME = getattr(settings, "elasticsearch_index", "a2a_agents")


class SearchIndex:
    def __init__(self):
        self.client = OpenSearch(hosts=[settings.opensearch_url])

    def ensure_index(self) -> None:
        if self.client.indices.exists(index=INDEX_NAME):
            return
        mapping = {
            "settings": {"index": {"number_of_shards": 1, "number_of_replicas": 0}},
            "mappings": {
                "properties": {
                    "tenantId": {"type": "keyword"},
                    "agentId": {"type": "keyword"},
                    "version": {"type": "keyword"},
                    "protocolVersion": {"type": "keyword"},
                    "name": {"type": "text"},
                    "description": {"type": "text"},
                    "publisherId": {"type": "keyword"},
                    "capabilities": {"type": "object", "enabled": True},
                    "skills.name": {"type": "text"},
                    "skills.description": {"type": "text"},
                    "public": {"type": "boolean"},
                    "createdAt": {"type": "date"},
                }
            },
        }
        self.client.indices.create(INDEX_NAME, body=mapping)

    def index_version(self, doc_id: str, body: Dict[str, Any]) -> bool:
        try:
            self.client.index(index=INDEX_NAME, id=doc_id, body=body, refresh=True)
            return True
        except Exception:
            return False

    def search(
        self,
        tenant_id: str,
        q: Optional[str],
        filters: Dict[str, Any],
        top: int,
        skip: int,
    ) -> Tuple[List[Dict[str, Any]], int]:
        must: List[Dict[str, Any]] = [{"term": {"tenantId": tenant_id}}]
        if q:
            must.append(
                {
                    "multi_match": {
                        "query": q,
                        "fields": ["name^3", "description^2", "skills.name", "skills.description"],
                    }
                }
            )
        # Filters
        if "protocolVersion" in filters:
            must.append({"term": {"protocolVersion": filters["protocolVersion"]}})
        if "publisherId" in filters:
            must.append({"term": {"publisherId": filters["publisherId"]}})
        if "capabilities" in filters and isinstance(filters["capabilities"], list):
            for cap in filters["capabilities"]:
                must.append({"exists": {"field": f"capabilities.{cap}"}})

        query = {"query": {"bool": {"must": must}}, "from": skip, "size": top}
        res = self.client.search(index=INDEX_NAME, body=query)
        hits = res.get("hits", {}).get("hits", [])
        total = res.get("hits", {}).get("total", {}).get("value", len(hits))
        items = [h.get("_source", {}) for h in hits]
        return items, int(total)

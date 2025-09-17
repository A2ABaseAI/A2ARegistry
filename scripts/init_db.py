#!/usr/bin/env python3
"""Initialize the A2A Agent Registry database with sample data."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, create_tables
from app.models.client import Client
from app.models.agent import Agent
from app.models.client import ClientEntitlement
from app.auth import get_password_hash
from app.services.agent_service import AgentService
from app.services.client_service import ClientService
from app.services.search_service import SearchService
from app.schemas.agent import AgentCreate


def create_sample_data():
    """Create sample data for testing and demonstration."""
    db = SessionLocal()
    
    try:
        # Create tables
        create_tables()
        
        # Create sample clients
        admin_client = Client(
            id="admin-client",
            name="Admin Client",
            description="Administrative client with full access",
            client_id="admin_client",
            client_secret=get_password_hash("admin_secret"),
            scopes=["admin", "agent:read", "agent:write", "client:manage"],
            is_active=True
        )
        
        user_client = Client(
            id="user-client",
            name="User Client",
            description="Regular user client",
            client_id="user_client",
            client_secret=get_password_hash("user_secret"),
            scopes=["agent:read", "agent:write"],
            is_active=True
        )
        
        demo_client = Client(
            id="demo-client",
            name="Demo Client",
            description="Demo client for testing and demonstration",
            client_id="demo-client",
            client_secret=get_password_hash("demo-secret"),
            scopes=["agent:read", "agent:write", "client:read"],
            is_active=True
        )
        
        db.add(admin_client)
        db.add(user_client)
        db.add(demo_client)
        db.commit()
        
        # Create sample agents
        agent_service = AgentService(db)
        
        # IT Support Agent
        it_agent_data = {
            "agent_card": {
                "id": "it-support-agent",
                "name": "IT Support Agent",
                "version": "2.1.0",
                "description": "Handles IT support queries and troubleshooting",
                "capabilities": {
                    "a2a_version": "1.0",
                    "supported_protocols": ["http", "grpc"],
                    "max_concurrent_requests": 100,
                    "timeout_seconds": 30,
                    "rate_limit_per_minute": 1000
                },
                "skills": {
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "context": {"type": "object"}
                        }
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "response": {"type": "string"},
                            "confidence": {"type": "number"}
                        }
                    }
                },
                "auth_schemes": [
                    {
                        "type": "apiKey",
                        "location": "header",
                        "name": "X-API-Key"
                    },
                    {
                        "type": "oauth2",
                        "flow": "client_credentials",
                        "token_url": "https://auth.example.com/oauth/token",
                        "scopes": ["agent:read", "agent:write"]
                    }
                ],
                "tee_details": {
                    "enabled": True,
                    "provider": "Intel SGX",
                    "attestation": "required",
                    "version": "2.0"
                },
                "provider": "Enterprise IT",
                "tags": ["support", "it", "troubleshooting"],
                "contact_url": "https://it.example.com/contact",
                "documentation_url": "https://docs.example.com/it-agent",
                "location": {
                    "url": "https://it.example.com/.well-known/agent.json",
                    "type": "agent_card"
                }
            },
            "is_public": True
        }
        
        it_agent = agent_service.create_agent(agent_data=AgentCreate(**it_agent_data), client_id=admin_client.id)
        
        # Benefits Agent
        benefits_agent_data = {
            "agent_card": {
                "id": "benefits-agent",
                "name": "Benefits Agent",
                "version": "1.5.0",
                "description": "Manages employee benefits and HR queries",
                "capabilities": {
                    "a2a_version": "1.0",
                    "supported_protocols": ["http"],
                    "max_concurrent_requests": 50,
                    "timeout_seconds": 45,
                    "rate_limit_per_minute": 500
                },
                "skills": {
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "employee_id": {"type": "string"}
                        }
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "answer": {"type": "string"},
                            "benefits_info": {"type": "object"}
                        }
                    }
                },
                "auth_schemes": [
                    {
                        "type": "oauth2",
                        "flow": "client_credentials",
                        "token_url": "https://hr.example.com/oauth/token",
                        "scopes": ["benefits:read"]
                    }
                ],
                "provider": "HR Department",
                "tags": ["hr", "benefits", "employee"],
                "location": {
                    "url": "https://hr.example.com/agents/benefits.json",
                    "type": "agent_card"
                }
            },
            "is_public": True
        }
        
        benefits_agent = agent_service.create_agent(agent_data=AgentCreate(**benefits_agent_data), client_id=admin_client.id)
        
        # Customer Service Agent
        customer_agent_data = {
            "agent_card": {
                "id": "customer-service-agent",
                "name": "Customer Service Agent",
                "version": "3.0.0",
                "description": "Handles customer inquiries and support requests",
                "capabilities": {
                    "a2a_version": "1.0",
                    "supported_protocols": ["http", "websocket"],
                    "max_concurrent_requests": 200,
                    "timeout_seconds": 60,
                    "rate_limit_per_minute": 2000
                },
                "skills": {
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "customer_query": {"type": "string"},
                            "customer_id": {"type": "string"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                        }
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "response": {"type": "string"},
                            "ticket_id": {"type": "string"},
                            "escalation_required": {"type": "boolean"}
                        }
                    }
                },
                "auth_schemes": [
                    {
                        "type": "apiKey",
                        "location": "header",
                        "name": "X-API-Key"
                    }
                ],
                "provider": "Customer Success Team",
                "tags": ["customer", "support", "service"],
                "location": {
                    "url": "https://support.example.com/agents/customer.json",
                    "type": "agent_card"
                }
            },
            "is_public": True
        }
        
        customer_agent = agent_service.create_agent(agent_data=AgentCreate(**customer_agent_data), client_id=admin_client.id)
        
        # Create entitlements
        client_service = ClientService(db)
        
        # Give user client access to IT and Benefits agents
        it_entitlement = ClientEntitlement(
            id="it-entitlement",
            client_id=user_client.id,
            agent_id=it_agent.id,
            scopes=["agent:read"],
            is_active=True
        )
        
        benefits_entitlement = ClientEntitlement(
            id="benefits-entitlement",
            client_id=user_client.id,
            agent_id=benefits_agent.id,
            scopes=["agent:read"],
            is_active=True
        )
        
        db.add(it_entitlement)
        db.add(benefits_entitlement)
        db.commit()
        
        # Index agents in search
        search_service = SearchService(db)
        search_service.create_index()
        search_service.index_agent(it_agent)
        search_service.index_agent(benefits_agent)
        search_service.index_agent(customer_agent)
        
        print("✅ Sample data created successfully!")
        print(f"📊 Created {len([admin_client, user_client])} clients")
        print(f"🤖 Created {len([it_agent, benefits_agent, customer_agent])} agents")
        print(f"🔗 Created {len([it_entitlement, benefits_entitlement])} entitlements")
        print("\n🔑 Test credentials:")
        print("Admin: client_id=admin_client, client_secret=admin_secret")
        print("User:  client_id=user_client, client_secret=user_secret")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()

# A2A Multi-Agent Orchestration Examples

This directory contains comprehensive examples demonstrating multi-agent orchestration using the A2A (Agent-to-Agent) Protocol. The examples showcase real-world scenarios where multiple AI agents work together to solve complex problems.

## 🎯 Overview

This collection demonstrates:
- **Multi-agent orchestration** using the A2A SDK framework
- **Real agent communication** through the A2A Registry
- **Customer service workflows** with Shopify and UPS agents
- **Agent discovery and coordination** patterns
- **Production-ready implementations** with proper error handling

## 📁 Directory Structure

```
crewai-and-langchain-examples/
├── agent_runner_example.py          # Main multi-agent orchestration framework
├── customer_service_demo.py          # Customer service workflow demo
├── README.md                         # This file
├── shopify-status-agent/             # Shopify order tracking agent
│   ├── app/                         # LangChain + FastAPI implementation
│   ├── simple_server.py             # Mock server for testing
│   ├── register_with_a2a.py        # A2A Registry registration
│   └── README.md                    # Agent-specific documentation
└── ups-tracking-agent/              # UPS package tracking agent
    ├── src/ups_agent/               # CrewAI implementation
    ├── simple_server.py             # Mock server for testing
    ├── register_with_a2a.py        # A2A Registry registration
    └── README.md                    # Agent-specific documentation
```

## 🚀 Quick Start

### Prerequisites

1. **A2A Registry Running**: Ensure the A2A Registry is running on `http://localhost:8000`
2. **Python Environment**: Python 3.11+ with virtual environment activated
3. **Dependencies**: Install required packages

```bash
cd /Users/user/dev/a2a-registry
source venv/bin/activate
pip install -r requirements.txt
```

### 1. Register Agents with A2A Registry

```bash
# Register Shopify Agent
cd examples/crewai-and-langchain-examples/shopify-status-agent
python register_with_a2a.py

# Register UPS Agent
cd ../ups-tracking-agent
python register_with_a2a.py
```

### 2. Start Agent Services

```bash
# Start Shopify Agent (Terminal 1)
cd examples/crewai-and-langchain-examples/shopify-status-agent
python simple_server.py

# Start UPS Agent (Terminal 2)
cd examples/crewai-and-langchain-examples/ups-tracking-agent
python simple_server.py
```

### 3. Run Multi-Agent Demos

```bash
# Run the main orchestration example
cd examples/crewai-and-langchain-examples
python agent_runner_example.py

# Run the customer service workflow demo
python customer_service_demo.py
```

## 🎭 Demo Scenarios

### 1. Multi-Agent Orchestration (`agent_runner_example.py`)

This comprehensive example demonstrates:

- **Agent Discovery**: Loading agents from the A2A Registry
- **Task Delegation**: Assigning specific tasks to individual agents
- **Workflow Management**: Creating and executing multi-step workflows
- **Agent Coordination**: Sequential and parallel agent execution
- **Error Handling**: Robust error handling and recovery

**Key Features:**
- ✅ Real agent communication through A2A Registry
- ✅ Multi-agent workflow orchestration
- ✅ Task delegation and coordination
- ✅ Sequential and parallel execution patterns
- ✅ Comprehensive error handling and logging

### 2. Customer Service Workflow (`customer_service_demo.py`)

This focused demo showcases a real-world customer service scenario:

1. **Customer Inquiry**: Customer asks about order status
2. **Shopify Agent**: Processes order inquiry and retrieves tracking info
3. **UPS Agent**: Provides detailed package tracking information
4. **Coordinated Response**: Both agents work together for comprehensive customer service

**Workflow:**
```
Customer → Shopify Agent → UPS Agent → Final Response
```

**Example Scenario:**
- Customer: "Hi, I'd like to check the status of my order ORD-2024-001"
- Shopify Agent: Retrieves order details and tracking number
- UPS Agent: Provides package location and delivery estimate
- Result: Comprehensive status update for the customer

## 🤖 Agent Implementations

### Shopify Status Agent

**Technology**: LangChain + FastAPI
**Purpose**: Order tracking and customer service
**Features**:
- Real-time Shopify API integration
- Order status lookup and tracking
- Customer inquiry processing
- Mock mode for testing

**Endpoints**:
- `GET /healthz` - Health check
- `POST /chat` - Chat interface for order inquiries

### UPS Tracking Agent

**Technology**: CrewAI + FastAPI
**Purpose**: Package tracking and delivery status
**Features**:
- UPS API integration with OAuth
- Multiple tracking number support
- Natural language processing
- Comprehensive status reporting

**Endpoints**:
- `GET /health` - Health check
- `POST /chat` - Chat interface for tracking inquiries

## 🔧 Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Shopify Agent │    │    UPS Agent    │
│   Port: 8005    │    │   Port: 8006    │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┼───────────────────────┐
                                 │                       │
                    ┌─────────────────┐    ┌─────────────────┐
                    │ Multi-Agent     │    │ A2A Registry    │
                    │ Orchestrator    │    │   Port: 8000    │
                    │ (Python SDK)    │    │                 │
                    └─────────────────┘    └─────────────────┘
```

## 📊 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| A2A Registry | http://localhost:8000 | Agent registry and discovery |
| Shopify Agent | http://localhost:8005 | Order tracking service |
| UPS Agent | http://localhost:8006 | Package tracking service |
| Multi-Agent Demo | Python scripts | Orchestration examples |

## 🧪 Testing Commands

### Direct Agent Communication

```bash
# Test Shopify Agent
curl -X POST http://localhost:8005/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the status of order #1001?", "session_id": "test-session"}'

# Test UPS Agent
curl -X POST http://localhost:8006/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Track package 1Z999AA10123456784", "session_id": "test-session"}'
```

### Registry API Testing

```bash
# List all agents
curl -H "Authorization: Bearer dev-admin-api-key" \
  http://localhost:8000/agents/public

# Get specific agent card
curl -H "Authorization: Bearer dev-admin-api-key" \
  http://localhost:8000/agents/{agent-id}/card
```

## 🔍 Key Features Demonstrated

### ✅ Multi-Agent Orchestration
- **Agent Discovery**: Automatic loading from A2A Registry
- **Task Delegation**: Assigning specific tasks to agents
- **Workflow Management**: Creating complex multi-step workflows
- **Coordination Patterns**: Sequential and parallel execution

### ✅ Real-World Integration
- **No Mock Data**: Uses real agents and registry communication
- **Production Patterns**: Error handling, logging, monitoring
- **A2A Protocol**: Standardized agent communication
- **Service Discovery**: Dynamic agent loading and management

### ✅ Customer Service Workflows
- **End-to-End Scenarios**: Complete customer inquiry processing
- **Agent Collaboration**: Multiple agents working together
- **Context Preservation**: Maintaining context across agent interactions
- **Comprehensive Responses**: Detailed customer service information

## 🛠️ Development

### Running Individual Components

```bash
# Run only the orchestration framework
python agent_runner_example.py

# Run only the customer service demo
python customer_service_demo.py

# Run individual agent servers
cd shopify-status-agent && python simple_server.py
cd ups-tracking-agent && python simple_server.py
```

### Customizing Workflows

The orchestration framework supports custom workflows:

```python
# Create custom workflow
workflow = orchestrator.create_workflow(
    name="Custom Workflow",
    steps_config=[
        {
            "name": "step1",
            "agent_id": "shopify-agent-id",
            "message": "Process order inquiry",
            "depends_on": []
        },
        {
            "name": "step2", 
            "agent_id": "ups-agent-id",
            "message": "Get tracking information",
            "depends_on": ["step1"]
        }
    ]
)

# Execute workflow
result = await orchestrator.execute_workflow(workflow.id)
```

## 🔧 Configuration

### Environment Variables

```bash
# A2A Registry Configuration
A2A_REGISTRY_URL=http://localhost:8000
A2A_REGISTRY_API_KEY=dev-admin-api-key

# Agent Service URLs (auto-discovered from registry)
SHOPIFY_AGENT_URL=http://localhost:8005
UPS_AGENT_URL=http://localhost:8006
```

### Agent Registration

Both agents are registered with the A2A Registry using the official SDK:

```python
# Example registration
agent_card = (
    AgentBuilder("Agent Name", "Description", "1.0.0", "Organization")
    .with_location("http://localhost:8005", "api_endpoint")
    .with_capabilities(capabilities)
    .with_auth_schemes(auth_schemes)
    .build()
)

client = A2AClient(registry_url="http://localhost:8000", api_key="dev-admin-api-key")
result = client.publish_agent(agent_card)
```

## 📋 Troubleshooting

### Common Issues

1. **Registry Not Running**
   ```bash
   # Start the A2A Registry
   cd /Users/user/dev/a2a-registry
   source venv/bin/activate
   python -m app.main
   ```

2. **Agents Not Registered**
   ```bash
   # Re-register agents
   cd shopify-status-agent && python register_with_a2a.py
   cd ups-tracking-agent && python register_with_a2a.py
   ```

3. **Agent Services Not Running**
   ```bash
   # Check if services are running
   curl http://localhost:8005/healthz  # Shopify
   curl http://localhost:8006/health   # UPS
   ```

4. **SDK Import Errors**
   ```bash
   # Ensure A2A SDK is installed
   pip install -e sdk/python/
   ```

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎯 Next Steps

1. **Extend Agents**: Add more sophisticated business logic
2. **Custom Workflows**: Create domain-specific multi-agent workflows
3. **Authentication**: Implement proper security and authentication
4. **Monitoring**: Add comprehensive observability and monitoring
5. **Scaling**: Deploy across multiple machines and environments

## 📖 Documentation

- **Agent Documentation**: See individual agent README files
- **A2A Protocol**: [A2A Protocol Specification](https://github.com/a2aproject/a2a-protocol)
- **A2A SDK**: [A2A SDK Documentation](https://github.com/a2aproject/a2a-sdk)
- **Registry API**: http://localhost:8000/docs (when registry is running)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**🎯 This collection successfully demonstrates real-world multi-agent orchestration using the A2A Protocol with production-ready implementations!**
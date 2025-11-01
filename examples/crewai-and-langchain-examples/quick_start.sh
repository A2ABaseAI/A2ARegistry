#!/bin/bash
# Quick Start Script for A2A Multi-Agent Examples

echo "🚀 A2A Multi-Agent Orchestration Quick Start"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "agent_runner_example.py" ]; then
    echo "❌ Please run this script from the crewai-and-langchain-examples directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "../../venv" ]; then
    echo "❌ Virtual environment not found. Please ensure the virtual environment is set up"
    echo "   Run: cd /Users/user/dev/a2a-registry && python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../../venv/bin/activate

# Check if A2A Registry is running
echo "🔍 Checking A2A Registry..."
if curl -s -H "Authorization: Bearer dev-admin-api-key" http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ A2A Registry is running on http://localhost:8000"
else
    echo "❌ A2A Registry is not running. Please start it first:"
    echo "   cd /Users/user/dev/a2a-registry && source venv/bin/activate && python -m registry.main"
    exit 1
fi

echo ""
echo "📋 Available Options:"
echo "1. Register agents with A2A Registry"
echo "2. Start agent services"
echo "3. Run multi-agent orchestration demo"
echo "4. Run customer service workflow demo"
echo "5. Exit"
echo ""

read -p "Choose an option (1-5): " choice

case $choice in
    1)
        echo "📝 Registering agents with A2A Registry..."
        
        echo "Registering Shopify Agent..."
        cd shopify-status-agent
        python register_with_a2a.py
        cd ..
        
        echo "Registering UPS Agent..."
        cd ups-tracking-agent
        python register_with_a2a.py
        cd ..
        
        echo "✅ Agents registered successfully!"
        ;;
    2)
        echo "🚀 Starting agent services..."
        echo "Note: This will start services in the background."
        echo "Use 'pkill -f simple_server.py' to stop them later."
        
        echo "Starting Shopify Agent on port 8005..."
        cd shopify-status-agent
        python simple_server.py &
        cd ..
        
        echo "Starting UPS Agent on port 8006..."
        cd ups-tracking-agent
        python simple_server.py &
        cd ..
        
        sleep 3
        
        # Check if services are running
        if curl -s http://localhost:8005/healthz > /dev/null 2>&1; then
            echo "✅ Shopify Agent is running on http://localhost:8005"
        else
            echo "❌ Shopify Agent failed to start"
        fi
        
        if curl -s http://localhost:8006/health > /dev/null 2>&1; then
            echo "✅ UPS Agent is running on http://localhost:8006"
        else
            echo "❌ UPS Agent failed to start"
        fi
        ;;
    3)
        echo "🎭 Running multi-agent orchestration demo..."
        python agent_runner_example.py
        ;;
    4)
        echo "🛍️ Running customer service workflow demo..."
        python customer_service_demo.py
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid option. Please choose 1-5."
        exit 1
        ;;
esac

echo ""
echo "🎉 Operation completed!"
echo ""
echo "📖 For more information, see README.md"
echo "🔧 To stop agent services: pkill -f simple_server.py"

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import {
  Book,
  Code,
  Shield,
  Database,
  Search,
  Heart,
  Key,
  Users,
  Globe,
  ChevronDown,
  ChevronUp,
  ChevronRight,
  Copy,
  Check,
  ExternalLink,
  Zap,
  Lock,
  Server,
  Play,
  Lightbulb,
  Rocket,
  Puzzle,
  Network,
} from 'lucide-react';

export default function DocsPage() {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['introduction']));

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const copyToClipboard = async (text: string, id: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const CodeBlock = ({ children, language = 'bash', id }: { children: string; language?: string; id: string }) => {
    // Map language names to syntax highlighter languages
    const langMap: Record<string, string> = {
      bash: 'bash',
      sh: 'bash',
      python: 'python',
      js: 'javascript',
      javascript: 'javascript',
      ts: 'typescript',
      typescript: 'typescript',
      go: 'go',
      java: 'java',
      xml: 'xml',
      json: 'json',
      yaml: 'yaml',
      http: 'http',
      curl: 'bash',
    };

    const highlightedLang = langMap[language.toLowerCase()] || language.toLowerCase() || 'text';

    return (
      <div className="relative group">
        <SyntaxHighlighter
          language={highlightedLang}
          style={vscDarkPlus}
          customStyle={{
            margin: 0,
            padding: '1rem',
            borderRadius: '0.5rem',
            fontSize: '0.875rem',
            lineHeight: '1.5',
            background: '#1e1e1e',
          }}
          PreTag="div"
        >
          {children}
        </SyntaxHighlighter>
        <button
          onClick={() => copyToClipboard(children, id)}
          className="absolute top-2 right-2 p-2 bg-gray-800 hover:bg-gray-700 rounded transition-colors opacity-0 group-hover:opacity-100 z-10"
          aria-label="Copy code"
        >
          {copiedCode === id ? (
            <Check className="h-4 w-4 text-green-400" />
          ) : (
            <Copy className="h-4 w-4 text-gray-300" />
          )}
        </button>
      </div>
    );
  };

  const InfoBox = ({ children, type = 'info' }: { children: React.ReactNode; type?: 'info' | 'tip' | 'warning' }) => (
    <div
      className={`p-4 rounded-lg border ${
        type === 'tip'
          ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
          : type === 'warning'
            ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800'
            : 'bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-800'
      }`}
    >
      {children}
    </div>
  );

  const sections = [
    {
      id: 'introduction',
      title: 'Introduction to A2A',
      icon: Lightbulb,
      content: (
        <div className="space-y-6">
          <div className="prose dark:prose-invert max-w-none">
            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">What is A2A?</h3>
            <p className="text-lg text-gray-700 dark:text-gray-300 mb-4">
              A2A stands for <strong>Agent-to-Agent</strong> — a protocol and ecosystem that enables AI agents to discover, communicate, and collaborate with each other seamlessly.
            </p>
            <p className="text-gray-700 dark:text-gray-300 mb-6">
              Think of it like a marketplace where AI agents can find each other, understand each other's capabilities, and work together to solve complex problems. Just like how humans collaborate by understanding what each person can do, A2A agents can discover each other's skills and capabilities.
            </p>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <Network className="h-8 w-8 text-primary-600 dark:text-primary-400 mb-3" />
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Agent Discovery</h4>
                <p className="text-gray-600 dark:text-gray-400">
                  Agents can discover each other's capabilities and find the right agents for specific tasks.
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <Puzzle className="h-8 w-8 text-primary-600 dark:text-primary-400 mb-3" />
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Agent Collaboration</h4>
                <p className="text-gray-600 dark:text-gray-400">
                  Multiple agents can work together, delegating tasks and combining their expertise.
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <Globe className="h-8 w-8 text-primary-600 dark:text-primary-400 mb-3" />
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Standardized Protocol</h4>
                <p className="text-gray-600 dark:text-gray-400">
                  A common protocol that all agents understand, enabling seamless communication.
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <Shield className="h-8 w-8 text-primary-600 dark:text-primary-400 mb-3" />
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Secure Communication</h4>
                <p className="text-gray-600 dark:text-gray-400">
                  Built-in security and authentication for safe agent-to-agent interactions.
                </p>
              </div>
            </div>

            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-8">How A2A Works - Visual Flow</h3>
            
            {/* Visual Flow Diagram */}
            <div className="bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 rounded-xl p-8 mb-8 border-2 border-primary-200 dark:border-primary-800">
              <div className="space-y-6">
                {/* Step 1 */}
                <div className="flex items-center gap-4">
                  <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold text-lg">
                    1
                  </div>
                  <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg p-4 border-2 border-primary-300 dark:border-primary-700 shadow-md">
                    <div className="flex items-center gap-3 mb-2">
                      <Users className="h-5 w-5 text-primary-600 dark:text-primary-400" />
                      <span className="font-semibold text-gray-900 dark:text-white">Customer asks question</span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">"Where is my package?"</p>
                  </div>
                </div>
                
                {/* Arrow */}
                <div className="flex justify-center">
                  <ChevronDown className="h-6 w-6 text-primary-500" />
                </div>

                {/* Step 2 */}
                <div className="flex items-center gap-4">
                  <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold text-lg">
                    2
                  </div>
                  <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg p-4 border-2 border-primary-300 dark:border-primary-700 shadow-md">
                    <div className="flex items-center gap-3 mb-2">
                      <Search className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                      <span className="font-semibold text-gray-900 dark:text-white">Customer Service Agent searches Registry</span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Finds tracking agents: UPS Agent, FedEx Agent</p>
                  </div>
                </div>

                {/* Arrow */}
                <div className="flex justify-center">
                  <ChevronDown className="h-6 w-6 text-primary-500" />
                </div>

                {/* Step 3 */}
                <div className="flex items-center gap-4">
                  <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold text-lg">
                    3
                  </div>
                  <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg p-4 border-2 border-green-300 dark:border-green-700 shadow-md">
                    <div className="flex items-center gap-3 mb-2">
                      <Network className="h-5 w-5 text-green-600 dark:text-green-400" />
                      <span className="font-semibold text-gray-900 dark:text-white">Delegates to UPS Tracking Agent</span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Agent detected UPS tracking number (starts with "1Z")</p>
                  </div>
                </div>

                {/* Arrow */}
                <div className="flex justify-center">
                  <ChevronDown className="h-6 w-6 text-primary-500" />
                </div>

                {/* Step 4 */}
                <div className="flex items-center gap-4">
                  <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold text-lg">
                    4
                  </div>
                  <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg p-4 border-2 border-purple-300 dark:border-purple-700 shadow-md">
                    <div className="flex items-center gap-3 mb-2">
                      <Check className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                      <span className="font-semibold text-gray-900 dark:text-white">Returns combined response</span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Tracking information provided to customer</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 rounded-lg p-6 mb-6">
              <p className="text-gray-700 dark:text-gray-300">
                This is <strong>multi-agent orchestration</strong> — agents working together seamlessly, discovered through the registry!
              </p>
            </div>

            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-8">What is the A2A Registry?</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              The <strong>A2A Agent Registry</strong> is like a phone book or directory for AI agents. It's a centralized service where:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 mb-6">
              <li>Agents can <strong>register</strong> themselves and describe their capabilities</li>
              <li>Other agents can <strong>discover</strong> available agents and their skills</li>
              <li>Developers can <strong>publish</strong> new agents to make them available</li>
              <li>Users can <strong>search</strong> for agents based on what they need</li>
            </ul>

            <InfoBox type="tip">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <strong>💡 Think of it this way:</strong> Just like you use Google to find websites, agents use the A2A Registry to find other agents. The registry tells agents "who can do what" and "how to talk to them."
              </p>
            </InfoBox>
          </div>
        </div>
      ),
    },
    {
      id: 'getting-started',
      title: 'Getting Started Tutorial',
      icon: Rocket,
      content: (
        <div className="space-y-6">
          <div className="prose dark:prose-invert max-w-none">
            <p className="text-lg text-gray-700 dark:text-gray-300 mb-6">
              Let's walk through building your first A2A-integrated application step by step!
            </p>

            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">Step 1: Install the SDK</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              First, install the A2A Registry Python SDK:
            </p>
            <CodeBlock id="install-sdk" language="bash">
{`# Install the Python SDK
pip install a2a-reg-sdk

# Or install from source
cd sdk/python
pip install -e .`}
            </CodeBlock>

            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-8">Step 2: Initialize the Client</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              Create a client instance and configure it with your credentials:
            </p>
            <CodeBlock id="init-client" language="python">
{`from a2a_reg_sdk import A2ARegClient

# Initialize the client with your credentials
client = A2ARegClient(
    registry_url="http://localhost:8000",
    client_id="myusername",  # Your username
    client_secret="secure-password-123",  # Your password
    scope="read write"  # Required permissions
)

# Authenticate with the registry
client.authenticate()
print("✅ Successfully authenticated!")`}
            </CodeBlock>
            <InfoBox type="tip">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <strong>💡 Tip:</strong> The SDK automatically handles token management for you. It will authenticate, refresh tokens, and manage session state - you don't need to worry about tokens manually!
              </p>
            </InfoBox>

            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-8">Step 3: Use the Runner Framework</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              The Runner framework integrates Registry and OpenSearch for automatic agent discovery and execution:
            </p>
            <CodeBlock id="use-runner" language="python">
{`import requests

RUNNER_URL = "http://localhost:8001"
REGISTRY_URL = "http://localhost:8000"

# Step 1: Refresh Runner to load agents from Registry
# Runner uses Registry SDK and loads agents into its internal registry
# OpenSearch powers semantic search in the Registry
response = requests.post(f"{RUNNER_URL}/agents/refresh", timeout=10)
print(f"✅ Runner loaded {response.json().get('agents_count', 0)} agents from Registry")

# Step 2: Use Runner to execute agents
# Runner automatically:
# - Searches Registry/OpenSearch for matching agents
# - Selects best agent based on skills
# - Executes agent with delegation support
# - Manages session memory

result = requests.post(
    f"{RUNNER_URL}/host/run",
    json={
        "prompt": "What agents are available?",
        "token": "my-session-123"
    },
    timeout=30
)

if result.status_code == 200:
    data = result.json()
    print(f"✅ Agent: {data['chosen_agent_id']}")
    print(f"✅ Response: {data['output']}")

# Check Runner health (shows loaded agents)
health = requests.get(f"{RUNNER_URL}/health")
print(f"✅ Runner has {health.json().get('agents_loaded', 0)} agents loaded")`}
            </CodeBlock>

            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-8">Step 4: Search Agents via Registry (OpenSearch)</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              Registry uses OpenSearch for powerful semantic search:
            </p>
            <CodeBlock id="search-agents" language="python">
{`from a2a_reg_sdk import A2ARegClient

# Registry uses OpenSearch for semantic search
client = A2ARegClient(
    registry_url="http://localhost:8000",
    api_key="dev-admin-api-key"
)

# OpenSearch semantic search finds agents by meaning, not just keywords
results = client.search_agents(
    query="customer support chatbot",
    semantic=True,  # Uses OpenSearch semantic search
    filters={"tags": ["ai", "chatbot"]},
    page=1,
    limit=10
)

print(f"Found {len(results.get('items', []))} matching agents via OpenSearch")

# Display results
for agent in results.get('items', []):
    print(f"- {agent.get('name')}: {agent.get('description', '')}")

# List all public agents (also uses OpenSearch internally)
agents = client.list_agents(page=1, limit=10, public_only=True)
print(f"\nTotal agents in Registry: {len(agents.get('items', []))}")`}
            </CodeBlock>

            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-8">Step 5: Get Agent Details</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              Get detailed information about agents from the Registry:
            </p>
            <CodeBlock id="get-agent" language="python">
{`# Get agent from Registry
agent = client.get_agent("agent-123")
print(f"Agent: {agent.name}")
print(f"Version: {agent.version}")
print(f"Description: {agent.description}")
print(f"Public: {agent.is_public}")

# Get agent card (full capabilities and skills)
agent_card = client.get_agent_card("agent-123")
print(f"Capabilities: {agent_card.capabilities}")
print(f"Skills: {len(agent_card.skills)} skills defined")
print(f"Endpoint: {agent_card.url}")

# The Runner uses this information to execute agents`}
            </CodeBlock>

            <InfoBox>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <strong>🎉 Congratulations!</strong> You've learned how to use the A2A Registry SDK to discover and explore agents. The SDK makes it much easier than using REST API calls directly!
              </p>
            </InfoBox>
          </div>
        </div>
      ),
    },
    {
      id: 'publishing-tutorial',
      title: 'Publishing Your First Agent',
      icon: Puzzle,
      content: (
        <div className="space-y-6">
          <div className="prose dark:prose-invert max-w-none">
            <p className="text-lg text-gray-700 dark:text-gray-300 mb-6">
              Learn how to publish your own AI agent to the registry so others can discover and use it!
            </p>

            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">What is an Agent Card?</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              An <strong>Agent Card</strong> is like a business card for your AI agent. It describes:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 mb-6">
              <li><strong>What the agent does</strong> (description, skills, capabilities)</li>
              <li><strong>How to talk to it</strong> (API endpoint, protocols, authentication)</li>
              <li><strong>What it needs</strong> (input formats, schemas)</li>
              <li><strong>What it provides</strong> (output formats, response schemas)</li>
            </ul>

            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-8">Step 1: Set Up Authentication</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              First, create a client with write permissions (requires CatalogManager or Administrator role):
            </p>
            <CodeBlock id="publish-setup" language="python">
{`from a2a_reg_sdk import A2ARegClient

# Initialize client with write permissions
client = A2ARegClient(
    registry_url="http://localhost:8000",
    client_id="myusername",
    client_secret="secure-password-123",
    scope="read write"  # Write permission required
)

# Authenticate
client.authenticate()
print("✅ Authenticated with write permissions")`}
            </CodeBlock>

            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-8">Step 2: Build Your Agent with SDK Builders</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              Use SDK builders to create your agent definition:
            </p>
            <CodeBlock id="publish-build-agent" language="python">
{`from a2a_reg_sdk import (
    AgentBuilder,
    AgentCapabilitiesBuilder,
    SecuritySchemeBuilder,
    AgentSkillBuilder,
    AgentInterfaceBuilder,
    AgentCardSpecBuilder
)

# Build agent capabilities
capabilities = AgentCapabilitiesBuilder().build()

# Build security scheme
security = (SecuritySchemeBuilder("apiKey")
    .location("header")
    .name("X-API-Key")
    .build())

# Build agent interface
interface = AgentInterfaceBuilder(
    "jsonrpc",
    ["text/plain"],  # Input formats
    ["text/plain"]   # Output formats
).build()

# Build agent skill
skill = (AgentSkillBuilder(
    "customer_support",
    "Customer Support",
    "Helps customers with their questions and issues",
    ["support", "customer", "help"])
    .examples([
        "What's the status of my order?",
        "I need help with a return",
        "Can you track my package?"
    ])
    .input_modes(["text/plain"])
    .output_modes(["text/plain"])
    .build())

# Build agent card
card = (AgentCardSpecBuilder(
    "Customer Support Agent",
    "AI agent for customer support inquiries",
    "https://api.mycompany.com/v1",
    "1.0.0")
    .with_provider("My Company", "https://mycompany.com")
    .with_capabilities(capabilities)
    .add_security_scheme(security)
    .add_skill(skill)
    .with_interface(interface)
    .build())

# Build the complete agent
agent = (AgentBuilder(
    "Customer Support Agent",
    "AI agent for customer support",
    "1.0.0",
    "My Company")
    .with_tags(["customer", "support", "ai"])
    .with_location("https://api.mycompany.com/v1", "api_endpoint")
    .with_capabilities(capabilities)
    .with_auth_schemes([security])
    .with_skills([skill])
    .with_agent_card(card)
    .public(True)
    .active(True)
    .build())`}
            </CodeBlock>

            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-8">Step 3: Publish Your Agent</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              Publish the agent to the registry:
            </p>
            <CodeBlock id="publish-agent" language="python">
{`# Publish the agent
published_agent = client.publish_agent(agent)

print(f"✅ Agent published successfully!")
print(f"   Agent ID: {published_agent.id}")
print(f"   Name: {published_agent.name}")
print(f"   Version: {published_agent.version}")
print(f"   Public: {published_agent.is_public}")

# Verify it was published
agent_details = client.get_agent(published_agent.id)
print(f"✅ Agent verified in registry")`}
            </CodeBlock>

            <InfoBox type="tip">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <strong>💡 Tip:</strong> The SDK builders make it easy to create complex agent definitions. They handle all the formatting and validation for you!
              </p>
            </InfoBox>

            <InfoBox type="warning">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <strong>⚠️ Important:</strong> To publish agents, your user account needs the <code>CatalogManager</code> or <code>Administrator</code> role. Regular users can only read/search agents.
              </p>
            </InfoBox>

            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-8">Understanding Agent Cards</h3>
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <p className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Minimal Agent Card Example:</p>
              <pre className="text-sm text-gray-700 dark:text-gray-300 overflow-x-auto">
{`{
  "name": "weather-agent",
  "version": "1.0.0",
  "author": "Weather Company",
  "description": "Provides weather forecasts",
  "api_base_url": "https://api.weather.com/v1",
  "capabilities": {
    "protocols": ["http"],
    "supported_formats": ["json"]
  },
  "skills": [
    {
      "name": "weather_forecast",
      "display_name": "Weather Forecast",
      "description": "Get weather forecasts for locations",
      "keywords": ["weather", "forecast", "temperature"]
    }
  ]
}`}
              </pre>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'use-cases',
      title: 'Common Use Cases & Examples',
      icon: Play,
      content: (
        <div className="space-y-6">
          <div className="prose dark:prose-invert max-w-none">
            <p className="text-lg text-gray-700 dark:text-gray-300 mb-6">
              Here are real-world examples of how the A2A Registry is used in practice.
            </p>

            <div className="space-y-8">
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">Use Case 1: Customer Service Orchestration</h3>
                <p className="text-gray-700 dark:text-gray-300 mb-4">
                  <strong>Scenario:</strong> A customer asks about their order status and package tracking.
                </p>
                
                {/* Visual Flow */}
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-900 rounded-lg p-6 mb-4 border border-blue-200 dark:border-blue-800">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <Users className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                      <span className="font-semibold text-gray-900 dark:text-white">Customer</span>
                    </div>
                    <ChevronRight className="h-5 w-5 text-gray-400" />
                    <div className="flex items-center gap-3">
                      <Search className="h-5 w-5 text-green-600 dark:text-green-400" />
                      <span className="font-semibold text-gray-900 dark:text-white">CS Agent</span>
                    </div>
                    <ChevronRight className="h-5 w-5 text-gray-400" />
                    <div className="flex items-center gap-3">
                      <Database className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                      <span className="font-semibold text-gray-900 dark:text-white">Registry</span>
                    </div>
                    <ChevronRight className="h-5 w-5 text-gray-400" />
                    <div className="flex items-center gap-3">
                      <Zap className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                      <span className="font-semibold text-gray-900 dark:text-white">UPS Agent</span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
                    Customer → CS Agent searches Registry → Finds UPS Agent → Gets tracking info → Returns to customer
                  </p>
                </div>
                <CodeBlock id="use-case-1" language="python">
{`import requests
from a2a_reg_sdk import A2ARegClient

# Configuration
REGISTRY_URL = "http://localhost:8000"
RUNNER_URL = "http://localhost:8001"
REGISTRY_API_KEY = "dev-admin-api-key"  # Or use OAuth credentials

# Step 1: Publish agents to Registry (using Registry SDK)
registry_client = A2ARegClient(
    registry_url=REGISTRY_URL,
    api_key=REGISTRY_API_KEY
)

# Publish Customer Service Agent to Registry
# (See publishing tutorial for full agent definition)
# customer_service_agent = ... (build agent with SDK)
# cs_agent_id = registry_client.publish_agent(customer_service_agent).id

# Step 2: Refresh Runner to load agents from Registry
# The Runner automatically loads agents from Registry using OpenSearch
refresh_response = requests.post(f"{RUNNER_URL}/agents/refresh", timeout=10)
print(f"Runner loaded {refresh_response.json().get('agents_count', 0)} agents")

# Step 3: Use Runner to execute agent with automatic delegation
# The Runner uses OpenSearch for semantic agent discovery and handles delegation
customer_query = "Where is my package? Tracking: 1Z999AA10123456784"

response = requests.post(
    f"{RUNNER_URL}/host/run",
    json={
        "prompt": customer_query,
        "token": "customer-session-123",
        "force_agent_id": "customer-service-agent-id"  # Optional: force specific agent
    },
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Agent: {result['chosen_agent_id']}")
    print(f"✅ Response: {result['output']}")
    
    # The Runner automatically:
    # 1. Searches Registry/OpenSearch for best agent
    # 2. Executes the agent
    # 3. Handles delegation if agent returns delegate field
    # 4. Combines responses from multiple agents
    # 5. Manages session memory across agents
else:
    print(f"❌ Error: {response.status_code} - {response.text}")

# The Runner framework handles:
# - OpenSearch semantic search for agent discovery
# - Automatic agent routing based on skills
# - Delegation flow between agents
# - Session memory management
# - Error handling and retries`}
                </CodeBlock>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">Use Case 2: Multi-Agent Workflow</h3>
                <p className="text-gray-700 dark:text-gray-300 mb-4">
                  <strong>Scenario:</strong> Process a customer order that requires multiple steps.
                </p>
                
                {/* Visual Workflow Diagram */}
                <div className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-gray-800 dark:to-gray-900 rounded-lg p-6 mb-4 border border-green-200 dark:border-green-800">
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 text-center border-2 border-primary-300 dark:border-primary-700">
                      <Rocket className="h-8 w-8 text-primary-600 dark:text-primary-400 mx-auto mb-2" />
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">Order Agent</p>
                    </div>
                    <div className="flex items-center justify-center">
                      <ChevronRight className="h-6 w-6 text-gray-400" />
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 text-center border-2 border-blue-300 dark:border-blue-700">
                      <Key className="h-8 w-8 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">Payment</p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 text-center border-2 border-green-300 dark:border-green-700">
                      <Database className="h-8 w-8 text-green-600 dark:text-green-400 mx-auto mb-2" />
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">Inventory</p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 text-center border-2 border-purple-300 dark:border-purple-700">
                      <Zap className="h-8 w-8 text-purple-600 dark:text-purple-400 mx-auto mb-2" />
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">Shipping</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 text-center mt-4">
                    All agents work in parallel, coordinated by Order Agent
                  </p>
                </div>
                
                <CodeBlock id="use-case-2" language="python">
{`import requests
import asyncio
from a2a_reg_sdk import A2ARegClient

REGISTRY_URL = "http://localhost:8000"
RUNNER_URL = "http://localhost:8001"
REGISTRY_API_KEY = "dev-admin-api-key"

# Step 1: Ensure all agents are published to Registry
registry_client = A2ARegClient(
    registry_url=REGISTRY_URL,
    api_key=REGISTRY_API_KEY
)

# Refresh Runner to load all agents from Registry
requests.post(f"{RUNNER_URL}/agents/refresh")

# Step 2: Use Runner framework for multi-agent orchestration
# The Runner handles delegation, OpenSearch discovery, and parallel execution

async def process_order_with_runner(order_data):
    """Process order using Runner framework with automatic agent discovery."""
    
    # The Runner uses OpenSearch to find the best agents for each task
    # Each agent can delegate to other agents, creating a workflow
    
    # Start with Order Processing Agent
    # It will automatically delegate to Payment, Inventory, and Shipping agents
    response = requests.post(
        f"{RUNNER_URL}/host/run",
        json={
            "prompt": f"Process order: {order_data}",
            "token": "order-session-456",
            "context_overrides": {
                "order_id": order_data.get("order_id"),
                "customer_id": order_data.get("customer_id")
            }
        },
        timeout=60  # Allow time for multi-agent delegation
    )
    
    if response.status_code == 200:
        result = response.json()
        
        # Runner returns:
        # - chosen_agent_id: The agent that started the workflow
        # - output: Combined response from all agents
        # - global_session: Shared state across all agents
        # - routing_scores: How agents were selected
        
        print(f"✅ Workflow Agent: {result['chosen_agent_id']}")
        print(f"✅ Combined Response: {result['output']}")
        print(f"✅ Agents Used: {result.get('global_session', {}).get('shared_state', {})}")
        
        return {
            "status": "success",
            "output": result['output'],
            "agents_used": result.get('routing_scores', {})
        }
    else:
        return {"status": "error", "message": response.text}

# Run the workflow
order = {
    "order_id": "12345",
    "customer_id": "user123",
    "items": ["product1", "product2"],
    "total": 99.99
}

result = asyncio.run(process_order_with_runner(order))

# The Runner framework automatically:
# 1. Uses OpenSearch to find agents matching the query
# 2. Routes to Order Processing Agent
# 3. Agent delegates to Payment, Inventory, Shipping agents
# 4. Runner orchestrates all calls
# 5. Combines responses into final result
# 6. Manages session state across all agents`}
                </CodeBlock>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">Use Case 3: Dynamic Agent Discovery</h3>
                <p className="text-gray-700 dark:text-gray-300 mb-4">
                  <strong>Scenario:</strong> Your application needs to find the best agent for a task at runtime.
                </p>
                
                {/* Visual Discovery Flow */}
                <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-gray-800 dark:to-gray-900 rounded-lg p-6 mb-4 border border-purple-200 dark:border-purple-800">
                  <div className="flex items-center justify-center gap-4 mb-4">
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-3 border-2 border-purple-300 dark:border-purple-700">
                      <Search className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                    </div>
                    <ChevronRight className="h-6 w-6 text-gray-400" />
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-3 border-2 border-blue-300 dark:border-blue-700">
                      <Database className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <ChevronRight className="h-6 w-6 text-gray-400" />
                    <div className="grid grid-cols-3 gap-2">
                      <div className="bg-white dark:bg-gray-800 rounded-lg p-2 border border-green-300 dark:border-green-700 text-center">
                        <p className="text-xs font-semibold text-gray-900 dark:text-white">Payment</p>
                      </div>
                      <div className="bg-white dark:bg-gray-800 rounded-lg p-2 border border-orange-300 dark:border-orange-700 text-center">
                        <p className="text-xs font-semibold text-gray-900 dark:text-white">Billing</p>
                      </div>
                      <div className="bg-white dark:bg-gray-800 rounded-lg p-2 border border-purple-300 dark:border-purple-700 text-center">
                        <p className="text-xs font-semibold text-gray-900 dark:text-white">Invoice</p>
                      </div>
                    </div>
                    <ChevronRight className="h-6 w-6 text-gray-400" />
                    <div className="bg-green-100 dark:bg-green-900/30 rounded-lg p-3 border-2 border-green-400 dark:border-green-600">
                      <Check className="h-6 w-6 text-green-600 dark:text-green-400" />
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
                    User query → Registry search → Multiple agents found → Best match selected
                  </p>
                </div>
                
                <CodeBlock id="use-case-3" language="python">
{`import requests
from a2a_reg_sdk import A2ARegClient

REGISTRY_URL = "http://localhost:8000"
RUNNER_URL = "http://localhost:8001"

# Step 1: Use Registry SDK to search agents
# Registry uses OpenSearch for semantic search
registry_client = A2ARegClient(
    registry_url=REGISTRY_URL,
    api_key="dev-admin-api-key"
)

# OpenSearch provides semantic search - finds agents by meaning, not just keywords
user_query = "I need to process a payment"

# Registry SDK search uses OpenSearch backend for semantic matching
results = registry_client.search_agents(
    query=user_query,
    semantic=True,  # Enable semantic search via OpenSearch
    page=1,
    limit=10
)

print(f"Found {len(results.get('items', []))} matching agents via OpenSearch")

# Step 2: Use Runner to automatically find and execute the best agent
# Runner uses its own skill selector with OpenSearch results
response = requests.post(
    f"{RUNNER_URL}/host/run",
    json={
        "prompt": user_query,
        "token": "user-session-789"
    },
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    
    # Runner automatically:
    # 1. Searches Registry/OpenSearch for matching agents
    # 2. Uses SkillSelector to score agents by relevance
    # 3. Picks the best agent based on skills and query
    # 4. Executes the agent
    # 5. Returns routing scores showing why agent was chosen
    
    print(f"✅ Selected Agent: {result['chosen_agent_id']}")
    print(f"✅ Response: {result['output']}")
    print(f"✅ Routing Scores: {result.get('routing_scores', {})}")
else:
    print(f"❌ Error: {response.status_code}")

# The framework handles:
# - OpenSearch semantic search (Registry)
# - Skill-based agent selection (Runner)
# - Automatic routing based on agent capabilities
# - No manual agent selection needed - it's automatic!`}
                </CodeBlock>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'api-reference',
      title: 'API Reference',
      icon: Code,
      content: (
        <div className="space-y-6">
          <div className="prose dark:prose-invert max-w-none">
            <p className="text-gray-700 dark:text-gray-300 mb-6">
              Complete API reference for all available endpoints. For interactive documentation, visit{' '}
              <Link href="http://localhost:8000/docs" target="_blank" className="text-primary-600 dark:text-primary-400 hover:underline">
                Swagger UI
              </Link>
              .
            </p>
            {/* Include condensed API reference here */}
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                For detailed API documentation with examples, visit the{' '}
                <Link href="http://localhost:8000/docs" target="_blank" className="text-primary-600 dark:text-primary-400 hover:underline font-semibold">
                  interactive Swagger UI
                </Link>
                . It provides live testing of all endpoints with up-to-date schemas.
              </p>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'authentication',
      title: 'Authentication Guide',
      icon: Shield,
      content: (
        <div className="space-y-6">
          <div className="prose dark:prose-invert max-w-none">
            <p className="text-gray-700 dark:text-gray-300 mb-6">
              Learn about the different authentication methods available in the A2A Registry.
            </p>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Why Authentication?</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              The registry supports both <strong>public</strong> and <strong>private</strong> agents. Public agents can be accessed by anyone, but private agents require authentication. Authentication also allows you to:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 mb-6">
              <li>Access your entitled (private) agents</li>
              <li>Publish new agents to the registry</li>
              <li>Search with advanced features</li>
              <li>Manage your published agents</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 mt-8">OAuth 2.0 Authentication with SDK</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              The SDK handles OAuth authentication automatically. Just provide your credentials when initializing the client:
            </p>
            <CodeBlock id="oauth-example" language="python">
{`from a2a_reg_sdk import A2ARegClient

# Initialize client with OAuth credentials
client = A2ARegClient(
    registry_url="http://localhost:8000",
    client_id="myusername",      # Your username
    client_secret="mypassword",    # Your password
    scope="read write"             # Required permissions
)

# Authenticate (SDK handles token management)
client.authenticate()
print("✅ Authenticated successfully!")

# Now you can use the client for API calls
# Token refresh happens automatically`}
            </CodeBlock>
            <InfoBox type="tip">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <strong>💡 Tip:</strong> The SDK automatically handles token authentication, refresh, and management. You don't need to manually handle tokens!
              </p>
            </InfoBox>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 mt-8">API Key Authentication</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              For programmatic access, you can use API keys instead of OAuth:
            </p>
            <CodeBlock id="api-key-example" language="python">
{`from a2a_reg_sdk import A2ARegClient

# Initialize client with API key
client = A2ARegClient(
    registry_url="http://localhost:8000",
    api_key="your-api-key"  # API key for authentication
)

# No need to authenticate - API key is used directly
agents = client.list_agents()
print(f"Found {len(agents.get('items', []))} agents")`}
            </CodeBlock>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 mt-8">Generating API Keys</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              Generate API keys programmatically with the SDK:
            </p>
            <CodeBlock id="generate-key" language="python">
{`from a2a_reg_sdk import A2ARegClient

# First, authenticate with OAuth (admin credentials required)
admin_client = A2ARegClient(
    registry_url="http://localhost:8000",
    client_id="admin-username",
    client_secret="admin-password",
    scope="admin"
)
admin_client.authenticate()

# Generate a new API key
api_key, key_info = admin_client.generate_api_key(
    scopes=["read", "write"],
    expires_days=30  # Optional: key expiration
)

print(f"API Key: {api_key}")
print(f"Key ID: {key_info.get('key_id')}")
print(f"Scopes: {key_info.get('scopes')}")

# Use the API key for future requests
client = A2ARegClient(
    registry_url="http://localhost:8000",
    api_key=api_key
)`}
            </CodeBlock>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 mt-8">Roles and Permissions</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              Different roles have different permissions:
            </p>
            <div className="grid md:grid-cols-2 gap-4 mb-6">
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">User Role</h4>
                <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                  <li>✓ Read public agents</li>
                  <li>✓ Search agents</li>
                  <li>✓ Access entitled agents</li>
                  <li>✗ Publish agents</li>
                </ul>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">CatalogManager / Administrator</h4>
                <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                  <li>✓ All User permissions</li>
                  <li>✓ Publish agents</li>
                  <li>✓ Delete agents</li>
                  <li>✓ Generate API tokens</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'sdks',
      title: 'SDKs & Libraries',
      icon: Code,
      content: (
        <div className="space-y-6">
          <div className="prose dark:prose-invert max-w-none">
            <p className="text-gray-700 dark:text-gray-300 mb-6">
              Official SDKs make it easy to integrate the A2A Registry into your applications. Choose the language that matches your stack!
            </p>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Python SDK</h3>
                <CodeBlock id="python-install" language="bash">
{`pip install a2a-reg-sdk`}
                </CodeBlock>
                <CodeBlock id="python-usage" language="python">
{`from a2a_reg_sdk import A2ARegClient

# Initialize client
client = A2ARegClient(
    registry_url="http://localhost:8000",
    api_key="your-api-key"
)

# Discover agents
agents = client.list_agents()

# Search for specific agents
results = client.search_agents({
    "q": "customer support",
    "top": 10
})

# Get agent details
agent = client.get_agent("agent-id-123")`}
                </CodeBlock>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">TypeScript/JavaScript SDK</h3>
                <CodeBlock id="ts-install" language="bash">
{`npm install @a2areg/sdk`}
                </CodeBlock>
                <CodeBlock id="ts-usage" language="typescript">
{`import { A2ARegClient } from '@a2areg/sdk';

// Initialize client
const client = new A2ARegClient({
  registryUrl: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

// Discover agents
const agents = await client.listAgents();

// Search for specific agents
const results = await client.searchAgents({
  q: 'customer support',
  top: 10
});

// Get agent details
const agent = await client.getAgent('agent-id-123');`}
                </CodeBlock>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Go SDK</h3>
                <CodeBlock id="go-install" language="bash">
{`go get github.com/A2AReg/a2a-registry/sdk/go/pkg/a2areg`}
                </CodeBlock>
                <CodeBlock id="go-usage" language="go">
{`import "github.com/A2AReg/a2a-registry/sdk/go/pkg/a2areg"

// Initialize client
client := a2areg.NewClient(
    "http://localhost:8000",
    "your-api-key",
)

// Discover agents
agents, err := client.ListAgents()

// Search for specific agents
results, err := client.SearchAgents(map[string]interface{}{
    "q": "customer support",
    "top": 10,
})`}
                </CodeBlock>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Java SDK</h3>
                <CodeBlock id="java-install" language="xml">
{`<dependency>
  <groupId>com.a2areg</groupId>
  <artifactId>a2a-reg-sdk</artifactId>
  <version>1.0.0</version>
</dependency>`}
                </CodeBlock>
                <CodeBlock id="java-usage" language="java">
{`import com.a2areg.sdk.A2ARegClient;

// Initialize client
A2ARegClient client = new A2ARegClient(
    "http://localhost:8000",
    "your-api-key"
);

// Discover agents
List<Agent> agents = client.listAgents();

// Search for specific agents
SearchResults results = client.searchAgents(
    Map.of("q", "customer support", "top", 10)
);`}
                </CodeBlock>
              </div>
            </div>

            <InfoBox>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <strong>📦 SDK Documentation:</strong> Each SDK has detailed README files in the <code>sdk/</code> directory with more examples and API reference. Check out the specific SDK folder for your language!
              </p>
            </InfoBox>
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="container mx-auto px-4 py-12 max-w-7xl">
      {/* Header */}
      <div className="mb-12 text-center">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Book className="h-12 w-12 text-primary-600 dark:text-primary-400" />
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white">
            A2A Registry Documentation
          </h1>
        </div>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
          Learn about the Agent-to-Agent ecosystem and how to use the A2A Registry to discover, publish, and orchestrate AI agents.
        </p>
      </div>

      {/* Quick Links */}
      <div className="grid md:grid-cols-4 gap-4 mb-12">
        <Link
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-3 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 transition-colors"
        >
          <Zap className="h-6 w-6 text-primary-600 dark:text-primary-400" />
          <div>
            <div className="font-semibold text-gray-900 dark:text-white">Swagger UI</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Interactive docs</div>
          </div>
          <ExternalLink className="h-4 w-4 text-gray-400 ml-auto" />
        </Link>
        <Link
          href="http://localhost:8000/openapi.json"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-3 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 transition-colors"
        >
          <Code className="h-6 w-6 text-primary-600 dark:text-primary-400" />
          <div>
            <div className="font-semibold text-gray-900 dark:text-white">OpenAPI Spec</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">JSON schema</div>
          </div>
          <ExternalLink className="h-4 w-4 text-gray-400 ml-auto" />
        </Link>
        <Link
          href="https://github.com/A2AReg/a2a-registry"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-3 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 transition-colors"
        >
          <Server className="h-6 w-6 text-primary-600 dark:text-primary-400" />
          <div>
            <div className="font-semibold text-gray-900 dark:text-white">GitHub</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Source code</div>
          </div>
          <ExternalLink className="h-4 w-4 text-gray-400 ml-auto" />
        </Link>
        <div className="flex items-center gap-3 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <Heart className="h-6 w-6 text-green-600 dark:text-green-400" />
          <div>
            <div className="font-semibold text-gray-900 dark:text-white">Status</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">All systems operational</div>
          </div>
        </div>
      </div>

      {/* Documentation Sections */}
      <div className="space-y-6">
        {sections.map((section) => {
          const IconComponent = section.icon;
          const isExpanded = expandedSections.has(section.id);
          return (
            <div
              key={section.id}
              className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-md transition-shadow"
            >
              <button
                onClick={() => toggleSection(section.id)}
                className="w-full flex items-center justify-between p-6 hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
                    <IconComponent className="h-6 w-6 text-primary-600 dark:text-primary-400" />
                  </div>
                  <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">{section.title}</h2>
                </div>
                {isExpanded ? (
                  <ChevronUp className="h-5 w-5 text-gray-400" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-400" />
                )}
              </button>
              {isExpanded && (
                <div className="px-6 pb-6 border-t border-gray-200 dark:border-gray-700 pt-6">
                  {section.content}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="mt-12 p-6 bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Need Help?
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Can't find what you're looking for? Check out the interactive Swagger documentation, explore examples in the repository, or visit our GitHub.
        </p>
        <div className="flex gap-4">
          <Link
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
          >
            Open Swagger UI <ExternalLink className="h-4 w-4" />
          </Link>
          <Link
            href="https://github.com/A2AReg/a2a-registry"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
          >
            Visit GitHub <ExternalLink className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}

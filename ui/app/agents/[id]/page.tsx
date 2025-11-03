'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { agentApi, AgentCard as AgentCardType } from '@/lib/api';
import { formatErrorMessage } from '@/lib/error-handler';
import { Loader2, ExternalLink, Package, Code, User, Tag, MessageSquare, Send } from 'lucide-react';
import Link from 'next/link';

export default function AgentDetailPage() {
  const params = useParams();
  const agentId = params?.id as string;
  
  const [agent, setAgent] = useState<AgentCardType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'details' | 'card' | 'test'>('details');
  const [testMessage, setTestMessage] = useState<string>('');
  const [testResponse, setTestResponse] = useState<string | null>(null);
  const [testLoading, setTestLoading] = useState<boolean>(false);
  const [testError, setTestError] = useState<string | null>(null);

  useEffect(() => {
    if (agentId) {
      loadAgent();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agentId]);

  const loadAgent = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to get agent card (requires auth)
      const card = await agentApi.getAgentCard(agentId);
      setAgent(card);
    } catch (err: any) {
      const status = err.response?.status;
      const errorDetail = err.response?.data?.detail;
      
      // Handle specific error cases
      if (status === 404) {
        setError(`Agent "${agentId}" was not found in the registry. The agent may not exist or may have been removed.`);
      } else if (status === 401) {
        setError(`Authentication required. Please login to view this agent.`);
      } else if (status === 403) {
        setError(`Access denied. This agent is private and you don't have permission to view it. If you believe you should have access, please contact the administrator.`);
      } else {
        // Use formatted error message or fallback
        const errorMsg = formatErrorMessage(err);
        setError(errorMsg || `Failed to load agent "${agentId}". ${errorDetail || 'Please check the agent ID and try again.'}`);
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
          <span className="ml-2 text-gray-600 dark:text-gray-400">Loading agent...</span>
        </div>
      </div>
    );
  }

  if (error || !agent) {
    const isNotFound = error?.toLowerCase().includes('not found') || error?.toLowerCase().includes('404');
    const isAuthError = error?.toLowerCase().includes('authentication') || error?.toLowerCase().includes('login');
    const isAccessDenied = error?.toLowerCase().includes('access denied') || error?.toLowerCase().includes('permission');

    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className={`rounded-lg p-6 ${
            isAuthError || isAccessDenied
              ? 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800'
              : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
          }`}>
            <h2 className={`text-xl font-semibold mb-2 ${
              isAuthError || isAccessDenied
                ? 'text-yellow-800 dark:text-yellow-200'
                : 'text-red-800 dark:text-red-200'
            }`}>
              {isNotFound ? 'Agent Not Found' : isAuthError ? 'Authentication Required' : isAccessDenied ? 'Access Denied' : 'Error Loading Agent'}
            </h2>
            <p className={`mb-4 ${
              isAuthError || isAccessDenied
                ? 'text-yellow-700 dark:text-yellow-300'
                : 'text-red-700 dark:text-red-300'
            }`}>
              {error || 'Agent not found'}
            </p>
            
            <div className="flex flex-wrap gap-3 mt-6">
              <Link 
                href="/" 
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors inline-block"
              >
                ← Browse Agents
              </Link>
              {isAuthError && (
                <Link 
                  href="/login" 
                  className="px-4 py-2 border border-primary-600 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors inline-block"
                >
                  Login
                </Link>
              )}
              {isNotFound && (
                <Link 
                  href="/search" 
                  className="px-4 py-2 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors inline-block"
                >
                  Search Agents
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Link href="/" className="text-primary-600 dark:text-primary-400 hover:underline mb-6 inline-block">
        ← Back to agents
      </Link>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {agent.name || agentId}
          </h1>
          {agent.description && (
            <p className="text-gray-600 dark:text-gray-400 text-lg">{agent.description}</p>
          )}
        </div>

        <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
          <div className="flex space-x-4">
            <button
              onClick={() => setActiveTab('details')}
              className={`pb-3 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'details'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              Details
            </button>
            <button
              onClick={() => setActiveTab('card')}
              className={`pb-3 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'card'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              Full Card
            </button>
            <button
              onClick={() => setActiveTab('test')}
              className={`pb-3 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'test'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              Test
            </button>
          </div>
        </div>

        {activeTab === 'details' ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-start space-x-3">
                <User className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Provider</p>
                  <p className="text-gray-900 dark:text-white">
                    {typeof agent.provider === 'string' 
                      ? agent.provider 
                      : agent.provider?.organization || 'Unknown'}
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <Package className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Version</p>
                  <p className="text-gray-900 dark:text-white">{agent.version}</p>
                </div>
              </div>
              {agent.url && (
                <div className="flex items-start space-x-3">
                  <ExternalLink className="h-5 w-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">URL</p>
                    <a
                      href={agent.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary-600 dark:text-primary-400 hover:underline"
                    >
                      {agent.url}
                    </a>
                  </div>
                </div>
              )}
            </div>

            {agent.capabilities && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Capabilities</h3>
                <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                  <pre className="text-sm text-gray-700 dark:text-gray-300 overflow-x-auto">
                    {JSON.stringify(agent.capabilities, null, 2)}
                  </pre>
                </div>
              </div>
            )}

            {agent.skills && agent.skills.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                  <Tag className="h-5 w-5 mr-2" />
                  Skills
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {agent.skills.map((skill: any, index: number) => (
                    <div
                      key={index}
                      className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700"
                    >
                      <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                        {skill.name || skill.id || `Skill ${index + 1}`}
                      </h4>
                      {skill.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{skill.description}</p>
                      )}
                      {skill.tags && skill.tags.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-2">
                          {skill.tags.map((tag: string, tagIndex: number) => (
                            <span
                              key={tagIndex}
                              className="px-2 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-xs rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : activeTab === 'test' ? (
          <TestAgentTab
            agent={agent}
            agentId={agentId}
            testMessage={testMessage}
            setTestMessage={setTestMessage}
            testResponse={testResponse}
            setTestResponse={setTestResponse}
            testLoading={testLoading}
            setTestLoading={setTestLoading}
            testError={testError}
            setTestError={setTestError}
          />
        ) : (
          <div>
            <pre className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 overflow-x-auto text-sm">
              {JSON.stringify(agent, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

// Test Agent Tab Component
interface TestAgentTabProps {
  agent: AgentCardType;
  agentId: string;
  testMessage: string;
  setTestMessage: (msg: string) => void;
  testResponse: string | null;
  setTestResponse: (resp: string | null) => void;
  testLoading: boolean;
  setTestLoading: (loading: boolean) => void;
  testError: string | null;
  setTestError: (error: string | null) => void;
}

function TestAgentTab({
  agent,
  agentId,
  testMessage,
  setTestMessage,
  testResponse,
  setTestResponse,
  testLoading,
  setTestLoading,
  testError,
  setTestError,
}: TestAgentTabProps) {
  const sendTestMessage = async (message: string = 'hello what you do?') => {
    if (!agent) return;

    setTestLoading(true);
    setTestError(null);
    setTestResponse(null);

    try {
      // Get agent URL from card - use url field from AgentCardSpec
      const agentUrl = (agent as any).url;
      if (!agentUrl) {
        throw new Error('Agent URL not found in card. Cannot test agent without an endpoint.');
      }

      // Determine endpoint from card interface
      const baseUrl = typeof agentUrl === 'string' ? agentUrl : '';
      // Use interface information if available
      const interface_ = (agent as any).interface;
      let endpoint = '/chat'; // Default endpoint
      
      // Check if there are additional interfaces defined
      if (interface_?.additionalInterfaces && interface_.additionalInterfaces.length > 0) {
        const httpInterface = interface_.additionalInterfaces.find((i: any) => i.transport === 'http');
        if (httpInterface?.url) {
          endpoint = httpInterface.url;
        }
      }
      
      const fullUrl = endpoint.startsWith('http') ? endpoint : `${baseUrl.replace(/\/$/, '')}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

      // Prepare request based on card skills schema
      const skills = agent.skills || [];
      let requestBody: any = { message };

      // Handle authentication if needed
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // Check for auth schemes in card
      const authSchemes = (agent as any).authSchemes || (agent as any).auth_schemes || [];
      // Note: In production, you'd handle actual auth tokens here

      // Send request to agent
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Agent responded with ${response.status}: ${errorText || response.statusText}`);
      }

      let responseData: any;
      const contentType = response.headers.get('content-type');
      
      // Handle different response types
      if (contentType?.includes('application/json')) {
        try {
          responseData = await response.json();
        } catch (e) {
          responseData = await response.text();
        }
      } else {
        responseData = await response.text();
      }

      // Extract response based on output schema - always convert to string for display
      // Handle the case where response might be an object with {status, message, response}
      let responseText = '';
      
      if (typeof responseData === 'string') {
        responseText = responseData;
      } else if (typeof responseData === 'object' && responseData !== null) {
        // First, try to extract a text message from common fields
        let messageToShow: any = null;
        
        if (responseData.response !== undefined) {
          messageToShow = responseData.response;
        } else if (responseData.message !== undefined) {
          messageToShow = responseData.message;
        } else if (responseData.text !== undefined) {
          messageToShow = responseData.text;
        } else if (responseData.content !== undefined) {
          messageToShow = responseData.content;
        } else if (responseData.output !== undefined) {
          messageToShow = responseData.output;
        }
        
        // If we found a message field, check if it's a string or object
        if (messageToShow !== null) {
          if (typeof messageToShow === 'string') {
            responseText = messageToShow;
          } else if (typeof messageToShow === 'object') {
            // If message itself is an object, stringify it nicely
            responseText = JSON.stringify(messageToShow, null, 2);
          } else {
            // Fallback: convert to string
            responseText = String(messageToShow);
          }
        } else {
          // No message field found, stringify the entire response
          responseText = JSON.stringify(responseData, null, 2);
        }
      } else {
        // Fallback for other types (number, boolean, etc.)
        responseText = String(responseData);
      }

      // Ensure we always have a string (never an object)
      if (typeof responseText !== 'string') {
        responseText = JSON.stringify(responseText, null, 2);
      }

      setTestResponse(responseText);
    } catch (err: any) {
      setTestError(err.message || 'Failed to test agent. Make sure the agent endpoint is accessible.');
      console.error('Test error:', err);
    } finally {
      setTestLoading(false);
    }
  };

  const handleSendTest = () => {
    const messageToSend = testMessage.trim() || 'hello what you do?';
    sendTestMessage(messageToSend);
  };

  const handleQuickTest = () => {
    setTestMessage('hello what you do?');
    sendTestMessage('hello what you do?');
  };

  return (
    <div className="space-y-6">
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-200 mb-2">
          Testing Agent with A2A Card
        </h3>
        <p className="text-sm text-blue-800 dark:text-blue-300">
          This test uses the agent card definition to call the agent&apos;s endpoint. 
          The card provides the URL, endpoints, and schema information needed to interact with the agent.
        </p>
      </div>

      {/* Agent Card Info */}
      <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
        <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Agent Endpoint</h4>
        <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
          <p>
            <span className="font-medium">URL:</span>{' '}
            <span className="font-mono text-xs">
              {(agent as any).url || (agent as any).location?.url || 'Not specified'}
            </span>
          </p>
          {(agent as any).endpoints && (
            <p>
              <span className="font-medium">Endpoints:</span>{' '}
              <span className="font-mono text-xs">{JSON.stringify((agent as any).endpoints)}</span>
            </p>
          )}
        </div>
      </div>

      {/* Test Interface */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
            <MessageSquare className="h-5 w-5 mr-2" />
            Test Agent
          </h3>
          <button
            onClick={handleQuickTest}
            disabled={testLoading}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white rounded-lg transition-colors text-sm"
          >
            Quick Test: &quot;hello what you do?&quot;
          </button>
        </div>

        {/* Message Input */}
        <div className="space-y-2">
          <label htmlFor="test-message" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Test Message
          </label>
          <div className="flex space-x-2">
            <input
              id="test-message"
              type="text"
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              placeholder="hello what you do?"
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !testLoading) {
                  handleSendTest();
                }
              }}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <button
              onClick={handleSendTest}
              disabled={testLoading}
              className="px-6 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white rounded-lg transition-colors flex items-center space-x-2"
            >
              {testLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Sending...</span>
                </>
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  <span>Send</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Response */}
        {testResponse && (
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-green-900 dark:text-green-200 mb-2">
              Agent Response
            </h4>
            <pre className="text-sm text-green-800 dark:text-green-300 whitespace-pre-wrap">
              {testResponse}
            </pre>
          </div>
        )}

        {/* Error */}
        {testError && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-red-900 dark:text-red-200 mb-2">
              Error
            </h4>
            <p className="text-sm text-red-800 dark:text-red-300">{testError}</p>
          </div>
        )}

        {/* Loading */}
        {testLoading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
            <span className="ml-2 text-gray-600 dark:text-gray-400">Sending message to agent...</span>
          </div>
        )}
      </div>
    </div>
  );
}


import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  CpuChipIcon, 
  TagIcon, 
  GlobeAltIcon, 
  ShieldCheckIcon,
  CodeBracketIcon,
  DocumentTextIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';
import api from '../services/api';
import { Agent } from '../types';

const AgentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  
  const { data: agent, isLoading, error } = useQuery({
    queryKey: ['agent', id],
    queryFn: () => api.getAgent(id!),
    enabled: !!id,
  });

  const { data: agentCard } = useQuery({
    queryKey: ['agent-card', id],
    queryFn: () => api.getAgentCard(id!),
    enabled: !!id,
  });

  if (isLoading) {
    return <LoadingSpinner text="Loading agent details..." />;
  }

  if (error || !agent) {
    return (
      <div className="card">
        <div className="card-body text-center py-12">
          <CpuChipIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Agent not found</h3>
          <p className="text-gray-600 mb-4">The requested agent could not be found.</p>
          <a href="/agents" className="btn btn-primary">
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Agents
          </a>
        </div>
      </div>
    );
  }

  const getAuthTypeColor = (type: string) => {
    switch (type) {
      case 'oauth2':
        return 'bg-blue-100 text-blue-800';
      case 'jwt':
        return 'bg-green-100 text-green-800';
      case 'api_key':
        return 'bg-yellow-100 text-yellow-800';
      case 'mtls':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <a href="/agents" className="mr-4 text-gray-400 hover:text-gray-600">
            <ArrowLeftIcon className="h-5 w-5" />
          </a>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{agent.name}</h1>
            <p className="text-gray-600">Agent Details</p>
          </div>
        </div>
        <div className="flex space-x-3">
          <button className="btn btn-secondary">
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            View Agent Card
          </button>
          <button className="btn btn-primary">
            Connect to Agent
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Basic Information</h3>
            </div>
            <div className="card-body space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <p className="text-gray-900">{agent.description}</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Version</label>
                  <p className="text-gray-900">{agent.version}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Provider</label>
                  <p className="text-gray-900">{agent.provider}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Location Type</label>
                  <div className="flex items-center">
                    <GlobeAltIcon className="h-4 w-4 text-gray-400 mr-1" />
                    <span className="text-gray-900">{agent.location_type}</span>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Location URL</label>
                  <a 
                    href={agent.location_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700 break-all"
                  >
                    {agent.location_url}
                  </a>
                </div>
              </div>

              {agent.tags && agent.tags.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>
                  <div className="flex flex-wrap gap-2">
                    {Array.isArray(agent.tags) && agent.tags.map((tag) => (
                      <span key={tag} className="badge badge-secondary">
                        <TagIcon className="h-3 w-3 mr-1" />
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Capabilities */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Capabilities</h3>
            </div>
            <div className="card-body space-y-4">
              {agent.capabilities && (Object.keys(agent.capabilities).length > 0) ? (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {agent.capabilities.a2a_version && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">A2A Version</label>
                        <p className="text-gray-900">{agent.capabilities.a2a_version}</p>
                      </div>
                    )}
                    {agent.capabilities.max_concurrent_requests && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Max Concurrent Requests</label>
                        <p className="text-gray-900">{agent.capabilities.max_concurrent_requests}</p>
                      </div>
                    )}
                  </div>
                  
                  {agent.capabilities.protocols && Array.isArray(agent.capabilities.protocols) && agent.capabilities.protocols.length > 0 && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Supported Protocols</label>
                      <div className="flex flex-wrap gap-2">
                        {agent.capabilities.protocols.map((protocol) => (
                          <span key={protocol} className="badge badge-primary">
                            {protocol}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {agent.capabilities.supported_formats && Array.isArray(agent.capabilities.supported_formats) && agent.capabilities.supported_formats.length > 0 && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Supported Formats</label>
                      <div className="flex flex-wrap gap-2">
                        {agent.capabilities.supported_formats.map((format) => (
                          <span key={format} className="badge badge-secondary">
                            {format}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center py-8">
                  <CpuChipIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 mb-2">No Capabilities Information</h4>
                  <p className="text-gray-600">This agent doesn't have detailed capabilities information available.</p>
                </div>
              )}
            </div>
          </div>

          {/* Skills */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Skills</h3>
            </div>
            <div className="card-body space-y-4">
              {agent.skills?.input_schema && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Input Schema</label>
                  <div className="bg-gray-50 rounded-md p-4">
                    <pre className="text-sm text-gray-800 overflow-x-auto">
                      <code>{JSON.stringify(agent.skills.input_schema, null, 2)}</code>
                    </pre>
                  </div>
                </div>
              )}
              
              {agent.skills?.output_schema && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Output Schema</label>
                  <div className="bg-gray-50 rounded-md p-4">
                    <pre className="text-sm text-gray-800 overflow-x-auto">
                      <code>{JSON.stringify(agent.skills.output_schema, null, 2)}</code>
                    </pre>
                  </div>
                </div>
              )}

              {agent.skills?.examples && agent.skills.examples.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Examples</label>
                  <div className="space-y-2">
                    {Array.isArray(agent.skills.examples) && agent.skills.examples.map((example, index) => (
                      <div key={index} className="bg-gray-50 rounded-md p-3">
                        <pre className="text-sm text-gray-800">{example}</pre>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {!agent.skills && (
                <div className="text-center py-8">
                  <CodeBracketIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 mb-2">No Skills Information</h4>
                  <p className="text-gray-600">This agent doesn't have detailed skills information available.</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Authentication */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Authentication</h3>
            </div>
            <div className="card-body space-y-3">
              {Array.isArray(agent.auth_schemes) && agent.auth_schemes.map((scheme, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                  <div className="flex items-center">
                    <ShieldCheckIcon className="h-5 w-5 text-gray-400 mr-2" />
                    <div>
                      <p className="font-medium text-gray-900">{scheme.type.toUpperCase()}</p>
                      <p className="text-sm text-gray-600">{scheme.description}</p>
                    </div>
                  </div>
                  <span className={`badge ${getAuthTypeColor(scheme.type)}`}>
                    {scheme.required ? 'Required' : 'Optional'}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* TEE Details */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Trusted Execution Environment</h3>
            </div>
            <div className="card-body">
              <div className="flex items-center justify-between mb-3">
                <span className="font-medium text-gray-900">TEE Enabled</span>
                <span className={`badge ${agent.tee_details?.enabled ? 'badge-success' : 'badge-secondary'}`}>
                  {agent.tee_details?.enabled ? 'Yes' : 'No'}
                </span>
              </div>
              
              {agent.tee_details?.enabled && (
                <div className="space-y-2">
                  {agent.tee_details.provider && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Provider</label>
                      <p className="text-gray-900">{agent.tee_details.provider}</p>
                    </div>
                  )}
                  {agent.tee_details.attestation && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Attestation</label>
                      <p className="text-gray-900 text-sm break-all">{agent.tee_details.attestation}</p>
                    </div>
                  )}
                </div>
              )}

              {!agent.tee_details && (
                <div className="text-center py-8">
                  <ShieldCheckIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 mb-2">No TEE Information</h4>
                  <p className="text-gray-600">This agent doesn't have Trusted Execution Environment details available.</p>
                </div>
              )}
            </div>
          </div>

          {/* Metadata */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Metadata</h3>
            </div>
            <div className="card-body space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Created</span>
                <span className="text-sm text-gray-900">
                  {new Date(agent.created_at).toLocaleDateString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Updated</span>
                <span className="text-sm text-gray-900">
                  {new Date(agent.updated_at).toLocaleDateString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Agent ID</span>
                <span className="text-sm text-gray-900 font-mono">{agent.id}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentDetail;

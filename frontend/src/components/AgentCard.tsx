import React from 'react';
import { Link } from 'react-router-dom';
import { CpuChipIcon, TagIcon, GlobeAltIcon } from '@heroicons/react/24/outline';
import { Agent } from '../types';

interface AgentCardProps {
  agent: Agent;
  showActions?: boolean;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent, showActions = true }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-success-100 text-success-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'error':
        return 'bg-error-100 text-error-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

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
    <div className="card hover:shadow-md transition-shadow duration-200">
      <div className="card-body">
        <div className="flex items-start justify-between">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CpuChipIcon className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">
                <Link to={`/agents/${agent.id}`} className="hover:text-primary-600">
                  {agent.name}
                </Link>
              </h3>
              <p className="text-sm text-gray-500">v{agent.version}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`badge ${getStatusColor('active')}`}>
              Active
            </span>
          </div>
        </div>

        <div className="mt-4">
          <p className="text-sm text-gray-600 line-clamp-2">{agent.description}</p>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center text-sm text-gray-500">
              <GlobeAltIcon className="h-4 w-4 mr-1" />
              {agent.location_type}
            </div>
            <div className="text-sm text-gray-500">
              {agent.provider}
            </div>
          </div>
        </div>

        {agent.tags && agent.tags.length > 0 && (
          <div className="mt-4">
            <div className="flex flex-wrap gap-1">
              {agent.tags.slice(0, 3).map((tag) => (
                <span key={tag} className="badge badge-secondary">
                  <TagIcon className="h-3 w-3 mr-1" />
                  {tag}
                </span>
              ))}
              {agent.tags.length > 3 && (
                <span className="text-xs text-gray-500">
                  +{agent.tags.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}

        {agent.auth_schemes && agent.auth_schemes.length > 0 && (
          <div className="mt-4">
            <div className="flex flex-wrap gap-1">
              {agent.auth_schemes.slice(0, 2).map((scheme, index) => (
                <span key={index} className={`badge ${getAuthTypeColor(scheme.type)}`}>
                  {scheme.type.toUpperCase()}
                </span>
              ))}
              {agent.auth_schemes.length > 2 && (
                <span className="text-xs text-gray-500">
                  +{agent.auth_schemes.length - 2} more
                </span>
              )}
            </div>
          </div>
        )}

        {showActions && (
          <div className="mt-6 flex items-center justify-between">
            <div className="text-xs text-gray-500">
              Updated {new Date(agent.updated_at).toLocaleDateString()}
            </div>
            <div className="flex space-x-2">
              <Link
                to={`/agents/${agent.id}`}
                className="btn btn-sm btn-primary"
              >
                View Details
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentCard;

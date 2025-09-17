import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  CpuChipIcon, 
  UserGroupIcon, 
  GlobeAltIcon, 
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import StatsCard from '../components/StatsCard';
import AgentCard from '../components/AgentCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { StatsSkeleton, CardSkeleton } from '../components/Skeleton';
import { StatusBadge } from '../components/Badge';
import api from '../services/api';
import { Stats, Agent, HealthStatus } from '../types';
import { formatRelativeTime } from '../utils/cn';

const Dashboard: React.FC = () => {
  const [recentAgents, setRecentAgents] = useState<Agent[]>([]);

  // Fetch stats
  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ['stats'],
    queryFn: () => api.getStats(),
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: (failureCount, error: any) => {
      if (error.response?.status === 403) {
        return false;
      }
      return failureCount < 3;
    },
  });

  // Fetch health status
  const { data: health, isLoading: healthLoading, error: healthError } = useQuery({
    queryKey: ['health'],
    queryFn: () => api.getHealth(),
    refetchInterval: 10000, // Refetch every 10 seconds
    retry: (failureCount, error: any) => {
      if (error.response?.status === 403) {
        return false;
      }
      return failureCount < 3;
    },
  });

  // Fetch recent agents
  const { data: agentsData, isLoading: agentsLoading } = useQuery({
    queryKey: ['recent-agents'],
    queryFn: () => api.getAgents(1, 6),
  });

  useEffect(() => {
    if (agentsData) {
      setRecentAgents(agentsData.agents);
    }
  }, [agentsData]);

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'unhealthy':
        return 'text-red-600 bg-red-100';
      case 'degraded':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getHealthStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return '✅';
      case 'unhealthy':
        return '❌';
      case 'degraded':
        return '⚠️';
      default:
        return '❓';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Overview of your A2A Agent Registry</p>
        </div>
        <div className="flex items-center space-x-4">
          {health && (
            <div className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${getHealthStatusColor(health.status)}`}>
              <span className="mr-1">{getHealthStatusIcon(health.status)}</span>
              {health.status.charAt(0).toUpperCase() + health.status.slice(1)}
            </div>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Registry Statistics</h2>
        <StatsCard stats={stats || {
          total_agents: 0,
          total_clients: 0,
          total_peers: 0,
          active_agents: 0,
          recent_registrations: 0,
          search_queries_today: 0,
        }} isLoading={statsLoading} />
      </div>

      {/* System Health */}
      {healthError ? (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">System Health</h3>
          </div>
          <div className="card-body">
            <div className="text-center py-8">
              <div className="text-yellow-600 mb-4">
                <ExclamationTriangleIcon className="h-12 w-12 mx-auto mb-2" />
                <h4 className="text-lg font-medium">Health Status Unavailable</h4>
                <p className="text-sm text-gray-600">
                  Unable to load system health information. This may require authentication.
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : health && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">System Health</h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getHealthStatusColor(health.components.database.status)}`}>
                  <span className="mr-1">{getHealthStatusIcon(health.components.database.status)}</span>
                  Database
                </div>
                {health.components.database.response_time_ms && (
                  <p className="text-xs text-gray-500 mt-1">
                    {health.components.database.response_time_ms}ms
                  </p>
                )}
              </div>
              <div className="text-center">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getHealthStatusColor(health.components.redis.status)}`}>
                  <span className="mr-1">{getHealthStatusIcon(health.components.redis.status)}</span>
                  Redis
                </div>
                {health.components.redis.response_time_ms && (
                  <p className="text-xs text-gray-500 mt-1">
                    {health.components.redis.response_time_ms}ms
                  </p>
                )}
              </div>
              <div className="text-center">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getHealthStatusColor(health.components.elasticsearch.status)}`}>
                  <span className="mr-1">{getHealthStatusIcon(health.components.elasticsearch.status)}</span>
                  Elasticsearch
                </div>
                {health.components.elasticsearch.response_time_ms && (
                  <p className="text-xs text-gray-500 mt-1">
                    {health.components.elasticsearch.response_time_ms}ms
                  </p>
                )}
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <div className="flex items-center">
                  <ClockIcon className="h-4 w-4 mr-1" />
                  Last Check: {new Date(health.timestamp * 1000).toLocaleTimeString()}
                </div>
                <div className="flex items-center">
                  <ChartBarIcon className="h-4 w-4 mr-1" />
                  Status: {health.status}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Agents */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Recent Agents</h2>
          <a href="/agents" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
            View all →
          </a>
        </div>
        
        {agentsLoading ? (
          <LoadingSpinner text="Loading recent agents..." />
        ) : recentAgents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recentAgents.map((agent) => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </div>
        ) : (
          <div className="card">
            <div className="card-body text-center py-12">
              <CpuChipIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No agents found</h3>
              <p className="text-gray-600 mb-4">Get started by registering your first agent.</p>
              <a href="/agents" className="btn btn-primary">
                Register Agent
              </a>
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a
              href="/agents"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <CpuChipIcon className="h-8 w-8 text-primary-600 mr-3" />
              <div>
                <h4 className="font-medium text-gray-900">Register Agent</h4>
                <p className="text-sm text-gray-600">Add a new agent to the registry</p>
              </div>
            </a>
            
            <a
              href="/clients"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <UserGroupIcon className="h-8 w-8 text-primary-600 mr-3" />
              <div>
                <h4 className="font-medium text-gray-900">Manage Clients</h4>
                <p className="text-sm text-gray-600">Configure OAuth clients</p>
              </div>
            </a>
            
            <a
              href="/federation"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <GlobeAltIcon className="h-8 w-8 text-primary-600 mr-3" />
              <div>
                <h4 className="font-medium text-gray-900">Federation</h4>
                <p className="text-sm text-gray-600">Configure peer registries</p>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

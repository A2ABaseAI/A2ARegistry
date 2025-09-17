import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  PlusIcon, 
  GlobeAltIcon, 
  ArrowPathIcon, 
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';
import api from '../services/api';
import { PeerRegistry } from '../types';
import toast from 'react-hot-toast';

const Federation: React.FC = () => {
  const [syncingPeers, setSyncingPeers] = useState<Set<string>>(new Set());

  const { data: peers, isLoading, error, refetch } = useQuery({
    queryKey: ['peers'],
    queryFn: async () => {
      try {
        console.log('Fetching peer registries...');
        const result = await api.getPeerRegistries();
        console.log('Peer registries result:', result);
        return result;
      } catch (error: any) {
        console.error('Federation API error details:', {
          message: error.message,
          status: error?.response?.status,
          statusText: error?.response?.statusText,
          data: error?.response?.data,
          error
        });
        
        // Handle authentication errors gracefully
        if (error?.response?.status === 403) {
          console.warn('Access denied - federation endpoint requires authentication');
          return [];
        }
        
        // Handle network errors
        if (error?.code === 'NETWORK_ERROR' || error?.message?.includes('Network Error')) {
          console.warn('Network error - federation endpoint may not be available');
          return [];
        }
        
        throw error;
      }
    },
    retry: (failureCount, error: any) => {
      // Don't retry on 403 errors
      if (error?.response?.status === 403) {
        return false;
      }
      return failureCount < 3;
    },
  });

  const handleSyncPeer = async (peerId: string) => {
    try {
      setSyncingPeers(prev => new Set(prev).add(peerId));
      await api.syncPeerRegistry(peerId);
      toast.success('Peer synchronization started');
      refetch();
    } catch (error) {
      toast.error('Failed to sync peer registry');
      console.error('Sync peer error:', error);
    } finally {
      setSyncingPeers(prev => {
        const newSet = new Set(prev);
        newSet.delete(peerId);
        return newSet;
      });
    }
  };

  const handleDeletePeer = async (peerId: string) => {
    if (window.confirm('Are you sure you want to delete this peer registry? This action cannot be undone.')) {
      try {
        await api.deletePeerRegistry(peerId);
        toast.success('Peer registry deleted successfully');
        refetch();
      } catch (error) {
        toast.error('Failed to delete peer registry');
        console.error('Delete peer error:', error);
      }
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'inactive':
        return <XCircleIcon className="h-5 w-5 text-gray-400" />;
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <XCircleIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'badge-success';
      case 'inactive':
        return 'badge-secondary';
      case 'error':
        return 'badge-error';
      default:
        return 'badge-secondary';
    }
  };

  if (isLoading) {
    return <LoadingSpinner text="Loading peer registries..." />;
  }

  // Ensure peers is always an array
  const safePeers = Array.isArray(peers) ? peers : [];

  if (error) {
    return (
      <div className="card">
        <div className="card-body text-center py-12">
          <GlobeAltIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading peer registries</h3>
          <p className="text-gray-600 mb-4">
            {error instanceof Error ? error.message : 'An unexpected error occurred'}
          </p>
          <button onClick={() => refetch()} className="btn btn-primary">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Federation</h1>
          <p className="text-gray-600">Manage peer registries and cross-registry synchronization</p>
        </div>
        <Link to="/federation/new" className="btn btn-primary">
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Peer Registry
        </Link>
      </div>

      {/* Federation Info */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">Federation Overview</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">
                {safePeers.length}
              </div>
              <div className="text-sm text-gray-600">Peer Registries</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {safePeers.filter(p => p.status === 'active').length}
              </div>
              <div className="text-sm text-gray-600">Active Peers</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {safePeers.filter(p => p.status === 'error').length}
              </div>
              <div className="text-sm text-gray-600">Errors</div>
            </div>
          </div>
        </div>
      </div>

      {/* Peer Registries */}
      {safePeers.length > 0 ? (
        <div className="space-y-6">
          <h2 className="text-lg font-semibold text-gray-900">Peer Registries</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {safePeers.map((peer) => (
              <div key={peer.id} className="card hover:shadow-md transition-shadow duration-200">
                <div className="card-body">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <GlobeAltIcon className="h-8 w-8 text-primary-600" />
                      </div>
                      <div className="ml-4">
                        <h3 className="text-lg font-medium text-gray-900">{peer.name}</h3>
                        <p className="text-sm text-gray-500">{peer.url}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(peer.status)}
                      <span className={`badge ${getStatusColor(peer.status)}`}>
                        {peer.status}
                      </span>
                    </div>
                  </div>

                  <div className="mt-4">
                    <p className="text-sm text-gray-600">{peer.description}</p>
                  </div>

                  <div className="mt-4 space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Sync Interval</label>
                      <p className="text-sm text-gray-600">{peer.sync_interval} minutes</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Last Sync</label>
                      <p className="text-sm text-gray-600">
                        {peer.last_sync 
                          ? new Date(peer.last_sync).toLocaleString()
                          : 'Never'
                        }
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Auth Token</label>
                      <div className="flex items-center">
                        <input
                          type="password"
                          value={peer.auth_token}
                          readOnly
                          className="input flex-1 font-mono text-sm"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 flex items-center justify-between">
                    <div className="text-xs text-gray-500">
                      Added {new Date(peer.created_at).toLocaleDateString()}
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleSyncPeer(peer.id)}
                        disabled={syncingPeers.has(peer.id)}
                        className="btn btn-sm btn-secondary"
                      >
                        {syncingPeers.has(peer.id) ? (
                          <div className="flex items-center">
                            <div className="loading-spinner h-3 w-3 mr-1" />
                            Syncing...
                          </div>
                        ) : (
                          <>
                            <ArrowPathIcon className="h-3 w-3 mr-1" />
                            Sync Now
                          </>
                        )}
                      </button>
                      <button className="btn btn-sm btn-secondary">
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeletePeer(peer.id)}
                        className="btn btn-sm btn-error"
                      >
                        <TrashIcon className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : error ? (
        <div className="card">
          <div className="card-body text-center py-12">
            <div className="text-red-600 mb-4">
              <GlobeAltIcon className="h-12 w-12 mx-auto mb-2" />
              <h3 className="text-lg font-medium">Error loading peer registries</h3>
              <p className="text-sm text-gray-600">
                {error instanceof Error ? error.message : 'An unexpected error occurred'}
              </p>
              {error instanceof Error && error.message.includes('403') && (
                <p className="text-sm text-blue-600 mt-2">
                  Federation management requires authentication. Please log in to access this feature.
                </p>
              )}
            </div>
            <button onClick={() => refetch()} className="btn btn-primary">
              Try Again
            </button>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="card-body text-center py-12">
            <GlobeAltIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No peer registries found</h3>
            <p className="text-gray-600 mb-4">
              Connect to other A2A registries to enable cross-registry agent discovery.
            </p>
            <Link to="/federation/new" className="btn btn-primary">
              Add Peer Registry
            </Link>
          </div>
        </div>
      )}

      {/* Federation Benefits */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">Benefits of Federation</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Cross-Registry Discovery</h4>
              <p className="text-sm text-gray-600">
                Discover agents from multiple registries, expanding your available agent ecosystem.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Automatic Synchronization</h4>
              <p className="text-sm text-gray-600">
                Keep agent catalogs synchronized across registries with configurable sync intervals.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Secure Communication</h4>
              <p className="text-sm text-gray-600">
                Authenticated peer-to-peer communication ensures secure federation.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Scalable Architecture</h4>
              <p className="text-sm text-gray-600">
                Build distributed agent networks that scale across organizations and regions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Federation;

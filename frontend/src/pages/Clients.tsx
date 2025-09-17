import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { PlusIcon, KeyIcon, EyeIcon, EyeSlashIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import LoadingSpinner from '../components/LoadingSpinner';
import api from '../services/api';
import { Client } from '../types';

const Clients: React.FC = () => {
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});

  const { data: clients, isLoading, error, refetch } = useQuery({
    queryKey: ['clients'],
    queryFn: async () => {
      try {
        return await api.getClients();
      } catch (error: any) {
        // Handle authentication errors gracefully
        if (error.response?.status === 403) {
          console.warn('Access denied - clients endpoint requires authentication');
          return [];
        }
        throw error;
      }
    },
    retry: (failureCount, error: any) => {
      // Don't retry on 403 errors
      if (error.response?.status === 403) {
        return false;
      }
      return failureCount < 3;
    },
  });

  const toggleSecretVisibility = (clientId: string) => {
    setShowSecrets(prev => ({
      ...prev,
      [clientId]: !prev[clientId]
    }));
  };

  const handleDeleteClient = async (clientId: string) => {
    if (window.confirm('Are you sure you want to delete this client? This action cannot be undone.')) {
      try {
        await api.deleteClient(clientId);
        toast.success('Client deleted successfully');
        refetch();
      } catch (error) {
        toast.error('Failed to delete client');
        console.error('Delete client error:', error);
      }
    }
  };

  if (isLoading) {
    return <LoadingSpinner text="Loading clients..." />;
  }

  if (error) {
    return (
      <div className="card">
        <div className="card-body text-center py-12">
          <KeyIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading clients</h3>
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
          <h1 className="text-2xl font-bold text-gray-900">OAuth Clients</h1>
          <p className="text-gray-600">Manage OAuth 2.0 client credentials</p>
        </div>
        <Link to="/clients/new" className="btn btn-primary">
          <PlusIcon className="h-4 w-4 mr-2" />
          Register Client
        </Link>
      </div>

      {/* Clients List */}
      {clients && Array.isArray(clients) && clients.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {clients.map((client) => (
            <div key={client.id} className="card hover:shadow-md transition-shadow duration-200">
              <div className="card-body">
                <div className="flex items-start justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <KeyIcon className="h-8 w-8 text-primary-600" />
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-medium text-gray-900">{client.name}</h3>
                      <p className="text-sm text-gray-500">Client ID: {client.client_id}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteClient(client.id)}
                    className="text-gray-400 hover:text-red-600 transition-colors"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>

                <div className="mt-4">
                  <p className="text-sm text-gray-600">{client.description}</p>
                </div>

                <div className="mt-4 space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Client Secret</label>
                    <div className="flex items-center">
                      <input
                        type={showSecrets[client.id] ? 'text' : 'password'}
                        value={client.client_secret}
                        readOnly
                        className="input flex-1 font-mono text-sm"
                      />
                      <button
                        type="button"
                        onClick={() => toggleSecretVisibility(client.id)}
                        className="ml-2 text-gray-400 hover:text-gray-600"
                      >
                        {showSecrets[client.id] ? (
                          <EyeSlashIcon className="h-5 w-5" />
                        ) : (
                          <EyeIcon className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Redirect URIs</label>
                    <div className="space-y-1">
                      {client.redirect_uris.map((uri, index) => (
                        <div key={index} className="text-sm text-gray-600 font-mono bg-gray-50 px-2 py-1 rounded">
                          {uri}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Scopes</label>
                    <div className="flex flex-wrap gap-1">
                      {Array.isArray(client.scopes) && client.scopes.map((scope) => (
                        <span key={scope} className="badge badge-primary">
                          {scope}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="mt-6 flex items-center justify-between">
                  <div className="text-xs text-gray-500">
                    Created {new Date(client.created_at).toLocaleDateString()}
                  </div>
                  <div className="flex space-x-2">
                    <button className="btn btn-sm btn-secondary">
                      Edit
                    </button>
                    <button className="btn btn-sm btn-primary">
                      View Entitlements
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="card">
          <div className="card-body text-center py-12">
            <div className="text-red-600 mb-4">
              <KeyIcon className="h-12 w-12 mx-auto mb-2" />
              <h3 className="text-lg font-medium">Error loading clients</h3>
              <p className="text-sm text-gray-600">
                {error instanceof Error ? error.message : 'An unexpected error occurred'}
              </p>
              {error instanceof Error && error.message.includes('403') && (
                <p className="text-sm text-blue-600 mt-2">
                  Client management requires authentication. Please log in to access this feature.
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
            <KeyIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No clients found</h3>
            <p className="text-gray-600 mb-4">Get started by registering your first OAuth client.</p>
            <Link to="/clients/new" className="btn btn-primary">
              Register Client
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default Clients;

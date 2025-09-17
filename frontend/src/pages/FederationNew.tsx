import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { 
  GlobeAltIcon, 
  ArrowLeftIcon,
  PlusIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import { PeerRegistry } from '../types';
import toast from 'react-hot-toast';

interface PeerFormData {
  name: string;
  base_url: string;
  description: string;
  auth_token: string;
  sync_interval: number;
}

const FederationNew: React.FC = () => {
  const [showToken, setShowToken] = useState(false);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue
  } = useForm<PeerFormData>({
    defaultValues: {
      sync_interval: 3600 // 1 hour in seconds
    }
  });

  const createPeerMutation = useMutation({
    mutationFn: (peer: Partial<PeerRegistry>) => api.createPeerRegistry(peer),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['peers'] });
      toast.success('Peer registry added successfully!');
      navigate('/federation');
    },
    onError: (error: any) => {
      toast.error('Failed to add peer registry: ' + (error.message || 'Unknown error'));
    }
  });

  const onSubmit = async (data: PeerFormData) => {
    try {
      await createPeerMutation.mutateAsync(data);
    } catch (error) {
      // Error is handled by onError
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => navigate('/federation')}
          className="flex items-center text-sm text-gray-600 hover:text-gray-900"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Back to Federation
        </button>
      </div>

      <div className="card">
        <div className="card-header">
          <h1 className="text-2xl font-bold text-gray-900">Add Peer Registry</h1>
          <p className="text-gray-600">Connect to another A2A registry for cross-registry agent discovery</p>
        </div>
        <div className="card-body">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                Registry Name *
              </label>
              <input
                {...register('name', { required: 'Registry name is required' })}
                type="text"
                className={`input ${errors.name ? 'input-error' : ''}`}
                placeholder="Partner Registry"
              />
              {errors.name && (
                <p className="mt-1 text-sm text-error-600">{errors.name.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="base_url" className="block text-sm font-medium text-gray-700 mb-1">
                Base URL *
              </label>
              <input
                {...register('base_url', { 
                  required: 'Base URL is required',
                  pattern: {
                    value: /^https?:\/\/.+/,
                    message: 'Must be a valid HTTP/HTTPS URL'
                  }
                })}
                type="url"
                className={`input ${errors.base_url ? 'input-error' : ''}`}
                placeholder="https://registry.example.com"
              />
              {errors.base_url && (
                <p className="mt-1 text-sm text-error-600">{errors.base_url.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                {...register('description')}
                rows={3}
                className="input"
                placeholder="Brief description of this peer registry"
              />
            </div>

            <div>
              <label htmlFor="auth_token" className="block text-sm font-medium text-gray-700 mb-1">
                Authentication Token *
              </label>
              <div className="relative">
                <input
                  {...register('auth_token', { required: 'Authentication token is required' })}
                  type={showToken ? 'text' : 'password'}
                  className={`input pr-10 ${errors.auth_token ? 'input-error' : ''}`}
                  placeholder="Enter authentication token"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowToken(!showToken)}
                >
                  {showToken ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.auth_token && (
                <p className="mt-1 text-sm text-error-600">{errors.auth_token.message}</p>
              )}
              <p className="mt-1 text-sm text-gray-500">
                This token will be used to authenticate with the peer registry
              </p>
            </div>

            <div>
              <label htmlFor="sync_interval" className="block text-sm font-medium text-gray-700 mb-1">
                Sync Interval (seconds)
              </label>
              <input
                {...register('sync_interval', { 
                  required: 'Sync interval is required',
                  min: { value: 300, message: 'Minimum sync interval is 5 minutes (300 seconds)' },
                  max: { value: 86400, message: 'Maximum sync interval is 24 hours (86400 seconds)' }
                })}
                type="number"
                min="300"
                max="86400"
                className={`input ${errors.sync_interval ? 'input-error' : ''}`}
              />
              {errors.sync_interval && (
                <p className="mt-1 text-sm text-error-600">{errors.sync_interval.message}</p>
              )}
              <p className="mt-1 text-sm text-gray-500">
                How often to synchronize with this peer registry (300-86400 seconds)
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <GlobeAltIcon className="h-5 w-5 text-blue-400" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-800">
                    Federation Benefits
                  </h3>
                  <div className="mt-2 text-sm text-blue-700">
                    <ul className="list-disc list-inside space-y-1">
                      <li>Discover agents from partner registries</li>
                      <li>Enable cross-registry agent communication</li>
                      <li>Expand your agent ecosystem</li>
                      <li>Share your agents with partner networks</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => navigate('/federation')}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createPeerMutation.isPending}
                className="btn btn-primary"
              >
                {createPeerMutation.isPending ? (
                  <div className="flex items-center">
                    <div className="loading-spinner h-4 w-4 mr-2" />
                    Adding...
                  </div>
                ) : (
                  'Add Peer Registry'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default FederationNew;

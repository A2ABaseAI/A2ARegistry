import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { 
  UserGroupIcon, 
  ArrowLeftIcon,
  PlusIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import { Client } from '../types';
import toast from 'react-hot-toast';

interface ClientFormData {
  name: string;
  description: string;
  redirect_uris: string[];
  scopes: string[];
}

const ClientNew: React.FC = () => {
  const [showSecret, setShowSecret] = useState(false);
  const [generatedSecret, setGeneratedSecret] = useState<string>('');
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue
  } = useForm<ClientFormData>({
    defaultValues: {
      scopes: ['read:agents', 'write:agents'],
      redirect_uris: []
    }
  });

  const createClientMutation = useMutation({
    mutationFn: (client: Partial<Client>) => api.createClient(client),
    onSuccess: (data) => {
      setGeneratedSecret(data.client_secret);
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      toast.success('Client created successfully!');
    },
    onError: (error: any) => {
      toast.error('Failed to create client: ' + (error.message || 'Unknown error'));
    }
  });

  const onSubmit = async (data: ClientFormData) => {
    try {
      await createClientMutation.mutateAsync(data);
    } catch (error) {
      // Error is handled by onError
    }
  };

  const addRedirectUri = () => {
    const currentUris = watch('redirect_uris') || [];
    setValue('redirect_uris', [...currentUris, '']);
  };

  const removeRedirectUri = (index: number) => {
    const currentUris = watch('redirect_uris') || [];
    setValue('redirect_uris', currentUris.filter((_, i) => i !== index));
  };

  const updateRedirectUri = (index: number, value: string) => {
    const currentUris = watch('redirect_uris') || [];
    const newUris = [...currentUris];
    newUris[index] = value;
    setValue('redirect_uris', newUris);
  };

  const addScope = () => {
    const currentScopes = watch('scopes') || [];
    setValue('scopes', [...currentScopes, '']);
  };

  const removeScope = (index: number) => {
    const currentScopes = watch('scopes') || [];
    setValue('scopes', currentScopes.filter((_, i) => i !== index));
  };

  const updateScope = (index: number, value: string) => {
    const currentScopes = watch('scopes') || [];
    const newScopes = [...currentScopes];
    newScopes[index] = value;
    setValue('scopes', newScopes);
  };

  if (generatedSecret) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => navigate('/clients')}
            className="flex items-center text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-1" />
            Back to Clients
          </button>
        </div>

        <div className="card">
          <div className="card-header">
            <h1 className="text-2xl font-bold text-gray-900">Client Created Successfully</h1>
          </div>
          <div className="card-body">
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-6">
              <div className="flex">
                <div className="flex-shrink-0">
                  <EyeIcon className="h-5 w-5 text-yellow-400" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">
                    Important: Save Your Client Secret
                  </h3>
                  <div className="mt-2 text-sm text-yellow-700">
                    <p>
                      This is the only time you'll be able to see the client secret. 
                      Make sure to copy it and store it securely.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Client ID</label>
                <div className="flex">
                  <input
                    type="text"
                    value={createClientMutation.data?.client_id || ''}
                    readOnly
                    className="input flex-1 font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => navigator.clipboard.writeText(createClientMutation.data?.client_id || '')}
                    className="ml-2 btn btn-secondary"
                  >
                    Copy
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Client Secret</label>
                <div className="flex">
                  <input
                    type={showSecret ? 'text' : 'password'}
                    value={generatedSecret}
                    readOnly
                    className="input flex-1 font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => setShowSecret(!showSecret)}
                    className="ml-2 btn btn-secondary"
                  >
                    {showSecret ? <EyeSlashIcon className="h-4 w-4" /> : <EyeIcon className="h-4 w-4" />}
                  </button>
                  <button
                    type="button"
                    onClick={() => navigator.clipboard.writeText(generatedSecret)}
                    className="ml-2 btn btn-secondary"
                  >
                    Copy
                  </button>
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => navigate('/clients')}
                className="btn btn-primary"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => navigate('/clients')}
          className="flex items-center text-sm text-gray-600 hover:text-gray-900"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Back to Clients
        </button>
      </div>

      <div className="card">
        <div className="card-header">
          <h1 className="text-2xl font-bold text-gray-900">Register New Client</h1>
          <p className="text-gray-600">Create a new OAuth 2.0 client for API access</p>
        </div>
        <div className="card-body">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                Client Name *
              </label>
              <input
                {...register('name', { required: 'Client name is required' })}
                type="text"
                className={`input ${errors.name ? 'input-error' : ''}`}
                placeholder="My Application"
              />
              {errors.name && (
                <p className="mt-1 text-sm text-error-600">{errors.name.message}</p>
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
                placeholder="Brief description of your application"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Redirect URIs
              </label>
              <div className="space-y-2">
                {(watch('redirect_uris') || []).map((uri, index) => (
                  <div key={index} className="flex">
                    <input
                      type="url"
                      value={uri}
                      onChange={(e) => updateRedirectUri(index, e.target.value)}
                      className="input flex-1"
                      placeholder="https://example.com/callback"
                    />
                    <button
                      type="button"
                      onClick={() => removeRedirectUri(index)}
                      className="ml-2 btn btn-sm btn-error"
                    >
                      Remove
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addRedirectUri}
                  className="btn btn-sm btn-secondary"
                >
                  <PlusIcon className="h-4 w-4 mr-1" />
                  Add Redirect URI
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Scopes
              </label>
              <div className="space-y-2">
                {(watch('scopes') || []).map((scope, index) => (
                  <div key={index} className="flex">
                    <input
                      type="text"
                      value={scope}
                      onChange={(e) => updateScope(index, e.target.value)}
                      className="input flex-1"
                      placeholder="read:agents"
                    />
                    <button
                      type="button"
                      onClick={() => removeScope(index)}
                      className="ml-2 btn btn-sm btn-error"
                    >
                      Remove
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addScope}
                  className="btn btn-sm btn-secondary"
                >
                  <PlusIcon className="h-4 w-4 mr-1" />
                  Add Scope
                </button>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Common scopes: read:agents, write:agents, read:clients, write:clients
              </p>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => navigate('/clients')}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createClientMutation.isPending}
                className="btn btn-primary"
              >
                {createClientMutation.isPending ? (
                  <div className="flex items-center">
                    <div className="loading-spinner h-4 w-4 mr-2" />
                    Creating...
                  </div>
                ) : (
                  'Create Client'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ClientNew;

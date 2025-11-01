'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { agentApi, authApi } from '@/lib/api';
import { formatErrorMessage } from '@/lib/error-handler';
import { Loader2, Upload, AlertCircle, CheckCircle2, ExternalLink, X } from 'lucide-react';
import Link from 'next/link';

export default function PublishPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [publishMethod, setPublishMethod] = useState<'url' | 'card'>('url');
  const [formData, setFormData] = useState({
    cardUrl: '',
    public: true,
    cardJson: '',
  });

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const userData = await authApi.getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);

      // Check if user has required roles
      const roles = userData.roles || [];
      if (!roles.includes('Administrator') && !roles.includes('CatalogManager')) {
        setError('You need Administrator or CatalogManager role to publish agents');
      }
    } catch (err: any) {
      if (err.response?.status === 401) {
        setIsAuthenticated(false);
        router.push('/login');
      } else {
        setError('Failed to verify authentication');
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      let publishData: any = {
        public: formData.public,
      };

      if (publishMethod === 'url') {
        if (!formData.cardUrl.trim()) {
          throw new Error('Card URL is required');
        }
        publishData.cardUrl = formData.cardUrl;
      } else {
        if (!formData.cardJson.trim()) {
          throw new Error('Card JSON is required');
        }
        try {
          publishData.card = JSON.parse(formData.cardJson);
        } catch {
          throw new Error('Invalid JSON format');
        }
      }

      const result = await agentApi.publishAgent(publishData);
      setSuccess(`Agent ${result.agentId} v${result.version} published successfully!`);
      
      // Reset form
      setFormData({
        cardUrl: '',
        public: true,
        cardJson: '',
      });

      // Redirect to agent page after 2 seconds
      setTimeout(() => {
        router.push(`/agents/${result.agentId}`);
      }, 2000);
    } catch (err: any) {
      setError(formatErrorMessage(err) || 'Failed to publish agent');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
        </div>
      </div>
    );
  }

  const roles = user?.roles || [];
  const canPublish = roles.includes('Administrator') || roles.includes('CatalogManager');

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
          Publish Agent
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Add a new agent to the registry by providing its card URL or card JSON
        </p>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6 flex items-start space-x-2">
          <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-red-800 dark:text-red-200 font-medium">Error</p>
            <p className="text-red-700 dark:text-red-300 text-sm mt-1">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      )}

      {success && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 mb-6 flex items-start space-x-2">
          <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-green-800 dark:text-green-200 font-medium">Success!</p>
            <p className="text-green-700 dark:text-green-300 text-sm mt-1">{success}</p>
          </div>
          <button
            onClick={() => setSuccess(null)}
            className="text-green-600 dark:text-green-400 hover:text-green-800 dark:hover:text-green-200"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      )}

      {!canPublish && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6 mb-6">
          <p className="text-yellow-800 dark:text-yellow-200 mb-2">
            <strong>Permission Required</strong>
          </p>
          <p className="text-yellow-700 dark:text-yellow-300 text-sm">
            You need Administrator or CatalogManager role to publish agents. Your current roles: {roles.join(', ') || 'None'}
          </p>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
              Publish Method
            </label>
            <div className="flex space-x-4">
              <button
                type="button"
                onClick={() => setPublishMethod('url')}
                className={`flex-1 px-4 py-3 border-2 rounded-lg transition-colors ${
                  publishMethod === 'url'
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                    : 'border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:border-gray-400 dark:hover:border-gray-600'
                }`}
              >
                <ExternalLink className="h-5 w-5 mx-auto mb-2" />
                <div className="font-medium">Card URL</div>
                <div className="text-xs mt-1">Publish from a URL</div>
              </button>
              <button
                type="button"
                onClick={() => setPublishMethod('card')}
                className={`flex-1 px-4 py-3 border-2 rounded-lg transition-colors ${
                  publishMethod === 'card'
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                    : 'border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:border-gray-400 dark:hover:border-gray-600'
                }`}
              >
                <Upload className="h-5 w-5 mx-auto mb-2" />
                <div className="font-medium">Card JSON</div>
                <div className="text-xs mt-1">Publish directly</div>
              </button>
            </div>
          </div>

          {publishMethod === 'url' ? (
            <div>
              <label
                htmlFor="cardUrl"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Card URL <span className="text-red-500">*</span>
              </label>
              <input
                type="url"
                id="cardUrl"
                value={formData.cardUrl}
                onChange={(e) => setFormData({ ...formData, cardUrl: e.target.value })}
                placeholder="https://example.com/.well-known/agent-card.json"
                required
                disabled={!canPublish}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                URL must use HTTPS and return a valid agent card JSON
              </p>
            </div>
          ) : (
            <div>
              <label
                htmlFor="cardJson"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Agent Card JSON <span className="text-red-500">*</span>
              </label>
              <textarea
                id="cardJson"
                value={formData.cardJson}
                onChange={(e) => setFormData({ ...formData, cardJson: e.target.value })}
                placeholder='{"name": "My Agent", "description": "...", "url": "https://...", "version": "1.0.0", ...}'
                required
                disabled={!canPublish}
                rows={12}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed font-mono text-sm"
              />
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Enter a valid agent card JSON following the A2A Agent Card specification
              </p>
            </div>
          )}

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="public"
              checked={formData.public}
              onChange={(e) => setFormData({ ...formData, public: e.target.checked })}
              disabled={!canPublish}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded disabled:opacity-50"
            />
            <label
              htmlFor="public"
              className="text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Make agent publicly discoverable
            </label>
          </div>

          <div className="flex space-x-4 pt-4">
            <button
              type="submit"
              disabled={loading || !canPublish}
              className="flex-1 bg-primary-600 hover:bg-primary-700 text-white font-medium py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin mr-2" />
                  Publishing...
                </>
              ) : (
                <>
                  <Upload className="h-5 w-5 mr-2" />
                  Publish Agent
                </>
              )}
            </button>
            <Link
              href="/"
              className="px-6 py-3 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-center"
            >
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}


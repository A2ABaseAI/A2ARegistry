'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { agentApi, Agent } from '@/lib/api';
import { formatErrorMessage } from '@/lib/error-handler';
import AgentList from '@/components/AgentList';
import { Loader2, Lock, AlertCircle } from 'lucide-react';
import Link from 'next/link';

export default function EntitledPage() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      setIsAuthenticated(true);
      await loadEntitledAgents();
    } catch (err: any) {
      if (err.response?.status === 401) {
        setIsAuthenticated(false);
        router.push('/login');
      } else {
        setError(formatErrorMessage(err) || 'Failed to load entitled agents');
        setLoading(false);
      }
    }
  }, [router, loadEntitledAgents]);

  const loadEntitledAgents = useCallback(async () => {
    try {
      setLoading(true);
      const response = await agentApi.getEntitledAgents(20, 0);
      setAgents(response.items);
      setError(null);
    } catch (err: any) {
      if (err.response?.status === 401) {
        setIsAuthenticated(false);
        router.push('/login');
      } else {
        setError(formatErrorMessage(err) || 'Failed to load entitled agents');
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center space-x-2 mb-2">
          <Lock className="h-6 w-6 text-primary-600 dark:text-primary-400" />
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
            My Entitled Agents
          </h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          Agents you have access to, including public agents and those you&apos;re entitled to
        </p>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6 flex items-start space-x-2">
          <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-red-800 dark:text-red-200 font-medium">Error</p>
            <p className="text-red-700 dark:text-red-300 text-sm mt-1">{error}</p>
            <Link
              href="/login"
              className="text-primary-600 dark:text-primary-400 hover:underline text-sm mt-2 inline-block"
            >
              Login to access entitled agents
            </Link>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
          <span className="ml-2 text-gray-600 dark:text-gray-400">Loading entitled agents...</span>
        </div>
      ) : agents.length > 0 ? (
        <>
          <div className="mb-4">
            <p className="text-gray-600 dark:text-gray-400">
              You have access to {agents.length} agent{agents.length !== 1 ? 's' : ''}
            </p>
          </div>
          <AgentList agents={agents} />
        </>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-12 text-center">
          <Lock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            No entitled agents found
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            You don&apos;t have access to any private agents yet.
          </p>
          <div className="space-x-4">
            <Link
              href="/"
              className="inline-block px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
            >
              Browse Public Agents
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}


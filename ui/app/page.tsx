'use client';

import { useState, useEffect } from 'react';
import { agentApi, Agent } from '@/lib/api';
import { formatErrorMessage } from '@/lib/error-handler';
import AgentCard from '@/components/AgentCard';
import SearchBar from '@/components/SearchBar';
import AgentList from '@/components/AgentList';
import { Search, Loader2 } from 'lucide-react';

export default function Home() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Agent[]>([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPublicAgents();
  }, []);

  const loadPublicAgents = async () => {
    try {
      setLoading(true);
      const response = await agentApi.getPublicAgents(20, 0);
      setAgents(response.items);
      setError(null);
    } catch (err: any) {
      setError(formatErrorMessage(err) || 'Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (!query.trim()) {
      setSearchResults([]);
      setSearching(false);
      return;
    }

    try {
      setSearching(true);
      const response = await agentApi.searchAgents({
        q: query,
        top: 20,
        skip: 0,
      });
      setSearchResults(response.items);
      setError(null);
    } catch (err: any) {
      setError(formatErrorMessage(err) || 'Search failed');
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const displayAgents = searchQuery ? searchResults : agents;
  const showSearchResults = searchQuery && !searching;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
          A2A Agent Registry
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Discover and manage AI agents for your applications
        </p>
      </div>

      <div className="mb-6">
        <SearchBar onSearch={handleSearch} />
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
          <p className="text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      {searching && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
          <span className="ml-2 text-gray-600 dark:text-gray-400">Searching...</span>
        </div>
      )}

      {showSearchResults && (
        <div className="mb-4">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
            Search Results
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Found {searchResults.length} agent{searchResults.length !== 1 ? 's' : ''}
          </p>
        </div>
      )}

      {loading && !searching ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
          <span className="ml-2 text-gray-600 dark:text-gray-400">Loading agents...</span>
        </div>
      ) : displayAgents.length > 0 ? (
        <AgentList agents={displayAgents} />
      ) : !searching ? (
        <div className="text-center py-12">
          <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            {searchQuery ? 'No agents found matching your search' : 'No agents available'}
          </p>
        </div>
      ) : null}
    </div>
  );
}


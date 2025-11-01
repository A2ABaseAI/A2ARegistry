'use client';

import { useState } from 'react';
import { agentApi, Agent } from '@/lib/api';
import { formatErrorMessage } from '@/lib/error-handler';
import SearchBar from '@/components/SearchBar';
import AgentList from '@/components/AgentList';
import { Loader2, Filter, X, Search } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Agent[]>([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    protocolVersion: '',
    publisherId: '',
  });
  const [showFilters, setShowFilters] = useState(false);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (!query.trim() && Object.values(filters).every(v => !v)) {
      setSearchResults([]);
      setSearching(false);
      return;
    }

    try {
      setSearching(true);
      const searchFilters: Record<string, any> = {};
      if (filters.protocolVersion) {
        searchFilters.protocolVersion = filters.protocolVersion;
      }
      if (filters.publisherId) {
        searchFilters.publisherId = filters.publisherId;
      }

      const response = await agentApi.searchAgents({
        q: query || undefined,
        filters: Object.keys(searchFilters).length > 0 ? searchFilters : undefined,
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

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    if (searchQuery || Object.values(newFilters).some(v => v)) {
      handleSearch(searchQuery);
    }
  };

  const clearFilters = () => {
    setFilters({ protocolVersion: '', publisherId: '' });
    setSearchQuery('');
    setSearchResults([]);
  };

  const hasActiveFilters = Object.values(filters).some(v => v) || searchQuery;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
          Search Agents
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Find agents by name, description, skills, or capabilities
        </p>
      </div>

      <div className="mb-6 space-y-4">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <SearchBar onSearch={handleSearch} placeholder="Search agents by name, description, or skills..." />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={cn(
              'px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center space-x-2',
              showFilters && 'bg-primary-50 dark:bg-primary-900/20 border-primary-500 text-primary-600 dark:text-primary-400'
            )}
          >
            <Filter className="h-4 w-4" />
            <span>Filters</span>
            {hasActiveFilters && (
              <span className="px-2 py-0.5 bg-primary-600 text-white text-xs rounded-full">
                Active
              </span>
            )}
          </button>
        </div>

        {showFilters && (
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Search Filters</h3>
              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="text-sm text-primary-600 dark:text-primary-400 hover:underline flex items-center space-x-1"
                >
                  <X className="h-4 w-4" />
                  <span>Clear all</span>
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Protocol Version
                </label>
                <input
                  type="text"
                  value={filters.protocolVersion}
                  onChange={(e) => handleFilterChange('protocolVersion', e.target.value)}
                  placeholder="e.g., 1.0"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Publisher ID
                </label>
                <input
                  type="text"
                  value={filters.publisherId}
                  onChange={(e) => handleFilterChange('publisherId', e.target.value)}
                  placeholder="e.g., example.com"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
          </div>
        )}

        {hasActiveFilters && (
          <div className="flex flex-wrap gap-2">
            {searchQuery && (
              <span className="px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-full text-sm flex items-center space-x-2">
                <span>Query: "{searchQuery}"</span>
                <button
                  onClick={() => {
                    setSearchQuery('');
                    handleSearch('');
                  }}
                  className="hover:text-primary-900 dark:hover:text-primary-100"
                >
                  <X className="h-4 w-4" />
                </button>
              </span>
            )}
            {filters.protocolVersion && (
              <span className="px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-full text-sm flex items-center space-x-2">
                <span>Protocol: {filters.protocolVersion}</span>
                <button
                  onClick={() => handleFilterChange('protocolVersion', '')}
                  className="hover:text-primary-900 dark:hover:text-primary-100"
                >
                  <X className="h-4 w-4" />
                </button>
              </span>
            )}
            {filters.publisherId && (
              <span className="px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-full text-sm flex items-center space-x-2">
                <span>Publisher: {filters.publisherId}</span>
                <button
                  onClick={() => handleFilterChange('publisherId', '')}
                  className="hover:text-primary-900 dark:hover:text-primary-100"
                >
                  <X className="h-4 w-4" />
                </button>
              </span>
            )}
          </div>
        )}
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

      {!searching && searchResults.length > 0 && (
        <div className="mb-4">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
            Search Results
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Found {searchResults.length} agent{searchResults.length !== 1 ? 's' : ''}
          </p>
        </div>
      )}

      {!searching && searchResults.length > 0 ? (
        <AgentList agents={searchResults} />
      ) : !searching && hasActiveFilters ? (
        <div className="text-center py-12">
          <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            No agents found matching your search criteria
          </p>
          <button
            onClick={clearFilters}
            className="mt-4 text-primary-600 dark:text-primary-400 hover:underline"
          >
            Clear filters and start over
          </button>
        </div>
      ) : !searching ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8">
          <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400 mb-2">
            Start searching for agents
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500">
            Enter a search query above or use filters to find agents
          </p>
        </div>
      ) : null}
    </div>
  );
}


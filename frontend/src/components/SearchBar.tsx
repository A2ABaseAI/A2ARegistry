import React, { useState } from 'react';
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline';

interface SearchBarProps {
  onSearch: (query: string, filters: any) => void;
  placeholder?: string;
  showFilters?: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({ 
  onSearch, 
  placeholder = "Search agents...",
  showFilters = true 
}) => {
  const [query, setQuery] = useState('');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [filters, setFilters] = useState({
    tags: [] as string[],
    capabilities: [] as string[],
    provider: '',
    location_type: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query, filters);
  };

  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      tags: [],
      capabilities: [],
      provider: '',
      location_type: '',
    });
    setQuery('');
    onSearch('', {});
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Main search input */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="input pl-10"
            placeholder={placeholder}
          />
        </div>

        {/* Advanced filters toggle */}
        {showFilters && (
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              className="flex items-center text-sm text-gray-600 hover:text-gray-900"
            >
              <FunnelIcon className="h-4 w-4 mr-1" />
              Advanced Filters
            </button>
            
            {(query || Object.values(filters).some(v => v !== '' && (Array.isArray(v) ? v.length > 0 : true))) && (
              <button
                type="button"
                onClick={clearFilters}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                Clear all
              </button>
            )}
          </div>
        )}

        {/* Advanced filters */}
        {showFilters && showAdvancedFilters && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
            {/* Provider filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Provider
              </label>
              <input
                type="text"
                value={filters.provider}
                onChange={(e) => handleFilterChange('provider', e.target.value)}
                className="input"
                placeholder="Filter by provider"
              />
            </div>

            {/* Location type filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location Type
              </label>
              <select
                value={filters.location_type}
                onChange={(e) => handleFilterChange('location_type', e.target.value)}
                className="input"
              >
                <option value="">All types</option>
                <option value="cloud">Cloud</option>
                <option value="edge">Edge</option>
                <option value="local">Local</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </div>

            {/* Tags filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tags
              </label>
              <input
                type="text"
                value={filters.tags.join(', ')}
                onChange={(e) => handleFilterChange('tags', e.target.value.split(',').map(t => t.trim()).filter(t => t))}
                className="input"
                placeholder="tag1, tag2, tag3"
              />
            </div>

            {/* Capabilities filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Capabilities
              </label>
              <input
                type="text"
                value={filters.capabilities.join(', ')}
                onChange={(e) => handleFilterChange('capabilities', e.target.value.split(',').map(c => c.trim()).filter(c => c))}
                className="input"
                placeholder="capability1, capability2"
              />
            </div>
          </div>
        )}

        {/* Search button */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="btn btn-primary"
          >
            <MagnifyingGlassIcon className="h-4 w-4 mr-2" />
            Search
          </button>
        </div>
      </form>
    </div>
  );
};

export default SearchBar;

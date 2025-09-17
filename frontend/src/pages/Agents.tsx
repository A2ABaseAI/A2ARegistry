import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { PlusIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import AgentCard from '../components/AgentCard';
import SearchBar from '../components/SearchBar';
import LoadingSpinner from '../components/LoadingSpinner';
import api from '../services/api';
import { SearchRequest } from '../types';

const Agents: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchFilters, setSearchFilters] = useState<any>({});
  const [currentPage, setCurrentPage] = useState(1);
  const [viewMode, setViewMode] = useState<'public' | 'entitled'>('public');

  // Fetch agents based on current view mode
  const { data: agentsData, isLoading, error, refetch } = useQuery({
    queryKey: ['agents', viewMode, currentPage, searchQuery, searchFilters],
    queryFn: async () => {
      try {
        if (searchQuery || Object.keys(searchFilters).length > 0) {
          const searchRequest: SearchRequest = {
            query: searchQuery || undefined,
            filters: Object.keys(searchFilters).length > 0 ? searchFilters : undefined,
            page: currentPage,
            limit: 20,
          };
          return await api.searchAgents(searchRequest);
        } else if (viewMode === 'entitled') {
          const agents = await api.getEntitledAgents();
          return {
            agents,
            total: agents.length,
            page: 1,
            limit: agents.length,
            total_pages: 1,
          };
        } else {
          return await api.getAgents(currentPage, 20);
        }
      } catch (error: any) {
        // Handle authentication errors gracefully
        if (error.response?.status === 403) {
          console.warn('Access denied - some features may require authentication');
          return {
            agents: [],
            total: 0,
            page: 1,
            limit: 20,
            total_pages: 0,
          };
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

  const handleSearch = (query: string, filters: any) => {
    setSearchQuery(query);
    setSearchFilters(filters);
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const renderPagination = () => {
    if (!agentsData || agentsData.total_pages <= 1) return null;

    const pages = [];
    const totalPages = agentsData.total_pages;
    const current = currentPage;

    // Always show first page
    pages.push(
      <button
        key={1}
        onClick={() => handlePageChange(1)}
        className={`px-3 py-2 text-sm font-medium rounded-md ${
          current === 1
            ? 'bg-primary-100 text-primary-700'
            : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        1
      </button>
    );

    // Show ellipsis if needed
    if (current > 3) {
      pages.push(
        <span key="ellipsis1" className="px-3 py-2 text-sm text-gray-500">
          ...
        </span>
      );
    }

    // Show current page and surrounding pages
    for (let i = Math.max(2, current - 1); i <= Math.min(totalPages - 1, current + 1); i++) {
      pages.push(
        <button
          key={i}
          onClick={() => handlePageChange(i)}
          className={`px-3 py-2 text-sm font-medium rounded-md ${
            current === i
              ? 'bg-primary-100 text-primary-700'
              : 'text-gray-700 hover:bg-gray-50'
          }`}
        >
          {i}
        </button>
      );
    }

    // Show ellipsis if needed
    if (current < totalPages - 2) {
      pages.push(
        <span key="ellipsis2" className="px-3 py-2 text-sm text-gray-500">
          ...
        </span>
      );
    }

    // Always show last page
    if (totalPages > 1) {
      pages.push(
        <button
          key={totalPages}
          onClick={() => handlePageChange(totalPages)}
          className={`px-3 py-2 text-sm font-medium rounded-md ${
            current === totalPages
              ? 'bg-primary-100 text-primary-700'
              : 'text-gray-700 hover:bg-gray-50'
          }`}
        >
          {totalPages}
        </button>
      );
    }

    return (
      <div className="flex items-center justify-between mt-6">
        <div className="text-sm text-gray-700">
          Showing {((current - 1) * 20) + 1} to {Math.min(current * 20, agentsData.total)} of {agentsData.total} agents
        </div>
        <div className="flex space-x-1">
          <button
            onClick={() => handlePageChange(current - 1)}
            disabled={current === 1}
            className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          {pages}
          <button
            onClick={() => handlePageChange(current + 1)}
            disabled={current === totalPages}
            className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Agents</h1>
          <p className="text-gray-600">Discover and manage AI agents in the registry</p>
        </div>
        <a href="/agents/new" className="btn btn-primary">
          <PlusIcon className="h-4 w-4 mr-2" />
          Register Agent
        </a>
      </div>

      {/* View Mode Toggle */}
      <div className="flex items-center space-x-4">
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('public')}
            className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
              viewMode === 'public'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Public Agents
          </button>
          <button
            onClick={() => setViewMode('entitled')}
            className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
              viewMode === 'entitled'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            My Entitled Agents
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <SearchBar
        onSearch={handleSearch}
        placeholder={`Search ${viewMode === 'public' ? 'public' : 'entitled'} agents...`}
        showFilters={viewMode === 'public'}
      />

      {/* Results */}
      {isLoading ? (
        <LoadingSpinner text="Loading agents..." />
      ) : error ? (
        <div className="card">
          <div className="card-body text-center py-12">
            <div className="text-red-600 mb-4">
              <MagnifyingGlassIcon className="h-12 w-12 mx-auto mb-2" />
              <h3 className="text-lg font-medium">Error loading agents</h3>
              <p className="text-sm text-gray-600">
                {error instanceof Error ? error.message : 'An unexpected error occurred'}
              </p>
              {error instanceof Error && error.message.includes('403') && (
                <p className="text-sm text-blue-600 mt-2">
                  Some features may require authentication. Please log in to access all agents.
                </p>
              )}
            </div>
            <button onClick={() => refetch()} className="btn btn-primary">
              Try Again
            </button>
          </div>
        </div>
      ) : agentsData && agentsData.agents.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agentsData.agents.map((agent) => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </div>
          {renderPagination()}
        </>
      ) : (
        <div className="card">
          <div className="card-body text-center py-12">
            <MagnifyingGlassIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {searchQuery || Object.keys(searchFilters).length > 0
                ? 'No agents found'
                : `No ${viewMode === 'public' ? 'public' : 'entitled'} agents`}
            </h3>
            <p className="text-gray-600 mb-4">
              {searchQuery || Object.keys(searchFilters).length > 0
                ? 'Try adjusting your search criteria'
                : viewMode === 'public'
                ? 'No public agents are currently available'
                : 'You don\'t have access to any agents yet'}
            </p>
            {viewMode === 'public' && (
              <a href="/agents/new" className="btn btn-primary">
                Register First Agent
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Agents;

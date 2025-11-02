'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { agentApi, Agent } from '@/lib/api';
import { formatErrorMessage } from '@/lib/error-handler';
import SearchBar from '@/components/SearchBar';
import AgentList from '@/components/AgentList';
import { Search, Loader2, Zap, Shield, Globe, Book, ArrowRight, Users, Code } from 'lucide-react';

export default function Home() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Agent[]>([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAgentList, setShowAgentList] = useState(false);

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
    setShowAgentList(true);
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

  const handleViewAllAgents = () => {
    setShowAgentList(true);
  };

  const displayAgents = searchQuery ? searchResults : agents;
  const showSearchResults = searchQuery && !searching;

  const features = [
    {
      icon: Search,
      title: 'Agent Discovery',
      description: 'Advanced search with lexical and semantic capabilities to find the perfect agent for your needs.',
    },
    {
      icon: Zap,
      title: 'Fast Performance',
      description: 'High-performance registry with Redis caching and horizontal scaling for enterprise use.',
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'OAuth 2.0 authentication, rate limiting, and comprehensive security headers.',
    },
    {
      icon: Globe,
      title: 'Federation',
      description: 'Cross-registry peering and synchronization for distributed agent ecosystems.',
    },
    {
      icon: Code,
      title: 'SDK Support',
      description: 'Comprehensive SDKs for Python, TypeScript, Go, and Java to integrate easily.',
    },
    {
      icon: Book,
      title: 'Well Documented',
      description: 'Complete API documentation, guides, and examples to get you started quickly.',
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-50 via-white to-primary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
              A2A Agent Registry
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-400 mb-8">
              Discover, manage, and orchestrate AI agents in the Agent-to-Agent ecosystem
            </p>
            <p className="text-lg text-gray-500 dark:text-gray-500 mb-12 max-w-2xl mx-auto">
              A centralized registry service for discovering and managing AI agents. 
              Build intelligent applications with our comprehensive agent marketplace.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link
                href="/search"
                className="inline-flex items-center justify-center px-8 py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg transition-colors"
              >
                <Search className="h-5 w-5 mr-2" />
                Explore Agents
              </Link>
              <Link
                href="/docs"
                className="inline-flex items-center justify-center px-8 py-3 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 font-semibold rounded-lg transition-colors"
              >
                <Book className="h-5 w-5 mr-2" />
                Documentation
              </Link>
            </div>

            {/* Search Bar */}
            <div className="max-w-2xl mx-auto">
              <SearchBar onSearch={handleSearch} />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      {!showAgentList && (
        <section className="py-20 bg-white dark:bg-gray-800">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
                Powerful Features
              </h2>
              <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                Everything you need to discover, publish, and manage AI agents at scale
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {features.map((feature, index) => {
                const IconComponent = feature.icon;
                return (
                  <div
                    key={index}
                    className="p-6 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 hover:shadow-lg transition-all"
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                        <IconComponent className="h-6 w-6 text-primary-600 dark:text-primary-400" />
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                        {feature.title}
                      </h3>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400">
                      {feature.description}
                    </p>
                  </div>
                );
              })}
            </div>

            <div className="mt-16 text-center">
              <button
                onClick={handleViewAllAgents}
                className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg transition-colors"
              >
                <Users className="h-5 w-5" />
                View All Available Agents
                <ArrowRight className="h-5 w-5" />
              </button>
            </div>
          </div>
        </section>
      )}

      {/* Agents Section */}
      {showAgentList && (
        <section className="py-12 bg-gray-50 dark:bg-gray-900">
          <div className="container mx-auto px-4">
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                {searchQuery ? 'Search Results' : 'Available Agents'}
              </h2>
              {searchQuery && showSearchResults && (
                <p className="text-gray-600 dark:text-gray-400">
                  Found {searchResults.length} agent{searchResults.length !== 1 ? 's' : ''}
                </p>
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

            {loading && !searching ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
                <span className="ml-2 text-gray-600 dark:text-gray-400">Loading agents...</span>
              </div>
            ) : displayAgents.length > 0 ? (
              <AgentList agents={displayAgents} />
            ) : !searching ? (
              <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                  {searchQuery ? 'No agents found matching your search' : 'No agents available'}
                </p>
                {!searchQuery && (
                  <Link
                    href="/publish"
                    className="inline-flex items-center gap-2 mt-4 text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
                  >
                    Publish your first agent <ArrowRight className="h-4 w-4" />
                  </Link>
                )}
              </div>
            ) : null}
          </div>
        </section>
      )}
    </div>
  );
}


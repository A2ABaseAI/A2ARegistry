import React from 'react';
import { Stats } from '../types';

interface StatsCardProps {
  stats: Stats;
  isLoading?: boolean;
}

const StatsCard: React.FC<StatsCardProps> = ({ stats, isLoading = false }) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card">
            <div className="card-body">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  const statItems = [
    {
      name: 'Total Agents',
      value: stats.total_agents,
      icon: '🤖',
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      name: 'Active Agents',
      value: stats.active_agents,
      icon: '✅',
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      name: 'Total Clients',
      value: stats.total_clients,
      icon: '👥',
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      name: 'Peer Registries',
      value: stats.total_peers,
      icon: '🌐',
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {statItems.map((item) => (
        <div key={item.name} className="card hover:shadow-md transition-shadow duration-200">
          <div className="card-body">
            <div className="flex items-center">
              <div className={`flex-shrink-0 p-3 rounded-lg ${item.bgColor}`}>
                <span className="text-2xl">{item.icon}</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{item.name}</p>
                <p className={`text-2xl font-bold ${item.color}`}>
                  {item.value.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default StatsCard;

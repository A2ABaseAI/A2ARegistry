'use client';

import Link from 'next/link';
import { Agent } from '@/lib/api';
import { ExternalLink, User, Package, Code } from 'lucide-react';
import { cn, truncate } from '@/lib/utils';

interface AgentCardProps {
  agent: Agent;
  className?: string;
}

export default function AgentCard({ agent, className }: AgentCardProps) {
  // Use SDK field names: id (not agentId), provider (not publisherId)
  const agentId = agent.id;
  
  if (!agentId) {
    console.warn('Agent missing ID:', agent);
    return null;
  }

  return (
    <Link href={`/agents/${agentId}`}>
      <div
        className={cn(
          'bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow cursor-pointer',
          className
        )}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              {agent.name || agentId || 'Unknown Agent'}
            </h3>
            {agent.description && (
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                {truncate(agent.description, 150)}
              </p>
            )}
          </div>
          <ExternalLink className="h-5 w-5 text-gray-400 flex-shrink-0 ml-2" />
        </div>

        <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
          {agent.provider && (
            <div className="flex items-center space-x-1">
              <User className="h-4 w-4" />
              <span className="font-medium">Provider:</span>
              <span>{agent.provider}</span>
            </div>
          )}
          {agent.version && (
            <div className="flex items-center space-x-1">
              <Package className="h-4 w-4" />
              <span className="font-medium">Version:</span>
              <span>{agent.version}</span>
            </div>
          )}
        </div>

        {agent.skills && agent.skills.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex flex-wrap gap-2">
              {agent.skills.slice(0, 3).map((skill: any, index: number) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-xs rounded"
                >
                  {skill.name || skill.id || `Skill ${index + 1}`}
                </span>
              ))}
              {agent.skills.length > 3 && (
                <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded">
                  +{agent.skills.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </Link>
  );
}


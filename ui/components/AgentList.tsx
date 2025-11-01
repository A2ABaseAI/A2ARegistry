'use client';

import { Agent } from '@/lib/api';
import AgentCard from './AgentCard';

interface AgentListProps {
  agents: Agent[];
}

export default function AgentList({ agents }: AgentListProps) {
  if (agents.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 dark:text-gray-400">No agents found</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {agents.map((agent, index) => {
        const agentId = agent.id;
        if (!agentId) {
          console.warn('Agent missing ID at index', index, agent);
          return null;
        }
        return <AgentCard key={agentId} agent={agent} />;
      })}
    </div>
  );
}


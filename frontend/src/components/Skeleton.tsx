import React from 'react';

interface SkeletonProps {
  className?: string;
  width?: string;
  height?: string;
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'full';
}

const Skeleton: React.FC<SkeletonProps> = ({ 
  className = '', 
  width = 'w-full', 
  height = 'h-4', 
  rounded = 'md' 
}) => {
  const roundedClass = {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full'
  }[rounded];

  return (
    <div 
      className={`animate-pulse bg-gray-200 ${width} ${height} ${roundedClass} ${className}`}
      aria-label="Loading..."
      role="status"
    />
  );
};

// Pre-built skeleton components for common patterns
export const CardSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`card ${className}`}>
    <div className="card-body">
      <div className="flex items-start space-x-4">
        <Skeleton width="w-12" height="h-12" rounded="lg" />
        <div className="flex-1 space-y-2">
          <Skeleton width="w-3/4" height="h-5" />
          <Skeleton width="w-1/2" height="h-4" />
          <Skeleton width="w-full" height="h-3" />
        </div>
      </div>
      <div className="mt-4 flex space-x-2">
        <Skeleton width="w-16" height="h-6" rounded="full" />
        <Skeleton width="w-20" height="h-6" rounded="full" />
      </div>
    </div>
  </div>
);

export const TableSkeleton: React.FC<{ rows?: number; cols?: number }> = ({ 
  rows = 5, 
  cols = 4 
}) => (
  <div className="space-y-3">
    {Array.from({ length: rows }, (_, i) => (
      <div key={i} className="flex space-x-4">
        {Array.from({ length: cols }, (_, j) => (
          <Skeleton 
            key={j} 
            width={j === 0 ? "w-1/4" : j === cols - 1 ? "w-1/6" : "w-1/3"} 
            height="h-4" 
          />
        ))}
      </div>
    ))}
  </div>
);

export const StatsSkeleton: React.FC = () => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
    {Array.from({ length: 3 }, (_, i) => (
      <div key={i} className="card">
        <div className="card-body text-center">
          <Skeleton width="w-16" height="h-16" rounded="lg" className="mx-auto mb-4" />
          <Skeleton width="w-24" height="h-8" className="mx-auto mb-2" />
          <Skeleton width="w-32" height="h-4" className="mx-auto" />
        </div>
      </div>
    ))}
  </div>
);

export default Skeleton;

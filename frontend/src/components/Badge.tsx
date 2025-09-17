import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../utils/cn';

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "bg-gray-100 text-gray-800 hover:bg-gray-200",
        primary: "bg-primary-100 text-primary-800 hover:bg-primary-200",
        secondary: "bg-gray-100 text-gray-800 hover:bg-gray-200",
        success: "bg-green-100 text-green-800 hover:bg-green-200",
        warning: "bg-yellow-100 text-yellow-800 hover:bg-yellow-200",
        error: "bg-red-100 text-red-800 hover:bg-red-200",
        info: "bg-blue-100 text-blue-800 hover:bg-blue-200",
        outline: "border border-gray-300 text-gray-700 hover:bg-gray-50",
        outlinePrimary: "border border-primary-300 text-primary-700 hover:bg-primary-50",
      },
      size: {
        sm: "px-2 py-0.5 text-xs",
        default: "px-2.5 py-0.5 text-xs",
        lg: "px-3 py-1 text-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  icon?: React.ReactNode;
  removable?: boolean;
  onRemove?: () => void;
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant, size, icon, removable, onRemove, children, ...props }, ref) => {
    return (
      <div
        className={cn(badgeVariants({ variant, size }), className)}
        ref={ref}
        {...props}
      >
        {icon && <span className="mr-1 h-3 w-3">{icon}</span>}
        {children}
        {removable && onRemove && (
          <button
            onClick={onRemove}
            className="ml-1 h-3 w-3 rounded-full hover:bg-black hover:bg-opacity-10 transition-colors"
            aria-label="Remove"
          >
            <svg
              className="h-3 w-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>
    );
  }
);

Badge.displayName = "Badge";

// Status Badge Component
interface StatusBadgeProps {
  status: 'active' | 'inactive' | 'pending' | 'error' | 'success' | 'warning';
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  const statusConfig = {
    active: { variant: 'success' as const, text: 'Active' },
    inactive: { variant: 'secondary' as const, text: 'Inactive' },
    pending: { variant: 'warning' as const, text: 'Pending' },
    error: { variant: 'error' as const, text: 'Error' },
    success: { variant: 'success' as const, text: 'Success' },
    warning: { variant: 'warning' as const, text: 'Warning' },
  };

  const config = statusConfig[status];

  return (
    <Badge variant={config.variant} className={className}>
      <div className="flex items-center">
        <div className="h-2 w-2 rounded-full bg-current mr-1.5" />
        {config.text}
      </div>
    </Badge>
  );
};

// Priority Badge Component
interface PriorityBadgeProps {
  priority: 'low' | 'medium' | 'high' | 'critical';
  className?: string;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ priority, className }) => {
  const priorityConfig = {
    low: { variant: 'info' as const, text: 'Low' },
    medium: { variant: 'warning' as const, text: 'Medium' },
    high: { variant: 'error' as const, text: 'High' },
    critical: { variant: 'error' as const, text: 'Critical' },
  };

  const config = priorityConfig[priority];

  return (
    <Badge variant={config.variant} className={className}>
      {config.text}
    </Badge>
  );
};

export { Badge, badgeVariants };

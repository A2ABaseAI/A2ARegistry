import React from 'react';
import toast, { Toaster, ToastBar } from 'react-hot-toast';
import { 
  CheckCircleIcon, 
  ExclamationCircleIcon, 
  InformationCircleIcon, 
  XCircleIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline';
import { cn } from '../utils/cn';

// Custom toast functions with consistent styling
export const showToast = {
  success: (message: string, options?: any) => {
    return toast.success(message, {
      duration: 4000,
      ...options,
    });
  },
  
  error: (message: string, options?: any) => {
    return toast.error(message, {
      duration: 6000,
      ...options,
    });
  },
  
  info: (message: string, options?: any) => {
    return toast(message, {
      duration: 5000,
      icon: <InformationCircleIcon className="h-5 w-5 text-blue-500" />,
      ...options,
    });
  },
  
  warning: (message: string, options?: any) => {
    return toast(message, {
      duration: 5000,
      icon: <ExclamationCircleIcon className="h-5 w-5 text-yellow-500" />,
      ...options,
    });
  },
  
  loading: (message: string, options?: any) => {
    return toast.loading(message, {
      ...options,
    });
  },
  
  promise: <T,>(
    promise: Promise<T>,
    msgs: {
      loading: string;
      success: string | ((data: T) => string);
      error: string | ((error: any) => string);
    },
    options?: any
  ) => {
    return toast.promise(promise, msgs, {
      duration: 4000,
      ...options,
    });
  },
};

// Custom Toaster component with enhanced styling
export const CustomToaster: React.FC = () => {
  return (
    <Toaster
      position="top-right"
      gutter={8}
      toastOptions={{
        duration: 4000,
        style: {
          background: 'white',
          color: '#374151',
          border: '1px solid #E5E7EB',
          borderRadius: '8px',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
          padding: '12px 16px',
          fontSize: '14px',
          maxWidth: '400px',
        },
        success: {
          iconTheme: {
            primary: '#10B981',
            secondary: 'white',
          },
          style: {
            border: '1px solid #D1FAE5',
            background: '#ECFDF5',
          },
        },
        error: {
          iconTheme: {
            primary: '#EF4444',
            secondary: 'white',
          },
          style: {
            border: '1px solid #FECACA',
            background: '#FEF2F2',
          },
        },
      }}
    >
      {(t) => (
        <ToastBar toast={t}>
          {({ icon, message }) => (
            <div className="flex items-center">
              <div className="flex-shrink-0">
                {icon}
              </div>
              <div className="ml-3 flex-1">
                {message}
              </div>
              {t.type !== 'loading' && (
                <button
                  onClick={() => toast.dismiss(t.id)}
                  className="ml-3 flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
                  aria-label="Dismiss notification"
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
              )}
            </div>
          )}
        </ToastBar>
      )}
    </Toaster>
  );
};

// Toast notification component for complex content
interface NotificationToastProps {
  title: string;
  message?: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  action?: {
    label: string;
    onClick: () => void;
  };
  onDismiss?: () => void;
}

export const NotificationToast: React.FC<NotificationToastProps> = ({
  title,
  message,
  type = 'info',
  action,
  onDismiss,
}) => {
  const icons = {
    success: <CheckCircleIcon className="h-5 w-5 text-green-500" />,
    error: <XCircleIcon className="h-5 w-5 text-red-500" />,
    warning: <ExclamationCircleIcon className="h-5 w-5 text-yellow-500" />,
    info: <InformationCircleIcon className="h-5 w-5 text-blue-500" />,
  };

  const bgColors = {
    success: 'bg-green-50 border-green-200',
    error: 'bg-red-50 border-red-200',
    warning: 'bg-yellow-50 border-yellow-200',
    info: 'bg-blue-50 border-blue-200',
  };

  return (
    <div className={cn(
      'max-w-sm w-full border rounded-lg shadow-lg p-4',
      bgColors[type]
    )}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          {icons[type]}
        </div>
        <div className="ml-3 flex-1">
          <p className="text-sm font-medium text-gray-900">
            {title}
          </p>
          {message && (
            <p className="mt-1 text-sm text-gray-600">
              {message}
            </p>
          )}
          {action && (
            <div className="mt-3">
              <button
                onClick={action.onClick}
                className="text-sm font-medium text-blue-600 hover:text-blue-500 transition-colors"
              >
                {action.label}
              </button>
            </div>
          )}
        </div>
        {onDismiss && (
          <div className="ml-4 flex-shrink-0">
            <button
              onClick={onDismiss}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Dismiss"
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper function to show custom notification toast
export const showNotification = (props: NotificationToastProps) => {
  return toast.custom((t) => (
    <NotificationToast
      {...props}
      onDismiss={() => toast.dismiss(t.id)}
    />
  ), {
    duration: props.type === 'error' ? 6000 : 5000,
  });
};

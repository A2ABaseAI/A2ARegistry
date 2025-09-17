import React from 'react';
import { useForm, UseFormReturn, FieldValues, SubmitHandler, UseFormProps } from 'react-hook-form';
import { cn } from '../utils/cn';
import { Button } from './Button';

interface FormProps<T extends FieldValues> extends Omit<React.FormHTMLAttributes<HTMLFormElement>, 'onSubmit' | 'children'> {
  onSubmit: SubmitHandler<T>;
  children: (methods: UseFormReturn<T>) => React.ReactNode;
  options?: UseFormProps<T>;
  className?: string;
}

export function Form<T extends FieldValues>({
  onSubmit,
  children,
  options,
  className,
  ...props
}: FormProps<T>) {
  const methods = useForm<T>(options);

  return (
    <form
      onSubmit={methods.handleSubmit(onSubmit)}
      className={cn('space-y-6', className)}
      {...props}
    >
      {children(methods)}
    </form>
  );
}

// Form Field Component
interface FormFieldProps {
  children: React.ReactNode;
  className?: string;
}

export const FormField: React.FC<FormFieldProps> = ({ children, className }) => {
  return (
    <div className={cn('space-y-2', className)}>
      {children}
    </div>
  );
};

// Form Group Component
interface FormGroupProps {
  title?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export const FormGroup: React.FC<FormGroupProps> = ({ 
  title, 
  description, 
  children, 
  className 
}) => {
  return (
    <div className={cn('space-y-4', className)}>
      {(title || description) && (
        <div className="space-y-1">
          {title && (
            <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          )}
          {description && (
            <p className="text-sm text-gray-600">{description}</p>
          )}
        </div>
      )}
      <div className="space-y-4">
        {children}
      </div>
    </div>
  );
};

// Form Actions Component
interface FormActionsProps {
  children: React.ReactNode;
  className?: string;
  align?: 'left' | 'center' | 'right';
}

export const FormActions: React.FC<FormActionsProps> = ({ 
  children, 
  className,
  align = 'right'
}) => {
  const alignClasses = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end',
  };

  return (
    <div className={cn(
      'flex items-center space-x-3 pt-6 border-t border-gray-200',
      alignClasses[align],
      className
    )}>
      {children}
    </div>
  );
};

// Form Error Component
interface FormErrorProps {
  message?: string;
  className?: string;
}

export const FormError: React.FC<FormErrorProps> = ({ message, className }) => {
  if (!message) return null;

  return (
    <div className={cn(
      'rounded-md bg-red-50 border border-red-200 p-4',
      className
    )}>
      <div className="flex">
        <div className="flex-shrink-0">
          <svg
            className="h-5 w-5 text-red-400"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800">
            There was an error with your submission
          </h3>
          <div className="mt-2 text-sm text-red-700">
            <p>{message}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Form Success Component
interface FormSuccessProps {
  message: string;
  className?: string;
}

export const FormSuccess: React.FC<FormSuccessProps> = ({ message, className }) => {
  return (
    <div className={cn(
      'rounded-md bg-green-50 border border-green-200 p-4',
      className
    )}>
      <div className="flex">
        <div className="flex-shrink-0">
          <svg
            className="h-5 w-5 text-green-400"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3">
          <p className="text-sm font-medium text-green-800">
            {message}
          </p>
        </div>
      </div>
    </div>
  );
};

// Submit Button Component
interface SubmitButtonProps {
  children: React.ReactNode;
  loading?: boolean;
  disabled?: boolean;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  className?: string;
}

export const SubmitButton: React.FC<SubmitButtonProps> = ({
  children,
  loading = false,
  disabled = false,
  variant = 'default',
  size = 'default',
  className,
}) => {
  return (
    <Button
      type="submit"
      variant={variant}
      size={size}
      loading={loading}
      disabled={disabled}
      className={className}
    >
      {children}
    </Button>
  );
};

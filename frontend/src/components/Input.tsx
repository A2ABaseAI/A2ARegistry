import React, { InputHTMLAttributes, forwardRef, useState } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../utils/cn';
import { EyeIcon, EyeSlashIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

const inputVariants = cva(
  "flex w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50 transition-colors",
  {
    variants: {
      variant: {
        default: "border-gray-300 focus:ring-primary-500",
        error: "border-red-300 focus:ring-red-500 focus:border-red-500",
        success: "border-green-300 focus:ring-green-500 focus:border-green-500",
      },
      size: {
        default: "h-10",
        sm: "h-9 px-2 text-sm",
        lg: "h-11 px-4",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface InputProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {
  label?: string;
  error?: string;
  success?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  showPasswordToggle?: boolean;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({
    className,
    variant,
    size,
    type = 'text',
    label,
    error,
    success,
    hint,
    leftIcon,
    rightIcon,
    showPasswordToggle = false,
    disabled,
    id,
    ...props
  }, ref) => {
    const [showPassword, setShowPassword] = useState(false);
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    
    const actualType = showPasswordToggle && type === 'password' 
      ? (showPassword ? 'text' : 'password')
      : type;

    const actualVariant = error ? 'error' : success ? 'success' : variant;

    return (
      <div className="space-y-1">
        {label && (
          <label 
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700"
          >
            {label}
          </label>
        )}
        
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <div className="h-5 w-5 text-gray-400">
                {leftIcon}
              </div>
            </div>
          )}
          
          <input
            type={actualType}
            className={cn(
              inputVariants({ variant: actualVariant, size }),
              leftIcon && "pl-10",
              (rightIcon || showPasswordToggle || error) && "pr-10",
              className
            )}
            ref={ref}
            id={inputId}
            disabled={disabled}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={
              error ? `${inputId}-error` : 
              success ? `${inputId}-success` : 
              hint ? `${inputId}-hint` : 
              undefined
            }
            {...props}
          />
          
          {(rightIcon || showPasswordToggle || error) && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
              {error && (
                <ExclamationCircleIcon className="h-5 w-5 text-red-400" />
              )}
              {!error && showPasswordToggle && type === 'password' && (
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="h-5 w-5 text-gray-400 hover:text-gray-600 transition-colors"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeSlashIcon /> : <EyeIcon />}
                </button>
              )}
              {!error && !showPasswordToggle && rightIcon && (
                <div className="h-5 w-5 text-gray-400">
                  {rightIcon}
                </div>
              )}
            </div>
          )}
        </div>
        
        {error && (
          <p id={`${inputId}-error`} className="text-sm text-red-600 flex items-center">
            <ExclamationCircleIcon className="h-4 w-4 mr-1 flex-shrink-0" />
            {error}
          </p>
        )}
        
        {success && !error && (
          <p id={`${inputId}-success`} className="text-sm text-green-600">
            {success}
          </p>
        )}
        
        {hint && !error && !success && (
          <p id={`${inputId}-hint`} className="text-sm text-gray-500">
            {hint}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export { Input, inputVariants };

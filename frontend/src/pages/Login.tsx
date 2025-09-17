import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { CpuChipIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

interface LoginFormData {
  clientId: string;
  clientSecret: string;
}

const Login: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>();

  const onSubmit = async (data: LoginFormData) => {
    try {
      setIsLoading(true);
      await login(data.clientId, data.clientSecret);
      toast.success('Login successful!');
      
      // Redirect to the page they were trying to access, or dashboard
      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
    } catch (error) {
      toast.error('Login failed. Please check your credentials.');
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <CpuChipIcon className="h-12 w-12 text-primary-600" />
        </div>
        <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
          A2A Agent Registry
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Sign in to your account using OAuth 2.0 client credentials
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="card">
          <div className="card-body">
            <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
              <div>
                <label htmlFor="clientId" className="block text-sm font-medium text-gray-700">
                  Client ID
                </label>
                <div className="mt-1">
                  <input
                    {...register('clientId', { required: 'Client ID is required' })}
                    type="text"
                    autoComplete="username"
                    className={`input ${errors.clientId ? 'input-error' : ''}`}
                    placeholder="Enter your client ID"
                  />
                  {errors.clientId && (
                    <p className="mt-1 text-sm text-error-600">{errors.clientId.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label htmlFor="clientSecret" className="block text-sm font-medium text-gray-700">
                  Client Secret
                </label>
                <div className="mt-1 relative">
                  <input
                    {...register('clientSecret', { required: 'Client Secret is required' })}
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    className={`input pr-10 ${errors.clientSecret ? 'input-error' : ''}`}
                    placeholder="Enter your client secret"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <EyeIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                  {errors.clientSecret && (
                    <p className="mt-1 text-sm text-error-600">{errors.clientSecret.message}</p>
                  )}
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn btn-primary w-full"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center">
                      <div className="loading-spinner h-4 w-4 mr-2" />
                      Signing in...
                    </div>
                  ) : (
                    'Sign in'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-gray-50 text-gray-500">Need help?</span>
            </div>
          </div>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Don't have a client?{' '}
              <Link to="/clients/new" className="font-medium text-primary-600 hover:text-primary-500">
                Register a new client
              </Link>
            </p>
          </div>
        </div>

        {/* Demo credentials */}
        <div className="mt-8 card">
          <div className="card-header">
            <h3 className="text-sm font-medium text-gray-900">Demo Credentials</h3>
          </div>
          <div className="card-body">
            <div className="space-y-2 text-sm">
              <div>
                <span className="font-medium text-gray-700">Client ID:</span>
                <span className="ml-2 font-mono text-gray-600">demo-client</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Client Secret:</span>
                <span className="ml-2 font-mono text-gray-600">demo-secret</span>
              </div>
            </div>
            <p className="mt-3 text-xs text-gray-500">
              These are demo credentials for testing purposes only.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;

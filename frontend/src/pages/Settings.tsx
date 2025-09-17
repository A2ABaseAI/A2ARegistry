import React from 'react';
import { 
  Cog6ToothIcon, 
  UserIcon, 
  ShieldCheckIcon, 
  BellIcon,
  KeyIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

const Settings: React.FC = () => {
  const settingsSections = [
    {
      title: 'Profile',
      description: 'Manage your account settings and preferences',
      icon: UserIcon,
      href: '/settings/profile',
    },
    {
      title: 'Security',
      description: 'Configure security settings and authentication',
      icon: ShieldCheckIcon,
      href: '/settings/security',
    },
    {
      title: 'Notifications',
      description: 'Set up notification preferences',
      icon: BellIcon,
      href: '/settings/notifications',
    },
    {
      title: 'API Keys',
      description: 'Manage API keys and access tokens',
      icon: KeyIcon,
      href: '/settings/api-keys',
    },
    {
      title: 'Federation',
      description: 'Configure federation and peer registry settings',
      icon: GlobeAltIcon,
      href: '/settings/federation',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600">Manage your registry configuration and preferences</p>
        </div>
      </div>

      {/* Settings Sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {settingsSections.map((section) => (
          <a
            key={section.title}
            href={section.href}
            className="card hover:shadow-md transition-shadow duration-200 cursor-pointer"
          >
            <div className="card-body">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <section.icon className="h-8 w-8 text-primary-600" />
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-gray-900">{section.title}</h3>
                  <p className="text-sm text-gray-600">{section.description}</p>
                </div>
              </div>
            </div>
          </a>
        ))}
      </div>

      {/* System Information */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">System Information</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Registry Details</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Version:</span>
                  <span className="text-gray-900 font-mono">1.0.0</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Environment:</span>
                  <span className="text-gray-900">Production</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Uptime:</span>
                  <span className="text-gray-900">24h 15m</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Updated:</span>
                  <span className="text-gray-900">2025-01-16</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Database Status</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className="text-green-600 font-medium">Healthy</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Response Time:</span>
                  <span className="text-gray-900">12ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Connections:</span>
                  <span className="text-gray-900">5/20</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Backup:</span>
                  <span className="text-gray-900">2h ago</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="btn btn-secondary">
              <Cog6ToothIcon className="h-4 w-4 mr-2" />
              Restart Services
            </button>
            <button className="btn btn-secondary">
              <ShieldCheckIcon className="h-4 w-4 mr-2" />
              Run Security Scan
            </button>
            <button className="btn btn-secondary">
              <KeyIcon className="h-4 w-4 mr-2" />
              Generate Backup
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;

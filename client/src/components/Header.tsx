import React from 'react';
import { Moon, Sun, Shield, Search, BarChart3, Network } from 'lucide-react';

interface HeaderProps {
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  activeTab: 'dashboard' | 'network';
  onTabChange: (tab: 'dashboard' | 'network') => void;
}

const Header: React.FC<HeaderProps> = ({ 
  isDarkMode, 
  onToggleDarkMode, 
  searchQuery, 
  onSearchChange,
  activeTab,
  onTabChange
}) => {
  return (
    <header className="header">
      <div className="container">
        <div className="flex justify-between items-center py-4">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-accent rounded-lg">
              <Shield className="h-6 w-6" style={{ color: 'white' }} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-primary">
                Globe
              </h1>
              <p className="text-sm text-secondary">
                Cryptocurrency Threat Analysis Platform
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center space-x-6">
            <nav className="flex space-x-4">
              <button
                onClick={() => onTabChange('dashboard')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  activeTab === 'dashboard'
                    ? 'bg-accent text-white'
                    : 'text-secondary hover:text-primary hover:bg-surface'
                }`}
              >
                <BarChart3 className="h-4 w-4" />
                <span>Dashboard</span>
              </button>
              <button
                onClick={() => onTabChange('network')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  activeTab === 'network'
                    ? 'bg-accent text-white'
                    : 'text-secondary hover:text-primary hover:bg-surface'
                }`}
              >
                <Network className="h-4 w-4" />
                <span>Network</span>
              </button>
            </nav>
          </div>

          {/* Search and Controls */}
          <div className="flex items-center space-x-4">
            {/* Search Bar */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center" style={{ pointerEvents: 'none' }}>
                <Search className="h-4 w-4 text-muted" />
              </div>
              <input
                type="text"
                placeholder="Search domains or addresses..."
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className="input"
              />
            </div>

            {/* Dark Mode Toggle */}
            <button
              onClick={onToggleDarkMode}
              className="btn"
              aria-label="Toggle dark mode"
            >
              {isDarkMode ? (
                <Sun className="h-5 w-5" />
              ) : (
                <Moon className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 
import React from 'react';
import { Search, BarChart3, Network } from 'lucide-react';
import UploadButton from './UploadButton';
import logo from '../media/logo.png';

interface HeaderProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  activeTab: 'dashboard' | 'network';
  onTabChange: (tab: 'dashboard' | 'network') => void;
  onFileUpload?: (file: File) => Promise<void>;
  isUploading?: boolean;
  currentFileName?: string;
}

const Header: React.FC<HeaderProps> = ({ 
  searchQuery, 
  onSearchChange,
  activeTab,
  onTabChange,
  onFileUpload,
  isUploading = false,
  currentFileName
}) => {
  return (
    <header className="header">
      <div className="container">
        <div className="flex items-center justify-between py-4">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3 flex-shrink-0 group">
            <div className="floating">
              <img 
                src={logo} 
                alt="Globe Logo" 
                className="h-8 w-8 object-contain transition-transform duration-300 group-hover:scale-110"
              />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-primary transition-all duration-300 group-hover:text-accent">
                Globe
              </h1>
              <p className="text-sm text-secondary">
                By Alterya
              </p>
            </div>
          </div>

          {/* Navigation Tabs - Centered */}
          <div className="flex items-center justify-center flex-1">
            <nav className="flex space-x-2">
              <button
                onClick={() => onTabChange('dashboard')}
                className={`tab-button ${activeTab === 'dashboard' ? 'active' : ''}`}
              >
                <BarChart3 className="h-4 w-4" />
                <span>Dashboard</span>
              </button>
              <button
                onClick={() => onTabChange('network')}
                className={`tab-button ${activeTab === 'network' ? 'active' : ''}`}
              >
                <Network className="h-4 w-4" />
                <span>Network</span>
              </button>
            </nav>
          </div>

          {/* Search and Controls */}
          <div className="flex items-center space-x-4 flex-shrink-0">
            {/* Upload Button */}
            {onFileUpload && (
              <UploadButton 
                onFileUpload={onFileUpload}
                isLoading={isUploading}
                currentFileName={currentFileName}
              />
            )}
            
            {/* Search Bar */}
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-muted transition-all duration-300 group-focus-within:text-accent group-focus-within:scale-110" />
              </div>
              <input
                type="text"
                placeholder="Search domains or addresses..."
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className="input pl-10 pr-4 py-2 w-64 transition-all duration-300 focus:w-80 focus:pl-12 focus:shadow-lg"
                style={{ 
                  paddingLeft: '2.5rem',
                  transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)'
                }}
              />
              {searchQuery && (
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <button
                    onClick={() => onSearchChange('')}
                    className="text-muted hover:text-error transition-all duration-200 hover:scale-110"
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>


          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 
import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import NetworkGraph from './components/NetworkGraph';
import { DataService } from './services/dataService';
import { VASPData } from './types';
import backgroundImage from './media/background.png';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check for saved theme preference or default to dark mode
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : true;
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'dashboard' | 'network'>('dashboard');
  const [data, setData] = useState<VASPData[]>([]);
  const [isDataLoading, setIsDataLoading] = useState(true);
  const [imageLoaded, setImageLoaded] = useState(false);

  // Apply dark mode class to document
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    // Save preference to localStorage
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
  }, [isDarkMode]);

  // Preload background image
  useEffect(() => {
    const img = new Image();
    img.onload = () => setImageLoaded(true);
    img.src = backgroundImage;
  }, []);

  // Load data once
  useEffect(() => {
    const loadData = async () => {
      try {
        setIsDataLoading(true);
        const dataService = DataService.getInstance();
        await dataService.loadData();
        setData(dataService.getData());
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setIsDataLoading(false);
      }
    };

    loadData();
  }, []);

  const toggleDarkMode = () => {
    setIsDarkMode((prev: boolean) => !prev);
  };

  const handleSearchChange = (query: string) => {
    setSearchQuery(query);
  };

  const handleTabChange = (tab: 'dashboard' | 'network') => {
    setActiveTab(tab);
  };

  if (isDataLoading || !imageLoaded) {
    return (
      <div className="loading-screen">
        <div className="loading-bg" style={{ backgroundImage: `url(${backgroundImage})` }}>
          <div className="loading-overlay">
            <div className="loading-content">
              <div className="loading-logo">
                <div className="globe-icon">
                  <div className="globe-ring"></div>
                  <div className="globe-ring"></div>
                  <div className="globe-ring"></div>
                </div>
              </div>
              <h1 className="loading-title">Globe</h1>
              <p className="loading-subtitle">Cryptocurrency Threat Analysis Platform</p>
              <div className="loading-progress">
                <div className="loading-bar">
                  <div className="loading-bar-fill"></div>
                </div>
                <p className="loading-text">
                  {!imageLoaded ? 'Preparing interface...' : 'Loading VASP intelligence data...'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container" style={{ backgroundImage: `url(${backgroundImage})` }}>
      <div className="app-overlay">
        <div className="app-content">
          <Header
            isDarkMode={isDarkMode}
            onToggleDarkMode={toggleDarkMode}
            searchQuery={searchQuery}
            onSearchChange={handleSearchChange}
            activeTab={activeTab}
            onTabChange={handleTabChange}
          />
          
          <main className="main-content">
            <div className="container py-8">
              <div className="content-wrapper">
                {activeTab === 'dashboard' ? (
                  <Dashboard searchQuery={searchQuery} />
                ) : (
                  <NetworkGraph data={data} searchQuery={searchQuery} />
                )}
              </div>
            </div>
          </main>
          
          <footer className="app-footer">
            <div className="container py-6">
              <div className="footer-content">
                <p className="text-center text-sm text-secondary">
                  © 2025 Globe - GLOBE by Alterya.
                </p>
              </div>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}

export default App;

import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import NetworkGraph from './components/NetworkGraph';
import { DataService } from './services/dataService';
import { VASPData } from './types';

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

  if (isDataLoading) {
    return (
      <div className="min-h-screen bg-gray-50 duration-300 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mb-4"></div>
          <p className="text-secondary">Loading VASP data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 duration-300">
      <Header
        isDarkMode={isDarkMode}
        onToggleDarkMode={toggleDarkMode}
        searchQuery={searchQuery}
        onSearchChange={handleSearchChange}
        activeTab={activeTab}
        onTabChange={handleTabChange}
      />
      
      <main className="container py-8">
        {activeTab === 'dashboard' ? (
          <Dashboard searchQuery={searchQuery} />
        ) : (
          <NetworkGraph data={data} searchQuery={searchQuery} />
        )}
      </main>
      
      <footer className="footer">
        <div className="container py-6">
          <p className="text-center text-sm text-secondary">
            © 2024 Globe - Cryptocurrency Threat Analysis Platform. Built with React & TypeScript.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

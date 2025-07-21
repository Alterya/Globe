import React, { useState, useEffect, useMemo } from 'react';
import { Globe, Shield, Database, TrendingUp, Server, AlertTriangle } from 'lucide-react';
import { DataService } from '../services/dataService';
import { VASPData, DomainStats } from '../types';
import StatCard from './StatCard';
import ChartCard from './ChartCard';
import PieChartWidget from './PieChartWidget';
import BarChartWidget from './BarChartWidget';

interface DashboardProps {
  searchQuery: string;
}

const Dashboard: React.FC<DashboardProps> = ({ searchQuery }) => {
  const [data, setData] = useState<VASPData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const dataService = DataService.getInstance();

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        await dataService.loadData();
        setData(dataService.getData());
      } catch (err) {
        setError('Failed to load VASP data');
        console.error('Dashboard data loading error:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [dataService]);

  const filteredData = useMemo(() => {
    if (!searchQuery.trim()) return data;
    return dataService.searchDomains(searchQuery);
  }, [data, searchQuery, dataService]);

  const stats = useMemo(() => {
    if (filteredData.length === 0) return null;
    
    // Create a temporary service instance with filtered data for stats calculation
    const tempService = new (class extends DataService {
      constructor(private filteredData: VASPData[]) {
        super();
        this.setData(filteredData);
      }
      
      private setData(data: VASPData[]) {
        (this as any).data = data;
        (this as any).isLoaded = true;
      }
    })(filteredData);

    return tempService.getDomainStats();
  }, [filteredData]);

  const chainData = useMemo(() => {
    if (!stats) return [];
    return stats.chainDistribution;
  }, [stats]);

  const discoveryMethodData = useMemo(() => {
    if (!stats) return [];
    return stats.discoveryMethodDistribution;
  }, [stats]);

  const topDomains = useMemo(() => {
    if (filteredData.length === 0) return [];
    const tempService = new (class extends DataService {
      constructor(private filteredData: VASPData[]) {
        super();
        (this as any).data = filteredData;
        (this as any).isLoaded = true;
      }
    })(filteredData);
    return tempService.getTopDomains(8);
  }, [filteredData]);

  const topIPs = useMemo(() => {
    if (filteredData.length === 0) return [];
    const tempService = new (class extends DataService {
      constructor(private filteredData: VASPData[]) {
        super();
        (this as any).data = filteredData;
        (this as any).isLoaded = true;
      }
    })(filteredData);
    return tempService.getTopIPs(8);
  }, [filteredData]);

  const inreachData = useMemo(() => {
    if (!stats) return [];
    return stats.inreachAvailability;
  }, [stats]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-error">
        <AlertTriangle className="h-5 w-5 mr-2" />
        <span>{error}</span>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center py-12">
        <p className="text-muted">No data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {/* Search Results Info */}
      {searchQuery && (
        <div className="alert alert-info">
          <p>
            Showing {filteredData.length.toLocaleString()} results for "{searchQuery}"
          </p>
        </div>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2">
        <StatCard
          title="Total Records"
          value={stats.totalDomains}
          subtitle="VASP threat entries"
          icon={<Database className="h-6 w-6" />}
        />
        <StatCard
          title="Unique Domains"
          value={stats.uniqueSourceDomains}
          subtitle="Source domains identified"
          icon={<Globe className="h-6 w-6" />}
        />
        <StatCard
          title="Crypto Addresses"
          value={stats.totalCryptoAddresses}
          subtitle="Unique addresses tracked"
          icon={<Shield className="h-6 w-6" />}
        />
        <StatCard
          title="Lookalike IPs"
          value={stats.uniqueLookalikeIPs}
          subtitle="Suspicious IP addresses"
          icon={<Server className="h-6 w-6" />}
        />
      </div>

      {/* Charts Grid */}
      <div className="dashboard-charts-grid">
        <ChartCard 
          title="Blockchain Distribution" 
          subtitle="Distribution of cryptocurrency chains"
        >
          <PieChartWidget data={chainData} />
        </ChartCard>

        <ChartCard 
          title="Discovery Methods" 
          subtitle="How threats were discovered"
        >
          <PieChartWidget 
            data={discoveryMethodData}
            colors={['#10b981', '#f59e0b', '#ef4444', '#8b5cf6']}
          />
        </ChartCard>

        <ChartCard 
          title="Top Threat Domains" 
          subtitle="Most frequently appearing domains"
        >
          <BarChartWidget data={topDomains} color="#6366f1" />
        </ChartCard>

        <ChartCard 
          title="Top Source IPs" 
          subtitle="Most common IP addresses"
        >
          <BarChartWidget data={topIPs} color="#10b981" />
        </ChartCard>

        <ChartCard 
          title="Intelligence Availability" 
          subtitle="InReach intelligence coverage"
        >
          <PieChartWidget 
            data={inreachData}
            colors={['#10b981', '#ef4444', '#f59e0b']}
          />
        </ChartCard>

        <ChartCard 
          title="Threat Overview" 
          subtitle="Key security insights"
        >
          <div className="flex flex-col justify-center h-full space-y-4">
            <div className="gradient-red rounded-lg p-6">
              <div className="flex items-center">
                <AlertTriangle className="h-8 w-8 text-error mr-3" />
                <div>
                  <p className="text-lg font-semibold text-primary">
                    High Risk Domains
                  </p>
                  <p className="text-sm text-secondary">
                    Multiple lookalike patterns detected
                  </p>
                </div>
              </div>
            </div>
            <div className="gradient-yellow rounded-lg p-6">
              <div className="flex items-center">
                <TrendingUp className="h-8 w-8 text-warning mr-3" />
                <div>
                  <p className="text-lg font-semibold text-primary">
                    Active Monitoring
                  </p>
                  <p className="text-sm text-secondary">
                    Continuous threat intelligence
                  </p>
                </div>
              </div>
            </div>
          </div>
        </ChartCard>
      </div>
    </div>
  );
};

export default Dashboard; 
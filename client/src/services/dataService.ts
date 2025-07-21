import Papa from 'papaparse';
import { VASPData, ChartData, DomainStats } from '../types';

export class DataService {
  private static instance: DataService;
  private data: VASPData[] = [];
  private isLoaded: boolean = false;

  public static getInstance(): DataService {
    if (!DataService.instance) {
      DataService.instance = new DataService();
    }
    return DataService.instance;
  }

  async loadData(): Promise<VASPData[]> {
    if (this.isLoaded) {
      return this.data;
    }

    try {
      const response = await fetch('/Japan_VASP_data.csv');
      const csvText = await response.text();
      
      const result = Papa.parse<VASPData>(csvText, {
        header: true,
        skipEmptyLines: true,
        transformHeader: (header) => header.trim(),
      });

      this.data = result.data;
      this.isLoaded = true;
      return this.data;
    } catch (error) {
      console.error('Error loading CSV data:', error);
      return [];
    }
  }

  private countItems<T>(items: T[], keyFn: (item: T) => string): ChartData[] {
    const counts = new Map<string, number>();
    
    items.forEach(item => {
      const key = keyFn(item);
      if (key && key !== '') {
        counts.set(key, (counts.get(key) || 0) + 1);
      }
    });

    return Array.from(counts.entries())
      .map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value,
        count: value,
        percentage: Math.round((value / items.length) * 100)
      }))
      .sort((a, b) => b.value - a.value);
  }

  getChainDistribution(): ChartData[] {
    return this.countItems(this.data, item => item.chain);
  }

  getDiscoveryMethodDistribution(): ChartData[] {
    return this.countItems(this.data, item => item.discovery_method);
  }

  getInreachAvailability(): ChartData[] {
    return this.countItems(this.data, item => item.inreach_intel_available);
  }

  getTopDomains(limit: number = 10): ChartData[] {
    return this.countItems(this.data, item => item.source_domain).slice(0, limit);
  }

  getTopIPs(limit: number = 10): ChartData[] {
    return this.countItems(
      this.data.filter(item => item.source_domain_ip !== 'UNRESOLVED'), 
      item => item.source_domain_ip
    ).slice(0, limit);
  }

  getDomainStats(): DomainStats {
    const uniqueSourceDomains = new Set(this.data.map(item => item.source_domain)).size;
    const uniqueLookalikeIPs = new Set(
      this.data
        .filter(item => item.lookalike_domain_ip !== 'UNRESOLVED')
        .map(item => item.lookalike_domain_ip)
    ).size;
    const totalCryptoAddresses = new Set(this.data.map(item => item.crypto_address)).size;

    return {
      totalDomains: this.data.length,
      uniqueSourceDomains,
      uniqueLookalikeIPs,
      totalCryptoAddresses,
      chainDistribution: this.getChainDistribution(),
      discoveryMethodDistribution: this.getDiscoveryMethodDistribution(),
      inreachAvailability: this.getInreachAvailability(),
    };
  }

  searchDomains(query: string): VASPData[] {
    const lowerQuery = query.toLowerCase();
    return this.data.filter(item => 
      item.source_domain.toLowerCase().includes(lowerQuery) ||
      item.lookalike_domain.toLowerCase().includes(lowerQuery) ||
      item.crypto_address.toLowerCase().includes(lowerQuery)
    );
  }

  getData(): VASPData[] {
    return this.data;
  }
} 
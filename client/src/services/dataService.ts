import Papa from 'papaparse';
import { VASPData, ChartData, DomainStats } from '../types';

export class DataService {
  private static instance: DataService;
  private data: VASPData[] = [];
  private isLoaded: boolean = false;
  private currentFileName: string = '';

  public static getInstance(): DataService {
    if (!DataService.instance) {
      DataService.instance = new DataService();
    }
    return DataService.instance;
  }

  async loadDataFromFile(file: File): Promise<VASPData[]> {
    try {
      const csvText = await this.readFileAsText(file);
      this.currentFileName = file.name;
      
      const result = Papa.parse<VASPData>(csvText, {
        header: true,
        skipEmptyLines: true,
        transformHeader: (header) => header.trim(),
      });

      if (result.errors.length > 0) {
        console.warn('CSV parsing warnings:', result.errors);
      }

      this.data = result.data.filter(item => item && Object.keys(item).length > 0);
      this.isLoaded = true;

      // Store data in localStorage for persistence
      this.saveToLocalStorage(csvText, file.name);
      
      return this.data;
    } catch (error) {
      console.error('Error loading CSV from file:', error);
      throw new Error('Failed to parse CSV file. Please check the file format.');
    }
  }

  async loadDataFromText(csvText: string, fileName: string = 'uploaded.csv'): Promise<VASPData[]> {
    try {
      this.currentFileName = fileName;
      
      const result = Papa.parse<VASPData>(csvText, {
        header: true,
        skipEmptyLines: true,
        transformHeader: (header) => header.trim(),
      });

      if (result.errors.length > 0) {
        console.warn('CSV parsing warnings:', result.errors);
      }

      this.data = result.data.filter(item => item && Object.keys(item).length > 0);
      this.isLoaded = true;

      // Store data in localStorage for persistence
      this.saveToLocalStorage(csvText, fileName);
      
      return this.data;
    } catch (error) {
      console.error('Error loading CSV from text:', error);
      throw new Error('Failed to parse CSV data. Please check the format.');
    }
  }

  async loadFromLocalStorage(): Promise<VASPData[]> {
    try {
      const storedData = localStorage.getItem('vasp_csv_data');
      const storedFileName = localStorage.getItem('vasp_csv_filename');
      
      if (storedData && storedFileName) {
        await this.loadDataFromText(storedData, storedFileName);
        return this.data;
      }
      
      return [];
    } catch (error) {
      console.error('Error loading from localStorage:', error);
      this.clearLocalStorage();
      return [];
    }
  }

  // Load data only from localStorage - no hardcoded CSV fallback
  async loadData(): Promise<VASPData[]> {
    if (this.isLoaded) {
      return this.data;
    }

    // Only load from localStorage - user must upload their own CSV
    const localData = await this.loadFromLocalStorage();
    return localData; // Returns empty array if no data found
  }

  private readFileAsText(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result;
        if (typeof result === 'string') {
          resolve(result);
        } else {
          reject(new Error('Failed to read file as text'));
        }
      };
      reader.onerror = () => reject(new Error('Error reading file'));
      reader.readAsText(file);
    });
  }

  private saveToLocalStorage(csvText: string, fileName: string): void {
    try {
      localStorage.setItem('vasp_csv_data', csvText);
      localStorage.setItem('vasp_csv_filename', fileName);
      localStorage.setItem('vasp_csv_timestamp', new Date().toISOString());
    } catch (error) {
      console.warn('Failed to save data to localStorage:', error);
    }
  }

  clearLocalStorage(): void {
    localStorage.removeItem('vasp_csv_data');
    localStorage.removeItem('vasp_csv_filename');
    localStorage.removeItem('vasp_csv_timestamp');
  }

  clearData(): void {
    this.data = [];
    this.isLoaded = false;
    this.currentFileName = '';
    this.clearLocalStorage();
  }

  hasData(): boolean {
    return this.isLoaded && this.data.length > 0;
  }

  getCurrentFileName(): string {
    return this.currentFileName;
  }

  getDataStats(): { records: number; fileName: string; uploadDate?: string } {
    const uploadDate = localStorage.getItem('vasp_csv_timestamp');
    return {
      records: this.data.length,
      fileName: this.currentFileName,
      uploadDate: uploadDate ? new Date(uploadDate).toLocaleDateString() : undefined
    };
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
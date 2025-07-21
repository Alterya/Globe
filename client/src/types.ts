export interface VASPData {
  source_domain: string;
  lookalike_domain: string;
  same_ip_domain: string;
  screenshot: string;
  crypto_address: string;
  chain: 'eth' | 'btc' | 'tron' | string;
  discovery_method: 'lookalike_source' | 'lookalike_target' | string;
  source_domain_ip: string;
  lookalike_domain_ip: string;
  same_ip_domain_ip: string;
  inreach_checked: 'Yes' | 'No';
  inreach_intel_available: 'Yes' | 'No';
  inreach_intel_summary: string;
}

export interface ChartData {
  name: string;
  value: number;
  count?: number;
  percentage?: number;
}

export interface TrendData {
  date: string;
  count: number;
  eth: number;
  btc: number;
  tron: number;
}

export interface DomainStats {
  totalDomains: number;
  uniqueSourceDomains: number;
  uniqueLookalikeIPs: number;
  totalCryptoAddresses: number;
  chainDistribution: ChartData[];
  discoveryMethodDistribution: ChartData[];
  inreachAvailability: ChartData[];
} 
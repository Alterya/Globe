import { VASPData } from '../types';

interface AIAnalysisResult {
  filteredData: VASPData[];
  insights: string[];
  explanation: string;
  suggestions: string[];
  confidence: number;
  hideEdges?: boolean;
  aggregateBy?: string;
}

export class AIService {
  private static instance: AIService;
  private apiKey: string | null = null;
  private baseUrl = 'https://api.openai.com/v1/chat/completions';

  public static getInstance(): AIService {
    if (!AIService.instance) {
      AIService.instance = new AIService();
    }
    return AIService.instance;
  }

  constructor() {
    const apiKey = process.env.REACT_APP_OPENAI_API_KEY;
    if (apiKey) {
      this.apiKey = apiKey;
    }
  }

  setApiKey(key: string): void {
    this.apiKey = key;
  }

  hasApiKey(): boolean {
    return !!this.apiKey;
  }

  async analyzeQuery(query: string, data: VASPData[]): Promise<AIAnalysisResult> {
    if (!this.hasApiKey() || data.length === 0) {
      return this.fallbackAnalysis(query, data);
    }

    try {
      const dataSummary = this.createDataSummary(data);
      const prompt = this.createAnalysisPrompt(query, dataSummary);

      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`,
        },
        body: JSON.stringify({
          model: 'gpt-4',
          messages: [
            {
              role: 'system',
              content: 'You are an expert cybersecurity analyst specializing in VASP (Virtual Asset Service Provider) threat intelligence. Respond only with valid JSON.'
            },
            {
              role: 'user',
              content: prompt
            }
          ],
          max_tokens: 1000,
          temperature: 0.1,
        }),
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const result = await response.json();
      const aiResponse = JSON.parse(result.choices[0].message.content);
      
      return this.parseAIResponse(aiResponse, data, query);
    } catch (error) {
      console.error('AI analysis failed:', error);
      return this.fallbackAnalysis(query, data);
    }
  }

  private createDataSummary(data: VASPData[]): string {
    const chains = Array.from(new Set(data.map(item => item.chain))).slice(0, 10);
    const domains = Array.from(new Set(data.map(item => item.source_domain))).slice(0, 10);
    const totalRecords = data.length;

    return `Dataset: ${totalRecords} VASP records
Blockchains: ${chains.join(', ')}
Top domains: ${domains.join(', ')}
Discovery methods: ${Array.from(new Set(data.map(item => item.discovery_method))).join(', ')}`;
  }

  private createAnalysisPrompt(query: string, dataSummary: string): string {
    return `Analyze this cybersecurity query for VASP threat intelligence data:

QUERY: "${query}"

DATA CONTEXT:
${dataSummary}

IMPORTANT: Understand these specific filtering commands:
- "filter bitcoin" or "show bitcoin" = ONLY bitcoin/btc chain data
- "remove bitcoin" or "exclude bitcoin" = EVERYTHING EXCEPT bitcoin
- "filter ethereum" = ONLY ethereum/eth chain data  
- "remove edges" = return data but mark to hide connections
- "aggregate by domain" = group by domain names
- "high connectivity" = domains appearing multiple times
- "isolated nodes" = domains appearing only once

Respond with EXACT JSON format:
{
  "filterCriteria": {
    "chains": ["btc"], // EXACT chains to include, null = all
    "excludeChains": ["eth"], // chains to exclude, null = none
    "discoveryMethods": null, // or ["lookalike_source", "lookalike_target"]
    "intelAvailable": null, // "Yes", "No", or null
    "ipResolved": null, // true, false, or null  
    "connectivity": null, // "high", "low", or null
    "aggregateBy": null, // "domain", "ip", "chain" or null
    "hideEdges": false, // true to remove connections
    "textSearch": null // search term or null
  },
  "insights": [
    "🔗 Filtered for Bitcoin blockchain only",
    "📊 Showing X nodes after filtering"
  ],
  "explanation": "Applied filter to show only Bitcoin addresses and their connections",
  "confidence": 0.9
}

Examples:
- "show bitcoin addresses" → chains: ["btc"]
- "remove bitcoin addresses" → excludeChains: ["btc"] 
- "remove all edges" → hideEdges: true
- "aggregate by domain" → aggregateBy: "domain"

Respond ONLY with valid JSON.`;
  }

  private parseAIResponse(aiResponse: any, data: VASPData[], query: string): AIAnalysisResult {
    try {
      const criteria = aiResponse.filterCriteria || {};
      const filteredData = this.applyAIFilters(data, criteria);
      
      return {
        filteredData,
        insights: aiResponse.insights || [],
        explanation: aiResponse.explanation || 'Applied AI-powered filtering',
        suggestions: this.getSuggestions(query, filteredData),
        confidence: aiResponse.confidence || 0.8,
        hideEdges: criteria.hideEdges || false,
        aggregateBy: criteria.aggregateBy || undefined
      };
    } catch (error) {
      console.error('Failed to parse AI response:', error);
      return this.fallbackAnalysis(query, data);
    }
  }

  private applyAIFilters(data: VASPData[], criteria: any): VASPData[] {
    let filteredData = data.filter(item => {
      // Filter by specific chains
      if (criteria.chains && criteria.chains.length > 0) {
        const hasMatchingChain = criteria.chains.some((chain: string) => 
          item.chain.toLowerCase().includes(chain.toLowerCase()));
        if (!hasMatchingChain) return false;
      }

      // Exclude specific chains
      if (criteria.excludeChains && criteria.excludeChains.length > 0) {
        const hasExcludedChain = criteria.excludeChains.some((chain: string) => 
          item.chain.toLowerCase().includes(chain.toLowerCase()));
        if (hasExcludedChain) return false;
      }

      // Filter by discovery method
      if (criteria.discoveryMethods && criteria.discoveryMethods.length > 0) {
        if (!criteria.discoveryMethods.includes(item.discovery_method)) return false;
      }

      // Filter by intel availability
      if (criteria.intelAvailable !== null) {
        if (item.inreach_intel_available !== criteria.intelAvailable) return false;
      }

      // Filter by IP resolution
      if (criteria.ipResolved !== null) {
        const hasValidIP = item.source_domain_ip && item.source_domain_ip !== 'N/A';
        if (criteria.ipResolved !== hasValidIP) return false;
      }

      // Text search
      if (criteria.textSearch) {
        const searchTerm = criteria.textSearch.toLowerCase();
        const searchableFields = [
          item.source_domain,
          item.crypto_address,
          item.source_domain_ip,
          item.chain
        ].join(' ').toLowerCase();
        
        if (!searchableFields.includes(searchTerm)) return false;
      }

      return true;
    });

    // Handle connectivity filtering
    if (criteria.connectivity) {
      const domainCounts = new Map<string, number>();
      data.forEach(item => {
        const count = domainCounts.get(item.source_domain) || 0;
        domainCounts.set(item.source_domain, count + 1);
      });

      if (criteria.connectivity === 'high') {
        filteredData = filteredData.filter(item => (domainCounts.get(item.source_domain) || 0) > 1);
      } else if (criteria.connectivity === 'low') {
        filteredData = filteredData.filter(item => (domainCounts.get(item.source_domain) || 0) === 1);
      }
    }

    // Handle aggregation
    if (criteria.aggregateBy) {
      const aggregated = new Map<string, VASPData[]>();
      
      filteredData.forEach(item => {
        let key: string;
        switch (criteria.aggregateBy) {
          case 'domain':
            key = item.source_domain;
            break;
          case 'ip':
            key = item.source_domain_ip || 'Unknown IP';
            break;
          case 'chain':
            key = item.chain;
            break;
          default:
            key = item.source_domain;
        }
        
        if (!aggregated.has(key)) {
          aggregated.set(key, []);
        }
        aggregated.get(key)!.push(item);
      });

      // Return representative items with aggregation metadata
      filteredData = Array.from(aggregated.entries()).map(([key, items]) => {
        const representative = items[0];
        (representative as any).aggregated = {
          count: items.length,
          key: key,
          type: criteria.aggregateBy
        };
        return representative;
      });
    }

    return filteredData;
  }

  private fallbackAnalysis(query: string, data: VASPData[]): AIAnalysisResult {
    const queryLower = query.toLowerCase();
    let filteredData = data;
    let hideEdges = false;
    let aggregateBy: string | undefined;
    let insights: string[] = [];
    let explanation = '';

    // Handle specific filtering commands (filter/remove bitcoin/ethereum)
    if (queryLower.includes('filter bitcoin') || queryLower.includes('show bitcoin')) {
      filteredData = filteredData.filter(item => item.chain.toLowerCase().includes('btc'));
      insights.push('🔗 Showing only Bitcoin addresses');
      explanation = 'Filtered for Bitcoin blockchain only';
    } else if (queryLower.includes('remove bitcoin') || queryLower.includes('exclude bitcoin')) {
      filteredData = filteredData.filter(item => !item.chain.toLowerCase().includes('btc'));
      insights.push('🚫 Excluded Bitcoin addresses');
      explanation = 'Filtered out Bitcoin blockchain data';
    } else if (queryLower.includes('filter ethereum') || queryLower.includes('show ethereum')) {
      filteredData = filteredData.filter(item => item.chain.toLowerCase().includes('eth'));
      insights.push('🔗 Showing only Ethereum addresses');
      explanation = 'Filtered for Ethereum blockchain only';
    } else if (queryLower.includes('remove ethereum') || queryLower.includes('exclude ethereum')) {
      filteredData = filteredData.filter(item => !item.chain.toLowerCase().includes('eth'));
      insights.push('🚫 Excluded Ethereum addresses');
      explanation = 'Filtered out Ethereum blockchain data';
    }

    // Handle edge removal
    if (queryLower.includes('remove edges') || queryLower.includes('hide edges') || queryLower.includes('no connections')) {
      hideEdges = true;
      insights.push('🔗 All connections hidden');
      explanation = explanation ? explanation + ' with connections removed' : 'Removed all connections between nodes';
    }

    // Handle aggregation
    if (queryLower.includes('aggregate by domain') || queryLower.includes('group by domain')) {
      aggregateBy = 'domain';
      insights.push('📊 Aggregated by domain names');
      explanation = explanation ? explanation + ' and grouped by domains' : 'Grouped data by domain names';
    } else if (queryLower.includes('aggregate by ip') || queryLower.includes('group by ip')) {
      aggregateBy = 'ip';
      insights.push('📊 Aggregated by IP addresses');
      explanation = explanation ? explanation + ' and grouped by IPs' : 'Grouped data by IP addresses';
    } else if (queryLower.includes('aggregate by chain') || queryLower.includes('group by chain')) {
      aggregateBy = 'chain';
      insights.push('📊 Aggregated by blockchain');
      explanation = explanation ? explanation + ' and grouped by chains' : 'Grouped data by blockchain type';
    }

    // Handle connectivity queries (isolated nodes)
    if (queryLower.includes('isolated') || queryLower.includes('single')) {
      const domainCounts = new Map<string, number>();
      data.forEach(item => {
        const count = domainCounts.get(item.source_domain) || 0;
        domainCounts.set(item.source_domain, count + 1);
      });
      filteredData = filteredData.filter(item => domainCounts.get(item.source_domain) === 1);
      insights.push('🔍 Showing isolated nodes only');
      explanation = 'Filtered for domains with single connections (isolated nodes)';
    }

    if (!explanation) {
      explanation = 'Applied text-based filtering';
    }

    return {
      filteredData,
      insights,
      explanation,
      suggestions: [],
      confidence: 0.8,
      hideEdges,
      aggregateBy
    };
  }

  private getSuggestions(query: string, data: VASPData[]): string[] {
    const suggestions = [];
    const uniqueChains = Array.from(new Set(data.map(item => item.chain)));
    
    if (uniqueChains.length > 1) {
      suggestions.push(`Try filtering by blockchain: ${uniqueChains.join(', ')}`);
    }
    
    if (data.length > 50) {
      suggestions.push('Consider aggregating by domain or IP to simplify the view');
    }
    
    suggestions.push('Use "remove edges" to focus on node data only');
    
    return suggestions.slice(0, 3);
  }
} 
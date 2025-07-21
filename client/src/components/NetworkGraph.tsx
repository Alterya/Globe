import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import * as d3 from 'd3';
import { Filter, RefreshCw, Globe, Server, Coins, Brain, MessageSquare, TrendingUp, Zap, AlertCircle, ExternalLink } from 'lucide-react';
import { VASPData } from '../types';
import { AIService } from '../services/aiService';

interface NetworkGraphProps {
  data: VASPData[];
  searchQuery: string;
}

interface NetworkNode extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  group: 'domain' | 'ip' | 'address';
  title: string;
  value: number;
}

interface NetworkLink extends d3.SimulationLinkDatum<NetworkNode> {
  source: string;
  target: string;
  label?: string;
  title: string;
}

const NetworkGraph: React.FC<NetworkGraphProps> = ({ data, searchQuery }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'domains' | 'ips' | 'addresses'>('all');
  const [isLoading, setIsLoading] = useState(false);
  const [windowSize, setWindowSize] = useState({ width: window.innerWidth, height: window.innerHeight });
  
  // AI RAG states
  const [ragQuery, setRagQuery] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [aiFilteredData, setAiFilteredData] = useState<VASPData[]>([]);
  const [aiExplanation, setAiExplanation] = useState('');
  const [aiInsights, setAiInsights] = useState<string[]>([]);
  const [aiError, setAiError] = useState<string | null>(null);
  const [aiConfidence, setAiConfidence] = useState(0);
  const [hideEdges, setHideEdges] = useState(false);
  const [aggregateBy, setAggregateBy] = useState<string | undefined>();
  
  const aiService = useMemo(() => AIService.getInstance(), []);

  const processNetworkData = useMemo(() => {
    const nodesMap = new Map<string, NetworkNode>();
    const links: NetworkLink[] = [];
    const linkSet = new Set<string>();

    // Use AI filtered data if available, otherwise use regular filtered data
    let baseData = aiFilteredData.length > 0 ? aiFilteredData : data;
    
    const filteredData = searchQuery 
      ? baseData.filter(item => 
          item.source_domain.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.crypto_address.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.source_domain_ip.toLowerCase().includes(searchQuery.toLowerCase())
        )
      : baseData;

    // Process each VASP record
    filteredData.forEach(item => {
      if (!item.source_domain || !item.crypto_address) return;

      const domainId = `domain_${item.source_domain}`;
      const addressId = `address_${item.crypto_address}`;
      const ipId = `ip_${item.source_domain_ip}`;

      // Add domain node
      if (!nodesMap.has(domainId)) {
        nodesMap.set(domainId, {
          id: domainId,
          label: item.source_domain.length > 20 ? `${item.source_domain.substring(0, 20)}...` : item.source_domain,
          group: 'domain',
          title: `Domain: ${item.source_domain}\nType: ${item.discovery_method}`,
          value: 1
        });
      } else {
        const node = nodesMap.get(domainId)!;
        node.value += 1;
      }

      // Add crypto address node
      if (!nodesMap.has(addressId)) {
        nodesMap.set(addressId, {
          id: addressId,
          label: `${item.crypto_address.substring(0, 12)}...`,
          group: 'address',
          title: `Address: ${item.crypto_address}\nChain: ${item.chain.toUpperCase()}`,
          value: 1
        });
      }

      // Add IP node if available and not UNRESOLVED
      if (item.source_domain_ip && item.source_domain_ip !== 'UNRESOLVED') {
        if (!nodesMap.has(ipId)) {
          nodesMap.set(ipId, {
            id: ipId,
            label: item.source_domain_ip,
            group: 'ip',
            title: `IP Address: ${item.source_domain_ip}`,
            value: 1
          });
        } else {
          const node = nodesMap.get(ipId)!;
          node.value += 1;
        }

        // Create link between domain and IP
        const domainIpLink = `${domainId}_${ipId}`;
        if (!linkSet.has(domainIpLink)) {
          links.push({
            source: domainId,
            target: ipId,
            title: 'Domain hosted on IP',
            label: 'hosts'
          });
          linkSet.add(domainIpLink);
        }
      }

      // Create link between domain and address
      const domainAddressLink = `${domainId}_${addressId}`;
      if (!linkSet.has(domainAddressLink)) {
        links.push({
          source: domainId,
          target: addressId,
          title: `Domain uses ${item.chain} address`,
          label: item.chain
        });
        linkSet.add(domainAddressLink);
      }
    });

    // Filter nodes based on selected filter
    const filteredNodes = Array.from(nodesMap.values()).filter(node => {
      if (selectedFilter === 'all') return true;
      if (selectedFilter === 'domains') return node.group === 'domain';
      if (selectedFilter === 'ips') return node.group === 'ip';
      if (selectedFilter === 'addresses') return node.group === 'address';
      return true;
    });

    const nodeIds = new Set(filteredNodes.map(n => n.id));
    let filteredLinks = links.filter(link => 
      nodeIds.has(link.source as string) && nodeIds.has(link.target as string)
    );

    // Hide edges if requested by AI
    if (hideEdges) {
      filteredLinks = [];
    }

    return {
      nodes: filteredNodes,
      links: filteredLinks
    };
  }, [data, searchQuery, selectedFilter, aiFilteredData, hideEdges]);

  // AI Analysis function with debouncing
  const analyzeWithAI = useCallback(async (query: string) => {
    if (!query.trim()) {
      setAiFilteredData([]);
      setAiExplanation('');
      setAiInsights([]);
      setAiError(null);
      setAiConfidence(0);
      setHideEdges(false);
      setAggregateBy(undefined);
      return;
    }

    setIsAnalyzing(true);
    setAiError(null);

    try {
      const result = await aiService.analyzeQuery(query, data);
      setAiFilteredData(result.filteredData);
      setAiExplanation(result.explanation);
      setAiInsights(result.insights);
      setAiConfidence(result.confidence);
      setHideEdges(result.hideEdges || false);
      setAggregateBy(result.aggregateBy);
    } catch (error) {
      setAiError('Failed to analyze query. Please try again.');
      console.error('AI analysis error:', error);
    } finally {
      setIsAnalyzing(false);
    }
  }, [aiService, data]);

  // Debounced AI analysis
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (ragQuery) {
        analyzeWithAI(ragQuery);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [ragQuery, analyzeWithAI]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      setWindowSize({ width: window.innerWidth, height: window.innerHeight });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (!svgRef.current || processNetworkData.nodes.length === 0) return;

    setIsLoading(true);

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous content

    // Calculate responsive dimensions based on available space
    const availableWidth = windowSize.width - 320 - 80; // Subtract sidebar width (320) + gaps/padding (80)
    const availableHeight = windowSize.height - 200; // Subtract header + footer + padding (200)
    
    const width = Math.max(600, Math.min(availableWidth, 1200)); // Min 600, max 1200
    const height = Math.max(400, Math.min(availableHeight, 700)); // Min 400, max 700
    const margin = 20;

    svg.attr('width', width).attr('height', height);

    const container = svg.append('g');

    // Create zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Color scale for different node types
    const colorScale = {
      domain: '#6366f1',
      ip: '#10b981',
      address: '#f59e0b'
    };

    // Create force simulation with fast, stable positioning
    const simulation = d3.forceSimulation<NetworkNode>(processNetworkData.nodes)
      .force('link', d3.forceLink<NetworkNode, NetworkLink>(processNetworkData.links)
        .id(d => d.id)
        .distance(100)
        .strength(0.7))
      .force('charge', d3.forceManyBody().strength(-300).distanceMin(15).distanceMax(300))
      .force('center', d3.forceCenter(width / 2, height / 2).strength(0.3))
      .force('collision', d3.forceCollide().radius(30).strength(0.9))
      .alphaDecay(0.02) // Faster convergence
      .velocityDecay(0.4) // High friction for stability
      .alpha(0.8) // Higher initial energy for faster settling
      .stop(); // Start stopped to pre-calculate positions

    // Pre-run simulation to get stable positions before showing nodes
    for (let i = 0; i < 100; i++) {
      simulation.tick();
    }
    
    // Now restart with lower energy for final settling
    simulation.alpha(0.1).restart();

    // Create links with fast, smooth entrance
    const linkContainer = container.append('g').attr('class', 'links');
    const link = linkContainer
      .selectAll('line')
      .data(processNetworkData.links)
      .join('line')
      .attr('stroke', 'var(--border-color)')
      .attr('stroke-opacity', 0) // Start invisible
      .attr('stroke-width', 2);
    
    // Links appear with nodes simultaneously
    link.transition()
      .duration(300)
      .ease(d3.easeCubicOut)
      .delay(0) // Same time as nodes
      .attr('stroke-opacity', 0.6);

    // Create link labels
    const linkLabel = container.append('g')
      .attr('class', 'link-labels')
      .selectAll('text')
      .data(processNetworkData.links)
      .join('text')
      .attr('font-size', '10px')
      .attr('fill', 'var(--text-secondary)')
      .attr('text-anchor', 'middle')
      .text(d => d.label || '');

    // Create nodes
    const node = container.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(processNetworkData.nodes)
      .join('g')
      .attr('class', 'node')
      .call(d3.drag<any, NetworkNode>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.1).restart(); // Minimal restart
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) {
            // Quick settling
            simulation.alphaTarget(0.05);
            setTimeout(() => simulation.alphaTarget(0), 100);
          }
          d.fx = null;
          d.fy = null;
        }));

    // Add circles to nodes with fast, controlled entrance
    const circles = node.append('circle')
      .attr('r', d => Math.max(8, Math.min(20, 5 + d.value * 2))) // Start at final size
      .attr('fill', d => colorScale[d.group])
      .attr('stroke', d => d3.color(colorScale[d.group])?.darker(0.5)?.toString() || '#000')
      .attr('stroke-width', 2)
      .attr('opacity', 0) // Start invisible
      .style('transform', 'scale(0.8)');

    // All nodes appear together instantly
    circles.transition()
      .duration(300)
      .ease(d3.easeCubicOut)
      .delay(0) // No stagger - all together
      .attr('opacity', 1)
      .style('transform', 'scale(1)');

    // Add labels to nodes with fast entrance
    const labels = node.append('text')
      .attr('dy', '.35em')
      .attr('x', d => Math.max(8, Math.min(20, 5 + d.value * 2)) + 5)
      .attr('font-size', '12px')
      .attr('fill', 'var(--text-primary)')
      .attr('opacity', 0) // Start invisible
      .text(d => d.label);

    // Labels appear with everything else
    labels.transition()
      .duration(300)
      .ease(d3.easeCubicOut)
      .delay(0) // Same time as nodes and links
      .attr('opacity', 1);

    // Add tooltips
    const tooltip = d3.select('body').append('div')
      .attr('class', 'tooltip')
      .style('opacity', 0)
      .style('position', 'absolute')
      .style('background', 'var(--surface-bg)')
      .style('border', '1px solid var(--border-color)')
      .style('border-radius', '8px')
      .style('padding', '12px')
      .style('font-size', '12px')
      .style('box-shadow', 'var(--shadow-lg)')
      .style('pointer-events', 'auto')
      .style('z-index', '1000')
      .style('max-width', '280px');

    const createTooltipContent = (d: NetworkNode) => {
      if (d.group === 'domain') {
        // Extract clean domain name (remove any aggregation prefixes)
        const domainName = d.label.replace(/^(domain_|aggregated_)/, '');
        const alteryaUrl = `https://alterya_rnd.alterya.io/explorer/domain/${domainName}`;
        
        // Check if this is an aggregated node
        const isAggregated = (d as any).aggregated;
        
        return `
          <div style="color: var(--text-primary); line-height: 1.4;">
            <div style="font-weight: 600; margin-bottom: 8px; color: var(--accent-color); display: flex; align-items: center; gap: 6px;">
              🌐 ${domainName}
              ${isAggregated ? `<span style="background: rgba(99, 102, 241, 0.1); color: var(--accent-color); padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 500;">${isAggregated.count} nodes</span>` : ''}
            </div>
            <div style="margin-bottom: 10px; font-size: 11px; color: var(--text-secondary);">
              ${d.title}${isAggregated ? `<br><small style="color: var(--accent-color);">Aggregated ${isAggregated.type}</small>` : ''}
            </div>
            <button 
              onclick="window.open('${alteryaUrl}', '_blank')"
              style="
                background: linear-gradient(135deg, var(--accent-color), #8b5cf6);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: 500;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 6px;
                transition: all 0.2s ease;
                width: 100%;
                justify-content: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
              "
              onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(99, 102, 241, 0.3)'"
              onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)'"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m18 13 6-6-6-6"/>
                <path d="M7 7h7v7"/>
                <path d="m7 17 10-10"/>
              </svg>
              View in Alterya Platform
            </button>
          </div>
        `;
      } else {
        // For non-domain nodes, show basic tooltip
        const nodeType = d.group === 'ip' ? '🖥️' : '₿';
        return `
          <div style="color: var(--text-primary); line-height: 1.4;">
            <div style="font-weight: 600; margin-bottom: 6px; color: var(--text-secondary);">
              ${nodeType} ${d.label}
            </div>
            <div style="font-size: 11px; color: var(--text-secondary);">
              ${d.title}
            </div>
          </div>
        `;
      }
    };

    let tooltipTimeout: NodeJS.Timeout | null = null;

    const showTooltip = (event: MouseEvent, d: NetworkNode) => {
      if (tooltipTimeout) {
        clearTimeout(tooltipTimeout);
        tooltipTimeout = null;
      }
      
      tooltip.transition()
        .duration(200)
        .style('opacity', .9);
      tooltip.html(createTooltipContent(d))
        .style('left', (event.pageX + 15) + 'px')
        .style('top', (event.pageY - 10) + 'px');
    };

    const hideTooltip = () => {
      tooltipTimeout = setTimeout(() => {
        tooltip.transition()
          .duration(300)
          .style('opacity', 0);
      }, 100);
    };

    const keepTooltipVisible = () => {
      if (tooltipTimeout) {
        clearTimeout(tooltipTimeout);
        tooltipTimeout = null;
      }
    };

    // Add event listeners to tooltip itself
    tooltip
      .on('mouseenter', keepTooltipVisible)
      .on('mouseleave', hideTooltip);

    node.on('mouseover', showTooltip)
      .on('mouseout', hideTooltip);

    // Update positions on simulation tick with optimized performance
    simulation.on('tick', () => {
      // Direct attribute updates for better performance during simulation
      link
        .attr('x1', d => (d.source as any).x || 0)
        .attr('y1', d => (d.source as any).y || 0)
        .attr('x2', d => (d.target as any).x || 0)
        .attr('y2', d => (d.target as any).y || 0);

      linkLabel
        .attr('x', d => ((d.source as any).x + (d.target as any).x) / 2)
        .attr('y', d => ((d.source as any).y + (d.target as any).y) / 2);

      node
        .attr('transform', d => `translate(${d.x || 0},${d.y || 0})`);
    });

    // Fast loading state transition
    simulation.on('end', () => {
      // Quick transition since animations are now faster
      setTimeout(() => {
        setIsLoading(false);
      }, 50);
    });

    return () => {
      simulation.stop();
      tooltip.remove();
    };
  }, [processNetworkData, windowSize]);

  const refreshNetwork = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current);
      const zoom = d3.zoom<SVGSVGElement, unknown>();
      svg.transition().duration(750).call(
        zoom.transform,
        d3.zoomIdentity
      );
    }
  };

    return (
    <div className="flex gap-6">
      {/* Left Sidebar with AI Interface */}
      <div className="w-80 space-y-4 h-fit">
        {/* AI RAG Interface */}
        <div className="ai-control-card">
          <div className="ai-header">
            <div className="ai-icon">
              <Brain className="h-4 w-4" />
            </div>
            <div className="ai-title-section">
              <h3 className="ai-title">AI Assistant</h3>
              <p className="ai-subtitle">Natural language graph control</p>
            </div>
          </div>
          
          <div className="ai-input-container">
            <div className="ai-input-icon">
              {isAnalyzing ? (
                <div className="ai-spinner" />
              ) : (
                <MessageSquare className="h-4 w-4" />
              )}
            </div>
            <textarea
              placeholder="Try: 'filter bitcoin addresses' • 'remove ethereum' • 'hide all edges' • 'aggregate by domain'"
              value={ragQuery}
              onChange={(e) => setRagQuery(e.target.value)}
              className="ai-textarea"
              rows={2}
            />
            {ragQuery && (
              <button
                onClick={() => {
                  setRagQuery('');
                  setAiFilteredData([]);
                  setAiExplanation('');
                  setAiInsights([]);
                  setAiError(null);
                  setAiConfidence(0);
                  setHideEdges(false);
                  setAggregateBy(undefined);
                }}
                className="ai-clear-button"
                title="Clear and reset"
              >
                ✕
              </button>
            )}
          </div>

          {/* AI Status */}
          {isAnalyzing && (
            <div className="ai-status-card" style={{ background: 'rgba(99, 102, 241, 0.06)', borderColor: 'rgba(99, 102, 241, 0.2)' }}>
              <div className="flex items-center space-x-2">
                <div className="ai-spinner" style={{ width: '12px', height: '12px' }} />
                <span className="text-xs" style={{ color: 'rgba(99, 102, 241, 0.9)' }}>Analyzing...</span>
              </div>
            </div>
          )}

          {/* AI Error */}
          {aiError && (
            <div className="ai-status-card" style={{ background: 'rgba(239, 68, 68, 0.06)', borderColor: 'rgba(239, 68, 68, 0.2)' }}>
              <div className="flex items-center space-x-2 text-xs" style={{ color: 'rgba(239, 68, 68, 0.9)' }}>
                <AlertCircle className="h-3 w-3" />
                <span>{aiError}</span>
              </div>
            </div>
          )}

          {/* AI Results */}
          {aiExplanation && (
            <div className="ai-results-card">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-4 w-4" style={{ color: 'rgba(99, 102, 241, 0.8)' }} />
                  <span className="text-sm font-medium" style={{ color: 'rgba(99, 102, 241, 0.9)' }}>Graph Updated</span>
                </div>
                {aiConfidence > 0 && (
                  <span className="ai-status-tag" style={{ background: 'rgba(99, 102, 241, 0.15)' }}>
                    {Math.round(aiConfidence * 100)}%
                  </span>
                )}
              </div>
              <p className="text-xs text-secondary mb-3" style={{ lineHeight: '1.4' }}>{aiExplanation}</p>
              
              {/* Live Stats */}
              <div className="ai-stat-grid">
                <div className="ai-stat-item">
                  <span className="text-muted">Nodes</span>
                  <span className="text-primary font-semibold">{processNetworkData.nodes.length}</span>
                </div>
                <div className="ai-stat-item">
                  <span className="text-muted">Edges</span>
                  <span className="text-primary font-semibold">{processNetworkData.links.length}</span>
                </div>
              </div>
              
              {/* Status Indicators */}
              <div className="ai-status-indicators">
                {hideEdges && (
                  <div className="ai-status-tag" style={{ background: 'rgba(245, 158, 11, 0.15)' }}>
                    <span>🔗</span><span>Hidden</span>
                  </div>
                )}
                {aggregateBy && (
                  <div className="ai-status-tag" style={{ background: 'rgba(59, 130, 246, 0.15)' }}>
                    <span>📊</span><span>By {aggregateBy}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Live Update Indicator */}
          {ragQuery && !isAnalyzing && (
            <div className="mt-2 p-1.5 bg-glass-bg border border-glass-border rounded">
              <div className="flex items-center space-x-1">
                <Zap className="h-3 w-3 text-accent" />
                <span className="text-xs font-medium text-secondary">Live Active</span>
              </div>
            </div>
          )}
        </div>
        {/* Controls */}
        <div className="card apple-card" style={{ padding: '1rem' }}>
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-primary mb-4" style={{ lineHeight: '1.6' }}>Network Graph</h3>
            <div className="space-y-4">
              {/* Filter Controls */}
              <div className="flex items-center space-x-3">
                <Filter className="h-4 w-4 text-secondary" />
                <select 
                  value={selectedFilter}
                  onChange={(e) => setSelectedFilter(e.target.value as any)}
                  className="input flex-1"
                  style={{ paddingLeft: '0.75rem', fontSize: '12px', lineHeight: '1.6' }}
                >
                  <option value="all">All Nodes</option>
                  <option value="domains">Domains Only</option>
                  <option value="ips">IPs Only</option>
                  <option value="addresses">Addresses Only</option>
                </select>
              </div>


            </div>
          </div>

          {/* Legend */}
          <div className="space-y-4">
            <h4 className="text-xs font-medium text-secondary" style={{ lineHeight: '1.6' }}>Legend</h4>
            <div className="space-y-3" style={{ fontSize: '11px', lineHeight: '1.7' }}>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: '#6366f1' }}></div>
                <span className="text-secondary flex items-center">
                  <Globe className="h-3 w-3 mr-2" />
                  Domains ({processNetworkData.nodes.filter(n => n.group === 'domain').length})
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: '#10b981' }}></div>
                <span className="text-secondary flex items-center">
                  <Server className="h-3 w-3 mr-2" />
                  IPs ({processNetworkData.nodes.filter(n => n.group === 'ip').length})
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: '#f59e0b' }}></div>
                <span className="text-secondary flex items-center">
                  <Coins className="h-3 w-3 mr-2" />
                  Addresses ({processNetworkData.nodes.filter(n => n.group === 'address').length})
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Stats */}
        {processNetworkData.nodes.length > 0 && (
          <div className="card" style={{ padding: '1rem' }}>
            <h4 className="text-sm font-medium text-secondary mb-2">Statistics</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center py-1">
                <span className="text-sm text-secondary">Total Nodes</span>
                <span className="text-lg font-bold text-primary">{processNetworkData.nodes.length}</span>
              </div>
              <div className="flex justify-between items-center py-1">
                <span className="text-sm text-secondary">Connections</span>
                <span className="text-lg font-bold text-primary">{processNetworkData.links.length}</span>
              </div>
              <div className="flex justify-between items-center py-1">
                <span className="text-sm text-secondary">Domains</span>
                <span className="text-lg font-bold text-primary">
                  {processNetworkData.nodes.filter(n => n.group === 'domain').length}
                </span>
              </div>
              <div className="flex justify-between items-center py-1">
                <span className="text-sm text-secondary">IP Addresses</span>
                <span className="text-lg font-bold text-primary">
                  {processNetworkData.nodes.filter(n => n.group === 'ip').length}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Graph Area */}
      <div className="flex-1">
        <div className="card apple-card relative" style={{ padding: '1.25rem' }}>
          {isLoading && (
            <div className="loading-overlay">
              <div className="flex items-center space-x-2">
                <div className="spinner"></div>
                <span className="text-secondary" style={{ fontSize: '12px', lineHeight: '1.6' }}>Building network...</span>
              </div>
            </div>
          )}
          <div className="w-full flex justify-center">
            <svg 
              ref={svgRef}
              className="border rounded-lg"
              style={{ background: 'var(--primary-bg)', border: '1px solid var(--border-color)' }}
            />
          </div>
          
          {processNetworkData.nodes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <p className="text-muted" style={{ fontSize: '12px', lineHeight: '1.6' }}>No network data available for current filters</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NetworkGraph; 
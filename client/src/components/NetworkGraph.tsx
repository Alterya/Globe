import React, { useEffect, useRef, useState, useMemo } from 'react';
import * as d3 from 'd3';
import { Filter, RefreshCw, Globe, Server, Coins } from 'lucide-react';
import { VASPData } from '../types';

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

  const processNetworkData = useMemo(() => {
    const nodesMap = new Map<string, NetworkNode>();
    const links: NetworkLink[] = [];
    const linkSet = new Set<string>();

    const filteredData = searchQuery 
      ? data.filter(item => 
          item.source_domain.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.crypto_address.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.source_domain_ip.toLowerCase().includes(searchQuery.toLowerCase())
        )
      : data;

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
    const filteredLinks = links.filter(link => 
      nodeIds.has(link.source as string) && nodeIds.has(link.target as string)
    );

    return {
      nodes: filteredNodes,
      links: filteredLinks
    };
  }, [data, searchQuery, selectedFilter]);

  useEffect(() => {
    if (!svgRef.current || processNetworkData.nodes.length === 0) return;

    setIsLoading(true);

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous content

    const width = 800;
    const height = 600;
    const margin = 40;

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

    // Create force simulation
    const simulation = d3.forceSimulation<NetworkNode>(processNetworkData.nodes)
      .force('link', d3.forceLink<NetworkNode, NetworkLink>(processNetworkData.links)
        .id(d => d.id)
        .distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));

    // Create links
    const link = container.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(processNetworkData.links)
      .join('line')
      .attr('stroke', 'var(--border-color)')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2);

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
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }));

    // Add circles to nodes
    node.append('circle')
      .attr('r', d => Math.max(8, Math.min(20, 5 + d.value * 2)))
      .attr('fill', d => colorScale[d.group])
      .attr('stroke', d => d3.color(colorScale[d.group])?.darker(0.5)?.toString() || '#000')
      .attr('stroke-width', 2);

    // Add labels to nodes
    node.append('text')
      .attr('dy', '.35em')
      .attr('x', d => Math.max(8, Math.min(20, 5 + d.value * 2)) + 5)
      .attr('font-size', '12px')
      .attr('fill', 'var(--text-primary)')
      .text(d => d.label);

    // Add tooltips
    const tooltip = d3.select('body').append('div')
      .attr('class', 'tooltip')
      .style('opacity', 0)
      .style('position', 'absolute')
      .style('background', 'var(--surface-bg)')
      .style('border', '1px solid var(--border-color)')
      .style('border-radius', '8px')
      .style('padding', '10px')
      .style('font-size', '12px')
      .style('box-shadow', 'var(--shadow-lg)')
      .style('pointer-events', 'none')
      .style('z-index', '1000');

    node.on('mouseover', (event, d) => {
      tooltip.transition()
        .duration(200)
        .style('opacity', .9);
      tooltip.html(d.title)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 28) + 'px');
    })
    .on('mouseout', () => {
      tooltip.transition()
        .duration(500)
        .style('opacity', 0);
    });

    // Update positions on simulation tick
    simulation.on('tick', () => {
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

    simulation.on('end', () => {
      setIsLoading(false);
    });

    return () => {
      simulation.stop();
      tooltip.remove();
    };
  }, [processNetworkData]);

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
    <div className="space-y-6">
      {/* Controls */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-primary">Network Graph</h3>
          <div className="flex items-center space-x-4">
            {/* Filter Controls */}
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-secondary" />
              <select 
                value={selectedFilter}
                onChange={(e) => setSelectedFilter(e.target.value as any)}
                className="input w-32"
                style={{ paddingLeft: '0.75rem' }}
              >
                <option value="all">All Nodes</option>
                <option value="domains">Domains Only</option>
                <option value="ips">IPs Only</option>
                <option value="addresses">Addresses Only</option>
              </select>
            </div>

            <button
              onClick={refreshNetwork}
              className="btn"
              title="Reset zoom and center network"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Legend */}
        <div className="flex items-center space-x-6 mb-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#6366f1' }}></div>
            <span className="text-secondary">
              <Globe className="h-3 w-3 inline mr-1" />
              Domains ({processNetworkData.nodes.filter(n => n.group === 'domain').length})
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#10b981' }}></div>
            <span className="text-secondary">
              <Server className="h-3 w-3 inline mr-1" />
              IPs ({processNetworkData.nodes.filter(n => n.group === 'ip').length})
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#f59e0b' }}></div>
            <span className="text-secondary">
              <Coins className="h-3 w-3 inline mr-1" />
              Addresses ({processNetworkData.nodes.filter(n => n.group === 'address').length})
            </span>
          </div>
        </div>

        <p className="text-sm text-secondary mb-4">
          Interactive network showing connections between domains, IP addresses, and cryptocurrency addresses. 
          Drag nodes to rearrange, zoom with mouse wheel, hover for details.
        </p>
      </div>

      {/* Network Container */}
      <div className="card relative">
        {isLoading && (
          <div className="loading-overlay">
            <div className="flex items-center space-x-2">
              <div className="spinner"></div>
              <span className="text-secondary">Building network...</span>
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
            <p className="text-muted">No network data available for current filters</p>
          </div>
        )}
      </div>

      {/* Stats */}
      {processNetworkData.nodes.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card text-center">
            <p className="text-2xl font-bold text-primary">{processNetworkData.nodes.length}</p>
            <p className="text-sm text-secondary">Total Nodes</p>
          </div>
          <div className="card text-center">
            <p className="text-2xl font-bold text-primary">{processNetworkData.links.length}</p>
            <p className="text-sm text-secondary">Connections</p>
          </div>
          <div className="card text-center">
            <p className="text-2xl font-bold text-primary">
              {processNetworkData.nodes.filter(n => n.group === 'domain').length}
            </p>
            <p className="text-sm text-secondary">Domains</p>
          </div>
          <div className="card text-center">
            <p className="text-2xl font-bold text-primary">
              {processNetworkData.nodes.filter(n => n.group === 'ip').length}
            </p>
            <p className="text-sm text-secondary">IP Addresses</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default NetworkGraph; 
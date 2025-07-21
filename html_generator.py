"""
HTML Generator Module
Creates interactive D3.js visualizations from NetworkX graphs with enhanced modern UI.
"""

import json
from typing import Any, Dict

import networkx as nx
from jinja2 import Template
from networkx.readwrite import json_graph


class HTMLGenerator:
    """Generates interactive HTML visualizations using D3.js with modern enhancements."""

    def __init__(self) -> None:
        self.template = self._get_html_template()

    def create_html(
        self, graph: nx.Graph, title: str = "Domain Network Visualization", width: int = 1200, height: int = 800
    ) -> str:
        """
        Create HTML content with enhanced D3.js visualization.

        Args:
            graph: NetworkX graph object
            title: Title for the visualization
            width: Canvas width
            height: Canvas height

        Returns:
            Complete HTML content as string
        """
        # Convert graph to D3.js format
        graph_data = json_graph.node_link_data(graph)

        # Calculate enhanced statistics
        stats = self._calculate_enhanced_stats(graph_data)

        # Render template with enhanced features
        html_content = self.template.render(
            title=title, width=width, height=height, graph_data=json.dumps(graph_data, indent=2), stats=stats
        )

        return html_content

    def _calculate_enhanced_stats(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate enhanced statistics from graph data."""
        nodes = graph_data["nodes"]
        links = graph_data["links"]

        # Basic counts
        domain_count = sum(1 for n in nodes if n.get("type") == "domain")
        crypto_count = sum(1 for n in nodes if n.get("type") == "crypto")

        # Domain type breakdown
        domain_types: Dict[str, int] = {}
        for node in nodes:
            if node.get("type") == "domain":
                dtype = node.get("domain_type", "unknown")
                domain_types[dtype] = domain_types.get(dtype, 0) + 1

        # Edge type breakdown
        edge_types: Dict[str, int] = {}
        for link in links:
            edge_type = link.get("type", "unknown")
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

        # Crypto chain breakdown
        crypto_chains: Dict[str, int] = {}
        for node in nodes:
            if node.get("type") == "crypto":
                chain = node.get("chain", "unknown").upper()
                crypto_chains[chain] = crypto_chains.get(chain, 0) + 1

        # Intelligence coverage
        intel_available = sum(1 for link in links if "intel" in str(link.get("discovery_method", "")).lower())
        intel_coverage = (intel_available / len(links) * 100) if links else 0

        return {
            "total_nodes": len(nodes),
            "total_links": len(links),
            "domain_nodes": domain_count,
            "crypto_nodes": crypto_count,
            "domain_types": domain_types,
            "edge_types": edge_types,
            "crypto_chains": crypto_chains,
            "intel_coverage": round(intel_coverage, 1),
            "network_density": (
                round(len(links) / (len(nodes) * (len(nodes) - 1) / 2) * 100, 2) if len(nodes) > 1 else 0
            ),
        }

    def _get_html_template(self) -> Template:
        """Get the enhanced Jinja2 HTML template with modern design."""
        template_str = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    
    <style>
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --accent-color: #f093fb;
            --text-primary: #2d3748;
            --text-secondary: #4a5568;
            --bg-primary: #ffffff;
            --bg-secondary: #f7fafc;
            --border-color: #e2e8f0;
            --success-color: #48bb78;
            --warning-color: #ed8936;
            --error-color: #f56565;
            --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            min-height: 100vh;
            color: var(--text-primary);
            overflow: hidden;
        }
        
        .app-container {
            display: flex;
            height: 100vh;
            max-width: 100vw;
            background: var(--bg-primary);
            box-shadow: var(--shadow-xl);
            border-radius: 16px;
            margin: 16px;
            overflow: hidden;
        }
        
        .sidebar {
            width: 350px;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .sidebar-header {
            padding: 24px;
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            color: white;
        }
        
        .sidebar-header h1 {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .sidebar-header p {
            font-size: 14px;
            opacity: 0.9;
            font-weight: 300;
        }
        
        .sidebar-content {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
        }
        
        .section {
            margin-bottom: 32px;
        }
        
        .section-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--border-color);
        }
        
        .section-title i {
            color: var(--primary-color);
        }
        
        .search-container {
            position: relative;
        }
        
        .search-input {
            width: 100%;
            padding: 12px 16px 12px 44px;
            border: 2px solid var(--border-color);
            border-radius: 12px;
            font-size: 14px;
            font-weight: 400;
            background: var(--bg-primary);
            transition: all 0.2s ease;
        }
        
        .search-input:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .search-icon {
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
            font-size: 16px;
        }
        
        .stat-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        
        .stat-item {
            background: var(--bg-primary);
            padding: 16px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            text-align: center;
            transition: all 0.2s ease;
        }
        
        .stat-item:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: var(--primary-color);
            display: block;
        }
        
        .stat-label {
            font-size: 12px;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .legend-grid {
            display: grid;
            gap: 12px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            background: var(--bg-primary);
            border-radius: 8px;
            border: 1px solid var(--border-color);
            transition: all 0.2s ease;
        }
        
        .legend-item:hover {
            box-shadow: var(--shadow-sm);
            transform: translateX(4px);
        }
        
        .legend-indicator {
            width: 16px;
            height: 16px;
            border-radius: 8px;
            flex-shrink: 0;
        }
        
        .legend-line {
            width: 24px;
            height: 4px;
            border-radius: 2px;
            flex-shrink: 0;
        }
        
        .legend-label {
            font-size: 14px;
            font-weight: 500;
            color: var(--text-primary);
        }
        
        .controls-grid {
            display: grid;
            gap: 8px;
        }
        
        .control-button {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 12px 16px;
            background: var(--bg-primary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .control-button:hover {
            background: var(--primary-color);
            color: white;
            transform: translateY(-1px);
            box-shadow: var(--shadow-sm);
        }
        
        .control-button.active {
            background: var(--primary-color);
            color: white;
            box-shadow: var(--shadow-sm);
        }
        
        .visualization-container {
            flex: 1;
            position: relative;
            background: var(--bg-primary);
            overflow: hidden;
        }
        
        #network-svg {
            width: 100%;
            height: 100%;
            cursor: grab;
            background: radial-gradient(circle at center, #f8faff 0%, #f1f5ff 100%);
        }
        
        #network-svg:active {
            cursor: grabbing;
        }
        
        .zoom-controls {
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            z-index: 10;
        }
        
        .zoom-btn {
            width: 44px;
            height: 44px;
            border: none;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            cursor: pointer;
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .zoom-btn:hover {
            background: var(--primary-color);
            color: white;
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }
        
        .tooltip {
            position: fixed;
            background: var(--bg-primary);
            color: var(--text-primary);
            padding: 16px;
            border-radius: 12px;
            pointer-events: none;
            font-size: 13px;
            line-height: 1.5;
            max-width: 320px;
            box-shadow: var(--shadow-xl);
            border: 1px solid var(--border-color);
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.2s ease;
        }
        
        .tooltip h4 {
            margin: 0 0 12px 0;
            color: var(--primary-color);
            font-size: 16px;
            font-weight: 600;
        }
        
        .tooltip p {
            margin: 6px 0;
            color: var(--text-secondary);
        }
        
        .tooltip strong {
            color: var(--text-primary);
            font-weight: 600;
        }
        
        .tooltip .address {
            font-family: 'SF Mono', Monaco, Inconsolata, 'Roboto Mono', monospace;
            background: var(--bg-secondary);
            padding: 4px 8px;
            border-radius: 6px;
            word-break: break-all;
            font-size: 12px;
            border: 1px solid var(--border-color);
        }
        
        .tooltip a {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 500;
        }
        
        .tooltip a:hover {
            text-decoration: underline;
        }
        
        .node {
            stroke: white;
            stroke-width: 2px;
            cursor: pointer;
            transition: all 0.2s ease;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }
        
        .node:hover {
            stroke-width: 3px;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2)) brightness(1.1);
            transform: scale(1.05);
        }
        
        .link {
            stroke-opacity: 0.6;
            transition: all 0.2s ease;
        }
        
        .link:hover {
            stroke-opacity: 1;
            stroke-width: 4px !important;
        }
        
        .status-bar {
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.95);
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-sm);
            font-size: 12px;
            color: var(--text-secondary);
            font-family: 'SF Mono', Monaco, monospace;
        }
        
        @media (max-width: 1024px) {
            .app-container {
                flex-direction: column;
                margin: 8px;
                border-radius: 12px;
            }
            
            .sidebar {
                width: 100%;
                height: 300px;
                border-right: none;
                border-bottom: 1px solid var(--border-color);
            }
            
            .sidebar-content {
                padding: 16px;
            }
            
            .stat-grid {
                grid-template-columns: repeat(4, 1fr);
            }
        }
        
        .loading-spinner {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 48px;
            height: 48px;
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: translate(-50%, -50%) rotate(0deg); }
            100% { transform: translate(-50%, -50%) rotate(360deg); }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="sidebar">
            <div class="sidebar-header">
                <h1>{{ title }}</h1>
                <p>Interactive network analysis and exploration</p>
            </div>
            
            <div class="sidebar-content">
                <div class="section">
                    <div class="section-title">
                        <i class="fas fa-search"></i>
                        Search Network
                    </div>
                    <div class="search-container">
                        <i class="fas fa-search search-icon"></i>
                        <input type="text" class="search-input" id="search-input" 
                               placeholder="Search domains or addresses...">
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">
                        <i class="fas fa-chart-bar"></i>
                        Network Statistics
                    </div>
                    <div class="stat-grid">
                        <div class="stat-item">
                            <span class="stat-value">{{ stats.total_nodes }}</span>
                            <span class="stat-label">Nodes</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{{ stats.total_links }}</span>
                            <span class="stat-label">Links</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{{ stats.domain_nodes }}</span>
                            <span class="stat-label">Domains</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{{ stats.crypto_nodes }}</span>
                            <span class="stat-label">Addresses</span>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">
                        <i class="fas fa-palette"></i>
                        Node Types
                    </div>
                    <div class="legend-grid">
                        <div class="legend-item">
                            <div class="legend-indicator" style="background: #FF6B6B; border-radius: 50%;"></div>
                            <span class="legend-label">Source Domains</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-indicator" style="background: #4ECDC4; border-radius: 50%;"></div>
                            <span class="legend-label">Lookalike Domains</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-indicator" style="background: #45B7D1; border-radius: 50%;"></div>
                            <span class="legend-label">Same IP Domains</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-indicator" style="background: #F7931A; border-radius: 4px;"></div>
                            <span class="legend-label">Bitcoin (BTC)</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-indicator" style="background: #627EEA; border-radius: 50%;"></div>
                            <span class="legend-label">Ethereum (ETH)</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-indicator" style="background: #FF060A; clip-path: polygon(50% 0%, 0% 100%, 100% 100%);"></div>
                            <span class="legend-label">Tron (TRON)</span>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">
                        <i class="fas fa-project-diagram"></i>
                        Relationships
                    </div>
                    <div class="legend-grid">
                        <div class="legend-item">
                            <div class="legend-line" style="background: #E74C3C;"></div>
                            <span class="legend-label">Domain → Crypto</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-line" style="background: #3498DB;"></div>
                            <span class="legend-label">Lookalike Domain</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-line" style="background: #F39C12;"></div>
                            <span class="legend-label">Same IP Domain</span>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">
                        <i class="fas fa-cogs"></i>
                        Controls
                    </div>
                    <div class="controls-grid">
                        <button class="control-button" onclick="togglePhysics()">
                            <i class="fas fa-play"></i>
                            Toggle Physics
                        </button>
                        <button class="control-button" onclick="centerGraph()">
                            <i class="fas fa-compress-arrows-alt"></i>
                            Center Graph
                        </button>
                        <button class="control-button" onclick="toggleLabels()">
                            <i class="fas fa-tags"></i>
                            Toggle Labels
                        </button>
                        <button class="control-button" onclick="exportImage()">
                            <i class="fas fa-download"></i>
                            Export PNG
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="visualization-container">
            <div class="loading-spinner" id="loading"></div>
            <svg id="network-svg"></svg>
            <div class="zoom-controls">
                <button class="zoom-btn" onclick="zoomIn()" title="Zoom In">
                    <i class="fas fa-plus"></i>
                </button>
                <button class="zoom-btn" onclick="zoomOut()" title="Zoom Out">
                    <i class="fas fa-minus"></i>
                </button>
                <button class="zoom-btn" onclick="resetZoom()" title="Reset Zoom">
                    <i class="fas fa-home"></i>
                </button>
            </div>
            <div class="status-bar" id="status-bar">
                Initializing network...
            </div>
        </div>
    </div>
    
    <div class="tooltip" id="tooltip"></div>

    <script>
        // Initialize global variables
        const graphData = {{ graph_data|safe }};
        const svg = d3.select("#network-svg");
        const width = {{ width }};
        const height = {{ height }};
        const tooltip = d3.select("#tooltip");
        const statusBar = d3.select("#status-bar");
        const loading = d3.select("#loading");
        
        let simulation, container, node, link, labels;
        let showLabels = true;
        let physicsEnabled = true;
        
        // Initialize the visualization
        function initializeVisualization() {
            // Setup SVG
            svg.attr("viewBox", [0, 0, width, height]);
            
            // Setup zoom behavior
            const zoom = d3.zoom()
                .scaleExtent([0.1, 10])
                .on("zoom", (event) => {
                    container.attr("transform", event.transform);
                    updateStatusBar(event.transform);
                });
            
            svg.call(zoom);
            container = svg.append("g");
            
            // Create force simulation
            simulation = d3.forceSimulation(graphData.nodes)
                .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(120))
                .force("charge", d3.forceManyBody().strength(-400))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide().radius(d => d.size + 8));
            
            // Create links
            link = container.append("g")
                .selectAll("line")
                .data(graphData.links)
                .join("line")
                .attr("class", "link")
                .attr("stroke", d => d.color)
                .attr("stroke-width", d => d.width)
                .on("mouseover", function(event, d) {
                    showLinkTooltip(event, d);
                })
                .on("mouseout", hideTooltip);
            
            // Create nodes
            node = container.append("g")
                .selectAll("g")
                .data(graphData.nodes)
                .join("g")
                .attr("class", "node")
                .call(drag(simulation));
            
            // Add shapes to nodes
            node.each(function(d) {
                const nodeGroup = d3.select(this);
                
                if (d.shape === 'circle') {
                    nodeGroup.append("circle")
                        .attr("r", d.size)
                        .attr("fill", d.color);
                } else if (d.shape === 'square') {
                    nodeGroup.append("rect")
                        .attr("width", d.size * 1.8)
                        .attr("height", d.size * 1.8)
                        .attr("x", -d.size * 0.9)
                        .attr("y", -d.size * 0.9)
                        .attr("rx", 4)
                        .attr("fill", d.color);
                } else if (d.shape === 'triangle') {
                    const size = d.size * 1.3;
                    nodeGroup.append("polygon")
                        .attr("points", `0,${-size} ${size * 0.866},${size * 0.5} ${-size * 0.866},${size * 0.5}`)
                        .attr("fill", d.color);
                }
            });
            
            // Add labels
            labels = node.append("text")
                .text(d => d.label.length > 20 ? d.label.substring(0, 20) + '...' : d.label)
                .attr("font-size", "11px")
                .attr("font-weight", "500")
                .attr("text-anchor", "middle")
                .attr("dy", d => d.size + 18)
                .attr("fill", "#4a5568")
                .style("pointer-events", "none");
            
            // Node interactions
            node
                .on("mouseover", function(event, d) {
                    showNodeTooltip(event, d);
                    highlightConnectedNodes(d);
                })
                .on("mouseout", function() {
                    hideTooltip();
                    resetHighlight();
                })
                .on("click", function(event, d) {
                    handleNodeClick(d);
                })
                .on("dblclick", function(event, d) {
                    focusOnNode(d);
                });
            
            // Update positions on simulation tick
            simulation.on("tick", () => {
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                node.attr("transform", d => `translate(${d.x},${d.y})`);
            });
            
            // Hide loading spinner
            loading.style("display", "none");
            updateStatusBar();
            
            // Auto-center after initial layout
            setTimeout(() => {
                centerGraph();
                statusBar.text(`Network loaded: ${graphData.nodes.length} nodes, ${graphData.links.length} links`);
            }, 2000);
        }
        
        // Enhanced tooltip functions
        function showNodeTooltip(event, d) {
            let content = `<h4><i class="fas fa-${d.type === 'domain' ? 'globe' : 'coins'}"></i> ${d.label}</h4>`;
            
            if (d.type === 'domain') {
                content += `<p><strong>Type:</strong> ${d.domain_type.charAt(0).toUpperCase() + d.domain_type.slice(1)} domain</p>`;
                content += `<p><strong>IP Address:</strong> ${d.ip_address}</p>`;
                if (d.url) {
                    content += `<p><strong>URL:</strong> <a href="${d.url}" target="_blank">${d.url}</a></p>`;
                }
                if (d.screenshot) {
                    content += `<p><strong>Screenshot:</strong> <a href="${d.screenshot}" target="_blank">View Screenshot</a></p>`;
                }
                if (d.inreach_intel_summary) {
                    content += `<p><strong>Intelligence:</strong> ${d.inreach_intel_summary}</p>`;
                }
            } else if (d.type === 'crypto') {
                content += `<p><strong>Blockchain:</strong> ${d.chain}</p>`;
                content += `<p><strong>Address:</strong><br><span class="address">${d.full_address}</span></p>`;
                if (d.explorer_link) {
                    content += `<p><strong>Explorer:</strong> <a href="${d.explorer_link}" target="_blank">View on Explorer</a></p>`;
                }
            }
            
            showTooltip(event, content);
        }
        
        function showLinkTooltip(event, d) {
            const content = `
                <h4><i class="fas fa-link"></i> Connection</h4>
                <p><strong>Type:</strong> ${d.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</p>
                <p><strong>Discovery:</strong> ${d.discovery_method || 'Unknown'}</p>
                <p><strong>From:</strong> ${d.source.label}</p>
                <p><strong>To:</strong> ${d.target.label}</p>
            `;
            showTooltip(event, content);
        }
        
        function showTooltip(event, content) {
            tooltip
                .style("opacity", 1)
                .html(content)
                .style("left", Math.min(event.pageX + 15, window.innerWidth - 340) + "px")
                .style("top", Math.max(event.pageY - 15, 10) + "px");
        }
        
        function hideTooltip() {
            tooltip.style("opacity", 0);
        }
        
        // Enhanced interaction functions
        function highlightConnectedNodes(d) {
            const connectedNodes = new Set([d.id]);
            const connectedLinks = new Set();
            
            graphData.links.forEach(link => {
                if (link.source.id === d.id) {
                    connectedNodes.add(link.target.id);
                    connectedLinks.add(link);
                }
                if (link.target.id === d.id) {
                    connectedNodes.add(link.source.id);
                    connectedLinks.add(link);
                }
            });
            
            node.style("opacity", n => connectedNodes.has(n.id) ? 1 : 0.2);
            link.style("opacity", l => connectedLinks.has(l) ? 1 : 0.1);
        }
        
        function resetHighlight() {
            node.style("opacity", 1);
            link.style("opacity", 0.6);
        }
        
        function handleNodeClick(d) {
            if (d.type === 'domain' && d.url) {
                window.open(d.url, '_blank');
            } else if (d.type === 'crypto' && d.explorer_link) {
                window.open(d.explorer_link, '_blank');
            }
        }
        
        function focusOnNode(d) {
            const transform = d3.zoomIdentity
                .translate(width / 2 - d.x, height / 2 - d.y)
                .scale(2);
            
            svg.transition()
                .duration(750)
                .call(d3.zoom().transform, transform);
        }
        
        // Control functions
        function zoomIn() {
            svg.transition().duration(300).call(d3.zoom().scaleBy, 1.5);
        }
        
        function zoomOut() {
            svg.transition().duration(300).call(d3.zoom().scaleBy, 1 / 1.5);
        }
        
        function resetZoom() {
            svg.transition().duration(500).call(d3.zoom().transform, d3.zoomIdentity);
        }
        
        function togglePhysics() {
            const button = event.target.closest('.control-button');
            if (physicsEnabled) {
                simulation.stop();
                button.classList.add('active');
                button.querySelector('i').className = 'fas fa-pause';
                physicsEnabled = false;
            } else {
                simulation.restart();
                button.classList.remove('active');
                button.querySelector('i').className = 'fas fa-play';
                physicsEnabled = true;
            }
        }
        
        function centerGraph() {
            const bounds = container.node().getBBox();
            const parent = svg.node().getBoundingClientRect();
            const fullWidth = parent.width;
            const fullHeight = parent.height;
            const widthScale = fullWidth / bounds.width;
            const heightScale = fullHeight / bounds.height;
            const scale = Math.min(widthScale, heightScale) * 0.85;
            const translate = [
                fullWidth / 2 - scale * (bounds.x + bounds.width / 2),
                fullHeight / 2 - scale * (bounds.y + bounds.height / 2)
            ];
            
            svg.transition()
                .duration(750)
                .call(d3.zoom().transform, d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
        }
        
        function toggleLabels() {
            showLabels = !showLabels;
            labels.style("display", showLabels ? "block" : "none");
            const button = event.target.closest('.control-button');
            button.querySelector('i').className = showLabels ? 'fas fa-tags' : 'far fa-tags';
        }
        
        function exportImage() {
            const svgElement = document.getElementById('network-svg');
            const svgString = new XMLSerializer().serializeToString(svgElement);
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            canvas.width = width;
            canvas.height = height;
            
            img.onload = function() {
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, width, height);
                ctx.drawImage(img, 0, 0);
                
                const link = document.createElement('a');
                link.download = 'domain-network.png';
                link.href = canvas.toDataURL();
                link.click();
            };
            
            img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgString)));
        }
        
        function updateStatusBar(transform) {
            const scale = transform ? transform.k : 1;
            const nodeCount = graphData.nodes.length;
            const linkCount = graphData.links.length;
            statusBar.text(`Nodes: ${nodeCount} | Links: ${linkCount} | Zoom: ${scale.toFixed(1)}x`);
        }
        
        // Search functionality
        const searchInput = document.getElementById('search-input');
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            
            if (searchTerm) {
                const matchingNodes = new Set();
                
                graphData.nodes.forEach(n => {
                    const matches = n.label.toLowerCase().includes(searchTerm) ||
                                  (n.full_address && n.full_address.toLowerCase().includes(searchTerm)) ||
                                  (n.chain && n.chain.toLowerCase().includes(searchTerm)) ||
                                  (n.domain_type && n.domain_type.toLowerCase().includes(searchTerm));
                    
                    if (matches) matchingNodes.add(n.id);
                });
                
                node.style("opacity", n => matchingNodes.has(n.id) ? 1 : 0.2);
                link.style("opacity", l => 
                    matchingNodes.has(l.source.id) || matchingNodes.has(l.target.id) ? 0.6 : 0.1
                );
                
                statusBar.text(`Found ${matchingNodes.size} matching nodes`);
            } else {
                resetHighlight();
                updateStatusBar();
            }
        });
        
        // Drag behavior
        function drag(simulation) {
            function dragstarted(event) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }
            
            function dragged(event) {
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }
            
            function dragended(event) {
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }
            
            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }
        
        // Initialize everything when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(initializeVisualization, 100);
        });
        
        // Add fade-in animation to app container
        document.querySelector('.app-container').classList.add('fade-in');
    </script>
</body>
</html>"""

        return Template(template_str)

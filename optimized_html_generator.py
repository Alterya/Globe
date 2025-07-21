"""
Optimized HTML Generator for Large Networks
Handles thousands of nodes efficiently with smart rendering and force simulation
"""

import json
from typing import Any, Dict

import networkx as nx
from jinja2 import Template
from networkx.readwrite import json_graph


class OptimizedHTMLGenerator:
    """Generates optimized HTML visualizations for large networks."""

    def __init__(self) -> None:
        self.template = self._get_optimized_template()

    def create_html(
        self, graph: nx.Graph, title: str = "Domain Network Visualization", width: int = 1200, height: int = 800
    ) -> str:
        """
        Create optimized HTML content for large networks.
        """
        # Convert graph to D3.js format
        graph_data = json_graph.node_link_data(graph)

        # Calculate statistics
        stats = self._calculate_stats(graph_data)

        # Optimize for large networks
        optimized_data = self._optimize_for_large_networks(graph_data)

        # Render template
        html_content = self.template.render(
            title=title,
            width=width,
            height=height,
            graph_data=json.dumps(optimized_data, indent=2),
            stats=stats,
            is_large_network=stats["total_nodes"] > 1000,
        )

        return html_content

    def _optimize_for_large_networks(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize network data for large datasets"""
        nodes = graph_data["nodes"]
        links = graph_data["links"]

        # For very large networks, prioritize important nodes
        if len(nodes) > 1000:
            # Keep all source domains (they're most important)
            priority_nodes = [n for n in nodes if n.get("domain_type") == "source"]

            # Sample other nodes based on type priority
            other_nodes = [n for n in nodes if n.get("domain_type") != "source"]

            if len(other_nodes) > 2000:
                # Prioritize crypto addresses and lookalike domains
                crypto_nodes = [n for n in other_nodes if n.get("type") == "crypto"][:500]
                lookalike_nodes = [n for n in other_nodes if n.get("domain_type") == "lookalike"][:100]
                same_ip_nodes = [n for n in other_nodes if n.get("domain_type") == "same_ip"][:1500]

                selected_nodes = priority_nodes + crypto_nodes + lookalike_nodes + same_ip_nodes
            else:
                selected_nodes = priority_nodes + other_nodes

            # Keep only relevant links
            node_ids = {n["id"] for n in selected_nodes}
            filtered_links = [l for l in links if l["source"] in node_ids and l["target"] in node_ids]

            return {"nodes": selected_nodes, "links": filtered_links}

        return graph_data

    def _calculate_stats(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate network statistics."""
        nodes = graph_data["nodes"]
        links = graph_data["links"]

        # Count node types
        node_counts = {}
        for node in nodes:
            node_type = node.get("domain_type") or node.get("type", "unknown")
            node_counts[node_type] = node_counts.get(node_type, 0) + 1

        return {"total_nodes": len(nodes), "total_links": len(links), "node_counts": node_counts}

    def _get_optimized_template(self) -> Template:
        """Get optimized HTML template for large networks."""
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
            width: 320px;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .sidebar-header {
            padding: 20px;
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            color: white;
        }
        
        .sidebar-header h1 {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .sidebar-header p {
            font-size: 12px;
            opacity: 0.9;
            font-weight: 300;
        }
        
        .sidebar-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        
        .section {
            margin-bottom: 24px;
        }
        
        .section-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 12px;
            padding-bottom: 6px;
            border-bottom: 2px solid var(--border-color);
        }
        
        .section-title i {
            color: var(--primary-color);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }
        
        .stat-item {
            background: var(--bg-primary);
            padding: 12px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            text-align: center;
        }
        
        .stat-value {
            font-size: 18px;
            font-weight: 700;
            color: var(--primary-color);
            display: block;
        }
        
        .stat-label {
            font-size: 10px;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .controls {
            display: grid;
            gap: 8px;
        }
        
        .control-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 10px 12px;
            background: var(--bg-primary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .control-btn:hover {
            background: var(--primary-color);
            color: white;
        }
        
        .control-btn.active {
            background: var(--primary-color);
            color: white;
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
        
        .loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.95);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            font-weight: 500;
            color: var(--text-primary);
        }
        
        .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 16px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .progress-bar {
            width: 200px;
            height: 4px;
            background: var(--border-color);
            border-radius: 2px;
            margin-top: 16px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: var(--primary-color);
            border-radius: 2px;
            transition: width 0.3s ease;
            width: 0%;
        }
        
        .status-bar {
            position: absolute;
            bottom: 16px;
            left: 16px;
            right: 16px;
            background: rgba(255, 255, 255, 0.95);
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-sm);
            font-size: 11px;
            color: var(--text-secondary);
            font-family: 'SF Mono', Monaco, monospace;
            text-align: center;
        }
        
        .zoom-controls {
            position: absolute;
            top: 16px;
            right: 16px;
            display: flex;
            flex-direction: column;
            gap: 4px;
            z-index: 100;
        }
        
        .zoom-btn {
            width: 36px;
            height: 36px;
            border: none;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
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
        }
        
        .tooltip {
            position: fixed;
            background: rgba(255, 255, 255, 0.98);
            color: var(--text-primary);
            padding: 16px;
            border-radius: 8px;
            pointer-events: none;
            font-size: 12px;
            line-height: 1.5;
            max-width: 300px;
            min-width: 250px;
            box-shadow: var(--shadow-xl);
            border: 1px solid var(--border-color);
            z-index: 9999;
            opacity: 0;
            transition: opacity 0.1s ease;
            word-wrap: break-word;
        }
        
        .tooltip h4 {
            margin: 0 0 12px 0;
            color: var(--primary-color);
            font-size: 14px;
            font-weight: 600;
        }
        
        .tooltip-content {
            display: grid;
            gap: 8px;
        }
        
        .tooltip-row {
            display: flex;
            justify-content: space-between;
            gap: 8px;
        }
        
        .tooltip-row strong {
            font-weight: 600;
            min-width: 80px;
        }
        
        .tooltip a {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 500;
        }
        
        .tooltip a:hover {
            text-decoration: underline;
        }
        
        .address-display {
            font-family: 'SF Mono', Monaco, Inconsolata, 'Roboto Mono', monospace;
            background: var(--bg-secondary);
            padding: 4px 6px;
            border-radius: 4px;
            word-break: break-all;
            font-size: 10px;
            border: 1px solid var(--border-color);
            margin-top: 4px;
        }
        
        .node {
            stroke: white;
            stroke-width: 1.5px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .node:hover {
            stroke-width: 2.5px;
            filter: brightness(1.1);
        }
        
        .link {
            stroke-opacity: 0.4;
            transition: all 0.2s ease;
        }
        
        .link:hover {
            stroke-opacity: 0.8;
            stroke-width: 3px !important;
        }
        
        .node-label {
            font-size: 9px;
            font-weight: 500;
            text-anchor: middle;
            fill: var(--text-secondary);
            pointer-events: none;
            user-select: none;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="sidebar">
            <div class="sidebar-header">
                <h1>{{ title }}</h1>
                <p>Interactive network analysis</p>
                {% if is_large_network %}
                <p style="color: #ffd700; font-weight: 500; margin-top: 8px;">
                    <i class="fas fa-info-circle"></i> Large network optimized
                </p>
                {% endif %}
            </div>
            
            <div class="sidebar-content">
                <div class="section">
                    <div class="section-title">
                        <i class="fas fa-chart-bar"></i>
                        Network Statistics
                    </div>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-value">{{ stats.total_nodes }}</span>
                            <span class="stat-label">Nodes</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{{ stats.total_links }}</span>
                            <span class="stat-label">Links</span>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">
                        <i class="fas fa-cogs"></i>
                        Controls
                    </div>
                    <div class="controls">
                        <button class="control-btn" onclick="togglePhysics()" id="physics-btn">
                            <i class="fas fa-play"></i>
                            Toggle Physics
                        </button>
                        <button class="control-btn" onclick="centerGraph()">
                            <i class="fas fa-compress-arrows-alt"></i>
                            Center View
                        </button>
                        <button class="control-btn" onclick="toggleLabels()" id="labels-btn">
                            <i class="fas fa-tags"></i>
                            Toggle Labels
                        </button>
                        <button class="control-btn" onclick="resetView()">
                            <i class="fas fa-refresh"></i>
                            Reset View
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="visualization-container">
            <div class="loading-overlay" id="loading">
                <div class="loading-spinner"></div>
                <div>Loading network visualization...</div>
                <div style="font-size: 11px; margin-top: 8px; opacity: 0.7;">
                    Optimizing {{ stats.total_nodes }} nodes for display
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progress"></div>
                </div>
            </div>
            
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
        // Global variables
        const graphData = {{ graph_data|safe }};
        const svg = d3.select("#network-svg");
        const width = {{ width }};
        const height = {{ height }};
        const tooltip = d3.select("#tooltip");
        const statusBar = d3.select("#status-bar");
        const loading = d3.select("#loading");
        const progress = d3.select("#progress");
        
        let simulation, container, node, link, labels;
        let showLabels = false; // Start with labels off for performance
        let physicsEnabled = true;
        let transform = d3.zoomIdentity;
        
        // Optimized initialization for large networks
        async function initializeVisualization() {
            updateProgress(10, "Setting up canvas...");
            
            // Setup SVG with optimized settings
            svg.attr("viewBox", [0, 0, width, height]);
            
            // Setup zoom with optimized performance
            const zoom = d3.zoom()
                .scaleExtent([0.1, 5])
                .on("zoom", (event) => {
                    transform = event.transform;
                    container.attr("transform", transform);
                    updateStatusBar();
                });
            
            svg.call(zoom);
            container = svg.append("g");
            
            updateProgress(25, "Creating force simulation...");
            
            // Optimized force simulation for large networks
            simulation = d3.forceSimulation(graphData.nodes)
                .force("link", d3.forceLink(graphData.links)
                    .id(d => d.id)
                    .distance(d => {
                        // Shorter distances for large networks
                        if (graphData.nodes.length > 1000) return 50;
                        return 80;
                    })
                    .strength(0.5))
                .force("charge", d3.forceManyBody()
                    .strength(d => {
                        // Weaker forces for large networks
                        if (graphData.nodes.length > 1000) return -100;
                        return -200;
                    }))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide()
                    .radius(d => (d.size || 10) + 2)
                    .strength(0.7))
                .alphaDecay(0.02) // Faster settling
                .velocityDecay(0.4); // More damping
            
            updateProgress(40, "Creating links...");
            
            // Create optimized links
            link = container.append("g")
                .attr("class", "links")
                .selectAll("line")
                .data(graphData.links)
                .join("line")
                .attr("class", "link")
                .attr("stroke", d => d.color || "#999")
                .attr("stroke-width", d => Math.max(1, (d.width || 1) * 0.8))
                .on("mouseover", function(event, d) {
                    if (graphData.nodes.length < 2000) { // Only show tooltips for smaller networks
                        showLinkTooltip(event, d);
                    }
                })
                .on("mouseout", hideTooltip);
            
            updateProgress(60, "Creating nodes...");
            
            // Create optimized nodes
            node = container.append("g")
                .attr("class", "nodes")
                .selectAll("g")
                .data(graphData.nodes)
                .join("g")
                .attr("class", "node")
                .call(drag(simulation));
            
            // Add shapes to nodes with optimized rendering
            node.each(function(d) {
                const nodeGroup = d3.select(this);
                const size = (d.size || 10) * 0.8; // Smaller nodes for large networks
                const color = d.color || "#69b3a2";
                
                if (d.shape === 'square' || (d.type === 'crypto' && d.chain === 'BTC')) {
                    nodeGroup.append("rect")
                        .attr("width", size * 1.6)
                        .attr("height", size * 1.6)
                        .attr("x", -size * 0.8)
                        .attr("y", -size * 0.8)
                        .attr("rx", 2)
                        .attr("fill", color);
                } else if (d.shape === 'triangle' || (d.type === 'crypto' && d.chain === 'TRON')) {
                    nodeGroup.append("polygon")
                        .attr("points", `0,${-size} ${size * 0.866},${size * 0.5} ${-size * 0.866},${size * 0.5}`)
                        .attr("fill", color);
                } else {
                    nodeGroup.append("circle")
                        .attr("r", size)
                        .attr("fill", color);
                }
            });
            
            updateProgress(80, "Setting up interactions...");
            
            // Optimized node interactions
            node
                .on("mouseover", function(event, d) {
                    showNodeTooltip(event, d);
                    if (graphData.nodes.length < 1500) { // Only highlight for smaller networks
                        highlightConnectedNodes(d);
                    }
                })
                .on("mouseout", function() {
                    hideTooltip();
                    if (graphData.nodes.length < 1500) {
                        resetHighlight();
                    }
                })
                .on("click", function(event, d) {
                    handleNodeClick(d);
                })
                .on("dblclick", function(event, d) {
                    focusOnNode(d);
                });
            
            // Add labels (initially hidden for performance)
            if (graphData.nodes.length < 1000) {
                labels = node.append("text")
                    .attr("class", "node-label")
                    .text(d => {
                        const label = d.label || d.id;
                        return label.length > 15 ? label.substring(0, 15) + '...' : label;
                    })
                    .attr("dy", d => (d.size || 10) + 12)
                    .style("display", showLabels ? "block" : "none");
            }
            
            updateProgress(95, "Starting simulation...");
            
            // Optimized tick function
            let tickCount = 0;
            simulation.on("tick", () => {
                tickCount++;
                
                // Update positions
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                node.attr("transform", d => `translate(${d.x},${d.y})`);
                
                // Update status every 10 ticks
                if (tickCount % 10 === 0) {
                    const alpha = simulation.alpha();
                    updateProgress(95 + alpha * 5, `Stabilizing layout... (${(alpha * 100).toFixed(1)}%)`);
                }
            });
            
            // Stop simulation after reasonable time for large networks
            if (graphData.nodes.length > 1000) {
                setTimeout(() => {
                    if (simulation.alpha() > 0.1) {
                        simulation.alpha(0.1);
                    }
                }, 3000);
            }
            
            updateProgress(100, "Complete!");
            
            // Hide loading and show network
            setTimeout(() => {
                loading.style("display", "none");
                updateStatusBar();
                
                // Auto-center view
                setTimeout(() => {
                    centerGraph();
                }, 500);
            }, 500);
        }
        
        // Enhanced tooltip functions
        function showNodeTooltip(event, d) {
            const content = generateNodeTooltipContent(d);
            showTooltip(event, content);
        }
        
        function generateNodeTooltipContent(d) {
            if (d.type === 'domain') {
                return `
                    <h4><i class="fas fa-globe"></i> ${d.label}</h4>
                    <div class="tooltip-content">
                        <div class="tooltip-row">
                            <strong>Type:</strong>
                            <span>${(d.domain_type || 'domain').replace('_', ' ')}</span>
                        </div>
                        ${d.ip_address ? `<div class="tooltip-row"><strong>IP:</strong> <span>${d.ip_address}</span></div>` : ''}
                        ${d.url ? `<div class="tooltip-row"><strong>URL:</strong> <a href="${d.url}" target="_blank">Visit</a></div>` : ''}
                        ${d.screenshot ? `<div class="tooltip-row"><strong>Screenshot:</strong> <a href="${d.screenshot}" target="_blank">View</a></div>` : ''}
                    </div>
                `;
            } else if (d.type === 'crypto') {
                return `
                    <h4><i class="fas fa-coins"></i> ${d.chain || 'Crypto'} Address</h4>
                    <div class="tooltip-content">
                        <div class="tooltip-row">
                            <strong>Chain:</strong>
                            <span>${(d.chain || 'Unknown').toUpperCase()}</span>
                        </div>
                        <div class="tooltip-row">
                            <strong>Address:</strong>
                        </div>
                        <div class="address-display">${d.full_address || d.id}</div>
                        ${d.explorer_link ? `<div class="tooltip-row" style="margin-top: 8px;"><a href="${d.explorer_link}" target="_blank"><i class="fas fa-external-link-alt"></i> View on Explorer</a></div>` : ''}
                    </div>
                `;
            }
            return `<h4>${d.label || d.id}</h4>`;
        }
        
        function showLinkTooltip(event, d) {
            const content = `
                <h4><i class="fas fa-link"></i> Connection</h4>
                <div class="tooltip-content">
                    <div class="tooltip-row">
                        <strong>Type:</strong>
                        <span>${(d.type || 'connection').replace('_', ' ')}</span>
                    </div>
                    <div class="tooltip-row">
                        <strong>From:</strong>
                        <span>${d.source.label || d.source.id}</span>
                    </div>
                    <div class="tooltip-row">
                        <strong>To:</strong>
                        <span>${d.target.label || d.target.id}</span>
                    </div>
                </div>
            `;
            showTooltip(event, content);
        }
        
        function showTooltip(event, content) {
            tooltip
                .transition().duration(0)
                .style("opacity", 1)
                .html(content);
            
            updateTooltipPosition(event);
        }
        
        function updateTooltipPosition(event) {
            const tooltipNode = tooltip.node();
            if (tooltipNode) {
                const tooltipRect = tooltipNode.getBoundingClientRect();
                const pageWidth = window.innerWidth;
                const pageHeight = window.innerHeight;
                
                let x = event.pageX + 15;
                let y = event.pageY - 15;
                
                if (x + tooltipRect.width > pageWidth - 20) {
                    x = event.pageX - tooltipRect.width - 15;
                }
                if (y + tooltipRect.height > pageHeight - 20) {
                    y = event.pageY - tooltipRect.height - 15;
                }
                
                tooltip
                    .style("left", x + "px")
                    .style("top", y + "px");
            }
        }
        
        function hideTooltip() {
            tooltip.transition().duration(200).style("opacity", 0);
        }
        
        // Optimized interaction functions
        function highlightConnectedNodes(d) {
            const connectedNodes = new Set([d.id]);
            const connectedLinks = new Set();
            
            graphData.links.forEach(link => {
                if (link.source.id === d.id || link.source === d.id) {
                    connectedNodes.add(link.target.id || link.target);
                    connectedLinks.add(link);
                }
                if (link.target.id === d.id || link.target === d.id) {
                    connectedNodes.add(link.source.id || link.source);
                    connectedLinks.add(link);
                }
            });
            
            node.style("opacity", n => connectedNodes.has(n.id) ? 1 : 0.2);
            link.style("opacity", l => connectedLinks.has(l) ? 0.8 : 0.1);
        }
        
        function resetHighlight() {
            node.style("opacity", 1);
            link.style("opacity", 0.4);
        }
        
        function handleNodeClick(d) {
            if (d.type === 'domain' && d.url) {
                window.open(d.url, '_blank');
            } else if (d.type === 'crypto' && d.explorer_link) {
                window.open(d.explorer_link, '_blank');
            }
        }
        
        function focusOnNode(d) {
            const scale = Math.min(3, Math.max(1, 1000 / graphData.nodes.length));
            const newTransform = d3.zoomIdentity
                .translate(width / 2 - d.x * scale, height / 2 - d.y * scale)
                .scale(scale);
            
            svg.transition()
                .duration(750)
                .call(d3.zoom().transform, newTransform);
        }
        
        // Control functions
        function zoomIn() {
            svg.transition().duration(200).call(d3.zoom().scaleBy, 1.5);
        }
        
        function zoomOut() {
            svg.transition().duration(200).call(d3.zoom().scaleBy, 1 / 1.5);
        }
        
        function resetZoom() {
            svg.transition().duration(400).call(d3.zoom().transform, d3.zoomIdentity);
        }
        
        function togglePhysics() {
            const button = document.getElementById('physics-btn');
            if (physicsEnabled) {
                simulation.stop();
                button.classList.add('active');
                button.innerHTML = '<i class="fas fa-pause"></i> Physics Paused';
                physicsEnabled = false;
            } else {
                simulation.restart();
                button.classList.remove('active');
                button.innerHTML = '<i class="fas fa-play"></i> Physics Active';
                physicsEnabled = true;
            }
        }
        
        function centerGraph() {
            if (!container.node()) return;
            
            const bounds = container.node().getBBox();
            const fullWidth = width;
            const fullHeight = height;
            const widthScale = fullWidth / bounds.width;
            const heightScale = fullHeight / bounds.height;
            const scale = Math.min(widthScale, heightScale, 2) * 0.8;
            
            const translate = [
                fullWidth / 2 - scale * (bounds.x + bounds.width / 2),
                fullHeight / 2 - scale * (bounds.y + bounds.height / 2)
            ];
            
            svg.transition()
                .duration(750)
                .call(d3.zoom().transform, d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
        }
        
        function toggleLabels() {
            if (labels) {
                showLabels = !showLabels;
                labels.style("display", showLabels ? "block" : "none");
                const button = document.getElementById('labels-btn');
                button.innerHTML = showLabels ? 
                    '<i class="fas fa-tags"></i> Hide Labels' : 
                    '<i class="fas fa-tags"></i> Show Labels';
            }
        }
        
        function resetView() {
            resetZoom();
            setTimeout(() => {
                centerGraph();
            }, 500);
        }
        
        function updateStatusBar() {
            const scale = transform.k;
            const nodeCount = graphData.nodes.length;
            const linkCount = graphData.links.length;
            statusBar.text(`Nodes: ${nodeCount} | Links: ${linkCount} | Zoom: ${scale.toFixed(1)}x`);
        }
        
        function updateProgress(percent, message) {
            progress.style("width", percent + "%");
            if (message) {
                loading.select("div").text(message);
            }
        }
        
        // Optimized drag behavior
        function drag(simulation) {
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.1).restart();
                d.fx = d.x;
                d.fy = d.y;
            }
            
            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }
            
            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }
            
            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }
        
        // Initialize when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(initializeVisualization, 100);
        });
    </script>
</body>
</html>"""

        return Template(template_str)

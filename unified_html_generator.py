"""
Unified HTML Generator for Domain Network Visualization
Properly integrates with NodeManager and provides smart optimizations for large networks
"""

import json
from typing import Any, Dict

import networkx as nx
from jinja2 import Template
from networkx.readwrite import json_graph


class UnifiedHTMLGenerator:
    """Unified HTML generator that works seamlessly with NodeManager for any network size."""

    def __init__(self) -> None:
        self.template = self._get_unified_template()

    def create_html(
        self, graph: nx.Graph, title: str = "Domain Network Visualization", width: int = 1200, height: int = 800
    ) -> str:
        """Create optimized HTML content for networks of any size."""
        # Convert graph to D3.js format
        graph_data = json_graph.node_link_data(graph)

        # Calculate statistics
        stats = self._calculate_stats(graph_data)

        # Smart optimization for large networks
        optimized_data = graph_data
        if stats["total_nodes"] > 1000:
            optimized_data = self._smart_optimize_network(graph_data)
            stats = self._calculate_stats(optimized_data)
            print(f"Optimized network: {stats['total_nodes']} nodes, {stats['total_links']} links")
        else:
            print(f"Using original network: {stats['total_nodes']} nodes, {stats['total_links']} links")

        # Determine performance settings
        is_large = stats["total_nodes"] > 500

        # Render template without graph_data
        html_content = self.template.render(
            title=title,
            width=width,
            height=height,
            stats=stats,
            is_large_network=is_large,
            performance_mode=is_large,
        )

        # Safely insert the graph data JSON (compact format to avoid size issues)
        graph_json = json.dumps(optimized_data, separators=(",", ":"))
        html_content = html_content.replace("// GRAPH_DATA_PLACEHOLDER", graph_json)

        print(f"Generated HTML length: {len(html_content)} characters")
        return html_content

    def _smart_optimize_network(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Smart optimization that understands the actual node structure."""
        nodes = graph_data["nodes"]
        links = graph_data["links"]

        print(f"🔧 Optimizing network: {len(nodes)} nodes, {len(links)} links")

        # Priority selection based on actual node structure
        priority_nodes = []
        other_nodes = []

        for node in nodes:
            domain_type = node.get("domain_type") or node.get("node_type", "")
            node_type = node.get("type", "")
            print(
                f"Processing node {node.get('id', 'unknown')}: type={node_type}, domain_type={domain_type}"
            )  # Debug print

            # Prioritize source domains (most important)
            if domain_type == "source_domain":
                priority_nodes.append(node)
            # Keep all crypto addresses (important for connections)
            elif node_type == "crypto":
                priority_nodes.append(node)
            # Keep lookalike domains (important relationships)
            elif domain_type == "lookalike_domain":
                priority_nodes.append(node)
            else:
                other_nodes.append(node)

        print(f"Priority nodes: {len(priority_nodes)}, Other nodes: {len(other_nodes)}")  # Debug print

        # Less aggressive sampling for large numbers of other nodes
        if len(other_nodes) > 1500:
            # Keep more representative sample of same_ip_domain nodes
            same_ip_nodes = [n for n in other_nodes if n.get("domain_type") == "same_ip_domain"]
            target_same_ip = 1000 if len(same_ip_nodes) > 2000 else 1200  # More aggressive for very large
            sample_rate = max(1, len(same_ip_nodes) // target_same_ip)
            selected_same_ip = same_ip_nodes[::sample_rate]
            selected_nodes = priority_nodes + selected_same_ip
        else:
            selected_nodes = priority_nodes + other_nodes

        print(f"Selected nodes: {len(selected_nodes)}")  # Debug print

        # Keep only relevant links
        node_ids = {n["id"] for n in selected_nodes}
        filtered_links = []

        for link in links:
            source_id = link["source"] if isinstance(link["source"], str) else link["source"]["id"]
            target_id = link["target"] if isinstance(link["target"], str) else link["target"]["id"]

            if source_id in node_ids and target_id in node_ids:
                filtered_links.append(link)

        print(f"✅ Optimized to: {len(selected_nodes)} nodes, {len(filtered_links)} links")

        return {"nodes": selected_nodes, "links": filtered_links}

    def _calculate_stats(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive network statistics."""
        nodes = graph_data["nodes"]
        links = graph_data["links"]

        # Count by node types
        node_counts: Dict[str, int] = {}
        domain_count = 0
        crypto_count = 0

        for node in nodes:
            node_type = node.get("node_type") or node.get("domain_type") or node.get("type", "unknown")
            node_counts[node_type] = node_counts.get(node_type, 0) + 1

            if node.get("type") == "domain":
                domain_count += 1
            elif node.get("type") == "crypto":
                crypto_count += 1

        # Count edge types
        edge_counts: Dict[str, int] = {}
        for link in links:
            edge_type = link.get("type", "unknown")
            edge_counts[edge_type] = edge_counts.get(edge_type, 0) + 1

        return {
            "total_nodes": len(nodes),
            "total_links": len(links),
            "domain_nodes": domain_count,
            "crypto_nodes": crypto_count,
            "node_counts": node_counts,
            "edge_counts": edge_counts,
        }

    def _get_unified_template(self) -> Template:
        """Get the unified HTML template with smart performance optimizations."""
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
        
        {% if is_large_network %}
        .performance-notice {
            background: rgba(255, 215, 0, 0.2);
            color: #ffd700;
            padding: 8px 12px;
            border-radius: 6px;
            margin-top: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        {% endif %}
        
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
        
        .stats-grid {
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
            background: rgba(255, 255, 255, 0.98);
            color: var(--text-primary);
            padding: 20px;
            border-radius: 12px;
            pointer-events: none;
            font-size: 15px;
            line-height: 1.6;
            max-width: 400px;
            min-width: 300px;
            box-shadow: var(--shadow-xl);
            border: 1px solid var(--border-color);
            z-index: 9999;
            opacity: 0;
            transition: opacity 0.1s ease;
            word-wrap: break-word;
        }
        
        .tooltip h4 {
            margin: 0 0 15px 0;
            color: var(--primary-color);
            font-size: 16px;
            font-weight: 600;
        }
        
        .tooltip-content {
            display: grid;
            gap: 10px;
        }
        
        .tooltip-row {
            display: flex;
            justify-content: space-between;
            gap: 12px;
        }
        
        .tooltip-row strong {
            font-weight: 600;
            min-width: 100px;
            color: var(--text-primary);
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
            padding: 8px 12px;
            border-radius: 6px;
            word-break: break-all;
            font-size: 12px;
            border: 1px solid var(--border-color);
            margin-top: 8px;
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
        }
        
        .link {
            stroke-opacity: 0.6;
            transition: all 0.2s ease;
        }
        
        .link:hover {
            stroke-opacity: 1;
            stroke-width: 4px !important;
        }
        
        .node-label {
            font-size: 11px;
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
                <p>Interactive network analysis and exploration</p>
                {% if is_large_network %}
                <div class="performance-notice">
                    <i class="fas fa-tachometer-alt"></i> Performance optimized for large network
                </div>
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
                            <div class="legend-indicator" style="background: #e74c3c; border-radius: 50%;"></div>
                            <span class="legend-label">Source Domains (Primary domains of interest)</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-indicator" style="background: #3498db; border-radius: 50%;"></div>
                            <span class="legend-label">Lookalike Domains (Similar naming patterns)</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-indicator" style="background: #1abc9c; border-radius: 50%;"></div>
                            <span class="legend-label">Same IP Domains (Shared hosting/IP)</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-indicator" style="background: #f39c12; border-radius: 4px;"></div>
                            <span class="legend-label">Bitcoin (BTC) Addresses (Square shape)</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-indicator" style="background: #9b59b6; border-radius: 50%;"></div>
                            <span class="legend-label">Ethereum (ETH) Addresses (Circle shape)</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-indicator" style="background: #e74c3c; clip-path: polygon(50% 0%, 0% 100%, 100% 100%);"></div>
                            <span class="legend-label">Tron (TRON) Addresses (Triangle shape)</span>
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
                            <div class="legend-line" style="background: #e74c3c;"></div>
                            <span class="legend-label">Domain → Crypto (Associated addresses)</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-line" style="background: #3498db;"></div>
                            <span class="legend-label">Lookalike Domain (Naming similarity)</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-line" style="background: #f39c12;"></div>
                            <span class="legend-label">Same IP Domain (Shared infrastructure)</span>
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
                            <i class="fas fa-play" id="physics-icon"></i>
                            <span id="physics-text">Toggle Physics</span>
                        </button>
                        <button class="control-button" onclick="centerGraph()">
                            <i class="fas fa-compress-arrows-alt"></i>
                            Center Graph
                        </button>
                        <button class="control-button" onclick="toggleLabels()">
                            <i class="fas fa-tags" id="labels-icon"></i>
                            <span id="labels-text">Toggle Labels</span>
                        </button>
                        <button class="control-button" onclick="resetView()">
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
                <div style="font-size: 12px; margin-top: 8px; opacity: 0.7;">
                    Processing {{ stats.total_nodes }} nodes
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
        const graphData = // GRAPH_DATA_PLACEHOLDER;
        const svg = d3.select("#network-svg");
        const width = {{ width }};
        const height = {{ height }};
        const tooltip = d3.select("#tooltip");
        const statusBar = d3.select("#status-bar");
        const loading = d3.select("#loading");
        const isLargeNetwork = {{ is_large_network|lower }};
        
        let simulation, container, node, link, labels;
        let showLabels = !isLargeNetwork; // Auto-adjust based on network size
        let physicsEnabled = true;
        let transform = d3.zoomIdentity;
        
        // Initialize the visualization with smart performance settings
        async function initializeVisualization() {
            console.log(`Initializing network with ${graphData.nodes.length} nodes and ${graphData.links.length} links`);
            
            // Setup SVG
            svg.attr("viewBox", [0, 0, width, height]);
            
            // Setup zoom behavior
            const zoom = d3.zoom()
                .scaleExtent([0.1, 8])
                .on("zoom", (event) => {
                    transform = event.transform;
                    container.attr("transform", transform);
                    updateStatusBar();
                });
            
            svg.call(zoom);
            container = svg.append("g");
            
            // Smart force simulation based on network size
            const nodeCount = graphData.nodes.length;
            const linkDistance = nodeCount > 1000 ? 30 : nodeCount > 500 ? 50 : 80;
            const chargeStrength = nodeCount > 1000 ? -50 : nodeCount > 500 ? -150 : -300;
            
            simulation = d3.forceSimulation(graphData.nodes)
                .force("link", d3.forceLink(graphData.links)
                    .id(d => d.id)
                    .distance(linkDistance)
                    .strength(0.5))
                .force("charge", d3.forceManyBody().strength(chargeStrength))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide()
                    .radius(d => (d.size || 15) + 5)
                    .strength(0.7))
                .alphaDecay({% if is_large_network %}0.05{% else %}0.03{% endif %})
                .velocityDecay(0.4);

            console.log(`Simulation started with ${graphData.nodes.length} nodes`);
            
            // Create links
            link = container.append("g")
                .attr("class", "links")
                .selectAll("line")
                .data(graphData.links)
                .join("line")
                .attr("class", "link")
                .attr("stroke", d => d.color || "#999")
                .attr("stroke-width", d => Math.max(1, (d.width || 2)))
                .on("mouseover", function(event, d) {
                    if (!isLargeNetwork) {
                        showLinkTooltip(event, d);
                    }
                })
                .on("mouseout", hideTooltip);
            
            // Create nodes
            node = container.append("g")
                .attr("class", "nodes")
                .selectAll("g")
                .data(graphData.nodes)
                .join("g")
                .attr("class", "node")
                .call(drag(simulation));
            
            // Add shapes to nodes based on their properties
            node.each(function(d) {
                const nodeGroup = d3.select(this);
                const size = d.size || 15;
                const color = d.color || "#69b3a2";
                const shape = d.shape || "circle";
                
                if (shape === "square" || d.node_type === "btc_address") {
                    nodeGroup.append("rect")
                        .attr("width", size * 1.6)
                        .attr("height", size * 1.6)
                        .attr("x", -size * 0.8)
                        .attr("y", -size * 0.8)
                        .attr("rx", 3)
                        .attr("fill", color);
                } else if (shape === "triangle" || d.node_type === "tron_address") {
                    nodeGroup.append("polygon")
                        .attr("points", `0,${-size} ${size * 0.866},${size * 0.5} ${-size * 0.866},${size * 0.5}`)
                        .attr("fill", color);
                } else {
                    nodeGroup.append("circle")
                        .attr("r", size)
                        .attr("fill", color);
                }
            });
            
            // Add labels if network is small enough
            if (!isLargeNetwork && showLabels) {
                labels = node.append("text")
                    .attr("class", "node-label")
                    .text(d => {
                        const label = d.label || d.id;
                        return label.length > 20 ? label.substring(0, 20) + '...' : label;
                    })
                    .attr("dy", d => (d.size || 15) + 16)
                    .style("display", showLabels ? "block" : "none");
            }
            
            // Node interactions
            node
                .on("mouseover", function(event, d) {
                    showNodeTooltip(event, d);
                    if (!isLargeNetwork) {
                        highlightConnectedNodes(d);
                    }
                })
                .on("mouseout", function() {
                    hideTooltip();
                    if (!isLargeNetwork) {
                        resetHighlight();
                    }
                })
                .on("click", function(event, d) {
                    handleNodeClick(d);
                })
                .on("dblclick", function(event, d) {
                    focusOnNode(d);
                });
            
            // Update positions on tick
            simulation.on("tick", () => {
                console.log('Tick - alpha:', simulation.alpha());
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                node.attr("transform", d => `translate(${d.x},${d.y})`);
            });
            
            // Auto-stabilize for large networks
            if (isLargeNetwork) {
                setTimeout(() => {
                    if (simulation.alpha() > 0.1) {
                        simulation.alpha(0.1);
                    }
                }, 3000);
            }
            
            // Hide loading and show network
            setTimeout(() => {
                loading.style("display", "none");
                updateStatusBar();
                // Auto-center the graph
                setTimeout(centerGraph, 1000);
            }, 1000);
        }
        
        // Enhanced tooltip functions
        function showNodeTooltip(event, d) {
            const content = generateNodeTooltipContent(d);
            showTooltip(event, content);
        }
        
        function generateNodeTooltipContent(d) {
            if (d.type === 'domain') {
                const domainType = (d.domain_type || d.node_type || 'domain').replace('_', ' ');
                return `
                    <h4><i class="fas fa-globe"></i> ${d.label || d.id}</h4>
                    <div class="tooltip-content">
                        <div class="tooltip-row">
                            <strong>Type:</strong>
                            <span>${domainType}</span>
                        </div>
                        ${d.ip_address ? `<div class="tooltip-row"><strong>IP:</strong> <span>${d.ip_address}</span></div>` : ''}
                        ${d.url ? `<div class="tooltip-row"><strong>URL:</strong> <a href="${d.url}" target="_blank">Visit</a></div>` : ''}
                        ${d.screenshot ? `<div class="tooltip-row"><strong>Screenshot:</strong> <a href="${d.screenshot}" target="_blank">View</a></div>` : ''}
                        ${d.discovery_method ? `<div class="tooltip-row"><strong>Discovery:</strong> <span>${d.discovery_method}</span></div>` : ''}
                    </div>
                `;
            } else if (d.type === 'crypto') {
                return `
                    <h4><i class="fas fa-coins"></i> ${(d.chain || 'Crypto').toUpperCase()} Address</h4>
                    <div class="tooltip-content">
                        <div class="tooltip-row">
                            <strong>Chain:</strong>
                            <span>${(d.chain || 'Unknown').toUpperCase()}</span>
                        </div>
                        <div class="tooltip-row">
                            <strong>Address:</strong>
                        </div>
                        <div class="address-display">${d.full_address || d.id}</div>
                        ${d.explorer_url ? `<div class="tooltip-row" style="margin-top: 12px;"><a href="${d.explorer_url}" target="_blank"><i class="fas fa-external-link-alt"></i> View on Explorer</a></div>` : ''}
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
        
        // Interaction functions
        function highlightConnectedNodes(d) {
            const connectedNodes = new Set([d.id]);
            const connectedLinks = new Set();
            
            graphData.links.forEach(link => {
                const sourceId = link.source.id || link.source;
                const targetId = link.target.id || link.target;
                
                if (sourceId === d.id) {
                    connectedNodes.add(targetId);
                    connectedLinks.add(link);
                }
                if (targetId === d.id) {
                    connectedNodes.add(sourceId);
                    connectedLinks.add(link);
                }
            });
            
            node.style("opacity", n => connectedNodes.has(n.id) ? 1 : 0.2);
            link.style("opacity", l => connectedLinks.has(l) ? 0.8 : 0.1);
        }
        
        function resetHighlight() {
            node.style("opacity", 1);
            link.style("opacity", 0.6);
        }
        
        function handleNodeClick(d) {
            if (d.type === 'domain' && d.url) {
                window.open(d.url, '_blank');
            } else if (d.type === 'crypto' && d.explorer_url) {
                window.open(d.explorer_url, '_blank');
            }
        }
        
        function focusOnNode(d) {
            const scale = Math.min(3, Math.max(1, 800 / graphData.nodes.length));
            const newTransform = d3.zoomIdentity
                .translate(width / 2 - d.x * scale, height / 2 - d.y * scale)
                .scale(scale);
            
            svg.transition()
                .duration(750)
                .call(d3.zoom().transform, newTransform);
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
            const icon = document.getElementById('physics-icon');
            const text = document.getElementById('physics-text');
            const button = event.target.closest('.control-button');
            
            if (physicsEnabled) {
                simulation.stop();
                button.classList.add('active');
                icon.className = 'fas fa-pause';
                text.textContent = 'Resume Physics';
                physicsEnabled = false;
            } else {
                simulation.restart();
                button.classList.remove('active');
                icon.className = 'fas fa-play';
                text.textContent = 'Pause Physics';
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
            const scale = Math.min(widthScale, heightScale, 3) * 0.85;
            
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
                const icon = document.getElementById('labels-icon');
                const text = document.getElementById('labels-text');
                icon.className = showLabels ? 'fas fa-tags' : 'far fa-tags';
                text.textContent = showLabels ? 'Hide Labels' : 'Show Labels';
            }
        }
        
        function resetView() {
            resetZoom();
            setTimeout(centerGraph, 500);
        }
        
        function updateStatusBar() {
            const scale = transform.k;
            const nodeCount = graphData.nodes.length;
            const linkCount = graphData.links.length;
            statusBar.text(`Nodes: ${nodeCount} | Links: ${linkCount} | Zoom: ${scale.toFixed(1)}x`);
        }
        
        // Drag behavior
        function drag(simulation) {
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.2).restart();
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
            console.log('DOM loaded, initializing visualization...');
            setTimeout(initializeVisualization, 200);
        });
    </script>
</body>
</html>"""

        return Template(template_str)

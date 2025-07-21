"""
Node Manager for Domain Network Visualization
Handles node data, styling, interactions, and rendering
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


@dataclass
class NodeStyle:
    """Configuration for node visual styling"""

    size: int = 20
    color: str = "#666666"
    stroke_color: str = "#333333"
    stroke_width: int = 2
    shape: str = "circle"  # circle, square, triangle
    label_size: int = 14
    label_color: str = "#333333"
    opacity: float = 0.8


@dataclass
class NodeData:
    """Individual node data structure"""

    id: str
    label: str
    type: str  # 'domain' or 'crypto'
    node_type: str  # 'source_domain', 'lookalike_domain', 'same_ip_domain', 'crypto_address'
    size: int
    color: str
    shape: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "label": self.label,
            "type": self.type,
            "node_type": self.node_type,
            "size": self.size,
            "color": self.color,
            "shape": self.shape,
            **self.metadata,
        }


class NodeManager:
    """Manages all node data and styling for the network visualization"""

    def __init__(self):
        self.nodes: Dict[str, NodeData] = {}
        self.node_styles = self._initialize_node_styles()
        self.node_counter = 0

    def _initialize_node_styles(self) -> Dict[str, NodeStyle]:
        """Initialize predefined node styles for different types"""
        return {
            "source_domain": NodeStyle(
                size=30,
                color="#e74c3c",  # Red
                stroke_color="#c0392b",
                stroke_width=3,
                shape="circle",
                label_size=16,
                label_color="#2c3e50",
                opacity=0.9,
            ),
            "lookalike_domain": NodeStyle(
                size=25,
                color="#3498db",  # Blue
                stroke_color="#2980b9",
                stroke_width=2,
                shape="circle",
                label_size=14,
                label_color="#2c3e50",
                opacity=0.8,
            ),
            "same_ip_domain": NodeStyle(
                size=25,
                color="#1abc9c",  # Teal
                stroke_color="#16a085",
                stroke_width=2,
                shape="circle",
                label_size=14,
                label_color="#2c3e50",
                opacity=0.8,
            ),
            "btc_address": NodeStyle(
                size=35,
                color="#f39c12",  # Orange
                stroke_color="#e67e22",
                stroke_width=3,
                shape="square",
                label_size=12,
                label_color="#2c3e50",
                opacity=0.9,
            ),
            "eth_address": NodeStyle(
                size=30,
                color="#9b59b6",  # Purple
                stroke_color="#8e44ad",
                stroke_width=2,
                shape="circle",
                label_size=12,
                label_color="#2c3e50",
                opacity=0.9,
            ),
            "tron_address": NodeStyle(
                size=30,
                color="#e74c3c",  # Red
                stroke_color="#c0392b",
                stroke_width=2,
                shape="triangle",
                label_size=12,
                label_color="#2c3e50",
                opacity=0.9,
            ),
        }

    def create_domain_node(self, domain_id: str, domain_type: str, metadata: Dict[str, Any]) -> NodeData:
        """Create a domain node with appropriate styling"""
        style = self.node_styles.get(domain_type, self.node_styles["source_domain"])

        # Create clean label (remove protocol prefixes)
        label = domain_id.replace("https://", "").replace("http://", "").replace("www.", "")
        if len(label) > 25:
            label = label[:22] + "..."

        node = NodeData(
            id=domain_id,
            label=label,
            type="domain",
            node_type=domain_type,
            size=style.size,
            color=style.color,
            shape=style.shape,
            metadata={
                "domain_type": domain_type,
                "ip_address": metadata.get("ip_address", ""),
                "screenshot": metadata.get("screenshot", ""),
                "url": metadata.get("url", ""),
                "inreach_intel_summary": metadata.get("inreach_intel_summary", ""),
                "discovery_method": metadata.get("discovery_method", ""),
                "style": {
                    "stroke_color": style.stroke_color,
                    "stroke_width": style.stroke_width,
                    "label_size": style.label_size,
                    "label_color": style.label_color,
                    "opacity": style.opacity,
                },
            },
        )

        self.nodes[domain_id] = node
        return node

    def create_crypto_node(self, address: str, chain: str, metadata: Dict[str, Any]) -> NodeData:
        """Create a crypto address node with appropriate styling"""
        node_type = f"{chain.lower()}_address"
        style = self.node_styles.get(node_type, self.node_styles["btc_address"])

        # Create readable label for crypto addresses
        if len(address) > 12:
            label = f"{address[:6]}...{address[-6:]}"
        else:
            label = address

        node = NodeData(
            id=address,
            label=label,
            type="crypto",
            node_type=node_type,
            size=style.size,
            color=style.color,
            shape=style.shape,
            metadata={
                "chain": chain,
                "full_address": address,
                "discovery_method": metadata.get("discovery_method", ""),
                "explorer_url": f"https://alterya_rnd.alterya.io/explorer/{chain}/{address}/overview",
                "style": {
                    "stroke_color": style.stroke_color,
                    "stroke_width": style.stroke_width,
                    "label_size": style.label_size,
                    "label_color": style.label_color,
                    "opacity": style.opacity,
                },
            },
        )

        self.nodes[address] = node
        return node

    def get_node(self, node_id: str) -> Optional[NodeData]:
        """Get a node by ID"""
        return self.nodes.get(node_id)

    def get_all_nodes(self) -> List[NodeData]:
        """Get all nodes as a list"""
        return list(self.nodes.values())

    def get_nodes_by_type(self, node_type: str) -> List[NodeData]:
        """Get all nodes of a specific type"""
        return [node for node in self.nodes.values() if node.node_type == node_type]

    def get_domain_nodes(self) -> List[NodeData]:
        """Get all domain nodes"""
        return [node for node in self.nodes.values() if node.type == "domain"]

    def get_crypto_nodes(self) -> List[NodeData]:
        """Get all crypto nodes"""
        return [node for node in self.nodes.values() if node.type == "crypto"]

    def update_node_style(self, node_id: str, style_updates: Dict[str, Any]) -> bool:
        """Update node styling"""
        if node_id not in self.nodes:
            return False

        node = self.nodes[node_id]
        for key, value in style_updates.items():
            if key in ["size", "color", "shape"]:
                setattr(node, key, value)
            elif key in node.metadata.get("style", {}):
                node.metadata["style"][key] = value

        return True

    def export_nodes_json(self) -> str:
        """Export all nodes to JSON format"""
        nodes_data = [node.to_dict() for node in self.nodes.values()]
        return json.dumps(nodes_data, indent=2)

    def export_nodes_for_d3(self) -> List[Dict[str, Any]]:
        """Export nodes in D3.js compatible format"""
        return [node.to_dict() for node in self.nodes.values()]

    def get_node_statistics(self) -> Dict[str, Any]:
        """Get statistics about the nodes"""
        stats = {
            "total_nodes": len(self.nodes),
            "domain_nodes": len(self.get_domain_nodes()),
            "crypto_nodes": len(self.get_crypto_nodes()),
            "by_type": {},
        }

        # Count by node type
        for node in self.nodes.values():
            node_type = node.node_type
            if node_type not in stats["by_type"]:
                stats["by_type"][node_type] = 0
            stats["by_type"][node_type] += 1

        return stats

    def clear_all_nodes(self):
        """Clear all nodes"""
        self.nodes.clear()
        self.node_counter = 0

    def get_tooltip_content(self, node: NodeData) -> str:
        """Generate rich tooltip content for a node"""
        if node.type == "domain":
            return self._get_domain_tooltip(node)
        elif node.type == "crypto":
            return self._get_crypto_tooltip(node)
        return f"<h4>{node.label}</h4>"

    def _get_domain_tooltip(self, node: NodeData) -> str:
        """Generate tooltip for domain nodes"""
        domain_type = node.metadata.get("domain_type", "unknown").replace("_", " ").title()
        ip_address = node.metadata.get("ip_address", "N/A")
        screenshot = node.metadata.get("screenshot", "")
        url = node.metadata.get("url", "")
        intel = node.metadata.get("inreach_intel_summary", "")
        discovery = node.metadata.get("discovery_method", "N/A")

        content = f"""
        <div class="tooltip-header">
            <h4><i class="fas fa-globe"></i> {node.label}</h4>
            <span class="tooltip-type">{domain_type}</span>
        </div>
        <div class="tooltip-content">
            <div class="tooltip-row">
                <strong>IP Address:</strong> {ip_address}
            </div>
            <div class="tooltip-row">
                <strong>Discovery:</strong> {discovery}
            </div>
        """

        if url:
            content += f'<div class="tooltip-row"><strong>URL:</strong> <a href="{url}" target="_blank" class="tooltip-link">{url}</a></div>'

        if intel:
            intel_preview = intel[:100] + "..." if len(intel) > 100 else intel
            content += f'<div class="tooltip-row"><strong>Intelligence:</strong> {intel_preview}</div>'

        if screenshot:
            content += f'<div class="tooltip-row"><strong>Screenshot:</strong> <a href="{screenshot}" target="_blank" class="tooltip-link">View Screenshot</a></div>'

        content += "</div>"
        return content

    def _get_crypto_tooltip(self, node: NodeData) -> str:
        """Generate tooltip for crypto nodes"""
        chain = node.metadata.get("chain", "Unknown")
        full_address = node.metadata.get("full_address", node.id)
        explorer_url = node.metadata.get("explorer_url", "")
        discovery = node.metadata.get("discovery_method", "N/A")

        content = f"""
        <div class="tooltip-header">
            <h4><i class="fas fa-coins"></i> {chain.upper()} Address</h4>
            <span class="tooltip-type crypto-badge">{chain.upper()}</span>
        </div>
        <div class="tooltip-content">
            <div class="tooltip-row">
                <strong>Address:</strong> 
                <div class="address-display">{full_address}</div>
            </div>
            <div class="tooltip-row">
                <strong>Chain:</strong> {chain.upper()}
            </div>
            <div class="tooltip-row">
                <strong>Discovery:</strong> {discovery}
            </div>
            <div class="tooltip-row">
                <a href="{explorer_url}" target="_blank" class="tooltip-explorer-link">
                    <i class="fas fa-external-link-alt"></i> View on Explorer
                </a>
            </div>
        </div>
        """

        return content

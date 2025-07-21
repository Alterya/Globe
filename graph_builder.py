"""
Domain Network Graph Builder
Builds NetworkX graphs from CSV data with enhanced node management
"""

import json
import logging
from typing import Any, Dict, List, Set, Tuple

import networkx as nx
import pandas as pd
from node_manager import NodeData, NodeManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DomainNetworkBuilder:
    """Builds and manages domain network graphs with enhanced node handling"""

    def __init__(self) -> None:
        self.graph = nx.Graph()
        self.node_manager = NodeManager()
        self.edges: List[Dict[str, Any]] = []
        self.processed_rows = 0
        self.skipped_rows = 0

    def load_csv_data(self, csv_file_path: str) -> pd.DataFrame:
        """Load and validate CSV data"""
        try:
            df = pd.read_csv(csv_file_path)
            logger.info(f"Loaded {len(df)} rows from {csv_file_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate the data"""
        original_count = len(df)

        # Remove rows where source_domain is missing
        df = df.dropna(subset=["source_domain"])

        # Remove rows where all key columns are missing
        key_columns = ["lookalike_domain", "same_ip_domain", "crypto_address"]
        df = df.dropna(subset=key_columns, how="all")

        cleaned_count = len(df)
        removed_count = original_count - cleaned_count

        logger.info(f"Cleaned data: {cleaned_count} rows remaining ({removed_count} removed)")

        return df

    def build_graph(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Build the complete network graph"""
        logger.info("Building network graph...")

        # Clear previous data
        self.graph.clear()
        self.node_manager.clear_all_nodes()
        self.edges = []
        self.processed_rows = 0
        self.skipped_rows = 0

        # Process each row
        for index, row in df.iterrows():
            try:
                self._process_row(row)
                self.processed_rows += 1
            except Exception as e:
                logger.warning(f"Error processing row {index}: {str(e)}")
                self.skipped_rows += 1

        # Add node attributes to graph
        self._add_node_attributes_to_graph()

        # Generate network statistics
        stats = self._generate_statistics()

        logger.info(f"Graph built successfully: {stats}")

        return {"nodes": self.node_manager.export_nodes_for_d3(), "links": self.edges, "statistics": stats}

    def _process_row(self, row: pd.Series) -> None:
        """Process a single row of data"""
        source_domain = self._normalize_domain(row["source_domain"])
        if not source_domain:
            return

        # Create source domain node
        source_node = self._create_or_get_domain_node(
            source_domain,
            "source_domain",
            {
                "ip_address": row.get("IPs", ""),
                "screenshot": row.get("screenshot", ""),
                "url": source_domain,
                "inreach_intel_summary": row.get("inreach_intel_summary", ""),
                "discovery_method": row.get("discovery_method", ""),
            },
        )

        # Process lookalike domains
        if pd.notna(row.get("lookalike_domain")):
            lookalike_domains = self._parse_domain_list(row["lookalike_domain"])
            for domain in lookalike_domains:
                self._create_domain_relationship(source_domain, domain, "lookalike_domain", row)

        # Process same IP domains
        if pd.notna(row.get("same_ip_domain")):
            same_ip_domains = self._parse_domain_list(row["same_ip_domain"])
            for domain in same_ip_domains:
                self._create_domain_relationship(source_domain, domain, "same_ip_domain", row)

        # Process crypto addresses
        if pd.notna(row.get("crypto_address")):
            crypto_addresses = self._parse_crypto_list(row["crypto_address"])
            chain = row.get("chain", "BTC")
            for address in crypto_addresses:
                self._create_crypto_relationship(source_domain, address, chain, row)

    def _create_or_get_domain_node(self, domain: str, domain_type: str, metadata: Dict[str, Any]) -> NodeData:
        """Create or retrieve a domain node"""
        existing_node = self.node_manager.get_node(domain)
        if existing_node:
            return existing_node

        return self.node_manager.create_domain_node(domain, domain_type, metadata)

    def _create_or_get_crypto_node(self, address: str, chain: str, metadata: Dict[str, Any]) -> NodeData:
        """Create or retrieve a crypto node"""
        existing_node = self.node_manager.get_node(address)
        if existing_node:
            return existing_node

        return self.node_manager.create_crypto_node(address, chain, metadata)

    def _create_domain_relationship(
        self, source_domain: str, target_domain: str, relationship_type: str, row: pd.Series
    ) -> None:
        """Create a domain-to-domain relationship"""
        target_domain = self._normalize_domain(target_domain)
        if not target_domain or target_domain == source_domain:
            return

        # Create target domain node
        target_node = self._create_or_get_domain_node(
            target_domain,
            relationship_type,
            {
                "ip_address": row.get("IPs", ""),
                "screenshot": row.get("screenshot", ""),
                "url": target_domain,
                "inreach_intel_summary": row.get("inreach_intel_summary", ""),
                "discovery_method": row.get("discovery_method", ""),
            },
        )

        # Create edge
        edge = {
            "source": source_domain,
            "target": target_domain,
            "type": relationship_type,
            "discovery_method": row.get("discovery_method", ""),
            "color": self._get_edge_color(relationship_type),
        }

        self.edges.append(edge)
        self.graph.add_edge(source_domain, target_domain, **edge)

    def _create_crypto_relationship(self, source_domain: str, crypto_address: str, chain: str, row: pd.Series) -> None:
        """Create a domain-to-crypto relationship"""
        if not crypto_address:
            return

        # Create crypto node
        crypto_node = self._create_or_get_crypto_node(
            crypto_address, chain, {"discovery_method": row.get("discovery_method", ""), "source_domain": source_domain}
        )

        # Create edge
        edge = {
            "source": source_domain,
            "target": crypto_address,
            "type": "domain_to_crypto",
            "chain": chain,
            "discovery_method": row.get("discovery_method", ""),
            "color": self._get_edge_color("domain_to_crypto"),
        }

        self.edges.append(edge)
        self.graph.add_edge(source_domain, crypto_address, **edge)

    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain name"""
        if pd.isna(domain):
            return ""

        domain = str(domain).strip().lower()

        # Remove protocol prefixes
        domain = domain.replace("https://", "").replace("http://", "")

        # Remove www prefix
        if domain.startswith("www."):
            domain = domain[4:]

        # Remove trailing slash
        domain = domain.rstrip("/")

        return domain

    def _parse_domain_list(self, domain_string: str) -> List[str]:
        """Parse comma-separated domain list"""
        if pd.isna(domain_string):
            return []

        domains = []
        for domain in str(domain_string).split(","):
            normalized = self._normalize_domain(domain.strip())
            if normalized:
                domains.append(normalized)

        return domains

    def _parse_crypto_list(self, crypto_string: str) -> List[str]:
        """Parse comma-separated crypto address list"""
        if pd.isna(crypto_string):
            return []

        addresses = []
        for address in str(crypto_string).split(","):
            address = address.strip()
            if address:
                addresses.append(address)

        return addresses

    def _get_edge_color(self, edge_type: str) -> str:
        """Get color for edge type"""
        color_map = {
            "lookalike_domain": "#3498db",  # Blue
            "same_ip_domain": "#f39c12",  # Orange
            "domain_to_crypto": "#e74c3c",  # Red
        }
        return color_map.get(edge_type, "#95a5a6")  # Default gray

    def _generate_statistics(self) -> Dict[str, Any]:
        """Generate network statistics"""
        node_stats = self.node_manager.get_node_statistics()

        # Count edges by type
        edge_counts: Dict[str, int] = {}
        for edge in self.edges:
            edge_type = edge["type"]
            edge_counts[edge_type] = edge_counts.get(edge_type, 0) + 1

        stats = {
            "nodes": node_stats["total_nodes"],
            "edges": len(self.edges),
            "processed_rows": self.processed_rows,
            "skipped_rows": self.skipped_rows,
            "node_breakdown": node_stats["by_type"],
            "edge_breakdown": edge_counts,
            "network_density": nx.density(self.graph) if self.graph.number_of_nodes() > 0 else 0,
        }

        return stats

    def _add_node_attributes_to_graph(self) -> None:
        """Add attributes from NodeManager to NetworkX graph nodes"""
        for node in self.node_manager.get_all_nodes():
            self.graph.add_node(node.id, **node.to_dict())

    def export_json(self, output_path: str) -> None:
        """Export graph data to JSON file"""
        data = {
            "nodes": self.node_manager.export_nodes_for_d3(),
            "links": self.edges,
            "statistics": self._generate_statistics(),
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Graph data exported to {output_path}")

    def get_networkx_graph(self) -> nx.Graph:
        """Get the NetworkX graph object"""
        return self.graph

    def get_node_manager(self) -> NodeManager:
        """Get the node manager"""
        return self.node_manager

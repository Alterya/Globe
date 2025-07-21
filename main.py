#!/usr/bin/env python3
"""
Domain Network Visualization Tool - Main Entry Point
Enhanced with NodeManager for better node handling and interactions
"""

import argparse
import logging
import os
import sys
from typing import Optional

from graph_builder import DomainNetworkBuilder
from unified_html_generator import UnifiedHTMLGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_output_directory(output_path: str) -> str:
    """Create output directory if it doesn't exist"""
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Created output directory: {output_dir}")
    return output_path


def main() -> None:
    """Main entry point for the domain network visualization tool"""
    parser = argparse.ArgumentParser(
        description="Generate interactive domain network visualizations from CSV data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py data.csv                          # Basic usage
  python main.py data.csv -o custom_output.html   # Custom output path
  python main.py data.csv --json network.json     # Export JSON data
  python main.py data.csv --width 1400 --height 900  # Custom dimensions
        """,
    )

    # Required arguments
    parser.add_argument("csv_file", help="Path to the CSV file containing domain and crypto address data")

    # Optional arguments
    parser.add_argument(
        "-o",
        "--output",
        default="output/network.html",
        help="Output path for the HTML visualization (default: output/network.html)",
    )

    parser.add_argument("--json", help="Export network data to JSON file (optional)")

    parser.add_argument("--width", type=int, default=1200, help="Width of the visualization canvas (default: 1200)")

    parser.add_argument("--height", type=int, default=800, help="Height of the visualization canvas (default: 800)")

    parser.add_argument(
        "--force-layout",
        choices=["force", "circular", "hierarchical"],
        default="force",
        help="Layout algorithm for the network (default: force)",
    )

    parser.add_argument(
        "--node-size-multiplier", type=float, default=1.0, help="Multiplier for node sizes (default: 1.0)"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Validate input file
        if not os.path.exists(args.csv_file):
            logger.error(f"Input CSV file not found: {args.csv_file}")
            sys.exit(1)

        logger.info(f"🚀 Starting domain network visualization")
        logger.info(f"📁 Input file: {args.csv_file}")
        logger.info(f"📊 Output file: {args.output}")

        # Step 1: Load and clean data
        logger.info("📥 Step 1: Loading and cleaning data...")
        builder = DomainNetworkBuilder()
        df = builder.load_csv_data(args.csv_file)
        clean_df = builder.clean_data(df)

        if len(clean_df) == 0:
            logger.error("❌ No valid data found after cleaning. Please check your CSV format.")
            sys.exit(1)

        # Step 2: Build network graph
        logger.info("🔨 Step 2: Building network graph...")
        network_data = builder.build_graph(clean_df)

        # Display statistics
        stats = network_data["statistics"]
        logger.info("📈 Network Statistics:")
        logger.info(f"   • Total nodes: {stats['nodes']}")
        logger.info(f"   • Total edges: {stats['edges']}")
        logger.info(f"   • Processed rows: {stats['processed_rows']}")
        if stats["skipped_rows"] > 0:
            logger.warning(f"   • Skipped rows: {stats['skipped_rows']}")

        logger.info("   • Node breakdown:")
        for node_type, count in stats["node_breakdown"].items():
            logger.info(f"     - {node_type.replace('_', ' ').title()}: {count}")

        logger.info("   • Edge breakdown:")
        for edge_type, count in stats["edge_breakdown"].items():
            logger.info(f"     - {edge_type.replace('_', ' ').title()}: {count}")

        logger.info(f"   • Network density: {stats['network_density']:.4f}")

        # Step 3: Export JSON if requested
        if args.json:
            logger.info(f"💾 Step 3a: Exporting JSON data to {args.json}")
            create_output_directory(args.json)
            builder.export_json(args.json)

        # Step 4: Generate HTML visualization
        logger.info("🎨 Step 3: Generating interactive HTML visualization...")
        create_output_directory(args.output)

        # Configure HTML generator
        html_generator = UnifiedHTMLGenerator()

        # Generate HTML using the existing interface
        html_content = html_generator.create_html(
            graph=builder.get_networkx_graph(),
            title=f"Domain Network Visualization - {os.path.basename(args.csv_file)}",
            width=args.width,
            height=args.height,
        )

        # Save HTML file
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info("✅ Visualization completed successfully!")
        logger.info(f"🌐 Open the following file in your browser: {os.path.abspath(args.output)}")

        # Additional output information
        if os.path.exists(args.output):
            file_size = os.path.getsize(args.output) / (1024 * 1024)  # MB
            logger.info(f"📄 Output file size: {file_size:.2f} MB")

        # Summary recommendations
        if stats["nodes"] > 500:
            logger.info("💡 Large network detected. Consider using filters or focusing on specific domains.")

        if stats["network_density"] > 0.3:
            logger.info("💡 Dense network detected. You may want to adjust the layout algorithm.")

    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ An error occurred: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

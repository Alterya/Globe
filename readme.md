# 🌐 Enhanced Domain Network Visualization Tool

An **advanced interactive domain network visualization tool** that generates beautiful, modern HTML network graphs from CSV data containing domain-related connections and cryptocurrency addresses. Features a sleek design with enhanced user experience and professional-grade visualizations.

## ✨ Key Features

### 🎨 **Modern Design & UX**
- **Gradient UI**: Beautiful modern interface with Inter font and smooth animations
- **Responsive Layout**: Optimized for desktop and mobile devices
- **Loading States**: Professional loading animations and status updates
- **Modern Icons**: FontAwesome integration for enhanced visual experience

### 🔍 **Interactive Network Graph**
- **Force-Directed Layout**: Advanced physics simulation with collision detection
- **Smooth Zoom & Pan**: Professional-grade navigation with momentum
- **Node Highlighting**: Intelligent connected node highlighting on hover
- **Rich Tooltips**: Contextual information with screenshots and intelligence data
- **Search & Filter**: Real-time network search with visual feedback

### 📊 **Node Types & Visualization**
- **🔴 Source Domains**: Red circles - original domains under investigation
- **🟢 Lookalike Domains**: Teal circles - suspicious lookalike domains  
- **🔵 Same IP Domains**: Blue circles - domains sharing IP addresses
- **🟠 Bitcoin (BTC)**: Orange rounded squares - Bitcoin addresses
- **🔵 Ethereum (ETH)**: Blue circles - Ethereum addresses
- **🔺 Tron (TRON)**: Red triangles - Tron addresses

### 🔗 **Relationship Types**
- **🔴 Domain → Crypto**: Red lines connecting domains to crypto addresses
- **🔵 Lookalike Domain**: Blue lines connecting lookalike domain relationships  
- **🟡 Same IP Domain**: Yellow/orange lines connecting same IP relationships

### 🛠️ **Advanced Controls**
- **Physics Toggle**: Start/stop force simulation
- **Auto-Center**: Intelligent graph centering and fitting
- **Label Control**: Show/hide node labels
- **PNG Export**: High-quality image export functionality
- **Status Bar**: Real-time network statistics and zoom level

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Poetry** (for dependency management)

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd scripts/nir_scripts/domain_network_visualization
   ```

2. **Install dependencies using Poetry:**
   ```bash
   poetry install
   ```

3. **Activate the Poetry environment:**
   ```bash
   poetry shell
   ```

### Basic Usage

Generate a network visualization from your CSV data:

```bash
python main.py path/to/your/data.csv
```

**Example with the Japan VASP data:**
```bash
python main.py "../domain_and_addresses_inreach/visualization_plot/japan_vasp_output/Japan_VASP_data.csv" \
  --output "output/japan_vasp_network.html" \
  --title "Japan VASP Network Analysis"
```

### Command Line Options

```bash
python main.py INPUT_FILE [OPTIONS]

Arguments:
  INPUT_FILE                Path to CSV file containing domain data

Options:
  --output, -o OUTPUT       Output HTML file path (default: output/network.html)
  --json-output JSON_PATH   Optional path to save graph JSON data
  --title TITLE             Title for the visualization
  --width WIDTH             Canvas width (default: 1200)
  --height HEIGHT           Canvas height (default: 800)
  --help                    Show help message
```

## 📊 Input Data Format

Your CSV file should contain the following columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `source_domain` | Original domain | ✅ Yes | `cruxatlanticexchange.trade` |
| `lookalike_domain` | Lookalike/suspicious domain | No | `cruxatlanticexchange.trade` |
| `same_ip_domain` | Domain sharing same IP | No | `similar-site.com` |
| `screenshot` | URL to domain screenshot | No | `https://urlscan.io/screenshots/...` |
| `crypto_address` | Cryptocurrency address | ✅ Yes | `0x184517198110570b6cde...` |
| `chain` | Cryptocurrency chain | ✅ Yes | `ETH`, `BTC`, `TRON` |
| `discovery_method` | How connection was discovered | No | `lookalike_source` |
| `source_domain_ip` | IP address of source domain | No | `209.222.98.191` |
| `lookalike_domain_ip` | IP of lookalike domain | No | `209.222.98.191` |
| `same_ip_domain_ip` | IP of same IP domain | No | `209.222.98.191` |
| `inreach_checked` | Whether inreach was checked | No | `Yes`, `No` |
| `inreach_intel_available` | Intel availability status | No | `Yes`, `No` |
| `inreach_intel_summary` | Summary of intelligence data | No | `Platforms: Website:...` |

### Sample CSV Row

```csv
source_domain,lookalike_domain,same_ip_domain,screenshot,crypto_address,chain,discovery_method,source_domain_ip,lookalike_domain_ip,same_ip_domain_ip,inreach_checked,inreach_intel_available,inreach_intel_summary
cruxatlanticexchange.trade,cruxatlanticexchange.trade,,https://urlscan.io/screenshots/example.png,0x184517198110570b6cde722633bf7221a345624d,eth,lookalike_source,209.222.98.191,209.222.98.191,,Yes,Yes,Platforms: Website:cruxatlanticexchange.trade
```

## 🎨 Enhanced Visualization Features

### Modern Interface Design
- **CSS Variables**: Consistent theming with professional color palette
- **Smooth Animations**: Fade-in effects and smooth transitions
- **Card-Based Layout**: Clean, organized information architecture
- **Hover Effects**: Subtle micro-interactions for better UX

### Interactive Controls
- **Enhanced Search**: Multi-field search with real-time results
- **Smart Tooltips**: Context-aware positioning and rich content
- **Keyboard Navigation**: Accessible interaction patterns
- **Double-Click Focus**: Double-click nodes to focus view

### Advanced Features
- **Network Statistics**: Real-time metrics display
- **Intelligence Coverage**: Percentage of connections with threat intel
- **Export Functionality**: High-quality PNG export
- **Status Updates**: Live feedback on user actions

## 🏗️ Project Structure

```
domain_network_visualization/
├── main.py                 # Enhanced CLI entry point
├── graph_builder.py        # CSV parsing and NetworkX graph construction
├── html_generator.py       # Modern D3.js HTML visualization generator
├── pyproject.toml          # Poetry config with updated dependencies
├── README.md              # This enhanced documentation
└── output/                # Generated HTML files
    └── network.html       # Default output location
```

## 🔧 Advanced Usage Examples

### Large Dataset Visualization
```bash
python main.py large_dataset.csv \
  --width 1600 --height 1200 \
  --title "Enterprise Network Analysis" \
  --json-output network_data.json
```

### Multiple Dataset Analysis
```bash
# Japan VASP analysis
python main.py japan_vasp_data.csv \
  --output reports/japan_vasp.html \
  --title "Japan VASP Network Analysis"

# Compare with other regional data
python main.py europe_data.csv \
  --output reports/europe_analysis.html \
  --title "European Domain Network"
```

### Research and Export
```bash
# Generate visualization with data export
python main.py research_data.csv \
  --json-output analysis/graph_structure.json \
  --title "Research Network Analysis" \
  --width 2000 --height 1500
```

## 📈 Output & Analysis

### Generated Files
1. **Interactive HTML**: Self-contained visualization with all dependencies
2. **JSON Export** (optional): Graph structure for programmatic analysis
3. **Console Statistics**: Comprehensive network metrics

### Example Output Statistics
```
📊 Network Statistics:
   • Total nodes: 549
   • Total edges: 1,291  
   • Domain nodes: 220
   • Crypto nodes: 329
   • Network density: 0.86%
   • Intelligence coverage: 61.8%
   
   • Edge types:
     - domain_to_crypto: 1,107
     - lookalike_domain: 184
     - same_ip_domain: 0
     
   • Crypto chains:
     - BTC: 131 addresses
     - ETH: 115 addresses  
     - TRON: 83 addresses
```

## 🎯 Use Cases & Applications

### Threat Intelligence Analysis
- **Lookalike Domain Detection**: Identify suspicious domain variants
- **Infrastructure Mapping**: Understand threat actor infrastructure
- **Crypto Address Clustering**: Track financial flows across networks

### Research & Investigation
- **Network Topology Analysis**: Understand connection patterns
- **Campaign Attribution**: Link related malicious activities
- **Temporal Analysis**: Track evolution of threat networks

### Compliance & Reporting
- **Visual Evidence**: Generate professional visualizations for reports
- **Stakeholder Communication**: Clear, intuitive network representations
- **Audit Trails**: Document investigation processes and findings

## 🚀 Performance Optimizations

### Large Dataset Handling
- **Efficient Rendering**: Optimized D3.js force simulation
- **Smart Collision Detection**: Prevents node overlap without performance cost
- **Lazy Loading**: Progressive enhancement for better initial load times

### Browser Compatibility
- **Modern Browser Support**: Chrome, Firefox, Safari, Edge (latest versions)
- **Mobile Responsive**: Touch-friendly controls and adaptive layout
- **High DPI Support**: Crisp rendering on retina displays

## 🤝 Contributing & Development

### Enhancement Areas
- **Additional Crypto Chains**: Support for more blockchain networks
- **Advanced Filtering**: Time-based and attribute-based filters
- **3D Visualization**: Three-dimensional network representation
- **Machine Learning Integration**: Automated pattern detection
- **Real-time Updates**: Live data streaming capabilities

### Development Setup
```bash
# Install development dependencies
poetry install --group dev

# Code formatting
poetry run black .

# Linting
poetry run ruff check .
```

## 🔒 Security & Privacy

- **Client-Side Processing**: All data processing happens locally
- **No External Dependencies**: Self-contained HTML output
- **Sanitized URLs**: Safe handling of potentially malicious domains
- **Data Validation**: Input sanitization and validation

## 📝 License

This project is part of the Alterya MVP codebase. Please refer to the main project license for terms and conditions.

## 🆘 Troubleshooting

### Common Issues

**Issue**: Visualization appears empty or incomplete
**Solution**: Verify CSV format matches expected schema, check console for errors

**Issue**: Performance issues with large datasets (>1000 nodes)
**Solution**: Consider data filtering or use JSON export for programmatic analysis

**Issue**: Export functionality not working
**Solution**: Ensure modern browser with canvas support, check popup blockers

**Issue**: Mobile display issues
**Solution**: Use landscape orientation, consider desktop for complex networks

### Getting Help

For technical support:
1. Check CSV data format and required columns
2. Verify browser compatibility and JavaScript enabled
3. Review console output for detailed error messages
4. Test with smaller dataset to isolate issues

---

## 🎉 What's New in Version 0.2.0

### 🎨 **Design Overhaul**
- Complete UI redesign with modern gradient interface
- Professional typography with Inter font family
- Smooth animations and micro-interactions
- Responsive grid layouts and card-based design

### 🔧 **Enhanced Functionality**  
- PNG export capability for high-quality images
- Improved search with multi-field matching
- Smart tooltip positioning that stays in viewport
- Enhanced status bar with real-time metrics

### ⚡ **Performance Improvements**
- Optimized force simulation parameters
- Better collision detection algorithm
- Smoother zoom and pan operations
- Efficient highlighting and filtering

### 🎯 **User Experience**
- Loading animations and progress feedback
- Context-aware tooltips with icons
- Double-click to focus on nodes
- Professional color palette and shadows

**Happy Analyzing! 🎉** 
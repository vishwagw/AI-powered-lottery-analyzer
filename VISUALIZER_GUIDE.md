# Lottery Analyzer - Visualization Guide

## Overview

The Lottery Analyzer includes two powerful visualization tools:

1. **Static Visualizations**: High-quality PNG charts generated from command line
2. **Interactive Web Dashboard**: Real-time interactive dashboard using Streamlit

## Generated Visualizations

When you run `python generate_visualizations.py all`, the following files are created in `data/results/`:

### 📊 Static Charts (PNG Format)

| File | Description |
|------|-------------|
| `frequency_all.png` | Bar chart of top 20 most common numbers |
| `hot_cold_all.png` | Comparison of hot (frequent) vs cold (rare) numbers |
| `odd_even_all.png` | Distribution and patterns of odd/even numbers |
| `sum_distribution_all.png` | Histogram showing distribution of winning number sums |
| `consecutive_all.png` | Analysis of consecutive number patterns |
| `number_pairs_all.png` | Most common number pairs that appear together |
| `digit_distribution_all.png` | Distribution of last digits (0-9) |

### 🌐 Interactive Dashboard (HTML)

| File | Description |
|------|-------------|
| `dashboard_all.html` | Interactive Plotly dashboard with all charts |

Open `dashboard_all.html` in any web browser to interact with:
- Hover for details
- Zoom and pan features
- Toggle data series on/off
- Download individual charts

## Quick Start - Static Visualizations

### Generate All Visualizations

```bash
# Generate visualizations for all data
python generate_visualizations.py all

# Generate visualizations for DLB only
python generate_visualizations.py dlb

# Generate visualizations for NLB only
python generate_visualizations.py nlb
```

### View Results

PNG files are saved to `data/results/` and can be:
- Opened in any image viewer
- Inserted into presentations
- Shared with others
- Printed at high quality (300 DPI)

## Interactive Web Dashboard

The Streamlit dashboard provides a complete interactive experience.

### Launch Dashboard

```bash
streamlit run streamlit_app.py
```

This opens your browser to: `http://localhost:8501`

### Dashboard Features

#### 🎯 Main Metrics
- Total draws analyzed
- Unique numbers found
- Average sum of numbers
- Odd/Even ratio
- Active data source

#### 📊 Frequency Tab
- Top 20+ most common numbers with interactive bar chart
- Adjustable range (5-30 numbers)
- Table view of frequency data

#### 🔥 Hot/Cold Tab
- Hot numbers (frequently drawn)
- Cold numbers (rarely drawn)
- Visual distribution scatter plot

#### 🎯 Patterns Tab
- Odd/Even distribution pie chart
- Consecutive number analysis
- Visual pattern comparison

#### 📈 Statistics Tab
- Minimum, maximum, average, and median sums
- Distribution histogram with mean line
- Statistical summary box

#### 🔗 Pairs Tab
- Most common number pairs (configurable)
- Interactive bar chart (5-30 pairs)
- Detailed table of pair frequencies

#### 🔢 Digits Tab
- Last digit distribution (0-9)
- Pie chart and bar chart views
- Frequency analysis by digit

#### 📋 Data Tab
- Raw data table
- Download as CSV
- Data record count

### Dashboard Controls

**Left Sidebar:**
- Data Source selector (All/DLB/NLB)
- Action buttons for graph generation
- Refresh cache option
- Information and disclaimer

**Chart Controls:**
- Adjust number of items shown via sliders
- Hover for detailed values
- Click legend items to toggle series
- Download individual charts (camera icon)

## Python API - Programmatic Visualizations

### Basic Usage

```python
from visualizer import LotteryVisualizer
from database import LotteryDatabase

# Initialize
db = LotteryDatabase()
viz = LotteryVisualizer(db)

# Generate individual charts
viz.plot_number_frequency(source='all', top_n=20, save=True)
viz.plot_hot_cold_numbers(source='DLB')
viz.plot_odd_even_distribution(source='NLB')

# Generate interactive dashboard
viz.create_interactive_dashboard(source='all')

# Generate all visualizations at once
viz.generate_all_visualizations(source='all')

db.close()
```

### Available Methods

```python
# Number frequency analysis
fig = viz.plot_number_frequency(
    source='all',      # 'all', 'DLB', or 'NLB'
    top_n=20,         # Show top N numbers
    save=True         # Save PNG file
)

# Hot and cold numbers
fig = viz.plot_hot_cold_numbers(source='all', save=True)

# Odd/even distribution
fig = viz.plot_odd_even_distribution(source='all', save=True)

# Sum distribution
fig = viz.plot_sum_distribution(source='all', save=True)

# Consecutive numbers
fig = viz.plot_consecutive_analysis(source='all', save=True)

# Number pairs analysis
fig = viz.plot_number_pairs(source='all', top_n=15, save=True)

# Digit distribution
fig = viz.plot_digit_distribution(source='all', save=True)

# Interactive dashboard
fig = viz.create_interactive_dashboard(source='all')

# Generate all charts
viz.generate_all_visualizations(source='all')
```

## Common Workflows

### Workflow 1: Quick Overview
```bash
# Add sample data
python utils.py add-sample

# Analyze and view
python utils.py analyze

# Generate charts
python generate_visualizations.py all

# View PNG files in data/results/
```

### Workflow 2: Interactive Exploration
```bash
# Start dashboard
streamlit run streamlit_app.py

# Browse different data sources
# Adjust filters and ranges
# Download specific charts
```

### Workflow 3: Automated Report Generation
```python
from visualizer import LotteryVisualizer
from database import LotteryDatabase

db = LotteryDatabase()
viz = LotteryVisualizer(db)

# Generate comprehensive visualization set
for source in ['all', 'DLB', 'NLB']:
    print(f"Generating {source} visualizations...")
    viz.generate_all_visualizations(source=source)

db.close()
print("All reports generated!")
```

## Customization

### Change Output Directory

```python
from visualizer import LotteryVisualizer
from pathlib import Path

viz = LotteryVisualizer(output_dir=Path("custom/path/to/results"))
viz.generate_all_visualizations()
```

### Modify Chart Styling

Edit `visualizer.py` to customize:

```python
# Change color scheme
colors = plt.cm.viridis(np.linspace(0, 1, len(numbers)))

# Change figure size
plt.rcParams['figure.figsize'] = (16, 10)

# Change DPI for export
plt.savefig(output_file, dpi=600)
```

### Save Multiple Formats

```python
# Add this to visualizer.py methods:
import matplotlib.pyplot as plt

# Save as PNG
plt.savefig('chart.png', dpi=300)

# Save as PDF
plt.savefig('chart.pdf', dpi=300)

# Save as SVG
plt.savefig('chart.svg')

# Save as high-res TIFF
plt.savefig('chart.tiff', dpi=600)
```

## Dashboard Performance

### Memory Usage
- Small dataset (10-100 draws): ~50-100 MB
- Medium dataset (100-1000 draws): ~100-500 MB
- Large dataset (1000+ draws): ~500+ MB

### Load Times
- Dashboard startup: 5-15 seconds
- Data refresh: 2-5 seconds
- Chart generation: 1-3 seconds

### Tips for Large Datasets
1. Use data source filter (DLB/NLB) to reduce data
2. Reduce point count with slider controls
3. Close other applications to free memory
4. Use static visualizations instead of interactive dashboard

## Chart Export

### From Dashboard
1. Hover over any chart
2. Click the camera icon (📷)
3. Chart downloads as PNG

### From Command Line
```bash
# All PNG files in data/results/
python generate_visualizations.py all

# Individual charts through Python
from visualizer import LotteryVisualizer
viz = LotteryVisualizer()
viz.plot_number_frequency(save=True)
```

### Converting Formats
```bash
# Install ImageMagick
pip install pillow

# Convert PNG to JPG
from PIL import Image
img = Image.open('frequency_all.png')
img.save('frequency_all.jpg', 'JPEG', quality=95)
```

## Troubleshooting

### Dashboard won't start
```bash
# Clear Streamlit cache
streamlit cache clear

# Start dashboard with debug
streamlit run streamlit_app.py --logger.level=debug
```

### Charts look pixelated
- Increase DPI: Edit `plt.savefig(..., dpi=300)`
- Increase figure size: Edit `plt.rcParams['figure.figsize']`

### Out of memory error
- Reduce dataset size (filter by DLB/NLB)
- Close other applications
- Use static visualizations instead

### Charts not appearing
1. Verify data exists: `python utils.py view`
2. Check data directory: `ls data/results/`
3. Review log file: `cat lottery_analyzer.log`

## Integration with Other Tools

### Use in Jupyter Notebook
```python
from visualizer import LotteryVisualizer

viz = LotteryVisualizer()
fig = viz.plot_number_frequency(source='all', save=False)
fig.show()
```

### Embed in Reports
```python
# Generate charts
python generate_visualizations.py all

# Use in Python-DOCX
from docx import Document
doc = Document()
doc.add_picture('data/results/frequency_all.png')
doc.save('lottery_report.docx')
```

### Create Presentation
```python
from pptx import Presentation

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[5])
pic = slide.shapes.add_picture('frequency_all.png', 0, 0)
prs.save('lottery_analysis.pptx')
```

## Statistical Details

### What Each Chart Shows

**Frequency Chart**
- Which lottery numbers appear most often
- Helps identify "hot" numbers in the dataset
- Based on actual draw history

**Hot/Cold Chart**
- Hot: Numbers above average frequency
- Cold: Numbers below average frequency
- Useful for identifying patterns

**Odd/Even Chart**
- Percentage of odd vs even numbers
- Common patterns in draws (e.g., 3 odd, 3 even)
- Helps understand distribution bias

**Sum Distribution**
- Histogram of total sum values
- Mean marked with dashed line
- Shows range and central tendency

**Consecutive Numbers**
- How often consecutive numbers appear (e.g., 5-6)
- Total occurrences across all draws
- Percentage of affected draws

**Number Pairs**
- Which numbers appear together
- Helps identify correlated numbers
- Most frequent combinations

**Digit Distribution**
- Last digit of numbers (0-9)
- Pie and bar chart views
- Checks for digit bias

## Data Privacy

All analysis is performed locally:
- No data sent to external servers
- All files stored in `data/` directory
- SQLite database remains on your machine
- Safe to use with sensitive data

## Performance Tips

1. **Use Filters**: Select DLB or NLB for faster loading
2. **Batch Processing**: Generate visualizations once, view many times
3. **Static Charts**: Use PNG instead of interactive dashboard for presentations
4. **Cache Data**: Dashboard caches data for 5 minutes automatically
5. **Close Browser Tabs**: Reduce memory usage when not viewing

## Next Steps

1. **Try Sample Data**:
   ```bash
   python utils.py add-sample
   streamlit run streamlit_app.py
   ```

2. **Scrape Real Data**:
   ```bash
   python main.py
   python generate_visualizations.py all
   ```

3. **Create Custom Visualizations**:
   - Edit `visualizer.py` to add new chart types
   - Extend `PatternAnalyzer` for new analysis
   - Create themed dashboards for specific needs

---

**Dashboard Version**: 1.0  
**Last Updated**: March 6, 2024  
**Charts Generated**: 7 static + 1 interactive  
**Supported Data Sources**: DLB, NLB, Combined

# Lottery Analyzer

A Python application to scrape lottery numbers from Sri Lankan lottery websites (DLB and NLB) and analyze patterns in winning numbers.

## Features

- **Web Scraping**: Scrapes lottery results from:
  - Dharmaraja Lotteries Bureau (DLB) - https://www.dlb.lk/
  - National Lottery Bureau (NLB) - https://www.nlb.lk/

- **Data Storage**: Stores scraped data in SQLite database

- **Pattern Analysis**:
  - Number frequency analysis
  - Hot and cold number identification
  - Number pair patterns
  - Odd/even distribution
  - Consecutive number patterns
  - Sum and digit patterns

- **Reporting**: Generates detailed JSON reports with analysis results

## Project Structure

```
lottery_analyzer/
├── scrapers/
│   ├── dlb_scraper.py      # DLB website scraper
│   ├── nlb_scraper.py      # NLB website scraper
│   └── __init__.py
├── analysis/
│   ├── pattern_analyzer.py # Pattern analysis engine
│   └── __init__.py
├── data/                    # Data storage directory
│   └── results/            # Analysis results
├── config.py               # Configuration settings
├── database.py             # Database management
├── main.py                 # Main application
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

1. Clone/create the project directory
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the complete analysis:
```bash
python main.py
```

This will:
1. Scrape lottery numbers from both DLB and NLB websites
2. Store data in SQLite database
3. Perform comprehensive pattern analysis
4. Save results to JSON files in the `data/results/` directory

### Use individual components:

#### Scrape data only:
```python
from scrapers import DLBScraper, NLBScraper
from database import LotteryDatabase

db = LotteryDatabase()

# Scrape DLB
with DLBScraper() as scraper:
    results = scraper.scrape_lottery_results()
    # Store in database...

# Scrape NLB
with NLBScraper() as scraper:
    results = scraper.scrape_lottery_results()
    # Store in database...
```

#### Analyze data:
```python
from analysis import PatternAnalyzer

analyzer = PatternAnalyzer()
report = analyzer.generate_report(source='all')
```

## Configuration

Edit `config.py` to customize:
- Website URLs
- Scraper timeout values
- Browser headless mode
- Database location
- Output directories

## Dependencies

- **selenium**: Web scraping with JavaScript rendering
- **beautifulsoup4**: HTML parsing
- **pandas**: Data analysis
- **numpy**: Numerical computations
- **requests**: HTTP requests
- **lxml**: XML processing
- **webdriver-manager**: Automatic driver management

## Analysis Outputs

The analyzer generates reports containing:

1. **Number Frequency**: Which numbers appear most/least often
2. **Hot/Cold Numbers**: Frequently vs rarely drawn numbers
3. **Number Pairs**: Which numbers tend to appear together
4. **Sum Patterns**: Statistics on sum of winning numbers
5. **Consecutive Numbers**: Occurrences of consecutive numbers
6. **Odd/Even Distribution**: Ratio and patterns of odd/even numbers

## Database Schema

### dlb_numbers & nlb_numbers tables:
- `id`: Primary key
- `draw_date`: Date of the draw
- `draw_number`: Draw identifier
- `numbers`: Comma-separated winning numbers
- `winning_amount`: Prize amount (optional)
- `source`: DLB or NLB
- `scraped_at`: Timestamp when scraped

### analysis_results table:
- `id`: Primary key
- `analysis_type`: Type of analysis performed
- `pattern`: Specific pattern identified
- `frequency`: How often it appears
- `percentage`: Percentage occurrence
- `created_at`: When analysis was run

## Logging

All activities are logged to:
- Console output
- `lottery_analyzer.log` file

## Notes

- The scrapers use Selenium with headless Chrome for JavaScript-heavy websites
- Initial runs may take time as Chrome driver is downloaded
- Data is stored locally in SQLite database for quick access
- Analysis can be run repeatedly without re-scraping

## Future Enhancements

- Predictive modeling using machine learning
- Web interface for visualization
- Scheduled automatic scraping
- Email notifications for pattern alerts
- Export to multiple formats (CSV, PDF)

## Disclaimer

This tool is for educational and analytical purposes only. Lottery drawings are random events, and past patterns cannot guarantee future results. Use responsibly.

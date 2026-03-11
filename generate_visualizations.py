"""
Command-line tool to generate all visualizations
Usage: python generate_visualizations.py [source]
       python generate_visualizations.py all
       python generate_visualizations.py DLB
"""

import logging
import sys
from pathlib import Path

from visualizer import LotteryVisualizer
from database import LotteryDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Generate visualizations for lottery data"""
    
    # Get source from command line argument
    source = sys.argv[1].lower() if len(sys.argv) > 1 else 'all'
    
    if source not in ['all', 'dlb', 'nlb']:
        print("Usage: python generate_visualizations.py [all|dlb|nlb]")
        print("\nExamples:")
        print("  python generate_visualizations.py all    # Analyze all data")
        print("  python generate_visualizations.py dlb    # Analyze DLB only")
        print("  python generate_visualizations.py nlb    # Analyze NLB only")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("Lottery Visualization Generator")
    logger.info("=" * 60)
    logger.info(f"\nGenerating visualizations for: {source.upper()}")
    
    try:
        # Initialize database and visualizer
        db = LotteryDatabase()
        visualizer = LotteryVisualizer(db)
        
        # Check if data exists
        if source == 'all':
            dlb_count = len(db.get_dlb_numbers())
            nlb_count = len(db.get_nlb_numbers())
            total = dlb_count + nlb_count
        elif source == 'dlb':
            total = len(db.get_dlb_numbers())
        else:
            total = len(db.get_nlb_numbers())
        
        if total == 0:
            logger.warning(f"\n⚠️ No data found for {source.upper()}")
            logger.info("Add sample data first: python utils.py add-sample")
            db.close()
            sys.exit(1)
        
        logger.info(f"Found {total} records to analyze\n")
        
        # Generate visualizations
        logger.info("Generating static visualizations...")
        logger.info("  - Number Frequency...")
        visualizer.plot_number_frequency(source=source)
        
        logger.info("  - Hot/Cold Numbers...")
        visualizer.plot_hot_cold_numbers(source=source)
        
        logger.info("  - Odd/Even Distribution...")
        visualizer.plot_odd_even_distribution(source=source)
        
        logger.info("  - Sum Distribution...")
        visualizer.plot_sum_distribution(source=source)
        
        logger.info("  - Consecutive Numbers...")
        visualizer.plot_consecutive_analysis(source=source)
        
        logger.info("  - Number Pairs...")
        visualizer.plot_number_pairs(source=source)
        
        logger.info("  - Digit Distribution...")
        visualizer.plot_digit_distribution(source=source)
        
        logger.info("  - Interactive Dashboard...")
        visualizer.create_interactive_dashboard(source=source)
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Visualization generation complete!")
        logger.info("=" * 60)
        logger.info(f"\nOutput files saved to: data/results/")
        logger.info("\nGenerated files:")
        logger.info(f"  - frequency_{source.lower()}.png")
        logger.info(f"  - hot_cold_{source.lower()}.png")
        logger.info(f"  - odd_even_{source.lower()}.png")
        logger.info(f"  - sum_distribution_{source.lower()}.png")
        logger.info(f"  - consecutive_{source.lower()}.png")
        logger.info(f"  - number_pairs_{source.lower()}.png")
        logger.info(f"  - digit_distribution_{source.lower()}.png")
        logger.info(f"  - dashboard_{source.lower()}.html (Interactive)")
        
        db.close()
        
    except Exception as e:
        logger.error(f"\n❌ Error generating visualizations: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

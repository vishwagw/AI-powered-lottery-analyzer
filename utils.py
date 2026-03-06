"""
Utility functions for database management and testing
"""

import logging
from database import LotteryDatabase
from analysis import PatternAnalyzer
import json
from datetime import datetime
from config import RESULTS_DIR

logger = logging.getLogger(__name__)


def add_sample_data():
    """Add sample lottery data for testing"""
    logger.info("Adding sample lottery data...")
    
    db = LotteryDatabase()
    
    # Sample DLB data
    sample_dlb = [
        ("2024-01-15", "DLB-001", [12, 23, 34, 45, 56, 67]),
        ("2024-01-16", "DLB-002", [11, 22, 33, 44, 55, 66]),
        ("2024-01-17", "DLB-003", [5, 15, 25, 35, 45, 55]),
        ("2024-01-18", "DLB-004", [2, 13, 24, 35, 46, 57]),
        ("2024-01-19", "DLB-005", [10, 20, 30, 40, 50, 60]),
    ]
    
    # Sample NLB data
    sample_nlb = [
        ("2024-01-15", "NLB-001", [7, 14, 21, 28, 35, 42]),
        ("2024-01-16", "NLB-002", [3, 9, 17, 26, 37, 48]),
        ("2024-01-17", "NLB-003", [1, 8, 15, 22, 29, 36]),
        ("2024-01-18", "NLB-004", [4, 12, 20, 31, 41, 49]),
        ("2024-01-19", "NLB-005", [6, 16, 27, 38, 47, 58]),
    ]
    
    for draw_date, draw_num, numbers in sample_dlb:
        db.insert_dlb_numbers(draw_date, draw_num, numbers)
    
    for draw_date, draw_num, numbers in sample_nlb:
        db.insert_nlb_numbers(draw_date, draw_num, numbers)
    
    db.close()
    logger.info("Sample data added successfully!")


def view_database_content():
    """View all data in the database"""
    db = LotteryDatabase()
    
    print("\n" + "="*60)
    print("DATABASE CONTENT")
    print("="*60)
    
    dlb_data = db.get_dlb_numbers()
    print(f"\nDLB Records: {len(dlb_data)}")
    for record in dlb_data[:5]:
        print(f"  {record['draw_date']} - {record['draw_number']}: {record['numbers']}")
    
    nlb_data = db.get_nlb_numbers()
    print(f"\nNLB Records: {len(nlb_data)}")
    for record in nlb_data[:5]:
        print(f"  {record['draw_date']} - {record['draw_number']}: {record['numbers']}")
    
    db.close()


def export_data_to_csv():
    """Export lottery data to CSV files"""
    import pandas as pd
    
    db = LotteryDatabase()
    
    # Export DLB
    dlb_data = db.get_dlb_numbers()
    if dlb_data:
        df_dlb = pd.DataFrame(dlb_data)
        dlb_file = RESULTS_DIR / "dlb_numbers.csv"
        df_dlb.to_csv(dlb_file, index=False)
        logger.info(f"DLB data exported to: {dlb_file}")
    
    # Export NLB
    nlb_data = db.get_nlb_numbers()
    if nlb_data:
        df_nlb = pd.DataFrame(nlb_data)
        nlb_file = RESULTS_DIR / "nlb_numbers.csv"
        df_nlb.to_csv(nlb_file, index=False)
        logger.info(f"NLB data exported to: {nlb_file}")
    
    db.close()


def quick_analysis():
    """Run a quick analysis on available data"""
    db = LotteryDatabase()
    
    dlb_count = len(db.get_dlb_numbers())
    nlb_count = len(db.get_nlb_numbers())
    
    print("\n" + "="*60)
    print("QUICK ANALYSIS SUMMARY")
    print("="*60)
    print(f"DLB Records Available: {dlb_count}")
    print(f"NLB Records Available: {nlb_count}")
    print(f"Total Records: {dlb_count + nlb_count}")
    
    if dlb_count + nlb_count > 0:
        analyzer = PatternAnalyzer(db)
        
        print("\nRunning analysis on combined data...")
        report = analyzer.generate_report('all')
        
        if report:
            # Print key findings
            print("\nKey Findings:")
            if 'frequency_analysis' in report:
                freq = report['frequency_analysis']
                print(f"\n  Most Common Numbers:")
                for num, count in freq.get('most_common', [])[:5]:
                    print(f"    #{num}: {count} occurrences")
            
            if 'hot_cold_numbers' in report:
                hc = report['hot_cold_numbers']
                print(f"\n  Hot Numbers: {hc.get('hot_numbers', [])}")
                print(f"  Cold Numbers: {hc.get('cold_numbers', [])}")
    
    db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "add-sample":
            add_sample_data()
        elif command == "view":
            view_database_content()
        elif command == "export":
            export_data_to_csv()
        elif command == "analyze":
            quick_analysis()
        else:
            print("Unknown command. Use: add-sample, view, export, or analyze")
    else:
        print("Lottery Database Utility")
        print("\nUsage:")
        print("  python utils.py add-sample  - Add sample data for testing")
        print("  python utils.py view        - View all database content")
        print("  python utils.py export      - Export data to CSV files")
        print("  python utils.py analyze     - Run quick analysis")

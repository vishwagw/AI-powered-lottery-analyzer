"""
Visualization utilities - helper functions for working with visualizations
"""

import webbrowser
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def open_dashboard_in_browser(dashboard_path: str = "data/results/dashboard_all.html"):
    """Open the interactive dashboard in default web browser"""
    path = Path(dashboard_path)
    
    if not path.exists():
        logger.error(f"Dashboard not found: {dashboard_path}")
        print(f"❌ Dashboard file not found: {dashboard_path}")
        print("Generate it first with: python generate_visualizations.py all")
        return False
    
    try:
        file_url = path.resolve().as_uri()
        webbrowser.open(file_url)
        logger.info(f"Opened dashboard: {file_url}")
        print(f"✅ Opening dashboard in browser: {file_url}")
        return True
    except Exception as e:
        logger.error(f"Error opening browser: {e}")
        print(f"❌ Could not open browser automatically")
        print(f"Manual URL: {path.resolve().as_uri()}")
        return False


def list_visualizations(results_dir: str = "data/results/"):
    """List all generated visualizations"""
    results_path = Path(results_dir)
    
    if not results_path.exists():
        print(f"Results directory not found: {results_dir}")
        return
    
    # Organize by type
    png_files = sorted(results_path.glob("*.png"))
    html_files = sorted(results_path.glob("*.html"))
    csv_files = sorted(results_path.glob("*.csv"))
    
    print("\n" + "="*60)
    print("AVAILABLE VISUALIZATIONS")
    print("="*60)
    
    if png_files:
        print(f"\n📊 Static Charts (PNG) - {len(png_files)} files:")
        for file in png_files:
            size_kb = file.stat().st_size / 1024
            print(f"  • {file.name} ({size_kb:.1f} KB)")
    
    if html_files:
        print(f"\n🌐 Interactive Dashboards (HTML) - {len(html_files)} files:")
        for file in html_files:
            size_kb = file.stat().st_size / 1024
            print(f"  • {file.name} ({size_kb:.1f} KB)")
            print(f"    Open with: python viz_utils.py open-dashboard")
    
    if csv_files:
        print(f"\n📋 Data Exports (CSV) - {len(csv_files)} files:")
        for file in csv_files:
            size_kb = file.stat().st_size / 1024
            print(f"  • {file.name} ({size_kb:.1f} KB)")
    
    print("\n" + "="*60 + "\n")


def clean_visualizations(results_dir: str = "data/results/", keep_data: bool = True):
    """Clean up old visualization files"""
    results_path = Path(results_dir)
    
    if not results_path.exists():
        print(f"Results directory not found: {results_dir}")
        return
    
    deleted_count = 0
    
    # Delete PNG files
    for file in results_path.glob("*.png"):
        file.unlink()
        deleted_count += 1
        print(f"Deleted: {file.name}")
    
    # Delete HTML files
    for file in results_path.glob("*.html"):
        file.unlink()
        deleted_count += 1
        print(f"Deleted: {file.name}")
    
    # Keep CSV if requested
    if not keep_data:
        for file in results_path.glob("*.csv"):
            file.unlink()
            deleted_count += 1
            print(f"Deleted: {file.name}")
    
    print(f"\n✅ Cleaned up {deleted_count} visualization files")


def generate_quick_report(source: str = "all"):
    """Generate a quick visual report"""
    print("\n" + "="*60)
    print(f"GENERATING VISUALIZATIONS FOR: {source.upper()}")
    print("="*60 + "\n")
    
    from visualizer import LotteryVisualizer
    from database import LotteryDatabase
    
    db = LotteryDatabase()
    viz = LotteryVisualizer(db)
    
    try:
        viz.generate_all_visualizations(source=source)
        print("\n" + "="*60)
        print("✅ VISUALIZATIONS GENERATED SUCCESSFULLY")
        print("="*60)
        print(f"\nFiles saved to: data/results/")
        print(f"\nTo view interactive dashboard:")
        print(f"  python viz_utils.py open-dashboard")
        print(f"\nOr manually open:")
        print(f"  data/results/dashboard_{source.lower()}.html\n")
        
    except Exception as e:
        print(f"\n❌ Error generating visualizations: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            list_visualizations()
        
        elif command == "clean":
            keep_data = "--keep-data" in sys.argv or "-k" in sys.argv
            print(f"Cleaning visualizations (keep data={keep_data})...")
            clean_visualizations(keep_data=keep_data)
        
        elif command == "open-dashboard":
            source = "all"
            if len(sys.argv) > 2:
                source = sys.argv[2].lower()
            dashboard_file = f"data/results/dashboard_{source}.html"
            open_dashboard_in_browser(dashboard_file)
        
        elif command == "gen" or command == "generate":
            source = "all"
            if len(sys.argv) > 2:
                source = sys.argv[2].lower()
            generate_quick_report(source)
        
        else:
            print("Lottery Visualization Utilities\n")
            print("Usage:")
            print("  python viz_utils.py list                    - List all visualizations")
            print("  python viz_utils.py gen [source]            - Generate visualizations")
            print("  python viz_utils.py open-dashboard [source] - Open interactive dashboard")
            print("  python viz_utils.py clean [--keep-data]     - Clean old visualizations")
            print("\nExamples:")
            print("  python viz_utils.py list")
            print("  python viz_utils.py gen all")
            print("  python viz_utils.py gen dlb")
            print("  python viz_utils.py open-dashboard all")
            print("  python viz_utils.py clean -k")
    
    else:
        print("Lottery Visualization Utilities\n")
        print("Usage:")
        print("  python viz_utils.py [command] [options]\n")
        print("Commands:")
        print("  list                    - List all generated visualizations")
        print("  gen [source]            - Generate visualizations (all/dlb/nlb)")
        print("  open-dashboard [source] - Open interactive dashboard in browser")
        print("  clean [--keep-data]     - Clean old visualization files\n")
        print("Examples:")
        print("  python viz_utils.py list")
        print("  python viz_utils.py gen")
        print("  python viz_utils.py open-dashboard")

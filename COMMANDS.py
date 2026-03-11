#!/usr/bin/env python3
"""
Quick command reference - Copy & paste ready commands for lottery analyzer
"""

print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║        🎲 LOTTERY ANALYZER - QUICK COMMAND REFERENCE 🎲       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 VISUALIZATION COMMANDS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VIEW CHARTS (Already Generated!)
  Just open folder: data/results/
  Or:
    python viz_utils.py list

GENERATE ALL CHARTS
  python generate_visualizations.py all
  python generate_visualizations.py dlb
  python generate_visualizations.py nlb

OPEN INTERACTIVE DASHBOARD
  python viz_utils.py open-dashboard

START WEB DASHBOARD
  streamlit run streamlit_app.py

MANAGE VISUALIZATIONS
  python viz_utils.py list           # List all files
  python viz_utils.py gen all        # Generate charts
  python viz_utils.py clean          # Delete old files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💾 DATA MANAGEMENT COMMANDS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADD SAMPLE DATA
  python utils.py add-sample

VIEW DATA
  python utils.py view

ANALYZE DATA
  python utils.py analyze

EXPORT TO CSV
  python utils.py export

SCRAPE REAL DATA
  python main.py

INSPECT WEBSITES
  python inspect_websites.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 QUICK WORKFLOWS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WORKFLOW 1: First Time Users (5 minutes)
  Step 1: python utils.py add-sample
  Step 2: python generate_visualizations.py all
  Step 3: python viz_utils.py list
  Step 4: Open data/results/*.png

WORKFLOW 2: Interactive Exploration (10 minutes)
  Step 1: python utils.py add-sample
  Step 2: streamlit run streamlit_app.py
  Step 3: Explore in browser
  Step 4: Download charts you like

WORKFLOW 3: Create Presentation (15 minutes)
  Step 1: python utils.py add-sample
  Step 2: python generate_visualizations.py all
  Step 3: Open data/results/frequency_all.png (and others)
  Step 4: Insert PNG files into PowerPoint

WORKFLOW 4: Share with Others
  Step 1: python generate_visualizations.py all
  Step 2: Send data/results/dashboard_all.html
  Step 3: They open in browser (no software needed!)

WORKFLOW 5: Automated Reports
  Step 1: python main.py          # Scrape data
  Step 2: python generate_visualizations.py all  # Generate charts
  Step 3: Schedule to run weekly/monthly

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 DOCUMENTATION

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

START HERE (Pick One):
  1. VISUALIZATION_QUICKSTART.md    ← 3-step visual start
  2. QUICKSTART.md                  ← Overall quick start
  3. PROJECT_COMPLETE.md            ← Status report

DETAILED GUIDES:
  VISUALIZER_GUIDE.md       ← Full API reference
  SETUP_GUIDE.md            ← Detailed setup
  INDEX.md                  ← Navigation guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎨 CHART DESCRIPTIONS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. FREQUENCY CHART
   Shows: Most common numbers (top 20)
   File:  frequency_all.png
   Use:   Find popular numbers

2. HOT/COLD CHART
   Shows: Frequent vs rarely drawn
   File:  hot_cold_all.png
   Use:   Compare extremes

3. ODD/EVEN CHART
   Shows: Distribution balance
   File:  odd_even_all.png
   Use:   Understand patterns

4. SUM DISTRIBUTION
   Shows: Statistics on sums
   File:  sum_distribution_all.png
   Use:   Range and average

5. CONSECUTIVE NUMBERS
   Shows: Consecutive patterns
   File:  consecutive_all.png
   Use:   Pattern frequency

6. NUMBER PAIRS
   Shows: Numbers appearing together
   File:  number_pairs_all.png
   Use:   Correlated numbers

7. DIGIT DISTRIBUTION
   Shows: Last digit patterns (0-9)
   File:  digit_distribution_all.png
   Use:   Digit bias detection

8. INTERACTIVE DASHBOARD
   Shows: All charts interactive
   File:  dashboard_all.html
   Use:   Exploration & analysis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙️ CONFIGURATION

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EDIT SETTINGS (config.py):
  DLB_URL = "https://www.dlb.lk/"
  NLB_URL = "https://www.nlb.lk/"
  TIMEOUT = 15
  HEADLESS_BROWSER = True

EDIT VISUALIZATIONS (visualizer.py):
  Change colors: colors = ['#FF6B6B', ...]
  Change size: figsize = (16, 10)
  Change DPI: dpi=600

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 TROUBLESHOOTING

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROBLEM: No data shown
SOLUTION: python utils.py add-sample

PROBLEM: Charts look blurry
SOLUTION: Edit visualizer.py, change dpi=300 to dpi=600

PROBLEM: Dashboard won't open
SOLUTION: streamlit run streamlit_app.py

PROBLEM: Out of memory
SOLUTION: Use DLB or NLB filter (not All)

PROBLEM: Download/save errors
SOLUTION: Check permissions in data/results/ folder

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 FILE LOCATIONS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Data:
  data/lottery.db              ← SQLite database
  data/results/                ← All visualizations

Charts:
  data/results/frequency_all.png
  data/results/hot_cold_all.png
  data/results/odd_even_all.png
  data/results/sum_distribution_all.png
  data/results/consecutive_all.png
  data/results/number_pairs_all.png
  data/results/digit_distribution_all.png

Dashboard:
  data/results/dashboard_all.html

Data Export:
  data/results/dlb_numbers.csv
  data/results/nlb_numbers.csv

Logs:
  lottery_analyzer.log

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 WHAT TO TRY FIRST

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Option 1 (Instant - 30 seconds)
  Open: data/results/
  Double-click: frequency_all.png

Option 2 (Quick - 1 minute)
  Command: python viz_utils.py open-dashboard
  Browser: Opens automatically

Option 3 (Interactive - 2 minutes)
  Command: streamlit run streamlit_app.py
  Browser: Full dashboard interface

Option 4 (Learning - 10 minutes)
  File: VISUALIZATION_QUICKSTART.md
  Learn: All features & usage

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 PROJECT STATUS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Web Scrapers        - Complete
✅ Database            - Complete
✅ Analysis Engine     - Complete
✅ 8 Visualizations    - Complete
✅ Interactive UI      - Complete
✅ Documentation       - Complete
✅ Sample Data         - Complete
✅ All Working         - YES!

STATUS: READY FOR IMMEDIATE USE ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 NEED HELP?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Questions?
  → Check VISUALIZATION_QUICKSTART.md
  → Check VISUALIZER_GUIDE.md
  → Check INDEX.md

Issues?
  → Review lottery_analyzer.log
  → See Troubleshooting section above
  → Check SETUP_GUIDE.md

How-to?
  → See specific guide file above
  → Check code comments
  → Try the example commands

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 BEGIN HERE!

Copy & paste one of these:

1. VIEW CHARTS IMMEDIATELY:
   python viz_utils.py list

2. OPEN INTERACTIVE DASHBOARD:
   python viz_utils.py open-dashboard

3. START WEB DASHBOARD:
   streamlit run streamlit_app.py

4. LEARN MORE:
   Read VISUALIZATION_QUICKSTART.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Version: 1.0
Status: ✅ Complete
Date: March 6, 2024
Ready: YES! 🎲📊

Everything is ready. Start exploring! 🚀
""")

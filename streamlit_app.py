"""
Streamlit web dashboard for lottery analysis visualizations
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from collections import Counter
import logging

from database import LotteryDatabase
from analysis import PatternAnalyzer
from visualizer import LotteryVisualizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Lottery Analyzer",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B6B;
        margin-bottom: 10px;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #FF6B6B;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = LotteryDatabase()
    st.session_state.analyzer = PatternAnalyzer(st.session_state.db)
    st.session_state.visualizer = LotteryVisualizer(st.session_state.db)

db = st.session_state.db
analyzer = st.session_state.analyzer
visualizer = st.session_state.visualizer

# Sidebar
st.sidebar.markdown("# 🎲 Lottery Analyzer")
st.sidebar.markdown("---")

# Data source selector
data_source = st.sidebar.selectbox(
    "Select Data Source",
    ["All", "DLB", "NLB"],
    help="Choose which lottery data to analyze"
)

# Load data
@st.cache_data(ttl=300)
def load_analysis_data(source):
    """Load and cache analysis data"""
    df = analyzer.load_data(source)
    if df.empty:
        return None, None
    
    report = analyzer.generate_report(source)
    return df, report

source_map = {"All": "all", "DLB": "DLB", "NLB": "NLB"}
df, report = load_analysis_data(source_map[data_source])

if df is None or df.empty:
    st.warning(f"⚠️ No data available for {data_source}. Please add sample data or scrape lottery numbers.")
    st.info("Run: `python utils.py add-sample` to add sample data")
    st.stop()

# Main header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="main-header">🎲 Lottery Pattern Analysis</div>', unsafe_allow_html=True)
with col2:
    st.metric("Total Draws", len(df))

st.markdown("---")

# Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    freq = Counter()
    for numbers in df['numbers']:
        freq.update(numbers)
    st.metric("Unique Numbers", len(freq))

with col2:
    avg_sum = np.mean([sum(numbers) for numbers in df['numbers']])
    st.metric("Avg Sum", f"{avg_sum:.1f}")

with col3:
    odd_count = sum(1 for numbers in df['numbers'] for n in numbers if n % 2 == 1)
    even_count = sum(1 for numbers in df['numbers'] for n in numbers if n % 2 == 0)
    st.metric("Odd/Even Ratio", f"{odd_count/even_count:.2f}" if even_count > 0 else "N/A")

with col4:
    st.metric("Data Source", data_source)

st.markdown("---")

# Create tabs for different visualizations
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    ["📊 Frequency", "🔥 Hot/Cold", "🎯 Patterns", "📈 Statistics", 
     "🔗 Pairs", "🔢 Digits", "📋 Data"]
)

# Tab 1: Number Frequency
with tab1:
    st.subheader("Number Frequency Analysis")
    
    top_n = st.slider("Show top N numbers", 5, 30, 20, key="freq_slider")
    
    frequency = Counter()
    for numbers in df['numbers']:
        frequency.update(numbers)
    
    top_numbers = frequency.most_common(top_n)
    freq_df = pd.DataFrame(top_numbers, columns=['Number', 'Frequency'])
    
    # Create plotly bar chart
    fig = px.bar(
        freq_df,
        x='Number',
        y='Frequency',
        title=f"Top {top_n} Most Common Lottery Numbers",
        labels={'Number': 'Lottery Number', 'Frequency': 'Times Appeared'},
        color='Frequency',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=500, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    # Display as table
    st.dataframe(freq_df.set_index('Number'), use_container_width=True)

# Tab 2: Hot/Cold Numbers
with tab2:
    st.subheader("Hot vs Cold Numbers Analysis")
    
    hot_cold = analyzer.analyze_hot_and_cold_numbers(df)
    hot_nums = hot_cold.get('hot_numbers', [])
    cold_nums = hot_cold.get('cold_numbers', [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🔥 Hot Numbers", len(hot_nums))
        if hot_nums:
            st.write("**Most Frequently Drawn:**")
            hot_df = pd.DataFrame(hot_nums, columns=['Number'])
            hot_df['Rank'] = range(1, len(hot_df) + 1)
            st.dataframe(hot_df.set_index('Rank'), use_container_width=True)
    
    with col2:
        st.metric("❄️ Cold Numbers", len(cold_nums))
        if cold_nums:
            st.write("**Rarely Drawn:**")
            cold_df = pd.DataFrame(cold_nums, columns=['Number'])
            cold_df['Rank'] = range(1, len(cold_df) + 1)
            st.dataframe(cold_df.set_index('Rank'), use_container_width=True)
    
    # Visualization
    all_nums = hot_nums + cold_nums
    num_type = ['Hot'] * len(hot_nums) + ['Cold'] * len(cold_nums)
    scatter_df = pd.DataFrame({
        'Number': all_nums,
        'Type': num_type
    })
    
    fig = px.scatter(
        scatter_df,
        x='Number',
        y='Type',
        color='Type',
        color_discrete_map={'Hot': '#FF6B6B', 'Cold': '#4ECDC4'},
        title="Hot vs Cold Numbers Distribution",
        size_max=20
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Tab 3: Pattern Analysis
with tab3:
    st.subheader("Pattern Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Odd/Even Distribution**")
        odd_even = analyzer.analyze_odd_even_distribution(df)
        odd_count = odd_even.get('total_odd', 0)
        even_count = odd_even.get('total_even', 0)
        
        fig = px.pie(
            values=[odd_count, even_count],
            names=['Odd', 'Even'],
            title="Odd vs Even Numbers",
            color_discrete_map={'Odd': '#FF9999', 'Even': '#66B2FF'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**Consecutive Numbers**")
        consecutive = analyzer.analyze_consecutive_numbers(df)
        total_consec = consecutive.get('total_consecutive', 0)
        
        consec_data = pd.DataFrame({
            'Type': ['With Consecutive', 'Without Consecutive'],
            'Count': [total_consec, len(df) - total_consec]
        })
        
        fig = px.bar(
            consec_data,
            x='Type',
            y='Count',
            title="Draws with Consecutive Numbers",
            color='Type',
            color_discrete_map={'With Consecutive': '#FF6B6B', 'Without Consecutive': '#4ECDC4'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# Tab 4: Statistics
with tab4:
    st.subheader("Statistical Analysis")
    
    sum_analysis = analyzer.analyze_sum_patterns(df)
    sums = [sum(numbers) for numbers in df['numbers']]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Min Sum", sum_analysis['min_sum'])
    col2.metric("Max Sum", sum_analysis['max_sum'])
    col3.metric("Avg Sum", f"{sum_analysis['avg_sum']:.2f}")
    col4.metric("Median Sum", f"{np.median(sums):.2f}")
    
    # Sum distribution histogram
    fig = px.histogram(
        x=sums,
        nbins=20,
        title="Distribution of Sum Values",
        labels={'x': 'Sum', 'count': 'Frequency'},
        color_discrete_sequence=['#A8D8EA']
    )
    fig.add_vline(x=sum_analysis['avg_sum'], line_dash="dash", line_color="red",
                  annotation_text=f"Mean: {sum_analysis['avg_sum']:.1f}",
                  annotation_position="top right")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# Tab 5: Number Pairs
with tab5:
    st.subheader("Most Common Number Pairs")
    
    top_pairs_n = st.slider("Show top N pairs", 5, 30, 15, key="pairs_slider")
    
    pair_freq = Counter()
    for numbers in df['numbers']:
        sorted_nums = sorted(numbers)
        for i in range(len(sorted_nums)):
            for j in range(i + 1, len(sorted_nums)):
                pair = (sorted_nums[i], sorted_nums[j])
                pair_freq[pair] += 1
    
    top_pairs = pair_freq.most_common(top_pairs_n)
    
    if top_pairs:
        pairs_data = pd.DataFrame(
            [(f"{p[0]}-{p[1]}", p[2] if len(p) > 2 else p[1]) 
             for p in [(pair[0][0], pair[0][1], pair[1]) for pair in top_pairs]],
            columns=['Pair', 'Frequency']
        )
        
        fig = px.barh(
            pairs_data,
            x='Frequency',
            y='Pair',
            title=f"Top {top_pairs_n} Most Common Number Pairs",
            color='Frequency',
            color_continuous_scale='Plasma'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(pairs_data.set_index('Pair'), use_container_width=True)
    else:
        st.info("No number pairs found in the data")

# Tab 6: Digit Distribution
with tab6:
    st.subheader("Last Digit Distribution")
    
    digit_freq = Counter()
    for numbers in df['numbers']:
        for num in numbers:
            digit_freq[num % 10] += 1
    
    digit_data = pd.DataFrame(
        sorted(digit_freq.items()),
        columns=['Digit', 'Frequency']
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            digit_data,
            values='Frequency',
            names='Digit',
            title="Last Digit Distribution (Pie)",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            digit_data,
            x='Digit',
            y='Frequency',
            title="Last Digit Distribution (Bar)",
            color='Frequency',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)

# Tab 7: Raw Data
with tab7:
    st.subheader("Raw Lottery Data")
    
    # Display raw data
    display_df = df.copy()
    if 'numbers' in display_df.columns:
        display_df['numbers'] = display_df['numbers'].apply(lambda x: ', '.join(map(str, x)))
    
    st.dataframe(display_df, use_container_width=True)
    
    # Export option
    col1, col2 = st.columns(2)
    
    with col1:
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"lottery_data_{data_source.lower()}.csv",
            mime="text/csv"
        )
    
    with col2:
        st.metric("Total Records", len(display_df))

# Sidebar actions
st.sidebar.markdown("---")
st.sidebar.subheader("Actions")

if st.sidebar.button("🔄 Refresh Cache", help="Clear cached data and reload"):
    st.cache_data.clear()
    st.rerun()

if st.sidebar.button("📊 Generate All Visualizations", help="Create PNG files of all charts"):
    with st.spinner("Generating visualizations..."):
        visualizer.generate_all_visualizations(source=source_map[data_source])
    st.success("✅ Visualizations generated! Check `/data/results/` folder")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📖 About
**Lottery Pattern Analyzer** v1.0

This dashboard analyzes historical lottery numbers to identify patterns and trends.

### ⚠️ Disclaimer
Lottery draws are random events. Historical patterns cannot predict future results. 
Use for educational purposes only.

### 🔗 Data Sources
- DLB (Dharmaraja Lotteries Bureau)
- NLB (National Lottery Bureau)
""")

st.sidebar.markdown("---")
st.sidebar.write("*Last updated: March 6, 2024*")

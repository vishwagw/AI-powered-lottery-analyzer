"""
Visualization module for lottery analysis results
Creates charts and graphs for pattern analysis
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from collections import Counter

from database import LotteryDatabase
from analysis import PatternAnalyzer
from config import RESULTS_DIR

logger = logging.getLogger(__name__)
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)


class LotteryVisualizer:
    """Create visualizations for lottery analysis"""
    
    def __init__(self, db: LotteryDatabase = None, output_dir: Path = RESULTS_DIR):
        self.db = db or LotteryDatabase()
        self.analyzer = PatternAnalyzer(self.db)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Visualizer initialized, output directory: {self.output_dir}")
    
    def plot_number_frequency(self, source: str = 'all', top_n: int = 20, save: bool = True):
        """Create bar chart of number frequencies"""
        logger.info(f"Creating number frequency chart for {source}...")
        
        df = self.analyzer.load_data(source)
        if df.empty:
            logger.warning(f"No data found for source: {source}")
            return None
        
        frequency = Counter()
        for numbers in df['numbers']:
            frequency.update(numbers)
        
        # Get top N numbers
        top_numbers = frequency.most_common(top_n)
        numbers = [str(item[0]) for item in top_numbers]
        counts = [item[1] for item in top_numbers]
        
        # Create figure
        fig = plt.figure(figsize=(14, 7))
        colors = plt.cm.viridis(np.linspace(0, 1, len(numbers)))
        bars = plt.bar(numbers, counts, color=colors, edgecolor='black', linewidth=1.2)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.xlabel('Lottery Number', fontsize=12, fontweight='bold')
        plt.ylabel('Frequency', fontsize=12, fontweight='bold')
        plt.title(f'Top {top_n} Most Common Lottery Numbers - {source}', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if save:
            output_file = self.output_dir / f"frequency_{source.lower()}.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Saved: {output_file}")
        
        return fig
    
    def plot_hot_cold_numbers(self, source: str = 'all', save: bool = True):
        """Create visualization of hot and cold numbers"""
        logger.info(f"Creating hot/cold numbers chart for {source}...")
        
        df = self.analyzer.load_data(source)
        if df.empty:
            logger.warning(f"No data found for source: {source}")
            return None
        
        result = self.analyzer.analyze_hot_and_cold_numbers(df)
        hot_nums = result.get('hot_numbers', [])
        cold_nums = result.get('cold_numbers', [])
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Hot numbers
        if hot_nums:
            ax1.barh(range(len(hot_nums)), hot_nums, color='#FF6B6B', edgecolor='black')
            ax1.set_yticks(range(len(hot_nums)))
            ax1.set_yticklabels([str(n) for n in hot_nums])
            ax1.set_xlabel('Frequency', fontweight='bold')
            ax1.set_title('Hot Numbers (Frequently Drawn)', fontweight='bold', fontsize=12)
            ax1.set_xlim(0, max(hot_nums) * 1.5 if hot_nums else 1)
        else:
            ax1.text(0.5, 0.5, 'No Hot Numbers Found', 
                    ha='center', va='center', fontsize=14)
            ax1.set_title('Hot Numbers', fontweight='bold')
        
        # Cold numbers
        if cold_nums:
            ax2.barh(range(len(cold_nums)), cold_nums, color='#4ECDC4', edgecolor='black')
            ax2.set_yticks(range(len(cold_nums)))
            ax2.set_yticklabels([str(n) for n in cold_nums])
            ax2.set_xlabel('Frequency', fontweight='bold')
            ax2.set_title('Cold Numbers (Rarely Drawn)', fontweight='bold', fontsize=12)
            ax2.set_xlim(0, max(cold_nums) * 1.5 if cold_nums else 1)
        else:
            ax2.text(0.5, 0.5, 'No Cold Numbers Found', 
                    ha='center', va='center', fontsize=14)
            ax2.set_title('Cold Numbers', fontweight='bold')
        
        plt.suptitle(f'Hot vs Cold Numbers - {source}', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save:
            output_file = self.output_dir / f"hot_cold_{source.lower()}.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Saved: {output_file}")
        
        return fig
    
    def plot_odd_even_distribution(self, source: str = 'all', save: bool = True):
        """Create pie chart of odd/even distribution"""
        logger.info(f"Creating odd/even distribution chart for {source}...")
        
        df = self.analyzer.load_data(source)
        if df.empty:
            logger.warning(f"No data found for source: {source}")
            return None
        
        result = self.analyzer.analyze_odd_even_distribution(df)
        odd_count = result.get('total_odd', 0)
        even_count = result.get('total_even', 0)
        
        # Create pie chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Pie chart
        sizes = [odd_count, even_count]
        labels = [f'Odd\n({odd_count})', f'Even\n({even_count})']
        colors = ['#FF9999', '#66B2FF']
        explode = (0.05, 0.05)
        
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               shadow=True, startangle=90, explode=explode, textprops={'fontsize': 12, 'weight': 'bold'})
        ax1.set_title('Odd vs Even Numbers Distribution', fontweight='bold', fontsize=12)
        
        # Distribution patterns
        patterns = result.get('distribution_patterns', {})
        if patterns:
            pattern_names = list(patterns.keys())[:10]
            pattern_counts = [patterns[p] for p in pattern_names]
            
            ax2.barh(pattern_names, pattern_counts, color='#95E1D3', edgecolor='black')
            ax2.set_xlabel('Occurrences', fontweight='bold')
            ax2.set_title('Most Common Odd/Even Patterns', fontweight='bold', fontsize=12)
        else:
            ax2.text(0.5, 0.5, 'No Pattern Data', ha='center', va='center', fontsize=14)
        
        plt.suptitle(f'Odd/Even Distribution - {source}', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        if save:
            output_file = self.output_dir / f"odd_even_{source.lower()}.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Saved: {output_file}")
        
        return fig
    
    def plot_sum_distribution(self, source: str = 'all', save: bool = True):
        """Create histogram of number sums"""
        logger.info(f"Creating sum distribution chart for {source}...")
        
        df = self.analyzer.load_data(source)
        if df.empty:
            logger.warning(f"No data found for source: {source}")
            return None
        
        sums = [sum(numbers) for numbers in df['numbers']]
        result = self.analyzer.analyze_sum_patterns(df)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Histogram
        ax1.hist(sums, bins=20, color='#A8D8EA', edgecolor='black', linewidth=1.2)
        ax1.axvline(result['avg_sum'], color='red', linestyle='--', linewidth=2, label=f"Mean: {result['avg_sum']:.1f}")
        ax1.set_xlabel('Sum of Numbers', fontweight='bold')
        ax1.set_ylabel('Frequency', fontweight='bold')
        ax1.set_title('Distribution of Winning Number Sums', fontweight='bold', fontsize=12)
        ax1.legend(fontsize=10)
        ax1.grid(alpha=0.3)
        
        # Statistics box
        stats_text = f"""
        Min: {result['min_sum']}
        Max: {result['max_sum']}
        Mean: {result['avg_sum']:.2f}
        Median: {np.median(sums):.2f}
        Std Dev: {np.std(sums):.2f}
        """
        ax2.text(0.5, 0.5, stats_text, ha='center', va='center', fontsize=12,
                family='monospace', bbox=dict(boxstyle='round', facecolor='#FFE5B4', alpha=0.8))
        ax2.axis('off')
        ax2.set_title('Sum Statistics', fontweight='bold', fontsize=12)
        
        plt.suptitle(f'Sum Distribution Analysis - {source}', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        if save:
            output_file = self.output_dir / f"sum_distribution_{source.lower()}.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Saved: {output_file}")
        
        return fig
    
    def plot_consecutive_analysis(self, source: str = 'all', save: bool = True):
        """Create visualization of consecutive number patterns"""
        logger.info(f"Creating consecutive numbers chart for {source}...")
        
        df = self.analyzer.load_data(source)
        if df.empty:
            logger.warning(f"No data found for source: {source}")
            return None
        
        result = self.analyzer.analyze_consecutive_numbers(df)
        total_consec = result.get('total_consecutive', 0)
        avg_consec = result.get('avg_consecutive_per_draw', 0)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Total consecutive count
        categories = ['With Consecutive', 'Without Consecutive']
        counts = [total_consec, len(df) - total_consec]
        colors = ['#FF6B6B', '#4ECDC4']
        
        bars = ax1.bar(categories, counts, color=colors, edgecolor='black', linewidth=1.5)
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Count', fontweight='bold')
        ax1.set_title('Draws with Consecutive Numbers', fontweight='bold', fontsize=12)
        ax1.set_ylim(0, len(df) * 1.1)
        
        # Stats text
        stats_text = f"""
        Total Consecutive Pairs: {total_consec}
        Total Draws: {len(df)}
        Avg per Draw: {avg_consec:.2f}
        Percentage: {(total_consec/len(df)*100):.1f}%
        """
        ax2.text(0.5, 0.5, stats_text, ha='center', va='center', fontsize=12,
                family='monospace', bbox=dict(boxstyle='round', facecolor='#FFE5B4', alpha=0.8))
        ax2.axis('off')
        ax2.set_title('Consecutive Analysis', fontweight='bold', fontsize=12)
        
        plt.suptitle(f'Consecutive Numbers Analysis - {source}', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        if save:
            output_file = self.output_dir / f"consecutive_{source.lower()}.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Saved: {output_file}")
        
        return fig
    
    def plot_number_pairs(self, source: str = 'all', top_n: int = 15, save: bool = True):
        """Create bar chart of most common number pairs"""
        logger.info(f"Creating number pairs chart for {source}...")
        
        df = self.analyzer.load_data(source)
        if df.empty:
            logger.warning(f"No data found for source: {source}")
            return None
        
        result = self.analyzer.analyze_number_pairs(df)
        top_pairs = result.get('most_common_pairs', [])[:top_n]
        
        if not top_pairs:
            logger.warning(f"No number pairs found for {source}")
            return None
        
        pair_labels = [f"{p[0]}-{p[1]}" for p in top_pairs]
        pair_counts = [p[2] if len(p) > 2 else p[1] for p in top_pairs]
        
        # Extract numeric values if needed
        pair_counts = []
        for item in top_pairs:
            if isinstance(item, tuple):
                if len(item) == 3:
                    pair_counts.append(item[2])
                elif len(item) == 2:
                    pair_counts.append(item[1])
        
        fig = plt.figure(figsize=(14, 7))
        colors = plt.cm.plasma(np.linspace(0, 1, len(pair_labels)))
        bars = plt.barh(pair_labels, pair_counts, color=colors, edgecolor='black', linewidth=1.2)
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            plt.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{int(width)}',
                    ha='left', va='center', fontsize=9, fontweight='bold')
        
        plt.xlabel('Frequency', fontsize=12, fontweight='bold')
        plt.title(f'Top {top_n} Most Common Number Pairs - {source}', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        if save:
            output_file = self.output_dir / f"number_pairs_{source.lower()}.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Saved: {output_file}")
        
        return fig
    
    def plot_digit_distribution(self, source: str = 'all', save: bool = True):
        """Create pie chart of digit distribution (0-9)"""
        logger.info(f"Creating digit distribution chart for {source}...")
        
        df = self.analyzer.load_data(source)
        if df.empty:
            logger.warning(f"No data found for source: {source}")
            return None
        
        result = self.analyzer.analyze_sum_patterns(df)
        digit_dist = result.get('digit_distribution', {})
        
        if not digit_dist:
            logger.warning(f"No digit distribution data for {source}")
            return None
        
        # Convert to sorted lists
        digits = sorted(digit_dist.keys())
        counts = [digit_dist[d] for d in digits]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Pie chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(digits)))
        ax1.pie(counts, labels=[str(d) for d in digits], autopct='%1.1f%%',
               colors=colors, startangle=90)
        ax1.set_title('Last Digit Distribution', fontweight='bold', fontsize=12)
        
        # Bar chart
        ax2.bar(range(len(digits)), counts, color=colors, edgecolor='black', linewidth=1.2)
        ax2.set_xticks(range(len(digits)))
        ax2.set_xticklabels(digits)
        ax2.set_xlabel('Last Digit', fontweight='bold')
        ax2.set_ylabel('Frequency', fontweight='bold')
        ax2.set_title('Last Digit Frequency', fontweight='bold', fontsize=12)
        ax2.grid(axis='y', alpha=0.3)
        
        plt.suptitle(f'Digit Distribution - {source}', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        if save:
            output_file = self.output_dir / f"digit_distribution_{source.lower()}.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Saved: {output_file}")
        
        return fig
    
    def create_interactive_dashboard(self, source: str = 'all'):
        """Create interactive plotly dashboard"""
        logger.info(f"Creating interactive dashboard for {source}...")
        
        df = self.analyzer.load_data(source)
        if df.empty:
            logger.warning(f"No data found for source: {source}")
            return None
        
        # Get analysis data
        freq_result = self.analyzer.analyze_number_frequency(df)
        hot_cold = self.analyzer.analyze_hot_and_cold_numbers(df)
        odd_even = self.analyzer.analyze_odd_even_distribution(df)
        sum_result = self.analyzer.analyze_sum_patterns(df)
        
        # Frequency data
        top_freq = freq_result.get('most_common', [])[:15]
        freq_nums = [str(item[0]) for item in top_freq]
        freq_counts = [item[1] for item in top_freq]
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Number Frequency', 'Odd vs Even Distribution',
                           'Sum Distribution', 'Hot vs Cold Numbers'),
            specs=[[{'type': 'bar'}, {'type': 'pie'}],
                   [{'type': 'histogram'}, {'type': 'bar'}]]
        )
        
        # Frequency bars
        fig.add_trace(
            go.Bar(x=freq_nums, y=freq_counts, name='Frequency', marker_color='indianred'),
            row=1, col=1
        )
        
        # Odd/even pie
        odd_even_data = [odd_even.get('total_odd', 0), odd_even.get('total_even', 0)]
        fig.add_trace(
            go.Pie(labels=['Odd', 'Even'], values=odd_even_data, name='Odd/Even'),
            row=1, col=2
        )
        
        # Sum histogram
        sums = [sum(numbers) for numbers in df['numbers']]
        fig.add_trace(
            go.Histogram(x=sums, name='Sum', marker_color='lightsalmon', nbinsx=20),
            row=2, col=1
        )
        
        # Hot/cold
        hot_nums = hot_cold.get('hot_numbers', [])
        cold_nums = hot_cold.get('cold_numbers', [])
        categories = ['Hot Numbers', 'Cold Numbers'] if hot_nums or cold_nums else ['No Data']
        values = [len(hot_nums), len(cold_nums)]
        
        fig.add_trace(
            go.Bar(x=categories, y=values, name='Count', marker_color=['red', 'blue']),
            row=2, col=2
        )
        
        # Update layout
        fig.update_xaxes(title_text='Number', row=1, col=1)
        fig.update_xaxes(title_text='Sum', row=2, col=1)
        fig.update_yaxes(title_text='Frequency', row=1, col=1)
        fig.update_yaxes(title_text='Count', row=2, col=1)
        fig.update_yaxes(title_text='Count', row=2, col=2)
        
        fig.update_layout(
            title_text=f'Lottery Analysis Dashboard - {source}',
            height=900,
            showlegend=True,
            hovermode='closest'
        )
        
        # Save interactive HTML
        output_file = self.output_dir / f"dashboard_{source.lower()}.html"
        fig.write_html(str(output_file))
        logger.info(f"Saved: {output_file}")
        
        return fig
    
    def generate_all_visualizations(self, source: str = 'all'):
        """Generate all visualizations for a data source"""
        logger.info(f"Generating all visualizations for {source}...")
        
        try:
            self.plot_number_frequency(source=source)
            plt.close('all')
            
            self.plot_hot_cold_numbers(source=source)
            plt.close('all')
            
            self.plot_odd_even_distribution(source=source)
            plt.close('all')
            
            self.plot_sum_distribution(source=source)
            plt.close('all')
            
            self.plot_consecutive_analysis(source=source)
            plt.close('all')
            
            self.plot_number_pairs(source=source)
            plt.close('all')
            
            self.plot_digit_distribution(source=source)
            plt.close('all')
            
            self.create_interactive_dashboard(source=source)
            
            logger.info(f"All visualizations created successfully for {source}!")
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}", exc_info=True)
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()

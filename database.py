"""
Database management for lottery data
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from config import DB_PATH


class LotteryDatabase:
    """Database handler for lottery numbers"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.init_database()
    
    def init_database(self):
        """Initialize database connection and create tables"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        
        # Create DLB numbers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dlb_numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draw_date TEXT NOT NULL,
                draw_number TEXT UNIQUE,
                numbers TEXT NOT NULL,
                winning_amount REAL,
                source TEXT DEFAULT 'DLB',
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(draw_date, source)
            )
        ''')
        
        # Create NLB numbers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS nlb_numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draw_date TEXT NOT NULL,
                draw_number TEXT UNIQUE,
                numbers TEXT NOT NULL,
                winning_amount REAL,
                source TEXT DEFAULT 'NLB',
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(draw_date, source)
            )
        ''')
        
        # Create analysis results table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_type TEXT NOT NULL,
                pattern TEXT NOT NULL,
                frequency INTEGER,
                percentage REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def insert_dlb_numbers(self, draw_date: str, draw_number: str, 
                          numbers: List[int], winning_amount: Optional[float] = None):
        """Insert DLB lottery numbers"""
        try:
            numbers_str = ','.join(map(str, numbers))
            self.cursor.execute('''
                INSERT INTO dlb_numbers (draw_date, draw_number, numbers, winning_amount)
                VALUES (?, ?, ?, ?)
            ''', (draw_date, draw_number, numbers_str, winning_amount))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def insert_nlb_numbers(self, draw_date: str, draw_number: str, 
                          numbers: List[int], winning_amount: Optional[float] = None):
        """Insert NLB lottery numbers"""
        try:
            numbers_str = ','.join(map(str, numbers))
            self.cursor.execute('''
                INSERT INTO nlb_numbers (draw_date, draw_number, numbers, winning_amount)
                VALUES (?, ?, ?, ?)
            ''', (draw_date, draw_number, numbers_str, winning_amount))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_dlb_numbers(self, limit: Optional[int] = None) -> List[Dict]:
        """Retrieve DLB lottery numbers"""
        query = 'SELECT * FROM dlb_numbers ORDER BY draw_date DESC'
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query)
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def get_nlb_numbers(self, limit: Optional[int] = None) -> List[Dict]:
        """Retrieve NLB lottery numbers"""
        query = 'SELECT * FROM nlb_numbers ORDER BY draw_date DESC'
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query)
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def get_all_numbers(self) -> List[Dict]:
        """Retrieve all lottery numbers from both sources"""
        dlb_data = self.get_dlb_numbers()
        nlb_data = self.get_nlb_numbers()
        return dlb_data + nlb_data
    
    def save_analysis_result(self, analysis_type: str, pattern: str, 
                            frequency: int, percentage: float):
        """Save analysis results"""
        self.cursor.execute('''
            INSERT INTO analysis_results (analysis_type, pattern, frequency, percentage)
            VALUES (?, ?, ?, ?)
        ''', (analysis_type, pattern, frequency, percentage))
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

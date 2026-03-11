"""
Web scraper for National Lottery Bureau (NLB)
https://www.nlb.lk/
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from config import NLB_URL, TIMEOUT, MAX_RETRIES, HEADLESS_BROWSER

logger = logging.getLogger(__name__)


class NLBScraper:
    """Scraper for NLB lottery results"""
    
    def __init__(self):
        self.url = NLB_URL
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Initialize Selenium Chrome driver"""
        try:
            options = webdriver.ChromeOptions()
            if HEADLESS_BROWSER:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(TIMEOUT)
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Chrome driver: {e}")
            raise
    
    def scrape_lottery_results(self) -> List[Dict]:
        """
        Scrape lottery results from NLB website
        Returns list of dictionaries with lottery data
        """
        results = []
        retries = 0
        
        while retries < MAX_RETRIES:
            try:
                logger.info(f"Fetching NLB results (attempt {retries + 1})...")
                self.driver.get(self.url)
                
                # Wait for page to load
                WebDriverWait(self.driver, TIMEOUT).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
                )
                
                # Give page time to fully render
                time.sleep(2)
                
                # Parse page content
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Look for lottery tables or result divs
                results = self._extract_numbers(soup)
                
                if results:
                    logger.info(f"Successfully scraped {len(results)} NLB results")
                    return results
                else:
                    logger.warning("No results found on page, retrying...")
                    retries += 1
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"Error scraping NLB: {e}")
                retries += 1
                time.sleep(2)
        
        logger.warning("Failed to scrape NLB results after max retries")
        return results
    
    def _extract_numbers(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract lottery numbers from parsed HTML"""
        results = []
        
        try:
            # Look for table rows with lottery data
            # This is a generic approach that may need adjustment based on actual HTML structure
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        try:
                            draw_date = cols[0].text.strip()
                            draw_number = cols[1].text.strip() if len(cols) > 1 else ""
                            numbers_text = cols[2].text.strip() if len(cols) > 2 else ""
                            
                            # Parse numbers (adjust parsing based on actual format)
                            numbers = self._parse_numbers(numbers_text)
                            
                            if numbers:
                                results.append({
                                    'draw_date': draw_date,
                                    'draw_number': draw_number,
                                    'numbers': numbers,
                                    'source': 'NLB'
                                })
                        except Exception as e:
                            logger.debug(f"Error parsing row: {e}")
                            continue
        
        except Exception as e:
            logger.error(f"Error extracting numbers from HTML: {e}")
        
        return results
    
    def _parse_numbers(self, numbers_text: str) -> List[int]:
        """Parse numbers from text string"""
        try:
            # Remove common delimiters and convert to integers
            numbers_text = numbers_text.replace('-', ' ').replace(',', ' ')
            numbers = [int(n) for n in numbers_text.split() if n.isdigit()]
            return numbers
        except Exception as e:
            logger.debug(f"Error parsing numbers: {e}")
            return []
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Chrome driver closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

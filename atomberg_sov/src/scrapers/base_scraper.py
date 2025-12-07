"""Base scraper class with common functionality"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all platform scrapers"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.logger = logger
        
    @abstractmethod
    def search(self, query: str, num_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search for a query on the platform.
        
        Args:
            query: Search query
            num_results: Number of results to retrieve
            
        Returns:
            List of search results with metadata
        """
        pass
    
    @abstractmethod
    def get_engagement_metrics(self, item_id: str) -> Dict[str, Any]:
        """
        Get engagement metrics for an item.
        
        Args:
            item_id: ID of the item
            
        Returns:
            Dictionary with engagement metrics
        """
        pass
    
    def extract_mentions(self, text: str, keywords: List[str]) -> Dict[str, int]:
        """
        Extract mentions of keywords from text.
        
        Args:
            text: Text to analyze
            keywords: List of keywords to look for
            
        Returns:
            Dictionary with mention counts
        """
        mentions = {}
        text_lower = text.lower()
        for keyword in keywords:
            mentions[keyword] = text_lower.count(keyword.lower())
        return mentions
    
    def log_operation(self, message: str):
        """Log an operation"""
        self.logger.info(f"[{self.platform_name}] {message}")

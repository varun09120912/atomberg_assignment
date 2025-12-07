"""Data processing utilities"""
from typing import Dict, List, Any
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and organize data from scrapers"""
    
    @staticmethod
    def filter_results_by_brand(results: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Filter results that mention specific brands.
        
        Args:
            results: List of search results
            keywords: Keywords to filter by
            
        Returns:
            Filtered list of results
        """
        filtered = []
        for result in results:
            text = (
                result.get("title", "") + " " +
                result.get("snippet", "") + " " +
                result.get("text", "") + " " +
                result.get("channel", "")
            ).lower()
            
            if any(keyword.lower() in text for keyword in keywords):
                filtered.append(result)
        
        return filtered
    
    @staticmethod
    def aggregate_by_brand(results: List[Dict[str, Any]], brand_keywords: Dict[str, List[str]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organize results by brand.
        
        Args:
            results: List of search results
            brand_keywords: Dictionary mapping brand names to keyword lists
            
        Returns:
            Dictionary with results organized by brand
        """
        brand_results = {brand: [] for brand in brand_keywords.keys()}
        
        for result in results:
            text = (
                result.get("title", "") + " " +
                result.get("snippet", "") + " " +
                result.get("text", "") + " " +
                result.get("channel", "")
            ).lower()
            
            for brand, keywords in brand_keywords.items():
                if any(keyword.lower() in text for keyword in keywords):
                    brand_results[brand].append(result)
                    break  # Assign to first matching brand
        
        return brand_results
    
    @staticmethod
    def save_to_json(data: Dict[str, Any], filepath: str) -> bool:
        """
        Save data to JSON file.
        
        Args:
            data: Data to save
            filepath: Output filepath
            
        Returns:
            Success status
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            return False
    
    @staticmethod
    def load_from_json(filepath: str) -> Dict[str, Any]:
        """
        Load data from JSON file.
        
        Args:
            filepath: Input filepath
            
        Returns:
            Loaded data
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return {}
    
    @staticmethod
    def deduplicate_results(results: List[Dict[str, Any]], key_field: str = "url") -> List[Dict[str, Any]]:
        """
        Remove duplicate results.
        
        Args:
            results: List of results
            key_field: Field to use for deduplication
            
        Returns:
            Deduplicated list
        """
        seen = set()
        deduplicated = []
        
        for result in results:
            key = result.get(key_field, "")
            if key and key not in seen:
                seen.add(key)
                deduplicated.append(result)
        
        return deduplicated

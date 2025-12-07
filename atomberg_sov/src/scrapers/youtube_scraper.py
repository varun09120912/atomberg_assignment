"""YouTube scraper"""
import requests
from typing import List, Dict, Any
from .base_scraper import BaseScraper
import os


class YouTubeScraper(BaseScraper):
    """Scraper for YouTube search results and videos"""
    
    def __init__(self):
        super().__init__("YouTube")
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        
    def search(self, query: str, num_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search YouTube videos using YouTube Data API.
        
        Args:
            query: Search query
            num_results: Number of results to retrieve
            
        Returns:
            List of video results
        """
        self.log_operation(f"Searching for: {query}")
        
        try:
            # Using youtube-search-python as it's more accessible
            from youtube_search import YoutubeSearch
            
            results_raw = YoutubeSearch(query, max_results=num_results).to_dict()
            
            results = []
            for item in results_raw:
                results.append({
                    "title": item.get("title", ""),
                    "url": f"https://www.youtube.com/watch?v={item.get('id', '')}",
                    "channel": item.get("channel", ""),
                    "views": self._parse_view_count(item.get("views", "0")),
                    "video_id": item.get("id", ""),
                    "platform": "YouTube",
                })
            return results
            
        except Exception as e:
            self.log_operation(f"Error during search: {str(e)}")
            return []
    
    def get_engagement_metrics(self, video_id: str) -> Dict[str, Any]:
        """
        Get engagement metrics for a YouTube video.
        """
        try:
            # This would require YouTube API key
            # For now, return mock metrics
            return {
                "platform": "YouTube",
                "likes": 0,
                "views": 0,
                "comments": 0,
                "shares": 0,
                "engagement_rate": 0.0,
            }
        except Exception as e:
            self.log_operation(f"Error getting metrics: {str(e)}")
            return {}
    
    @staticmethod
    def _parse_view_count(view_str: str) -> int:
        """Parse YouTube view count string"""
        try:
            view_str = view_str.lower().strip()
            if 'k' in view_str:
                return int(float(view_str.replace('k', '')) * 1000)
            elif 'm' in view_str:
                return int(float(view_str.replace('m', '')) * 1000000)
            else:
                return int(view_str.replace(',', ''))
        except:
            return 0

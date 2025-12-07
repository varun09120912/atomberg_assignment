"""Twitter/X scraper"""
import requests
from typing import List, Dict, Any
from .base_scraper import BaseScraper
import os


class TwitterScraper(BaseScraper):
    """Scraper for Twitter/X posts"""
    
    def __init__(self):
        super().__init__("Twitter/X")
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
    def search(self, query: str, num_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search Twitter using Twitter API v2.
        
        Args:
            query: Search query
            num_results: Number of results to retrieve
            
        Returns:
            List of tweets
        """
        self.log_operation(f"Searching for: {query}")
        
        if not self.bearer_token:
            self.log_operation("Twitter API key not configured")
            return []
        
        try:
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "User-Agent": "AtombergSoVAgent/1.0"
            }
            params = {
                "query": query,
                "max_results": min(num_results, 100),
                "tweet.fields": "public_metrics,created_at,author_id",
                "expansions": "author_id",
                "user.fields": "username,public_metrics"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if "data" in data:
                users = {user["id"]: user for user in data.get("includes", {}).get("users", [])}
                
                for tweet in data["data"][:num_results]:
                    author_id = tweet.get("author_id", "")
                    author = users.get(author_id, {})
                    
                    results.append({
                        "id": tweet.get("id", ""),
                        "text": tweet.get("text", ""),
                        "author": author.get("username", ""),
                        "created_at": tweet.get("created_at", ""),
                        "likes": tweet.get("public_metrics", {}).get("like_count", 0),
                        "retweets": tweet.get("public_metrics", {}).get("retweet_count", 0),
                        "replies": tweet.get("public_metrics", {}).get("reply_count", 0),
                        "quotes": tweet.get("public_metrics", {}).get("quote_count", 0),
                        "platform": "Twitter/X",
                    })
            return results
            
        except Exception as e:
            self.log_operation(f"Error during search: {str(e)}")
            return []
    
    def get_engagement_metrics(self, tweet_id: str) -> Dict[str, Any]:
        """
        Get engagement metrics for a tweet.
        """
        return {
            "platform": "Twitter/X",
            "likes": 0,
            "retweets": 0,
            "replies": 0,
            "quotes": 0,
            "engagement_rate": 0.0,
        }

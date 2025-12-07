"""Engagement metrics analyzer"""
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EngagementAnalyzer:
    """Analyze engagement metrics"""
    
    def __init__(self):
        self.logger = logger
    
    def calculate_engagement_rate(self, metrics: Dict[str, int], reach: int = 1000) -> float:
        """
        Calculate engagement rate from metrics.
        
        Args:
            metrics: Dictionary with engagement counts
            reach: Number of people who saw the content
            
        Returns:
            Engagement rate as percentage
        """
        if reach == 0:
            return 0.0
        
        total_engagement = sum(metrics.values())
        engagement_rate = (total_engagement / reach) * 100
        return round(engagement_rate, 2)
    
    def analyze_platform_engagement(self, results: List[Dict[str, Any]], platform: str) -> Dict[str, Any]:
        """
        Analyze engagement metrics for a platform.
        
        Args:
            results: List of items from the platform
            platform: Platform name
            
        Returns:
            Dictionary with engagement analysis
        """
        if not results:
            return {
                "platform": platform,
                "total_items": 0,
                "avg_engagement": 0.0,
                "total_engagement": 0,
                "engagement_distribution": {}
            }
        
        total_items = len(results)
        total_engagement = 0
        engagement_values = []
        
        for item in results:
            item_engagement = 0
            
            if platform == "Twitter/X":
                item_engagement = item.get("likes", 0) + item.get("retweets", 0) + item.get("replies", 0)
            elif platform == "YouTube":
                item_engagement = item.get("views", 0) + item.get("likes", 0)
            elif platform == "Instagram":
                item_engagement = item.get("likes", 0) + item.get("comments", 0)
            elif platform == "Google":
                item_engagement = item.get("position", 0)  # Lower position = higher engagement potential
            
            engagement_values.append(item_engagement)
            total_engagement += item_engagement
        
        avg_engagement = total_engagement / total_items if total_items > 0 else 0
        
        return {
            "platform": platform,
            "total_items": total_items,
            "avg_engagement": round(avg_engagement, 2),
            "total_engagement": total_engagement,
            "max_engagement": max(engagement_values) if engagement_values else 0,
            "min_engagement": min(engagement_values) if engagement_values else 0,
        }
    
    def compare_engagement(self, atomberg_metrics: Dict[str, Any], competitor_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare Atomberg's engagement with competitors.
        
        Args:
            atomberg_metrics: Atomberg engagement metrics
            competitor_metrics: List of competitor metrics
            
        Returns:
            Comparison analysis
        """
        avg_competitor_engagement = sum(m.get("avg_engagement", 0) for m in competitor_metrics) / len(competitor_metrics) if competitor_metrics else 0
        
        atomberg_avg = atomberg_metrics.get("avg_engagement", 0)
        
        if avg_competitor_engagement == 0:
            difference_percent = 0.0
        else:
            difference_percent = ((atomberg_avg - avg_competitor_engagement) / avg_competitor_engagement) * 100
        
        return {
            "atomberg_avg_engagement": atomberg_avg,
            "competitor_avg_engagement": round(avg_competitor_engagement, 2),
            "difference_percent": round(difference_percent, 2),
            "outperforming": difference_percent > 0,
        }
    
    def identify_top_performers(self, results: List[Dict[str, Any]], platform: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Identify top performing items.
        
        Args:
            results: List of items
            platform: Platform name
            top_n: Number of top items to return
            
        Returns:
            List of top performing items with scores
        """
        scored_results = []
        
        for item in results:
            score = 0
            if platform == "Twitter/X":
                score = item.get("likes", 0) + (item.get("retweets", 0) * 2) + item.get("replies", 0)
            elif platform == "YouTube":
                score = item.get("views", 0)
            elif platform == "Instagram":
                score = item.get("likes", 0) + (item.get("comments", 0) * 2)
            
            scored_results.append({**item, "engagement_score": score})
        
        # Sort by engagement score descending
        sorted_results = sorted(scored_results, key=lambda x: x["engagement_score"], reverse=True)
        
        return sorted_results[:top_n]

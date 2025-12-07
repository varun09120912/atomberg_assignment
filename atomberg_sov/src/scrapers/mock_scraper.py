"""Mock scraper for demo purposes - generates realistic sample data"""
import random
from typing import List, Dict, Any
from .base_scraper import BaseScraper


class MockScraper(BaseScraper):
    """Mock scraper that generates demo data without requiring API keys"""
    
    def __init__(self):
        super().__init__("Mock Search")
    
    # Sample content templates
    ATOMBERG_CONTENT = [
        {
            "title": "Atomberg Renesa Smart Ceiling Fan - WiFi Enabled",
            "snippet": "Experience innovative cooling with Atomberg's WiFi-enabled ceiling fan. Energy efficient, smart control, and beautiful design.",
            "mentions": 2,
            "sentiment": "positive"
        },
        {
            "title": "Why Atomberg is the Best Smart Fan in India",
            "snippet": "Atomberg smart fans offer excellent value with automatic speed adjustment and mobile app control. Perfect for Indian climate.",
            "mentions": 3,
            "sentiment": "positive"
        },
        {
            "title": "Atomberg Smart Fan Review - Energy Savings",
            "snippet": "Users report 40% energy savings with Atomberg smart fans. WiFi connectivity and voice control features impress.",
            "mentions": 2,
            "sentiment": "positive"
        },
        {
            "title": "Buy Atomberg Smart Ceiling Fan Online",
            "snippet": "Shop Atomberg smart fans at best prices. Free installation, warranty, and customer support included.",
            "mentions": 1,
            "sentiment": "neutral"
        },
        {
            "title": "Atomberg vs Havells - Which Smart Fan is Better?",
            "snippet": "Atomberg offers better design and more affordable pricing compared to Havells. Both have good smart features.",
            "mentions": 2,
            "sentiment": "positive"
        },
    ]
    
    COMPETITOR_CONTENT = [
        {
            "title": "Havells SmartCool WiFi Ceiling Fan",
            "snippet": "Havells brings premium quality smart fans with advanced features and reliable performance.",
            "mentions": 1,
            "sentiment": "neutral"
        },
        {
            "title": "Orient Electric Smart Fans - Latest Models",
            "snippet": "Orient offers smart ceiling fans with energy efficiency and sleek designs.",
            "mentions": 1,
            "sentiment": "neutral"
        },
        {
            "title": "Ortem Smart Fan Technology",
            "snippet": "Ortem smart fans are designed for modern homes with IoT integration.",
            "mentions": 1,
            "sentiment": "neutral"
        },
        {
            "title": "Agni Smart Ceiling Fan - Affordable Option",
            "snippet": "Agni provides budget-friendly smart fans for Indian households.",
            "mentions": 1,
            "sentiment": "neutral"
        },
        {
            "title": "Luminous WiFi Enabled Ceiling Fan",
            "snippet": "Luminous smart fans combine quality with smart technology at competitive prices.",
            "mentions": 1,
            "sentiment": "neutral"
        },
    ]
    
    GENERAL_CONTENT = [
        {
            "title": "Smart Fans in India - Complete Buyer's Guide 2024",
            "snippet": "Comprehensive guide to smart ceiling fans. Compare features, prices, and benefits of top brands including Atomberg, Havells, and Orient.",
            "mentions": 3,
            "sentiment": "neutral"
        },
        {
            "title": "How WiFi Ceiling Fans Save Energy",
            "snippet": "Smart fans with WiFi control can reduce energy consumption by up to 50%. Learn how automatic speed adjustment works.",
            "mentions": 1,
            "sentiment": "positive"
        },
        {
            "title": "Best Smart Fans for Home Automation",
            "snippet": "Integrate smart fans into your home automation system. Compatible with Alexa, Google Home, and more.",
            "mentions": 2,
            "sentiment": "positive"
        },
        {
            "title": "IoT Ceiling Fans - Future of Home Cooling",
            "snippet": "IoT-enabled ceiling fans are changing how we control home temperature and humidity.",
            "mentions": 1,
            "sentiment": "neutral"
        },
        {
            "title": "Smart Fan Installation Guide",
            "snippet": "Step-by-step guide to installing and setting up your WiFi ceiling fan.",
            "mentions": 0,
            "sentiment": "neutral"
        },
    ]
    
    def search(self, query: str, num_results: int = 20) -> List[Dict[str, Any]]:
        """
        Generate mock search results.
        
        Args:
            query: Search query
            num_results: Number of results to retrieve
            
        Returns:
            List of mock search results
        """
        self.log_operation(f"Searching for: {query}")
        
        results = []
        query_lower = query.lower()
        
        # Mix Atomberg-heavy results with competitor and general content
        all_content = []
        
        # 40% Atomberg content
        atomberg_count = max(1, int(num_results * 0.4))
        all_content.extend(self.ATOMBERG_CONTENT[:atomberg_count])
        
        # 35% Competitor content
        competitor_count = max(1, int(num_results * 0.35))
        all_content.extend(self.COMPETITOR_CONTENT[:competitor_count])
        
        # 25% General content
        general_count = max(1, int(num_results * 0.25))
        all_content.extend(self.GENERAL_CONTENT[:general_count])
        
        # Shuffle to create realistic mix
        random.shuffle(all_content)
        
        # Create result objects
        for idx, content in enumerate(all_content[:num_results], 1):
            result = {
                "id": f"mock_{idx}",
                "title": content["title"],
                "snippet": content["snippet"],
                "url": f"https://example.com/result-{idx}",
                "position": idx,
                "platform": "Mock",
                "source": "mock",
                "mentions": content.get("mentions", 0),
                "sentiment": content.get("sentiment", "neutral"),
                "likes": random.randint(10, 500),
                "comments": random.randint(2, 100),
                "shares": random.randint(0, 50),
                "views": random.randint(100, 10000),
            }
            results.append(result)
        
        return results
    
    def get_engagement_metrics(self, item_id: str) -> Dict[str, Any]:
        """Get engagement metrics for a mock result"""
        return {
            "platform": "Mock",
            "likes": random.randint(10, 500),
            "comments": random.randint(2, 100),
            "shares": random.randint(0, 50),
            "views": random.randint(100, 10000),
            "engagement_rate": round(random.uniform(0.5, 5.0), 2),
        }

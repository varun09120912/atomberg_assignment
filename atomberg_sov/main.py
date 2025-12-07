"""Main orchestrator for the Atomberg SoV AI Agent"""
import logging
from typing import Dict, Any, List
import os
import json
from datetime import datetime

from src.scrapers import MockScraper
from src.analyzers import SentimentAnalyzer, EngagementAnalyzer, SoVAnalyzer
from src.utils import DataProcessor, ReportGenerator
from src.config import (
    NUM_RESULTS, OUTPUT_DIR, DATA_DIR
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SoVAnalysisAgent:
    """Main AI Agent for Share of Voice Analysis"""
    
    def __init__(self, brand_keywords: Dict[str, List[str]] = None, search_keywords: List[str] = None):
        self.logger = logger
        
        # Set brand and search keywords
        if brand_keywords is None:
            self.brand_keywords = {
                "atomberg": ["atomberg", "smart fan atomberg", "atomberg ceiling fan"],
                "havells": ["havells"],
                "orient": ["orient"],
                "ortem": ["ortem"],
                "agni": ["agni"],
                "carro": ["carro"],
                "luminous": ["luminous"],
            }
        else:
            self.brand_keywords = brand_keywords
            
        if search_keywords is None:
            self.search_keywords = [
                "smart fan",
                "smart ceiling fan",
                "WiFi controlled fan",
            ]
        else:
            self.search_keywords = search_keywords
        
        # Initialize scraper
        self.scraper = MockScraper()
        
        # Initialize analyzers
        self.sentiment_analyzer = SentimentAnalyzer()
        self.engagement_analyzer = EngagementAnalyzer()
        self.sov_analyzer = SoVAnalyzer()
        
        # Initialize utilities
        self.data_processor = DataProcessor()
        self.report_generator = ReportGenerator(OUTPUT_DIR)
        
        # Ensure output directories exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(DATA_DIR, exist_ok=True)
        
        self.logger.info("SoV Analysis Agent initialized")
        self.logger.info(f"Brands to track: {list(self.brand_keywords.keys())}")
        self.logger.info(f"Search keywords: {self.search_keywords}")
    
    def analyze_keyword(self, keyword: str) -> Dict[str, Any]:
        """
        Complete analysis for a single keyword.
        
        Args:
            keyword: Search keyword to analyze
            
        Returns:
            Comprehensive analysis results
        """
        self.logger.info(f"Starting analysis for keyword: '{keyword}'")
        
        # Search using mock scraper
        results = self.scraper.search(keyword, NUM_RESULTS)
        self.logger.info(f"Retrieved {len(results)} results")
        
        # Deduplicate
        results = self.data_processor.deduplicate_results(results)
        
        # Process and analyze results
        analysis = {
            "keyword": keyword,
            "timestamp": datetime.now().isoformat(),
            "raw_results_count": len(results),
            "raw_results": results[:5],  # Include first 5 for reference
            "brand_analysis": self._analyze_brands(results, self.brand_keywords),
            "sentiment_analysis": self._analyze_sentiments(results),
            "engagement_analysis": self._analyze_engagement(results),
        }
        
        # Calculate SoV
        sov_analysis = self._calculate_sov(analysis)
        analysis["sov_analysis"] = sov_analysis
        
        self.logger.info(f"Analysis complete for keyword: '{keyword}'")
        return analysis
    
    def _analyze_brands(self, results: List[Dict[str, Any]], brand_keywords: Dict[str, List[str]] = None) -> Dict[str, Any]:
        """Analyze brand mentions in results"""
        if brand_keywords is None:
            # Default brand keywords if not provided
            brand_keywords = {
                "atomberg": ["atomberg", "smart fan atomberg", "atomberg ceiling fan"],
                "havells": ["havells"],
                "orient": ["orient"],
                "ortem": ["ortem"],
                "agni": ["agni"],
                "carro": ["carro"],
                "luminous": ["luminous"],
            }
        
        brand_mentions = {brand: 0 for brand in brand_keywords.keys()}
        brand_results = {brand: [] for brand in brand_keywords.keys()}
        
        for result in results:
            text = (result.get("title", "") + " " + result.get("snippet", "")).lower()
            
            for brand, keywords in brand_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in text:
                        brand_mentions[brand] += 1
                        brand_results[brand].append(result)
                        break
        
        return {
            "mentions": brand_mentions,
            "total_results": len(results),
            "brand_results": {brand: len(items) for brand, items in brand_results.items()}
        }
    
    def _analyze_sentiments(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment of content"""
        sentiments = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_polarity = 0
        
        for item in results:
            # Use sentiment from mock data if available
            if "sentiment" in item:
                sentiment_label = item["sentiment"]
            else:
                text = item.get("title", "") + " " + item.get("snippet", "")
                sentiment_obj = self.sentiment_analyzer.analyze_sentiment(text)
                sentiment_label = sentiment_obj.get("sentiment", "neutral")
                total_polarity += sentiment_obj.get("polarity", 0)
            
            sentiments.append(sentiment_label)
            
            if sentiment_label == "positive":
                positive_count += 1
            elif sentiment_label == "negative":
                negative_count += 1
            else:
                neutral_count += 1
        
        total = len(results)
        
        return {
            "total_items": total,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "positive_percentage": round((positive_count / total * 100) if total > 0 else 0, 2),
            "negative_percentage": round((negative_count / total * 100) if total > 0 else 0, 2),
            "neutral_percentage": round((neutral_count / total * 100) if total > 0 else 0, 2),
            "avg_polarity": round(total_polarity / total if total > 0 else 0, 3),
        }
    
    def _analyze_engagement(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement metrics"""
        total_likes = sum(item.get("likes", 0) for item in results)
        total_comments = sum(item.get("comments", 0) for item in results)
        total_shares = sum(item.get("shares", 0) for item in results)
        total_views = sum(item.get("views", 0) for item in results)
        total_engagement = total_likes + total_comments + total_shares
        
        return {
            "total_items": len(results),
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_views": total_views,
            "total_engagement": total_engagement,
            "avg_likes_per_item": round(total_likes / len(results) if results else 0, 2),
            "avg_engagement_per_item": round(total_engagement / len(results) if results else 0, 2),
        }
    
    def _calculate_sov(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Share of Voice metrics"""
        brand_data = analysis.get("brand_analysis", {})
        mentions = brand_data.get("mentions", {})
        
        atomberg_mentions = mentions.get("atomberg", 0)
        competitor_mentions = {
            brand: count for brand, count in mentions.items()
            if brand != "atomberg"
        }
        
        # Calculate mention-based SoV
        mention_sov = self.sov_analyzer.calculate_mention_based_sov(
            atomberg_mentions, competitor_mentions
        )
        
        # Calculate engagement-based SoV
        engagement_data = analysis.get("engagement_analysis", {})
        atomberg_engagement = engagement_data.get("total_engagement", 0)
        competitor_engagement = {brand: 100 for brand in competitor_mentions.keys()}
        
        engagement_sov = self.sov_analyzer.calculate_engagement_based_sov(
            atomberg_engagement, competitor_engagement
        )
        
        # Calculate positive voice
        sentiment_data = analysis.get("sentiment_analysis", {})
        positive_sov = self.sov_analyzer.calculate_positive_voice_sov(
            sentiment_data.get("positive_count", 0),
            sentiment_data.get("total_items", 1),
            {brand: (25, 100) for brand in competitor_mentions.keys()}
        )
        
        # Composite SoV
        composite_sov = self.sov_analyzer.calculate_composite_sov(
            mention_sov, engagement_sov, positive_sov
        )
        
        summary = self.sov_analyzer.generate_sov_summary(composite_sov)
        
        return {
            "mention_based": mention_sov,
            "engagement_based": engagement_sov,
            "positive_voice": positive_sov,
            "composite_sov": composite_sov,
            "summary": summary,
        }
    
    def analyze_multiple_keywords(self, keywords: List[str] = None) -> Dict[str, Any]:
        """
        Analyze multiple keywords and aggregate results.
        
        Args:
            keywords: List of keywords to analyze. If None, uses instance search_keywords
            
        Returns:
            Aggregated analysis results
        """
        if keywords is None:
            keywords = self.search_keywords
        
        all_analyses = {}
        
        for keyword in keywords:
            analysis = self.analyze_keyword(keyword)
            all_analyses[keyword] = analysis
        
        # Generate aggregate insights
        aggregate_insights = self._generate_aggregate_insights(all_analyses)
        
        return {
            "keyword_analyses": all_analyses,
            "aggregate_insights": aggregate_insights,
            "timestamp": datetime.now().isoformat(),
        }
    
    def _generate_aggregate_insights(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights across multiple keyword analyses"""
        all_sov_scores = []
        
        for keyword, analysis in analyses.items():
            sov_data = analysis.get("sov_analysis", {})
            if sov_data:
                all_sov_scores.append(sov_data.get("composite_sov", {}).get("atomberg", 0))
        
        avg_sov = sum(all_sov_scores) / len(all_sov_scores) if all_sov_scores else 0
        
        return {
            "average_sov": round(avg_sov, 2),
            "keywords_analyzed": len(analyses),
            "top_keywords": sorted(
                [(kw, analyses[kw].get("sov_analysis", {}).get("composite_sov", {}).get("atomberg", 0))
                 for kw in analyses.keys()],
                key=lambda x: x[1],
                reverse=True
            )[:5] if analyses else [],
        }
    
    def generate_report(self, analysis_data: Dict[str, Any], format: str = "html") -> bool:
        """
        Generate a report from analysis data.
        
        Args:
            analysis_data: Analysis results
            format: Report format (html, txt)
            
        Returns:
            Success status
        """
        if format == "html":
            return self.report_generator.generate_html_report(analysis_data)
        elif format == "txt":
            return self.report_generator.generate_text_report(analysis_data)
        else:
            self.logger.error(f"Unsupported format: {format}")
            return False
    
    def save_analysis(self, analysis_data: Dict[str, Any], filename: str = "analysis.json") -> bool:
        """
        Save analysis data to file.
        
        Args:
            analysis_data: Analysis results
            filename: Output filename
            
        Returns:
            Success status
        """
        filepath = os.path.join(DATA_DIR, filename)
        return self.data_processor.save_to_json(analysis_data, filepath)


def get_user_input():
    """Get user input for brands and search keywords"""
    print("\n" + "="*70)
    print("ATOMBERG SHARE OF VOICE ANALYSIS - CONFIGURATION")
    print("="*70 + "\n")
    
    # Get brand information
    print("📊 BRAND CONFIGURATION")
    print("-" * 70)
    
    # Get primary brand name
    primary_brand = input("Enter your primary brand name (default: atomberg): ").strip()
    if not primary_brand:
        primary_brand = "atomberg"
    
    # Get primary brand keywords
    primary_keywords_str = input(f"Enter keywords for '{primary_brand}' (comma-separated, e.g., 'atomberg,smart fan atomberg'): ").strip()
    if primary_keywords_str:
        primary_keywords = [kw.strip() for kw in primary_keywords_str.split(",")]
    else:
        primary_keywords = [primary_brand, f"smart fan {primary_brand}", f"{primary_brand} ceiling fan"]
    
    # Get competitor brands
    competitors_str = input("Enter competitor brand names (comma-separated, e.g., 'havells,orient,agni'): ").strip()
    if competitors_str:
        competitors = [brand.strip() for brand in competitors_str.split(",")]
    else:
        competitors = ["havells", "orient", "ortem", "agni", "carro", "luminous"]
    
    # Build brand keywords dictionary
    brand_keywords = {primary_brand: primary_keywords}
    for competitor in competitors:
        brand_keywords[competitor] = [competitor]
    
    print("\n✅ Brand Configuration:")
    for brand, keywords in brand_keywords.items():
        print(f"   • {brand}: {keywords}")
    
    # Get search keywords
    print("\n🔍 SEARCH KEYWORDS")
    print("-" * 70)
    
    search_keywords_str = input("Enter search keywords to analyze (comma-separated, e.g., 'smart fan,smart ceiling fan,WiFi fan'): ").strip()
    if search_keywords_str:
        search_keywords = [kw.strip() for kw in search_keywords_str.split(",")]
    else:
        search_keywords = [
            "smart fan",
            "smart ceiling fan",
            "WiFi controlled fan",
        ]
    
    print("\n✅ Search Keywords:")
    for i, kw in enumerate(search_keywords, 1):
        print(f"   {i}. {kw}")
    
    return brand_keywords, search_keywords


def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("ATOMBERG SHARE OF VOICE (SoV) ANALYSIS AGENT")
    print("="*70 + "\n")
    
    # Get user input
    brand_keywords, search_keywords = get_user_input()
    
    # Initialize agent with user inputs
    agent = SoVAnalysisAgent(brand_keywords=brand_keywords, search_keywords=search_keywords)
    
    # Analyze multiple keywords
    print("\n\n" + "="*70)
    print("STARTING ANALYSIS")
    print("="*70 + "\n")
    
    logger.info("Starting analysis of search keywords...")
    results = agent.analyze_multiple_keywords()
    
    # Save results
    logger.info("Saving analysis results...")
    agent.save_analysis(results)
    
    # Generate reports
    logger.info("Generating HTML report...")
    agent.generate_report(results, format="html")
    
    logger.info("Generating text report...")
    agent.generate_report(results, format="txt")
    
    # Print summary to console
    print("\n" + "="*70)
    print("ANALYSIS SUMMARY")
    print("="*70)
    
    insights = results.get("aggregate_insights", {})
    print(f"\nAverage Share of Voice: {insights.get('average_sov', 0)}%")
    print(f"Keywords Analyzed: {insights.get('keywords_analyzed', 0)}")
    
    print("\nTop Keywords by Atomberg SoV:")
    for keyword, sov in insights.get('top_keywords', []):
        print(f"  • {keyword}: {sov}%")
    
    print("\nDetailed Results by Keyword:")
    print("-" * 70)
    
    for keyword, analysis in results.get("keyword_analyses", {}).items():
        sov_data = analysis.get("sov_analysis", {})
        print(f"\n📊 Keyword: '{keyword}'")
        print(f"   Atomberg SoV: {sov_data.get('composite_sov', {}).get('atomberg', 0)}%")
        print(f"   Rank: {sov_data.get('summary', {}).get('rank', 'N/A')}/{sov_data.get('summary', {}).get('total_brands', 'N/A')}")
    
    print("\n" + "="*70)
    print(f"✅ Analysis complete! Reports saved to: {OUTPUT_DIR}")
    print(f"📁 Data saved to: {DATA_DIR}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

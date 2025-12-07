"""Sentiment analysis module"""
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze sentiment of text content"""
    
    def __init__(self):
        self.logger = logger
        self.use_textblob = False
        try:
            from textblob import TextBlob
            self.textblob = TextBlob
            self.use_textblob = True
        except ImportError:
            self.logger.info("TextBlob not available, using fallback sentiment analysis")
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with polarity and subjectivity scores
        """
        if not text or not isinstance(text, str):
            return {"polarity": 0.0, "subjectivity": 0.0, "sentiment": "neutral"}
        
        try:
            if self.use_textblob:
                blob = self.textblob(text)
                polarity = blob.sentiment.polarity  # -1 to 1
                subjectivity = blob.sentiment.subjectivity  # 0 to 1
            else:
                # Fallback: simple sentiment based on keywords
                polarity, subjectivity = self._simple_sentiment(text)
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "polarity": round(polarity, 3),
                "subjectivity": round(subjectivity, 3),
                "sentiment": sentiment,
            }
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {str(e)}")
            return {"polarity": 0.0, "subjectivity": 0.0, "sentiment": "neutral"}
    
    def batch_analyze(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Analyze sentiment for multiple texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment dictionaries
        """
        return [self.analyze_sentiment(text) for text in texts]
    
    def _simple_sentiment(self, text: str) -> Tuple[float, float]:
        """
        Simple sentiment analysis using keyword matching.
        """
        positive_words = {
            "good", "great", "excellent", "amazing", "awesome", "love", "best",
            "wonderful", "fantastic", "perfect", "nice", "smart", "innovative",
            "efficient", "powerful", "reliable", "quality", "impressive", "outstanding",
            "superior", "elegant", "modern", "advanced", "affordable", "best value"
        }
        negative_words = {
            "bad", "poor", "terrible", "awful", "hate", "worst", "horrible",
            "disappointing", "useless", "broken", "cheap", "slow", "unreliable",
            "weak", "disappointing", "issue", "problem", "defect", "inferior"
        }
        
        text_lower = text.lower()
        words = text_lower.split()
        
        pos_count = sum(1 for word in words if any(pos in word for pos in positive_words))
        neg_count = sum(1 for word in words if any(neg in word for neg in negative_words))
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0, 0.3  # Default neutral with some subjectivity
        
        polarity = (pos_count - neg_count) / total
        subjectivity = min(1.0, total / len(words)) if words else 0.0
        
        return min(1.0, max(-1.0, polarity)), min(1.0, subjectivity)
    
    def get_sentiment_distribution(self, sentiments: List[str]) -> Dict[str, float]:
        """
        Get distribution of sentiments.
        
        Args:
            sentiments: List of sentiment labels
            
        Returns:
            Dictionary with sentiment distribution percentages
        """
        total = len(sentiments)
        if total == 0:
            return {"positive": 0.0, "negative": 0.0, "neutral": 100.0}
        
        counts = {
            "positive": sentiments.count("positive"),
            "negative": sentiments.count("negative"),
            "neutral": sentiments.count("neutral"),
        }
        
        return {
            label: round((count / total) * 100, 2)
            for label, count in counts.items()
        }

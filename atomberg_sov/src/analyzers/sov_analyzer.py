"""Share of Voice analyzer"""
from typing import Dict, List, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SoVAnalyzer:
    """Calculate and analyze Share of Voice metrics"""
    
    def __init__(self):
        self.logger = logger
    
    def calculate_mention_based_sov(self, atomberg_mentions: int, competitor_mentions: Dict[str, int]) -> Dict[str, float]:
        """
        Calculate SoV based on mention counts.
        
        Args:
            atomberg_mentions: Number of Atomberg mentions
            competitor_mentions: Dictionary of competitor mentions
            
        Returns:
            SoV percentages for each brand
        """
        total_mentions = atomberg_mentions + sum(competitor_mentions.values())
        
        if total_mentions == 0:
            return {"atomberg": 0.0, "competitors": {}}
        
        sov = {
            "atomberg": round((atomberg_mentions / total_mentions) * 100, 2),
            "competitors": {
                brand: round((mentions / total_mentions) * 100, 2)
                for brand, mentions in competitor_mentions.items()
            }
        }
        
        return sov
    
    def calculate_engagement_based_sov(self, atomberg_engagement: float, competitor_engagement: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate SoV based on engagement metrics.
        
        Args:
            atomberg_engagement: Atomberg engagement sum
            competitor_engagement: Dictionary of competitor engagement
            
        Returns:
            SoV percentages based on engagement
        """
        total_engagement = atomberg_engagement + sum(competitor_engagement.values())
        
        if total_engagement == 0:
            return {"atomberg": 0.0, "competitors": {}}
        
        sov = {
            "atomberg": round((atomberg_engagement / total_engagement) * 100, 2),
            "competitors": {
                brand: round((engagement / total_engagement) * 100, 2)
                for brand, engagement in competitor_engagement.items()
            }
        }
        
        return sov
    
    def calculate_positive_voice_sov(self, atomberg_positive_count: int, atomberg_total_count: int,
                                     competitor_data: Dict[str, Tuple[int, int]]) -> Dict[str, float]:
        """
        Calculate Share of Positive Voice.
        
        Args:
            atomberg_positive_count: Count of positive mentions for Atomberg
            atomberg_total_count: Total mentions for Atomberg
            competitor_data: Dictionary mapping competitor names to (positive_count, total_count) tuples
            
        Returns:
            SoV of positive mentions for each brand
        """
        atomberg_pov = (atomberg_positive_count / atomberg_total_count * 100) if atomberg_total_count > 0 else 0
        
        competitor_pov = {
            brand: (pos_count / total_count * 100) if total_count > 0 else 0
            for brand, (pos_count, total_count) in competitor_data.items()
        }
        
        # Total positive voice
        total_positive = atomberg_positive_count + sum(pos for pos, _ in competitor_data.values())
        total_mentions = atomberg_total_count + sum(total for _, total in competitor_data.values())
        
        if total_mentions == 0:
            positive_sov = {"atomberg": 0.0, "competitors": {}}
        else:
            positive_sov = {
                "atomberg": round((atomberg_positive_count / total_positive * 100) if total_positive > 0 else 0, 2),
                "competitors": {
                    brand: round((competitor_data[brand][0] / total_positive * 100) if total_positive > 0 else 0, 2)
                    for brand in competitor_data.keys()
                }
            }
        
        return {
            "positive_voice_percentage": {
                "atomberg": round(atomberg_pov, 2),
                "competitors": {brand: round(pov, 2) for brand, pov in competitor_pov.items()}
            },
            "share_of_positive_voice": positive_sov,
        }
    
    def calculate_composite_sov(self, mention_sov: Dict[str, Any], engagement_sov: Dict[str, Any],
                               positive_sov: Dict[str, Any], weights: Dict[str, float] = None) -> Dict[str, float]:
        """
        Calculate composite SoV using weighted metrics.
        
        Args:
            mention_sov: SoV based on mentions
            engagement_sov: SoV based on engagement
            positive_sov: Share of positive voice
            weights: Weights for each metric (must sum to 1.0)
            
        Returns:
            Composite SoV scores
        """
        if weights is None:
            weights = {
                "mention": 0.4,
                "engagement": 0.4,
                "positive": 0.2,
            }
        
        # Ensure weights sum to 1
        total_weight = sum(weights.values())
        if total_weight != 1.0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        atomberg_composite = (
            mention_sov.get("atomberg", 0) * weights["mention"] +
            engagement_sov.get("atomberg", 0) * weights["engagement"] +
            positive_sov.get("share_of_positive_voice", {}).get("atomberg", 0) * weights["positive"]
        )
        
        composite_sov = {
            "atomberg": round(atomberg_composite, 2),
            "competitors": {}
        }
        
        # Calculate for each competitor
        all_competitors = set()
        all_competitors.update(mention_sov.get("competitors", {}).keys())
        all_competitors.update(engagement_sov.get("competitors", {}).keys())
        
        for brand in all_competitors:
            brand_composite = (
                mention_sov.get("competitors", {}).get(brand, 0) * weights["mention"] +
                engagement_sov.get("competitors", {}).get(brand, 0) * weights["engagement"] +
                positive_sov.get("share_of_positive_voice", {}).get("competitors", {}).get(brand, 0) * weights["positive"]
            )
            composite_sov["competitors"][brand] = round(brand_composite, 2)
        
        return composite_sov
    
    def generate_sov_summary(self, composite_sov: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate a summary of SoV analysis.
        
        Args:
            composite_sov: Composite SoV scores
            
        Returns:
            Summary with rankings and insights
        """
        atomberg_score = composite_sov["atomberg"]
        competitor_scores = [(brand, score) for brand, score in composite_sov["competitors"].items()]
        competitor_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Calculate rank
        rank = 1
        for brand, score in competitor_scores:
            if score > atomberg_score:
                rank += 1
        
        total_brands = len(competitor_scores) + 1
        
        return {
            "atomberg_sov": atomberg_score,
            "rank": rank,
            "total_brands": total_brands,
            "top_competitor": competitor_scores[0] if competitor_scores else None,
            "competitor_rankings": competitor_scores,
            "performance_gap": round(atomberg_score - competitor_scores[0][1], 2) if competitor_scores else 0,
        }

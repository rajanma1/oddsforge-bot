import numpy as np
from typing import Optional

class QuantMath:
    @staticmethod
    def calculate_ev(p_true: float, p_market: float) -> float:
        """
        Calculate Expected Value (EV).
        EV = (p_true * profit) - (p_false * stake)
        Profit per $1 stake = (1 / p_market) - 1
        """
        if p_market <= 0 or p_market >= 1:
            return -1.0
        
        profit_if_win = (1.0 / p_market) - 1.0
        p_false = 1.0 - p_true
        
        ev = (p_true * profit_if_win) - (p_false * 1.0)
        return ev

    @staticmethod
    def calculate_kelly_size(p_true: float, p_market: float, fraction: float = 0.25) -> float:
        """
        Calculate Kelly Criterion position size.
        f* = (b*p - q) / b
        where:
        b = decimal odds - 1 (profit_if_win)
        p = probability of winning
        q = probability of losing (1-p)
        """
        if p_market <= 0 or p_market >= 1:
            return 0.0
            
        b = (1.0 / p_market) - 1.0
        p = p_true
        q = 1.0 - p
        
        if b <= 0:
            return 0.0
            
        f_star = (b * p - q) / b
        
        # Apply fractional Kelly for safety and return
        return max(0.0, f_star * fraction)

class ProbabilityEstimator:
    """
    Abstract base class for probability estimation.
    Can be swapped with ML models, oracle feeds, or statistical signals.
    """
    def estimate(self, market_data: dict, external_signals: dict) -> float:
        # Simple baseline: use market price with a small sentiment adjustment
        # In production, this would be a sophisticated model.
        market_price = market_data.get('price', 0.5)
        sentiment = external_signals.get('sentiment', 0.0) # -1 to 1
        
        adjusted_prob = market_price + (sentiment * 0.02)
        return max(0.01, min(0.99, adjusted_prob))

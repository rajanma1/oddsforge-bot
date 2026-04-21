import asyncio
from typing import Dict, Any
from core.math import QuantMath, ProbabilityEstimator
from api.clob_client import PolymarketCLOB
from risk.risk_manager import RiskManager
from config.settings import settings
import structlog

logger = structlog.get_logger(__name__)

class OrderManager:
    """
    Coordinates trade execution logic: Math -> Risk -> CLOB
    """
    def __init__(
        self, 
        clob: PolymarketCLOB, 
        risk: RiskManager, 
        math: QuantMath, 
        prob_estimator: ProbabilityEstimator
    ):
        self.clob = clob
        self.risk = risk
        self.math = math
        self.prob_estimator = prob_estimator

    async def evaluate_and_execute(self, market: Dict[str, Any]):
        """
        Main logic for a single market opportunity.
        """
        try:
            market_price = market.get('midpoint_price')
            token_id = market.get('yes_token_id')
            
            if not market_price or not token_id:
                return

            # 1. Estimate True Probability
            # In a real bot, we'd pass external signals here
            p_true = self.prob_estimator.estimate(market, {})
            
            # 2. Calculate EV
            ev = self.math.calculate_ev(p_true, market_price)
            
            if ev < settings.EV_THRESHOLD:
                # No edge found
                return

            logger.info("edge_detected", 
                        question=market.get('question'), 
                        p_true=p_true, 
                        p_market=market_price, 
                        ev=ev)

            # 3. Calculate Kelly Size
            bankroll = settings.BANKROLL
            kelly_fraction = self.math.calculate_kelly_size(p_true, market_price, settings.KELLY_FRACTION)
            
            if kelly_fraction <= 0:
                return

            target_size_usdc = bankroll * kelly_fraction
            
            # Cap by settings
            target_size_usdc = min(target_size_usdc, settings.MAX_POSITION_SIZE)

            # Minimum order size check
            if target_size_usdc < settings.MIN_ORDER_SIZE:
                logger.debug("order_too_small", size=target_size_usdc, min=settings.MIN_ORDER_SIZE)
                return

            # 4. Risk Check
            if not self.risk.check_trade_safety(target_size_usdc):
                return

            # 5. Execute Order
            # For a limit order slightly better than midpoint (e.g., 0.1 cent better)
            # If buying "Yes", we want to pay as little as possible.
            execution_price = round(market_price + 0.001, 3)
            if execution_price >= 1.0: execution_price = 0.999
            
            # Calculate quantity (number of shares)
            # Size in USDC / Price = Shares
            quantity = round(target_size_usdc / execution_price, 2)

            resp = await self.clob.place_limit_order(
                token_id=token_id,
                price=execution_price,
                size=quantity,
                side="BUY"
            )

            # 6. Update Risk Metrics
            success = resp.get('status') in ['OK', 'DRY_RUN']
            self.risk.update_on_trade(target_size_usdc if success else 0, success)
            
            if success:
                logger.info("trade_executed_successfully", 
                            token_id=token_id, 
                            price=execution_price, 
                            quantity=quantity)
            else:
                logger.error("trade_execution_failed", error=resp.get('error'))

        except Exception as e:
            logger.error("execution_pipeline_error", error=str(e))

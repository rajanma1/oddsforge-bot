import time
from typing import Dict, Any
from config.settings import settings
import structlog

logger = structlog.get_logger(__name__)

class RiskManager:
    """
    Handles risk limits, position sizing constraints, and circuit breakers.
    """
    def __init__(self):
        self.daily_pnl = 0.0
        self.total_exposure = 0.0
        self.consecutive_failures = 0
        self.last_reset_time = time.time()
        self.halted = False

    def check_trade_safety(self, size: float) -> bool:
        """
        Validates if a trade is safe to execute based on risk parameters.
        """
        # 1. Reset daily stats if 24h passed
        if time.time() - self.last_reset_time > 86400:
            self.reset_daily_stats()

        # 2. Check circuit breaker
        if self.halted or self.consecutive_failures >= 3:
            logger.warning("risk_halt_active", failures=self.consecutive_failures)
            return False

        # 3. Check daily loss limit
        # Note: This is a simplified check. Real-time PNL tracking would be better.
        if self.daily_pnl < -(settings.DAILY_LOSS_LIMIT * settings.BANKROLL):
            logger.warning("daily_loss_limit_reached", pnl=self.daily_pnl)
            return False

        # 4. Check total exposure
        if self.total_exposure + size > settings.TOTAL_EXPOSURE_CAP:
            logger.warning("exposure_cap_reached", current=self.total_exposure, adding=size)
            return False

        # 5. Check max position size
        if size > settings.MAX_POSITION_SIZE:
            logger.warning("max_position_size_exceeded", size=size)
            return False

        return True

    def update_on_trade(self, size: float, success: bool):
        """
        Updates risk metrics after a trade attempt.
        """
        if success:
            self.total_exposure += size
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1
            if self.consecutive_failures >= 3:
                self.halted = True
                logger.error("circuit_breaker_tripped", failures=self.consecutive_failures)

    def reset_daily_stats(self):
        self.daily_pnl = 0.0
        self.last_reset_time = time.time()
        self.halted = False
        self.consecutive_failures = 0
        logger.info("daily_risk_stats_reset")

    def release_exposure(self, size: float):
        self.total_exposure = max(0.0, self.total_exposure - size)

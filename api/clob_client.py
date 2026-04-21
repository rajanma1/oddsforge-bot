import asyncio
from typing import Dict, Any, Optional
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from config.settings import settings
import structlog

logger = structlog.get_logger(__name__)

class PolymarketCLOB:
    """
    Wrapper for Polymarket CLOB API (Trading and Orderbook)
    """
    def __init__(self):
        # Initialize the official SDK client if credentials exist
        if settings.POLY_PRIVATE_KEY:
            self.client = ClobClient(
                host="https://clob.polymarket.com",
                key=settings.POLY_API_KEY,
                secret=settings.POLY_API_SECRET,
                passphrase=settings.POLY_API_PASSPHRASE,
                private_key=settings.POLY_PRIVATE_KEY.get_secret_value(),
                chain_id=settings.CHAIN_ID
            )
            logger.info("clob_client_initialized", host="https://clob.polymarket.com")
        else:
            self.client = None
            logger.warning("clob_client_uninitialized_missing_creds")

    async def is_ready(self) -> bool:
        """
        Verifies if the client can connect to the CLOB API.
        """
        try:
            if not self.client:
                return False
            # Simple check to see if we can fetch something
            resp = self.client.get_ok()
            return resp == "OK"
        except Exception as e:
            logger.error("clob_health_check_failed", error=str(e))
            return False

    async def get_market_price(self, token_id: str) -> Optional[float]:
        """
        Fetches the midpoint price for a specific token.
        """
        try:
            # Use run_in_executor if the SDK call is blocking, 
            # but most py-clob-client methods have async variants or are lightweight.
            # Here we assume standard SDK usage.
            resp = self.client.get_midpoint(token_id)
            if resp and 'mid' in resp:
                return float(resp['mid'])
            return None
        except Exception as e:
            logger.error("get_price_failed", token_id=token_id, error=str(e))
            return None

    async def place_limit_order(self, token_id: str, price: float, size: float, side: str) -> Dict[str, Any]:
        """
        Places a limit order on the CLOB.
        side: "BUY" or "SELL"
        """
        if settings.DRY_RUN:
            logger.info("dry_run_order_placement", token_id=token_id, price=price, size=size, side=side)
            return {"status": "DRY_RUN", "order_id": "mock_id"}

        try:
            order_args = OrderArgs(
                price=price,
                size=size,
                side=side,
                token_id=token_id
            )
            # Create and post the order
            order = self.client.create_order(order_args)
            resp = self.client.post_order(order)
            
            logger.info("order_placed", token_id=token_id, price=price, size=size, side=side, resp=resp)
            return resp
        except Exception as e:
            logger.error("order_placement_failed", token_id=token_id, error=str(e))
            return {"status": "ERROR", "error": str(e)}

    async def get_balance(self, asset_id: str) -> float:
        """
        Get USDC/pUSD balance.
        """
        try:
            # The SDK usually provides a way to check allowance and balance
            # For simplicity, returning a placeholder if not directly in basic client
            # In production, we'd use the wallet address from settings.
            return 1000.0 # Placeholder
        except Exception as e:
            logger.error("get_balance_failed", error=str(e))
            return 0.0

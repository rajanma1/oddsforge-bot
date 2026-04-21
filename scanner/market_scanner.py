import asyncio
from typing import List, Dict, Any
from api.gamma_client import GammaClient
from api.clob_client import PolymarketCLOB
from config.settings import settings
import structlog

logger = structlog.get_logger(__name__)

class MarketScanner:
    """
    Scans and filters markets for potential trading opportunities.
    """
    def __init__(self, gamma_client: GammaClient, clob_client: PolymarketCLOB):
        self.gamma = gamma_client
        self.clob = clob_client

    async def scan(self) -> List[Dict[str, Any]]:
        """
        Full scan cycle: Fetch -> Filter -> Enrich with Price
        """
        logger.info("starting_market_scan")
        
        # 1. Fetch active markets
        raw_markets = await self.gamma.get_active_markets(limit=200)
        if not raw_markets:
            return []

        # 2. Filter for crypto binaries
        crypto_markets = await self.gamma.filter_crypto_binaries(raw_markets)
        
        # 3. Filter by liquidity and enrichment
        opportunities = []
        for market in crypto_markets:
            try:
                # Check liquidity (if available in Gamma metadata)
                liquidity = float(market.get('liquidity', 0))
                if liquidity < settings.MIN_LIQUIDITY:
                    continue

                # Get token IDs for binary outcomes (usually Yes/No)
                tokens = market.get('tokens', [])
                if len(tokens) != 2:
                    continue

                # We focus on the "Yes" token usually (index 0)
                yes_token = tokens[0]
                no_token = tokens[1]
                
                # Enrich with CLOB midpoint price
                price = await self.clob.get_market_price(yes_token['token_id'])
                
                if price:
                    market['midpoint_price'] = price
                    market['yes_token_id'] = yes_token['token_id']
                    market['no_token_id'] = no_token['token_id']
                    opportunities.append(market)
                    
            except Exception as e:
                logger.error("market_enrichment_failed", market_id=market.get('id'), error=str(e))
                continue

        logger.info("scan_complete", opportunities_found=len(opportunities))
        return opportunities

import hmac
import hashlib
import time
import aiohttp
import asyncio
from typing import List, Dict, Any
from config.settings import settings
import structlog

logger = structlog.get_logger(__name__)

class GammaClient:
    """
    Client for Polymarket Gamma API (Market Discovery)
    """
    BASE_URL = "https://gamma-api.polymarket.com"

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_active_markets(self, limit: int = 100) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/markets?active=true&closed=false&limit={limit}&order=volumeNum&ascending=false"
        session = await self.get_session()
        try:
            async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error("gamma_api_error", status=response.status)
                        return []
            except Exception as e:
                logger.error("gamma_api_exception", error=str(e))
                return []

    async def filter_crypto_binaries(self, markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters for short-term crypto binaries
        """
        filtered = []
        for m in markets:
            q = m.get('question', '').lower()
            # Look for BTC, ETH, SOL price action binaries
            if any(coin in q for coin in ['btc', 'eth', 'sol', 'xrp']):
                if m.get('tokens') and len(m['tokens']) == 2: # Binary
                    filtered.append(m)
        return filtered

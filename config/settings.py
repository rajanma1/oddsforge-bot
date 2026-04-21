from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from typing import Optional

class Settings(BaseSettings):
    # Polymarket API Credentials
    POLY_API_KEY: str = Field(..., description="Polymarket CLOB API Key")
    POLY_API_SECRET: str = Field(..., description="Polymarket CLOB API Secret")
    POLY_API_PASSPHRASE: str = Field(..., description="Polymarket CLOB API Passphrase")
    POLY_PRIVATE_KEY: SecretStr = Field(..., description="Ethereum Private Key for signing orders")
    
    # Wallet Settings
    FUNDER_ADDRESS: Optional[str] = Field(None, description="Address of the funder wallet")
    CHAIN_ID: int = 137  # Polygon Mainnet
    
    # Trading Strategy Settings
    BANKROLL: float = 10000.0      # Base bankroll for Kelly sizing
    MIN_LIQUIDITY: float = 500.0  # Minimum liquidity in USDC
    MIN_ORDER_SIZE: float = 5.0    # Minimum USDC per trade
    EV_THRESHOLD: float = 0.005   # 0.5 cent edge
    KELLY_FRACTION: float = 0.25  # 0.25x fractional Kelly for safety
    MAX_POSITION_SIZE: float = 100.0 # Max USDC per trade
    DRY_RUN: bool = True
    
    # Risk Management
    DAILY_LOSS_LIMIT: float = 0.05 # 5% max daily loss
    TOTAL_EXPOSURE_CAP: float = 5000.0 # Max USDC across all open positions
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

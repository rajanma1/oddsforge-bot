from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from typing import Optional

class Settings(BaseSettings):
    # Polymarket API Credentials
    POLY_API_KEY: Optional[str] = Field(None, description="Polymarket CLOB API Key")
    POLY_API_SECRET: Optional[str] = Field(None, description="Polymarket CLOB API Secret")
    POLY_API_PASSPHRASE: Optional[str] = Field(None, description="Polymarket CLOB API Passphrase")
    POLY_PRIVATE_KEY: Optional[SecretStr] = Field(None, description="Ethereum Private Key for signing orders")
    
    # Wallet Settings
    FUNDER_ADDRESS: Optional[str] = Field(None, description="Address of the funder wallet")
    CHAIN_ID: int = 137  # Polygon Mainnet
    
    # Trading Strategy Settings
    BANKROLL: float = 3.0      # User budget: $3
    MIN_LIQUIDITY: float = 100.0  # Lowered for $3 budget
    MIN_ORDER_SIZE: float = 0.5    # Minimum $0.50 per trade
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

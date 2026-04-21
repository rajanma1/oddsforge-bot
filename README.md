# OddsForge Bot: High-Frequency Polymarket Quant Bot

A production-ready, automated quantitative trading bot for Polymarket designed to capture tiny mispricings in short-duration binary markets.

## Features
- **High-Frequency Scanning**: Asynchronous loops for low-latency market discovery.
- **Quant Math Engine**: Real-time Expected Value (EV) and Kelly Criterion sizing.
- **Official SDK**: Built on Polymarket's `py-clob-client`.
- **Security First**: Pydantic-based secret management, non-root Docker execution, and EIP-712 signing.
- **Risk Controls**: Daily loss limits, exposure caps, bankroll-aware sizing, and automatic circuit breakers.
- **Health Checks**: Startup verification of API connectivity.

## Tech Stack
- Python 3.12+ (Asyncio/Aiohttp)
- Polymarket CLOB SDK
- Pydantic Settings
- Structlog (JSON logging)
- Docker & Docker Compose

## Setup Instructions

### 1. Prerequisites
- Python 3.12+
- Docker & Docker Compose (optional for deployment)
- Polymarket API Credentials (Key, Secret, Passphrase)
- Ethereum Private Key with USDC on Polygon

### 2. Configuration
Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
```

### 3. Running the Bot
**Local Installation:**
```bash
pip install -r requirements.txt
python main.py
```

**Docker Deployment:**
```bash
docker-compose up --build -d
```

## Trading Logic
The bot follows a rigorous quantitative pipeline:
1. **Scanner**: Filters for active crypto binary markets (BTC/ETH/SOL) with sufficient liquidity.
2. **Pricing**: Fetches real-time CLOB midpoint prices.
3. **Probability**: Estimates "True Probability" using a swappable `ProbabilityEstimator`.
4. **EV Calculation**: `EV = (p_true * profit) - (p_false * stake)`.
5. **Kelly Sizing**: Calculates fractional Kelly size for optimal bankroll growth with safety.
6. **Execution**: Places limit orders slightly better than midpoint for instant fills.

## Security Checklist
- [ ] Ensure `DRY_RUN=True` for initial testing.
- [ ] Never share your `.env` file or commit it to version control.
- [ ] Use a dedicated trading wallet with limited funds.
- [ ] Monitor logs regularly for risk limit hits or API errors.

## Backtesting
The modular design allows for easy backtesting. Simply replace the `GammaClient` and `PolymarketCLOB` with historical data providers in the `MarketScanner` and `OrderManager`.

## Disclaimer
Trading involves significant risk. This bot is provided for educational purposes. Use at your own risk.

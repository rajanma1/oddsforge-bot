import asyncio
import signal
from config.settings import settings
from api.gamma_client import GammaClient
from api.clob_client import PolymarketCLOB
from scanner.market_scanner import MarketScanner
from executor.order_manager import OrderManager
from risk.risk_manager import RiskManager
from core.math import QuantMath, ProbabilityEstimator
from monitor.logger import setup_logging
from utils.wallet import WalletManager
import structlog

# Initialize logging
setup_logging()
logger = structlog.get_logger(__name__)

class OddsForgeBot:
    def __init__(self):
        self.running = True
        
        # Check if wallet exists, if not, offer creation
        if not settings.POLY_PRIVATE_KEY:
            logger.warning("no_wallet_found_generating_new")
            new_wallet = WalletManager.create_new_wallet()
            WalletManager.save_to_env(new_wallet['private_key'], new_wallet['address'])
            logger.info("please_update_env_and_restart")
            # In a real CLI, we might pause here, but for now we proceed with uninitialized client
        
        # Initialize components
        self.gamma = GammaClient()
        self.clob = PolymarketCLOB()
        self.risk = RiskManager()
        self.math = QuantMath()
        self.prob_estimator = ProbabilityEstimator()
        
        self.scanner = MarketScanner(self.gamma, self.clob)
        self.executor = OrderManager(self.clob, self.risk, self.math, self.prob_estimator)

    async def run_loop(self):
        """
        Main execution loop.
        """
        logger.info("bot_started", dry_run=settings.DRY_RUN)
        
        # Initial health check
        if not await self.clob.is_ready():
            logger.critical("clob_api_not_reachable_on_startup")
            if not settings.DRY_RUN:
                return

        while self.running:
            try:
                # 1. Scan for opportunities
                opportunities = await self.scanner.scan()
                
                # 2. Process opportunities in parallel
                tasks = []
                for opp in opportunities:
                    tasks.append(self.executor.evaluate_and_execute(opp))
                
                if tasks:
                    await asyncio.gather(*tasks)
                
                # 3. Sleep between scans (low latency but respect rate limits)
                # For HFT on Polymarket, 1-2 seconds is typical
                await asyncio.sleep(2)
                
            except asyncio.CancelledError:
                self.running = False
                break
            except Exception as e:
                logger.error("main_loop_error", error=str(e))
                await asyncio.sleep(5) # Back off on error

    def stop(self):
        logger.info("stopping_bot")
        self.running = False

    async def cleanup(self):
        await self.gamma.close()
        logger.info("cleanup_complete")

from utils.wallet import WalletManager
from utils.bridge import BridgeManager
from utils.database import init_db, SessionLocal, User
import sys
import os
import asyncio
import signal
import structlog
from config.settings import settings
from passlib.context import CryptContext
from pydantic import SecretStr

# Auth setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
init_db()

async def run_setup_wizard():
    """
    Complete operational journey: Registration -> Wallet -> Funding -> Trading.
    """
    print("\n" + "╔" + "═"*50 + "╗")
    print("║" + " "*14 + "ODDSFORGE BOT LAUNCH SYSTEM" + " "*14 + "║")
    print("╚" + "═"*50 + "╝")
    
    db = SessionLocal()
    
    # 1. USER REGISTRATION / SIGN UP
    print("\n[👤] STEP 1: USER REGISTRATION")
    username = input("Enter new username: ")
    password = input("Enter password: ")
    
    # Check if user exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"[✓] Welcome back, {username}! Authenticating...")
        user = existing_user
    else:
        # 2. WALLET CREATION
        print("\n[🔑] STEP 2: WALLET CREATION")
        new_wallet = WalletManager.create_new_wallet()
        hashed_password = pwd_context.hash(password)
        
        user = User(
            username=username,
            hashed_password=hashed_password,
            wallet_address=new_wallet['address'],
            encrypted_private_key=new_wallet['private_key'], # In prod, encrypt with user password
            balance_usdc=0.0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"    [✓] Created unique wallet for {username}: {user.wallet_address}")
    
    # 3. FUNDING MODULE
    print("\n[💰] STEP 3: FUNDING MODULE")
    print(f"    Current Balance: {user.balance_usdc} USDC")
    print("    Deposit instructions:")
    instr = BridgeManager.get_deposit_instructions(user.wallet_address)
    for chain, addr in instr.items():
        print(f"      - {chain}: {addr}")
    
    funding_choice = input("\nDetect funds automatically? [Y/n]: ")
    if funding_choice.lower() != "n":
        deposit_amount = await BridgeManager.monitor_deposits(user.wallet_address)
        user.balance_usdc += deposit_amount
        db.commit()
        print(f"\n[💎] NEW BALANCE: {user.balance_usdc} USDC")
    
    # 4. AUTOMATED TRADING ENGINE ACTIVATION
    print("\n[🚀] STEP 4: TRADING ENGINE ACTIVATION")
    if user.balance_usdc >= 0.5: # Sufficient funds check
        print(f"    [✓] Sufficient funds detected ({user.balance_usdc} USDC).")
        print("    [✓] Activating High-Frequency Trading Loop...")
        # Update settings with user's specific wallet and bankroll
        settings.POLY_PRIVATE_KEY = SecretStr(user.encrypted_private_key)
        settings.BANKROLL = user.balance_usdc
        db.close()
        return True
    else:
        print("    [X] Insufficient funds (< 0.5 USDC). Trading inactive.")
        db.close()
        return False

async def main():
    # Run the full operational journey
    operational = await run_setup_wizard()
    
    if not operational:
        print("\n[!] Setup incomplete. Bot exiting.")
        sys.exit(0)

    # Initialize components after registration and funding
    bot = OddsForgeBot()
    
    # Handle graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, bot.stop)

    try:
        await bot.run_loop()
    except Exception as e:
        logger.critical("bot_crashed", error=str(e))
    finally:
        await bot.cleanup()
        logger.info("bot_shutdown_complete")

if __name__ == "__main__":
    asyncio.run(main())

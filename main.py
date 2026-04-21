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

async def run_setup_wizard():
    """
    Interactive setup wizard for first-time users.
    """
    print("\n" + "╔" + "═"*50 + "╗")
    print("║" + " "*14 + "ODDSFORGE BOT SETUP WIZARD" + " "*14 + "║")
    print("╚" + "═"*50 + "╝")
    
    if not settings.POLY_PRIVATE_KEY:
        print("\n[!] No wallet detected.")
        choice = input("Do you want to (1) Create a new wallet or (2) Connect existing? [1/2]: ")
        
        if choice == "1":
            new_wallet = WalletManager.create_new_wallet()
            print("\n[✓] NEW WALLET GENERATED:")
            print(f"    Address: {new_wallet['address']}")
            print(f"    Private Key: {new_wallet['private_key']}")
            print("\n[!] IMPORTANT: Copy the Private Key into your .env file.")
            print(f"[!] Fund this address with at least $3 USDC on Polygon to start.")
        else:
            print("\n[!] Please paste your Private Key into the .env file and restart.")
        
        input("\nPress Enter once you have updated your .env file...")
        sys.exit(0)

async def main():
    # Run setup wizard if needed
    if not settings.POLY_PRIVATE_KEY:
        await run_setup_wizard()

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

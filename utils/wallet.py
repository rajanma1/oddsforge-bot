from eth_account import Account
import secrets
from cryptography.fernet import Fernet
import os
import structlog

logger = structlog.get_logger(__name__)

class WalletManager:
    """
    Handles secure wallet generation and private key management.
    """
    @staticmethod
    def create_new_wallet():
        """
        Generates a new Ethereum-compatible (Polygon/BSC/ETH) wallet.
        """
        # Enable HD wallet features
        Account.enable_unaudited_hdwallet_features()
        
        # Generate a random 32-byte private key
        priv = secrets.token_hex(32)
        private_key = "0x" + priv
        acct = Account.from_key(private_key)
        
        logger.info("new_wallet_generated", address=acct.address)
        return {
            "address": acct.address,
            "private_key": private_key
        }

    @staticmethod
    def encrypt_key(private_key: str, password: str) -> bytes:
        """
        Encrypts a private key using a user-provided password.
        """
        # In a real app, we'd derive a key from the password using PBKDF2
        # For this version, we'll use a simple Fernet key for the session
        key = Fernet.generate_key()
        f = Fernet(key)
        return f.encrypt(private_key.encode()), key

    @staticmethod
    def save_to_env(private_key: str, address: str):
        """
        Helper to format for .env (educational use only).
        In production, use a vault or encrypted database.
        """
        print("\n" + "="*50)
        print("CRITICAL: SAVE THESE CREDENTIALS")
        print(f"Address: {address}")
        print(f"Private Key: {private_key}")
        print("="*50 + "\n")

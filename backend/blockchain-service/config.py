from pydantic import BaseSettings
from typing import List, Dict

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "blockchain-service"
    service_version: str = "3.0.0"
    service_port: int = 8103
    debug: bool = False
    
    # Blockchain Network Configuration
    ethereum_rpc_url: str = "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
    ethereum_testnet_url: str = "https://goerli.infura.io/v3/YOUR_PROJECT_ID"
    polygon_rpc_url: str = "https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID"
    bsc_rpc_url: str = "https://bsc-dataseed.binance.org/"
    
    # Hyperledger Fabric Configuration
    hyperledger_peer_endpoint: str = "grpc://localhost:7051"
    hyperledger_orderer_endpoint: str = "grpc://localhost:7050"
    hyperledger_ca_endpoint: str = "http://localhost:7054"
    hyperledger_channel: str = "vedhavriddhi-channel"
    hyperledger_chaincode: str = "trading-chaincode"
    
    # Wallet and Key Management
    wallet_private_key: str = ""  # Should be in environment/secrets
    wallet_mnemonic: str = ""
    keystore_path: str = "/app/keystore"
    
    # Smart Contract Addresses
    settlement_contract_address: str = ""
    tokenization_contract_address: str = ""
    escrow_contract_address: str = ""
    
    # Gas Configuration
    default_gas_limit: int = 21000
    max_gas_price_gwei: int = 50
    gas_price_strategy: str = "medium"  # slow, medium, fast
    
    # Settlement Configuration
    confirmation_blocks: int = 3
    settlement_timeout_minutes: int = 30
    max_retry_attempts: int = 3
    
    # Database Configuration
    blockchain_db_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/vedhavriddhi_blockchain"
    redis_url: str = "redis://localhost:6379/10"
    
    # Supported Networks
    supported_networks: List[str] = [
        "ethereum", "polygon", "bsc", "hyperledger"
    ]
    
    # Network Monitoring
    block_monitoring_enabled: bool = True
    block_check_interval_seconds: int = 15
    
    # Security
    multi_sig_enabled: bool = True
    required_signatures: int = 2
    
    # External Services
    trading_engine_url: str = "http://localhost:8080"
    settlement_service_url: str = "http://localhost:8006"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

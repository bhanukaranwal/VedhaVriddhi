from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal

class BlockchainNetwork(str, Enum):
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    HYPERLEDGER = "hyperledger"
    BINANCE_SMART_CHAIN = "bsc"

class SettlementStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    CONFIRMED = "confirmed"
    FAILED = "failed"

class ContractType(str, Enum):
    SETTLEMENT = "settlement"
    ESCROW = "escrow"
    TOKENIZATION = "tokenization"
    GOVERNANCE = "governance"

class SettlementRequest(BaseModel):
    trade_id: str = Field(..., description="Trade identifier")
    buyer_address: str = Field(..., description="Buyer blockchain address")
    seller_address: str = Field(..., description="Seller blockchain address")
    amount: Decimal = Field(..., description="Settlement amount")
    currency: str = Field(..., description="Settlement currency")
    network: BlockchainNetwork = Field(..., description="Target blockchain network")
    settlement_date: datetime = Field(..., description="Expected settlement date")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Settlement(BaseModel):
    settlement_id: str = Field(..., description="Unique settlement identifier")
    trade_id: str = Field(..., description="Related trade ID")
    transaction_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    block_number: Optional[int] = Field(None, description="Block number")
    network: BlockchainNetwork = Field(..., description="Blockchain network")
    status: SettlementStatus = Field(default=SettlementStatus.PENDING)
    amount: Decimal = Field(..., description="Settlement amount")
    currency: str = Field(..., description="Settlement currency")
    gas_fee: Optional[Decimal] = Field(None, description="Transaction gas fee")
    confirmation_count: int = Field(default=0, description="Network confirmations")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = Field(None)
    failed_at: Optional[datetime] = Field(None)
    error_message: Optional[str] = Field(None)

class SmartContractRequest(BaseModel):
    contract_type: ContractType = Field(..., description="Type of smart contract")
    network: BlockchainNetwork = Field(..., description="Target blockchain network")
    parameters: Dict[str, Any] = Field(..., description="Contract parameters")
    parties: List[str] = Field(..., description="Contract parties (addresses)")
    expiry_date: Optional[datetime] = Field(None, description="Contract expiry")

class SmartContract(BaseModel):
    contract_id: str = Field(..., description="Unique contract identifier")
    contract_address: str = Field(..., description="Deployed contract address")
    contract_type: ContractType = Field(..., description="Contract type")
    network: BlockchainNetwork = Field(..., description="Blockchain network")
    abi: Dict[str, Any] = Field(..., description="Contract ABI")
    bytecode: str = Field(..., description="Contract bytecode")
    deployment_hash: str = Field(..., description="Deployment transaction hash")
    parties: List[str] = Field(..., description="Contract parties")
    parameters: Dict[str, Any] = Field(..., description="Contract parameters")
    status: str = Field(default="active", description="Contract status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deployed_at: datetime = Field(default_factory=datetime.utcnow)

class TokenizedAsset(BaseModel):
    token_id: str = Field(..., description="Unique token identifier")
    asset_id: str = Field(..., description="Original asset identifier")
    contract_address: str = Field(..., description="Token contract address")
    network: BlockchainNetwork = Field(..., description="Blockchain network")
    total_supply: Decimal = Field(..., description="Total token supply")
    decimal_places: int = Field(default=18, description="Token decimal places")
    symbol: str = Field(..., description="Token symbol")
    name: str = Field(..., description="Token name")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BlockchainTransaction(BaseModel):
    tx_id: str = Field(..., description="Internal transaction ID")
    transaction_hash: str = Field(..., description="Blockchain transaction hash")
    network: BlockchainNetwork = Field(..., description="Blockchain network")
    from_address: str = Field(..., description="Sender address")
    to_address: str = Field(..., description="Recipient address")
    amount: Optional[Decimal] = Field(None, description="Transaction amount")
    gas_used: Optional[int] = Field(None, description="Gas used")
    gas_price: Optional[Decimal] = Field(None, description="Gas price")
    block_number: Optional[int] = Field(None, description="Block number")
    confirmation_count: int = Field(default=0)
    status: str = Field(default="pending")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = Field(None)

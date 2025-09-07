import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Any
from datetime import datetime, timedelta

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from core.rule_engine import RuleEngine
from core.transaction_screening import TransactionScreening
from core.regulatory_reporting import RegulatoryReporting
from core.audit_trail import AuditTrail
from database.compliance_db import ComplianceDB
from config import Settings
from models import *

logger = structlog.get_logger()

class ComplianceService:
    def __init__(self):
        self.settings = Settings()
        self.rule_engine = RuleEngine(self.settings)
        self.screening = TransactionScreening(self.settings)
        self.reporting = RegulatoryReporting(self.settings)
        self.audit = AuditTrail(self.settings)
        self.db = ComplianceDB(self.settings)
        self.running = False

    async def start(self):
        """Start compliance service"""
        logger.info("Starting Compliance Service")
        
        try:
            await self.db.initialize()
            await self.rule_engine.initialize()
            await self.screening.initialize()
            await self.reporting.initialize()
            
            # Start background monitoring
            asyncio.create_task(self.compliance_monitoring_loop())
            asyncio.create_task(self.reporting_loop())
            
            self.running = True
            logger.info("Compliance Service started successfully")
            
        except Exception as e:
            logger.error("Failed to start Compliance Service", error=str(e))
            raise

    async def stop(self):
        """Stop compliance service"""
        logger.info("Stopping Compliance Service")
        self.running = False
        await self.db.close()

    async def compliance_monitoring_loop(self):
        """Continuous compliance monitoring"""
        while self.running:
            try:
                # Screen recent transactions
                await self.screen_transactions()
                
                # Check rule violations
                await self.check_rule_violations()
                
                # Monitor position limits
                await self.monitor_position_limits()
                
                await asyncio.sleep(60)  # Every minute
                
            except Exception as e:
                logger.error("Compliance monitoring error", error=str(e))
                await asyncio.sleep(30)

    async def reporting_loop(self):
        """Periodic regulatory reporting"""
        while self.running:
            try:
                await self.generate_scheduled_reports()
                await asyncio.sleep(3600)  # Every hour
                
            except Exception as e:
                logger.error("Reporting loop error", error=str(e))
                await asyncio.sleep(600)

    async def screen_transactions(self):
        """Screen recent transactions for violations"""
        try:
            recent_trades = await self.db.get_recent_trades()
            
            for trade in recent_trades:
                violations = await self.screening.screen_transaction(trade)
                
                if violations:
                    await self.handle_violations(trade, violations)
                    
        except Exception as e:
            logger.error("Transaction screening failed", error=str(e))

compliance_service = ComplianceService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await compliance_service.start()
    yield
    await compliance_service.stop()

app = FastAPI(
    title="VedhaVriddhi Compliance Service",
    description="Regulatory compliance and monitoring",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "compliance-service",
        "version": "2.0.0",
        "running": compliance_service.running
    }

@app.get("/compliance/status")
async def get_compliance_status():
    """Get overall compliance status"""
    try:
        violations = await compliance_service.db.get_active_violations()
        pending_reports = await compliance_service.db.get_pending_reports()
        
        return {
            "status": "compliant" if not violations else "violations_detected",
            "active_violations": len(violations),
            "pending_reports": len(pending_reports),
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting compliance status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get compliance status")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        log_config=None,
        access_log=False,
        reload=False
    )

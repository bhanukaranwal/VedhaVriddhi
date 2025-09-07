from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class RuleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class ViolationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"

class ViolationStatus(str, Enum):
    ACTIVE = "active"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"

class ComplianceRule(BaseModel):
    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    rule_type: str = Field(..., description="Type of compliance rule")
    regulation_source: str = Field(..., description="SEBI, RBI, FEMA, Internal")
    status: RuleStatus = RuleStatus.ACTIVE
    severity: ViolationSeverity = ViolationSeverity.WARNING
    parameters: Dict[str, Any] = Field(default_factory=dict)
    condition_logic: str = Field(..., description="Rule evaluation logic")
    action_required: str = Field(..., description="Action when rule is violated")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

class ComplianceViolation(BaseModel):
    violation_id: str = Field(..., description="Unique violation identifier")
    rule_id: str = Field(..., description="ID of violated rule")
    rule_name: str = Field(..., description="Name of violated rule")
    portfolio_id: Optional[str] = None
    transaction_id: Optional[str] = None
    user_id: Optional[str] = None
    violation_type: str = Field(..., description="Type of violation")
    severity: ViolationSeverity
    status: ViolationStatus = ViolationStatus.ACTIVE
    description: str = Field(..., description="Violation description")
    details: Dict[str, Any] = Field(default_factory=dict)
    current_value: Optional[float] = None
    limit_value: Optional[float] = None
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None

class ComplianceReport(BaseModel):
    report_id: str = Field(..., description="Unique report identifier")
    report_type: str = Field(..., description="Type of regulatory report")
    report_name: str = Field(..., description="Report name")
    regulation_source: str = Field(..., description="Regulatory body")
    portfolio_id: Optional[str] = None
    period_start: datetime = Field(..., description="Report period start")
    period_end: datetime = Field(..., description="Report period end")
    status: str = Field(default="draft", description="Report status")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str = Field(..., description="User who generated report")
    submitted_at: Optional[datetime] = None
    submitted_by: Optional[str] = None
    due_date: datetime = Field(..., description="Regulatory filing due date")
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    data: Dict[str, Any] = Field(default_factory=dict)

class AuditTrail(BaseModel):
    audit_id: str = Field(..., description="Unique audit identifier")
    user_id: str = Field(..., description="User who performed action")
    user_name: str = Field(..., description="User name")
    action: str = Field(..., description="Action performed")
    resource: str = Field(..., description="Resource affected")
    resource_id: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: str = Field(..., description="IP address")
    user_agent: str = Field(..., description="User agent string")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool = Field(default=True)
    error_message: Optional[str] = None

class ComplianceAlert(BaseModel):
    alert_id: str = Field(..., description="Unique alert identifier")
    alert_type: str = Field(..., description="Type of alert")
    severity: ViolationSeverity
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    details: Dict[str, Any] = Field(default_factory=dict)
    portfolio_id: Optional[str] = None
    user_id: Optional[str] = None
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = Field(default=False)
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None

class ComplianceStatus(BaseModel):
    overall_status: str = Field(..., description="Overall compliance status")
    active_violations: int = Field(default=0)
    critical_violations: int = Field(default=0)
    pending_reports: int = Field(default=0)
    overdue_reports: int = Field(default=0)
    last_audit_date: Optional[datetime] = None
    next_audit_due: Optional[datetime] = None
    compliance_score: float = Field(default=100.0, ge=0, le=100)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

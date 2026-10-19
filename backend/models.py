from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class OrderDecisionCreate(BaseModel):
    recommendation_id: int
    decision: str = Field(..., pattern="^(approved|modified|rejected)$")
    modified_qty: Optional[int] = None
    modified_supplier_id: Optional[str] = None
    decision_reason: Optional[str] = None


class OrderCommentUpdate(BaseModel):
    comments: Optional[str] = None


class SubstitutionSelectCreate(BaseModel):
    substitution_id: int
    shortage_item_id: str
    selected_alternative_id: str
    clinical_notes: Optional[str] = None


class SubstitutionSimulateRequest(BaseModel):
    substitution_id: int = 0
    shortage_item_id: str = ""
    alternative_item_id: str = ""
    shortage_item_description: Optional[str] = None
    alternative_item_description: Optional[str] = None
    branch_id: Optional[str] = None
    facility_ids: Optional[list[str]] = None
    prompt: Optional[str] = None


class SubstitutionSimulateDecision(BaseModel):
    decision: str = Field(..., pattern="^(approved|rejected|modified)$")
    facility_ids: Optional[list[str]] = None


class RecallActionCreate(BaseModel):
    recall_id: int
    action_type: str = Field(..., pattern="^(quarantined|removed|traced_patients|acknowledged|destroyed|vendor_returned|under_investigation)$")
    notes: Optional[str] = None


class TransferConfirmCreate(BaseModel):
    transfer_id: int
    decision: str = Field(..., pattern="^(confirmed|approved|rejected|cancelled|modified)$")
    actual_qty: Optional[int] = None
    notes: Optional[str] = None


class AgentQueryRequest(BaseModel):
    prompt: str
    item_id: Optional[str] = None
    context: Optional[dict[str, Any]] = None


class FeatureBranchCreate(BaseModel):
    branch_id: str = Field(..., min_length=3, max_length=63, pattern="^[a-z0-9-]+$")
    parent: str = "production"
    ttl_seconds: Optional[int] = 86400  # Default 24h


class BranchRoleAssignment(BaseModel):
    branch_id: str
    identity: str
    role_type: str = Field(default="USER", pattern="^(USER|GROUP|SERVICE_PRINCIPAL)$")
    permission: str = "CAN_CONNECT_AND_CREATE"


class MigrationRunRequest(BaseModel):
    branch_id: str
    sql_content: str
    migration_name: str

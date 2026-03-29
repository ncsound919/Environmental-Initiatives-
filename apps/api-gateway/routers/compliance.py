"""
Level 5 – Compliance & Regulatory Audit Logging
Provides tamper-evident audit logs for all 13 ECOS projects.
Supports: ISO 14001, EPA reporting, carbon-credit verification.
"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import json
import hashlib

router = APIRouter(prefix="/api/compliance", tags=["Compliance"])

# ── In-memory audit chain (replace with TimescaleDB in prod) ──────────────
_audit_chain: List[dict] = []


def _compute_hash(entry: dict, prev_hash: str) -> str:
    payload = json.dumps(entry, sort_keys=True, default=str) + prev_hash
    return hashlib.sha256(payload.encode()).hexdigest()


# ── Schemas ───────────────────────────────────────────────────────────────
class AuditEvent(BaseModel):
    project_id: str          # e.g. "P01" .. "P13"
    tenant_id: str           # multi-tenant identifier
    actor: str               # user or service account
    action: str              # CREATE | UPDATE | DELETE | READ | EXPORT
    resource: str            # what was acted on
    payload: Optional[dict] = None
    tags: List[str] = []


class AuditRecord(AuditEvent):
    id: str
    timestamp: str
    hash: str
    prev_hash: str


class ComplianceReport(BaseModel):
    tenant_id: str
    project_id: Optional[str] = None
    from_ts: Optional[str] = None
    to_ts: Optional[str] = None
    standard: str = "ISO-14001"   # ISO-14001 | EPA | CARBON-VCS | GDPR


# ── Endpoints ─────────────────────────────────────────────────────────────
@router.post("/log", response_model=AuditRecord, summary="Append tamper-evident audit event")
def log_event(event: AuditEvent):
    prev_hash = _audit_chain[-1]["hash"] if _audit_chain else "genesis"
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **event.model_dump(),
        "prev_hash": prev_hash,
    }
    entry["hash"] = _compute_hash(entry, prev_hash)
    _audit_chain.append(entry)
    return entry


@router.get("/logs", response_model=List[AuditRecord], summary="Query audit logs")
def get_logs(
    tenant_id: str = Query(...),
    project_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
):
    results = [e for e in _audit_chain if e["tenant_id"] == tenant_id]
    if project_id:
        results = [e for e in results if e["project_id"] == project_id]
    if action:
        results = [e for e in results if e["action"] == action]
    return results[-limit:]


@router.get("/verify", summary="Verify audit chain integrity")
def verify_chain():
    """Walk the chain and confirm every hash matches."""
    if not _audit_chain:
        return {"status": "ok", "entries": 0, "message": "Chain is empty"}
    prev_hash = "genesis"
    for i, entry in enumerate(_audit_chain):
        expected = _compute_hash({k: v for k, v in entry.items() if k != "hash"}, prev_hash)
        if entry["hash"] != expected:
            return {"status": "CORRUPT", "first_bad_index": i, "entry_id": entry["id"]}
        prev_hash = entry["hash"]
    return {"status": "ok", "entries": len(_audit_chain), "tip_hash": _audit_chain[-1]["hash"]}


@router.post("/report", summary="Generate compliance report for a standard")
def generate_report(req: ComplianceReport):
    events = [e for e in _audit_chain if e["tenant_id"] == req.tenant_id]
    if req.project_id:
        events = [e for e in events if e["project_id"] == req.project_id]
    summary = {
        "standard": req.standard,
        "tenant_id": req.tenant_id,
        "project_id": req.project_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_events": len(events),
        "breakdown": {},
    }
    for e in events:
        summary["breakdown"][e["action"]] = summary["breakdown"].get(e["action"], 0) + 1
    return summary


@router.get("/standards", summary="List supported regulatory standards")
def list_standards():
    return {
        "standards": [
            {"id": "ISO-14001", "name": "ISO 14001 Environmental Management", "regions": ["global"]},
            {"id": "EPA", "name": "US EPA Reporting", "regions": ["US"]},
            {"id": "CARBON-VCS", "name": "Verra VCS Carbon Credit Verification", "regions": ["global"]},
            {"id": "GDPR", "name": "EU GDPR Data Processing Records", "regions": ["EU"]},
            {"id": "SEC-ESG", "name": "SEC ESG Disclosure Requirements", "regions": ["US"]},
        ]
    }

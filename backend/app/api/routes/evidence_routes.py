"""Evidence graph inspection API routes."""

from fastapi import APIRouter, HTTPException
from app.api.routes.addresses import VERIFICATION_HISTORY_CACHE

router = APIRouter(prefix="/evidence", tags=["Evidence Graph"])


@router.get("/{verification_id}")
async def get_evidence_graph_by_id(verification_id: str):
    """Retrieve the directed evidence graph and relationship verification tree for a given verification ID."""
    if verification_id not in VERIFICATION_HISTORY_CACHE:
        raise HTTPException(status_code=404, detail=f"Verification result '{verification_id}' not found.")

    record = VERIFICATION_HISTORY_CACHE[verification_id]
    if "evidence_graph" in record and record["evidence_graph"]:
        return record["evidence_graph"]

    raise HTTPException(status_code=404, detail=f"Evidence graph not available for verification ID '{verification_id}'.")

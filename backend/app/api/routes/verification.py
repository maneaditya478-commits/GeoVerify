"""Core verification API route."""

from fastapi import APIRouter, HTTPException, Depends
from app.schemas.address import VerificationRequest
from app.schemas.verification import VerificationResponse
from app.verification.engine import verification_engine
from app.api.routes.addresses import VERIFICATION_HISTORY_CACHE

router = APIRouter(tags=["Verification"])


@router.post("/verify", response_model=VerificationResponse)
async def verify_address(request: VerificationRequest):
    """Execute complete multi-signal geographic consistency verification on an Indian address."""
    if not request.address and not request.structured:
        raise HTTPException(status_code=400, detail="Either 'address' free-form string or 'structured' object must be provided.")

    result = await verification_engine.verify(request)
    
    # Store in history cache
    VERIFICATION_HISTORY_CACHE[result.verification_id] = result.model_dump()
    
    return result

"""Core verification API route with caching and batch processing (Phase 8.2)."""

import asyncio
from typing import List, Dict, Any, Optional, Union
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.schemas.address import VerificationRequest
from app.schemas.verification import VerificationResponse
from app.verification.engine import verification_engine
from app.api.routes.addresses import VERIFICATION_HISTORY_CACHE
from app.core.cache import verification_cache, CryptographicCacheKeyGenerator
from app.config import settings

router = APIRouter(tags=["Verification"])


class BatchVerificationRequest(BaseModel):
    items: List[VerificationRequest] = Field(..., max_length=settings.BATCH_MAX_SIZE, description="List of verification requests")


class BatchItemResult(BaseModel):
    index: int = Field(..., description="0-indexed position corresponding to input batch")
    status: str = Field(..., description="Item status: SUCCESS, ERROR, PARTIAL")
    success: bool = True
    verification_id: Optional[str] = None
    verification_result: Optional[VerificationResponse] = None
    error_message: Optional[str] = None


class BatchVerificationResponse(BaseModel):
    total_items: int
    successful_items: int
    failed_items: int
    total_requested: Optional[int] = None
    successful_count: Optional[int] = None
    failed_count: Optional[int] = None
    results: List[BatchItemResult]


@router.post("/verify", response_model=VerificationResponse)
async def verify_address(request: VerificationRequest) -> VerificationResponse:
    """Execute complete multi-signal geographic consistency verification on an Indian address."""
    if not request.address and not request.structured:
        raise HTTPException(
            status_code=400,
            detail="Either 'address' free-form string or 'structured' object must be provided.",
        )

    # 1. Check L2 Verification Cache if enabled
    cache_key = None
    if settings.ENABLE_RESPONSE_CACHING:
        struct = request.structured
        coords = None
        if struct and struct.coordinates:
            coords = (struct.coordinates.latitude, struct.coordinates.longitude)
        cache_key = CryptographicCacheKeyGenerator.generate_key(
            query=request.address or "",
            state=struct.state if struct else None,
            district=struct.district if struct else None,
            subdistrict=struct.subdistrict if struct else None,
            pincode=struct.pincode if struct else None,
            coordinates=coords,
        )
        cached_result = verification_cache.get(cache_key)
        if cached_result:
            return cached_result

    # 2. Execute verification engine
    result = await verification_engine.verify(request)

    # 3. Store in caches
    if cache_key and settings.ENABLE_RESPONSE_CACHING:
        verification_cache.set(cache_key, result)

    VERIFICATION_HISTORY_CACHE[result.verification_id] = result.model_dump()

    return result


@router.post("/verify/batch", response_model=BatchVerificationResponse)
async def verify_batch_addresses(batch: Union[BatchVerificationRequest, List[VerificationRequest]]) -> BatchVerificationResponse:
    """Batch address verification with bounded size and per-item partial failure isolation."""
    items = batch.items if isinstance(batch, BatchVerificationRequest) else batch
    if len(items) > settings.BATCH_MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch size {len(items)} exceeds maximum allowed of {settings.BATCH_MAX_SIZE}.",
        )

    async def _verify_single(index: int, item: VerificationRequest) -> BatchItemResult:
        try:
            if not item.address and not item.structured:
                return BatchItemResult(
                    index=index,
                    status="ERROR",
                    success=False,
                    error_message="Empty address and structured object.",
                )
            res = await verify_address(item)
            return BatchItemResult(
                index=index,
                status="SUCCESS",
                success=True,
                verification_id=res.verification_id,
                verification_result=res,
            )
        except Exception as e:
            return BatchItemResult(
                index=index,
                status="ERROR",
                success=False,
                error_message=str(e),
            )

    tasks = [_verify_single(idx, item) for idx, item in enumerate(items)]
    results = await asyncio.gather(*tasks)

    success_count = sum(1 for r in results if r.status == "SUCCESS")
    failed_count = len(results) - success_count

    return BatchVerificationResponse(
        total_items=len(results),
        successful_items=success_count,
        failed_items=failed_count,
        total_requested=len(results),
        successful_count=success_count,
        failed_count=failed_count,
        results=sorted(results, key=lambda x: x.index),
    )

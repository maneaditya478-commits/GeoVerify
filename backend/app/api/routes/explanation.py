"""API route for detailed geographic verification explanations, research mode, and reasoning paths."""

from fastapi import APIRouter, HTTPException, status
from app.schemas.address import VerificationRequest
from app.schemas.verification import VerificationResponse, VerificationExplanationResponse
from app.verification.engine import verification_engine
from app.services.multilingual_alignment import multilingual_alignment_engine
from app.graph.path_explainer import GraphPathExplainer

router = APIRouter(tags=["Explanation"])


@router.post("/verify/explain", response_model=VerificationExplanationResponse)
async def explain_verification(request: VerificationRequest) -> VerificationExplanationResponse:
    """Provides rich, step-by-step explainability, graph traversal paths, temporal evidence,

    landmark associations, and calibrated probabilistic confidence for an address verification.
    """
    if not request.address and not request.structured:
        raise HTTPException(
            status_code=400,
            detail="Either 'address' free-form string or 'structured' object must be provided.",
        )

    # Enable research flags for deep explanation
    request.research_mode = True
    request.include_graph_path = True

    # 1. Run core verification engine
    verif_res: VerificationResponse = await verification_engine.verify(request)

    # 2. Multilingual breakdown & script analysis
    raw_text = request.address or ""
    multi_align = multilingual_alignment_engine.align_and_expand(raw_text)
    multi_breakdown = {
        "primary_script": multi_align.primary_script,
        "is_mixed_script": multi_align.is_mixed_script,
        "detected_scripts": multi_align.detected_scripts,
        "expanded_address": multi_align.expanded_address,
        "expanded_tokens": [t.model_dump() for t in multi_align.expanded_tokens],
        "extracted_hints": {
            "district": multi_align.extracted_district_hint,
            "taluka": multi_align.extracted_taluka_hint,
            "locality": multi_align.extracted_locality_hint
        }
    }

    # 3. Construct narrative
    narrative = []
    narrative.append(f"Decision Verdict: {verif_res.status.value} (Consistency Score: {verif_res.score}/100)")
    narrative.append(f"Verification Summary: {verif_res.summary}")

    # Confidence profile breakdown
    if verif_res.confidence_profile:
        cp = verif_res.confidence_profile
        narrative.append(
            f"Calibrated Confidence Profile: Composite={cp.composite_confidence:.2%}, "
            f"Candidate Retrieval={cp.candidate_confidence:.2%}, "
            f"Geographic Consistency={cp.geographic_consistency_confidence:.2%}, "
            f"Ambiguity Uncertainty={cp.ambiguity_confidence:.2%}, "
            f"Completeness={cp.evidence_completeness:.2%}"
        )

    # Temporal breakdown
    if verif_res.temporal_evidence:
        narrative.append("Temporal Geographic Reasoning:")
        for te in verif_res.temporal_evidence:
            narrative.append(f"  - [{te.status.value}] {te.explanation}")

    # Landmark breakdown
    if verif_res.landmark_evidence:
        narrative.append("Landmark-Aware Spatial Associations:")
        for lm in verif_res.landmark_evidence:
            narrative.append(f"  - [{lm.distance_bucket.value}] {lm.explanation}")

    # Graph explanation
    if verif_res.subgraph_evidence:
        graph_narrative = GraphPathExplainer.generate_subgraph_explanation(verif_res.subgraph_evidence)
        narrative.extend(graph_narrative)

    return VerificationExplanationResponse(
        verification_id=verif_res.verification_id,
        timestamp=verif_res.timestamp,
        status=verif_res.status,
        score=verif_res.score,
        confidence_profile=verif_res.confidence_profile,
        temporal_evidence=verif_res.temporal_evidence,
        landmark_evidence=verif_res.landmark_evidence,
        subgraph_evidence=verif_res.subgraph_evidence,
        multilingual_breakdown=multi_breakdown,
        explanation_narrative=narrative,
        verification_response=verif_res
    )

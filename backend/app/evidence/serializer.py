"""Evidence Graph serialization utilities."""

from typing import Dict, Any
from app.evidence.graph import EvidenceGraph


class EvidenceGraphSerializer:
    """Serializes EvidenceGraph to JSON, Cytoscape, and D3 formats for API responses and visualizers."""

    @staticmethod
    def to_dict(graph: EvidenceGraph) -> Dict[str, Any]:
        return {
            "nodes": [n.model_dump() for n in graph.nodes],
            "relationships": [e.model_dump() for e in graph.edges],
            "summary": graph.summary,
            "conflicts_count": graph.conflicts_count,
            "warnings_count": graph.warnings_count
        }

    @staticmethod
    def to_cytoscape(graph: EvidenceGraph) -> Dict[str, Any]:
        elements = []
        for n in graph.nodes:
            elements.append({
                "group": "nodes",
                "data": {
                    "id": n.id,
                    "label": n.label,
                    "type": n.node_type.value,
                    "level": n.level,
                    "status": n.status.value,
                    **n.properties
                }
            })
        for e in graph.edges:
            elements.append({
                "group": "edges",
                "data": {
                    "id": e.id,
                    "source": e.source,
                    "target": e.target,
                    "label": e.label,
                    "relationship": e.relationship.value,
                    "severity": e.severity.value,
                    "passed": e.passed,
                    "evidence": e.evidence_text
                }
            })
        return {"elements": elements}


evidence_serializer = EvidenceGraphSerializer()

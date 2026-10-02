"""Graph Path Explainer generating human-readable and structured reasoning trees."""

from typing import List, Optional
from app.graph.models import EvidencePath, SubgraphEvidence


class GraphPathExplainer:
    """Translates graph paths into clear, deterministic reasoning narratives."""

    @classmethod
    def explain_path(cls, path: EvidencePath) -> str:
        if not path.steps:
            return path.narrative or "Single entity verified."

        parts = []
        for step in path.steps:
            parts.append(
                f"'{step.from_node.name}' ({step.from_node.node_type.value}) is [{step.edge_type.value.lower().replace('_', ' ')}] "
                f"'{step.to_node.name}' ({step.to_node.node_type.value})"
            )
        return " -> ".join(parts)

    @classmethod
    def generate_subgraph_explanation(cls, subgraph: SubgraphEvidence) -> List[str]:
        lines: List[str] = []
        if not subgraph.nodes:
            lines.append("No geographic graph entities resolved.")
            return lines

        lines.append(f"Resolved {len(subgraph.nodes)} geographic entities in verification graph:")
        for node in subgraph.nodes:
            loc_str = f" in {node.district}, {node.state}" if node.district and node.state else ""
            lines.append(f"- [{node.node_type.value}] {node.name}{loc_str}")

        if subgraph.paths:
            lines.append("Verified Hierarchical Relationship Paths:")
            for p in subgraph.paths:
                lines.append(f"  * {cls.explain_path(p)}")
        elif not subgraph.is_consistent:
            lines.append("WARNING: Disconnected or conflicting hierarchy detected across resolved entities.")

        return lines

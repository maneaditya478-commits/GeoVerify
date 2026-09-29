"""Automated Chart and Visualization Generator for GeoVerify India Benchmark."""

from pathlib import Path
from typing import Dict, Any, List
import matplotlib
matplotlib.use("Agg")  # Headless non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Visualizer:
    """Generates publication-quality diagnostic charts from benchmark evaluation metrics."""

    @classmethod
    def generate_all_charts(cls, metrics: Dict[str, Any], results: List[Any], output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.style.use("ggplot")

        cls._chart_hierarchy_accuracy(metrics, output_dir / "hierarchy_accuracy.png")
        cls._chart_category_performance(metrics, output_dir / "category_performance.png")
        cls._chart_script_language(metrics, output_dir / "script_language_accuracy.png")
        cls._chart_completeness_vs_accuracy(results, output_dir / "completeness_vs_accuracy.png")
        cls._chart_confusion_matrix(metrics, output_dir / "confusion_matrix.png")
        cls._chart_latency_distribution(metrics, output_dir / "latency_distribution.png")
        cls._chart_error_distribution(results, output_dir / "error_distribution.png")
        print(f"[OK] Generated 7 benchmark visualization charts in {output_dir}")

    @staticmethod
    def _chart_hierarchy_accuracy(metrics: Dict[str, Any], save_path: Path):
        er = metrics.get("entity_resolution", {})
        labels = ["State", "District", "Sub-District", "Locality", "PIN Code", "Exact Hierarchy"]
        scores = [
            er.get("state_accuracy", 0) * 100,
            er.get("district_accuracy", 0) * 100,
            er.get("subdistrict_accuracy", 0) * 100,
            er.get("locality_accuracy", 0) * 100,
            er.get("pincode_accuracy", 0) * 100,
            er.get("exact_hierarchy_accuracy", 0) * 100
        ]

        fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
        colors = ["#10b981", "#14b8a6", "#06b6d4", "#3b82f6", "#6366f1", "#8b5cf6"]
        bars = ax.bar(labels, scores, color=colors, edgecolor="#1e293b", width=0.55)

        ax.set_title("Administrative Hierarchy Resolution Accuracy (%)", fontsize=13, fontweight="bold", pad=12)
        ax.set_ylabel("Accuracy (%)", fontsize=11)
        ax.set_ylim(0, 105)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5, f"{score:.1f}%",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

    @staticmethod
    def _chart_category_performance(metrics: Dict[str, Any], save_path: Path):
        cat_data = metrics.get("category_metrics", {})
        if not cat_data:
            return

        categories = list(cat_data.keys())
        accs = [cat_data[c].get("status_acc", 0) * 100 for c in categories]

        # Sort by accuracy
        sorted_pairs = sorted(zip(categories, accs), key=lambda x: x[1])
        categories, accs = zip(*sorted_pairs)

        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        colors = ["#ef4444" if a < 70 else "#f59e0b" if a < 85 else "#10b981" for a in accs]
        bars = ax.barh(categories, accs, color=colors, edgecolor="#1e293b", height=0.6)

        ax.set_title("Verification Status Accuracy by Address Category (%)", fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Accuracy (%)", fontsize=11)
        ax.set_xlim(0, 105)
        ax.grid(axis="x", linestyle="--", alpha=0.5)

        for bar, acc in zip(bars, accs):
            ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2, f"{acc:.1f}%",
                    ha="left", va="center", fontsize=9, fontweight="bold")

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

    @staticmethod
    def _chart_script_language(metrics: Dict[str, Any], save_path: Path):
        sc_data = metrics.get("script_metrics", {})
        if not sc_data:
            return

        scripts = list(sc_data.keys())
        hierarchy_accs = [sc_data[s].get("exact_hierarchy_acc", 0) * 100 for s in scripts]
        status_accs = [sc_data[s].get("status_acc", 0) * 100 for s in scripts]

        x = np.arange(len(scripts))
        width = 0.35

        fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
        b1 = ax.bar(x - width/2, hierarchy_accs, width, label="Exact Hierarchy Acc", color="#3b82f6", edgecolor="#1e293b")
        b2 = ax.bar(x + width/2, status_accs, width, label="Status Classification Acc", color="#10b981", edgecolor="#1e293b")

        ax.set_title("Accuracy by Input Script (Latin vs Devanagari vs Mixed)", fontsize=13, fontweight="bold", pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels([s.title() for s in scripts], fontsize=11, fontweight="bold")
        ax.set_ylabel("Accuracy (%)", fontsize=11)
        ax.set_ylim(0, 105)
        ax.legend(loc="lower right")
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

    @staticmethod
    def _chart_completeness_vs_accuracy(results: List[Any], save_path: Path):
        if not results:
            return

        completeness_levels = ["COMPLETE", "ADEQUATE", "PARTIAL", "MINIMAL"]
        accs = []
        counts = []

        for lvl in completeness_levels:
            sub = [r for r in results if (getattr(r, "completeness_level", None) or "ADEQUATE") == lvl or (hasattr(r, "metadata") and getattr(r.metadata, "completeness", None) == lvl)]
            if not sub:
                # Fallback group by score range
                if lvl == "COMPLETE":
                    sub = [r for r in results if r.completeness_score >= 85]
                elif lvl == "ADEQUATE":
                    sub = [r for r in results if 70 <= r.completeness_score < 85]
                elif lvl == "PARTIAL":
                    sub = [r for r in results if 40 <= r.completeness_score < 70]
                else:
                    sub = [r for r in results if r.completeness_score < 40]

            acc = (sum(1 for r in sub if r.status_matched) / len(sub) * 100) if sub else 0.0
            accs.append(acc)
            counts.append(len(sub))

        fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
        colors = ["#10b981", "#14b8a6", "#f59e0b", "#ef4444"]
        bars = ax.bar(completeness_levels, accs, color=colors, edgecolor="#1e293b", width=0.5)

        ax.set_title("Status Accuracy vs Address Completeness Level", fontsize=13, fontweight="bold", pad=12)
        ax.set_ylabel("Status Accuracy (%)", fontsize=11)
        ax.set_ylim(0, 105)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        for bar, acc, cnt in zip(bars, accs, counts):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5, f"{acc:.1f}%\n(n={cnt})",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

    @staticmethod
    def _chart_confusion_matrix(metrics: Dict[str, Any], save_path: Path):
        cm = metrics.get("status_classification", {}).get("confusion_matrix", {})
        if not cm:
            return

        statuses = list(cm.keys())
        matrix = np.array([[cm[exp][pred] for pred in statuses] for exp in statuses])

        fig, ax = plt.subplots(figsize=(8, 7), dpi=300)
        cax = ax.matshow(matrix, cmap="Blues", alpha=0.85)

        for i in range(len(statuses)):
            for j in range(len(statuses)):
                val = matrix[i, j]
                ax.text(j, i, str(val), va="center", ha="center", fontsize=11, fontweight="bold",
                        color="white" if val > matrix.max() / 2 else "black")

        fig.colorbar(cax)
        ax.set_xticks(range(len(statuses)))
        ax.set_yticks(range(len(statuses)))
        ax.set_xticklabels(statuses, rotation=45, ha="left", fontsize=9, fontweight="bold")
        ax.set_yticklabels(statuses, fontsize=9, fontweight="bold")
        ax.set_xlabel("Predicted Status", fontsize=11, fontweight="bold", labelpad=10)
        ax.set_ylabel("Expected Status", fontsize=11, fontweight="bold", labelpad=10)
        ax.set_title("Verification Status Confusion Matrix", fontsize=13, fontweight="bold", pad=20)

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

    @staticmethod
    def _chart_latency_distribution(metrics: Dict[str, Any], save_path: Path):
        comp_perf = metrics.get("component_performance", {}).get("components", {})
        if not comp_perf:
            return

        components = [
            "Normalizer", "Transliteration", "Parser", "Entity Resolution", "Verification Engine"
        ]
        keys = [
            "address_normalizer", "indic_transliteration", "address_parser", "entity_resolution", "verification_engine_pipeline"
        ]
        p50 = [comp_perf.get(k, {}).get("p50_ms", 0) for k in keys]
        p95 = [comp_perf.get(k, {}).get("p95_ms", 0) for k in keys]
        p99 = [comp_perf.get(k, {}).get("p99_ms", 0) for k in keys]

        x = np.arange(len(components))
        width = 0.25

        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        ax.bar(x - width, p50, width, label="P50 (Median)", color="#10b981", edgecolor="#1e293b")
        ax.bar(x, p95, width, label="P95", color="#3b82f6", edgecolor="#1e293b")
        ax.bar(x + width, p99, width, label="P99", color="#8b5cf6", edgecolor="#1e293b")

        ax.set_title("Component Latency Benchmarks (P50 / P95 / P99 ms)", fontsize=13, fontweight="bold", pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels(components, fontsize=10, fontweight="bold")
        ax.set_ylabel("Latency (milliseconds)", fontsize=11)
        ax.legend(loc="upper left")
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

    @staticmethod
    def _chart_error_distribution(results: List[Any], save_path: Path):
        if not results:
            return

        err_counts: Dict[str, int] = {}
        for r in results:
            cat = getattr(r, "error_category", None)
            if cat and cat != "NONE":
                err_counts[cat] = err_counts.get(cat, 0) + 1

        if not err_counts:
            err_counts["NONE"] = len(results)

        labels = list(err_counts.keys())
        counts = list(err_counts.values())

        fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
        bars = ax.barh(labels, counts, color="#f43f5e", edgecolor="#1e293b", height=0.55)

        ax.set_title("Error Diagnostic Category Distribution", fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Error Count", fontsize=11)
        ax.grid(axis="x", linestyle="--", alpha=0.5)

        for bar, cnt in zip(bars, counts):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2, str(cnt),
                    ha="left", va="center", fontsize=10, fontweight="bold")

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

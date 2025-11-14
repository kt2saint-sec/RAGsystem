#!/usr/bin/env python3
"""
Reciprocal Rank Fusion (RRF) for Hybrid Search
Combines semantic and keyword search results intelligently
"""

from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReciprocalRankFusion:
    """
    Combine results from multiple retrieval systems using RRF algorithm.

    RRF Formula: score(d) = Σ 1/(k + rank(d))
    Where k is a constant (typically 60) and rank starts from 1.

    Reference: "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods"
    """

    def __init__(self, k: int = 60):
        """
        Args:
            k: Ranking constant (default 60, as per original RRF paper)
               Lower k gives more weight to top-ranked results
        """
        self.k = k

    def fuse(
        self,
        semantic_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        semantic_weight: float = 0.6,
        keyword_weight: float = 0.4
    ) -> List[Dict[str, Any]]:
        """
        Fuse semantic and keyword search results using weighted RRF.

        Args:
            semantic_results: Results from ChromaDB vector search
            keyword_results: Results from BM25 keyword search
            semantic_weight: Weight for semantic results (0-1)
            keyword_weight: Weight for keyword results (0-1)

        Returns:
            Unified ranked results with combined scores
        """
        # Normalize weights
        total_weight = semantic_weight + keyword_weight
        if total_weight > 0:
            semantic_weight /= total_weight
            keyword_weight /= total_weight
        else:
            semantic_weight = 0.5
            keyword_weight = 0.5

        # Build scoring dictionary
        scores = {}
        doc_data = {}

        # Process semantic results (use content hash as key)
        for rank, result in enumerate(semantic_results, start=1):
            content_key = hash(result["content"])
            rrf_score = semantic_weight * (1 / (self.k + rank))

            scores[content_key] = scores.get(content_key, 0) + rrf_score

            if content_key not in doc_data:
                doc_data[content_key] = result.copy()
                doc_data[content_key]["semantic_rank"] = rank
                doc_data[content_key]["semantic_score"] = result.get("similarity_score", result.get("distance", 0))

        # Process keyword results
        for rank, result in enumerate(keyword_results, start=1):
            content_key = hash(result["content"])
            rrf_score = keyword_weight * (1 / (self.k + rank))

            scores[content_key] = scores.get(content_key, 0) + rrf_score

            if content_key not in doc_data:
                doc_data[content_key] = result.copy()
                doc_data[content_key]["keyword_rank"] = rank
                doc_data[content_key]["bm25_score"] = result.get("bm25_score", 0)
            else:
                # Document appeared in both results
                doc_data[content_key]["keyword_rank"] = rank
                doc_data[content_key]["bm25_score"] = result.get("bm25_score", 0)

        # Create final ranked list
        fused_results = []
        for content_key, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            doc = doc_data[content_key]
            doc["rrf_score"] = round(score, 6)
            doc["appeared_in"] = []

            if "semantic_rank" in doc:
                doc["appeared_in"].append("semantic")
            if "keyword_rank" in doc:
                doc["appeared_in"].append("keyword")

            fused_results.append(doc)

        return fused_results


def test_rrf():
    """Test RRF fusion with sample data"""
    logger.info("Testing Reciprocal Rank Fusion")

    # Sample semantic results
    semantic_results = [
        {"content": "React hooks allow functional components to use state", "similarity_score": 0.95, "technology": "React"},
        {"content": "useState is the most common hook", "similarity_score": 0.87, "technology": "React"},
        {"content": "useEffect handles side effects", "similarity_score": 0.82, "technology": "React"},
    ]

    # Sample keyword results (different order)
    keyword_results = [
        {"content": "useState is the most common hook", "bm25_score": 12.5, "technology": "React"},
        {"content": "useEffect handles side effects", "bm25_score": 10.2, "technology": "React"},
        {"content": "Custom hooks reuse stateful logic", "bm25_score": 8.1, "technology": "React"},
    ]

    # Test fusion
    rrf = ReciprocalRankFusion(k=60)
    fused = rrf.fuse(semantic_results, keyword_results, semantic_weight=0.6, keyword_weight=0.4)

    logger.info("\nFused Results (top 5):")
    for i, result in enumerate(fused[:5], 1):
        logger.info(f"\n{i}. RRF Score: {result['rrf_score']:.6f}")
        logger.info(f"   Content: {result['content'][:60]}...")
        logger.info(f"   Appeared in: {', '.join(result['appeared_in'])}")
        if 'semantic_rank' in result:
            logger.info(f"   Semantic rank: {result['semantic_rank']}")
        if 'keyword_rank' in result:
            logger.info(f"   Keyword rank: {result['keyword_rank']}")

    logger.info("\n✓ RRF fusion test complete")


if __name__ == "__main__":
    test_rrf()

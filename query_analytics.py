#!/usr/bin/env python3
"""
Query Analytics for RAG System
Tracks query patterns for autocomplete and analytics
"""

import redis
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryAnalytics:
    """
    Track query patterns for autocomplete and analytics.
    """

    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 3):
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Query analytics initialized: {redis_host}:{redis_port} (db={redis_db})")
        except Exception as e:
            logger.warning(f"Redis unavailable for query analytics: {e}")
            self.redis_client = None

        self.QUERY_FREQ_KEY = "rag:query_frequency"
        self.QUERY_METADATA_KEY = "rag:query_metadata:{}"
        self.AUTOCOMPLETE_PREFIX_KEY = "rag:autocomplete:{}"

    def track_query(self, query: str, technology_filter: Optional[str] = None):
        """
        Track query execution for analytics and autocomplete.

        Stores:
        1. Query frequency (sorted set for ranking)
        2. Query metadata (last seen, technology filter)
        3. Prefix index for autocomplete
        """
        if not self.redis_client:
            return

        try:
            query_lower = query.lower().strip()

            # Increment query frequency
            self.redis_client.zincrby(self.QUERY_FREQ_KEY, 1, query_lower)

            # Store metadata
            metadata = {
                "original_query": query,
                "technology_filter": technology_filter,
                "last_seen": datetime.utcnow().isoformat(),
                "count": int(self.redis_client.zscore(self.QUERY_FREQ_KEY, query_lower) or 1)
            }
            self.redis_client.setex(
                self.QUERY_METADATA_KEY.format(query_lower),
                timedelta(days=30),
                json.dumps(metadata)
            )

            # Build prefix index for autocomplete (2-char to full query)
            words = query_lower.split()
            for word in words:
                for i in range(2, min(len(word) + 1, 10)):  # Limit prefix length
                    prefix = word[:i]
                    prefix_key = self.AUTOCOMPLETE_PREFIX_KEY.format(prefix)
                    self.redis_client.zadd(prefix_key, {query_lower: 1}, nx=True)
                    self.redis_client.expire(prefix_key, timedelta(days=30))

        except Exception as e:
            logger.error(f"Failed to track query: {e}")

    def get_autocomplete_suggestions(
        self,
        partial_query: str,
        limit: int = 5,
        technology_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get autocomplete suggestions based on partial query input.

        Args:
            partial_query: User's current input (e.g., "How to use Rea")
            limit: Max suggestions to return
            technology_filter: Filter by technology if provided

        Returns:
            List of suggestions with metadata
        """
        if not self.redis_client:
            return []

        try:
            partial_lower = partial_query.lower().strip()

            # Strategy 1: Exact prefix match on full query
            matching_queries = self.redis_client.zrevrange(
                self.QUERY_FREQ_KEY,
                0,
                -1,
                withscores=True
            )

            prefix_matches = [
                (query, score) for query, score in matching_queries
                if query.startswith(partial_lower)
            ]

            # Strategy 2: Word-level prefix match
            if len(partial_lower) >= 2:
                last_word = partial_lower.split()[-1] if partial_lower.split() else partial_lower
                if len(last_word) >= 2:
                    prefix_key = self.AUTOCOMPLETE_PREFIX_KEY.format(last_word[:min(len(last_word), 5)])

                    prefix_candidates = self.redis_client.zrevrange(prefix_key, 0, limit * 2)
                    for candidate in prefix_candidates:
                        if candidate not in [q for q, _ in prefix_matches]:
                            score = self.redis_client.zscore(self.QUERY_FREQ_KEY, candidate) or 0
                            prefix_matches.append((candidate, score))

            # Sort by frequency and limit
            prefix_matches.sort(key=lambda x: x[1], reverse=True)
            top_matches = prefix_matches[:limit]

            # Enrich with metadata
            suggestions = []
            for query, frequency in top_matches:
                metadata_key = self.QUERY_METADATA_KEY.format(query)
                metadata_json = self.redis_client.get(metadata_key)

                if metadata_json:
                    metadata = json.loads(metadata_json)

                    # Filter by technology if specified
                    if technology_filter and metadata.get("technology_filter") != technology_filter:
                        continue

                    suggestions.append({
                        "query": metadata["original_query"],
                        "frequency": int(frequency),
                        "technology_filter": metadata.get("technology_filter"),
                        "last_seen": metadata.get("last_seen")
                    })

            return suggestions[:limit]

        except Exception as e:
            logger.error(f"Failed to get autocomplete suggestions: {e}")
            return []

    def get_top_queries(self, limit: int = 20, timeframe: str = "all") -> List[Dict[str, Any]]:
        """
        Get top queries by frequency.

        Args:
            limit: Number of queries to return
            timeframe: 'all', 'day', 'week', 'month' (currently supports 'all')

        Returns:
            List of queries with metadata sorted by frequency
        """
        if not self.redis_client:
            return []

        try:
            top_queries = self.redis_client.zrevrange(
                self.QUERY_FREQ_KEY,
                0,
                limit - 1,
                withscores=True
            )

            results = []
            for query, frequency in top_queries:
                metadata_key = self.QUERY_METADATA_KEY.format(query)
                metadata_json = self.redis_client.get(metadata_key)

                if metadata_json:
                    metadata = json.loads(metadata_json)
                    results.append({
                        "query": metadata["original_query"],
                        "frequency": int(frequency),
                        "technology_filter": metadata.get("technology_filter"),
                        "last_seen": metadata.get("last_seen")
                    })

            return results

        except Exception as e:
            logger.error(f"Failed to get top queries: {e}")
            return []

    def get_similar_queries(self, query: str, limit: int = 5) -> List[str]:
        """
        Find similar queries based on shared words.

        Uses word overlap heuristic (not semantic similarity).
        """
        if not self.redis_client:
            return []

        try:
            query_words = set(query.lower().split())

            all_queries = self.redis_client.zrevrange(self.QUERY_FREQ_KEY, 0, 200)

            similarities = []
            for candidate in all_queries:
                candidate_words = set(candidate.split())
                overlap = len(query_words & candidate_words)

                if overlap > 0 and candidate != query.lower():
                    similarities.append((candidate, overlap))

            # Sort by word overlap
            similarities.sort(key=lambda x: x[1], reverse=True)

            return [q for q, _ in similarities[:limit]]

        except Exception as e:
            logger.error(f"Failed to get similar queries: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get query analytics statistics"""
        if not self.redis_client:
            return {"error": "Redis unavailable"}

        try:
            total_queries = self.redis_client.zcard(self.QUERY_FREQ_KEY)
            top_queries = self.get_top_queries(20)

            return {
                "total_unique_queries": total_queries,
                "top_20_queries": [
                    {"query": q["query"][:50], "hits": q["frequency"]}
                    for q in top_queries[:20]
                ],
                "analytics_enabled": True
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}


def test_query_analytics():
    """Test query analytics functionality"""
    logger.info("Testing Query Analytics")

    analytics = QueryAnalytics()

    # Track some queries
    test_queries = [
        ("How to use React hooks?", "React Docs"),
        ("How to use React hooks?", "React Docs"),  # Duplicate
        ("Python async await", "Python Docs"),
        ("FastAPI CORS configuration", "FastAPI Docs"),
        ("React useState", "React Docs"),
    ]

    logger.info("\nTracking queries...")
    for query, tech in test_queries:
        analytics.track_query(query, tech)
        logger.info(f"  Tracked: {query}")

    # Test autocomplete
    logger.info("\nTesting autocomplete for 'How to':")
    suggestions = analytics.get_autocomplete_suggestions("How to", limit=5)
    for i, suggestion in enumerate(suggestions, 1):
        logger.info(f"  {i}. {suggestion['query']} (freq: {suggestion['frequency']})")

    # Test top queries
    logger.info("\nTop queries:")
    top = analytics.get_top_queries(limit=10)
    for i, query in enumerate(top, 1):
        logger.info(f"  {i}. {query['query']} (freq: {query['frequency']})")

    # Test similar queries
    logger.info("\nSimilar to 'React hooks':")
    similar = analytics.get_similar_queries("React hooks", limit=3)
    for i, query in enumerate(similar, 1):
        logger.info(f"  {i}. {query}")

    logger.info("\n✓ Query analytics test complete")


if __name__ == "__main__":
    test_query_analytics()

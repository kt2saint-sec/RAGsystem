#!/usr/bin/env python3
"""
Cache Warming System for RAG Production
Tracks query frequency and pre-warms cache with popular queries
"""

import redis
import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueryStats:
    """Query statistics for cache warming"""
    query: str
    hit_count: int
    last_accessed: float
    technology_filter: Optional[str] = None


class CacheWarmer:
    """
    Intelligent cache warming for RAG systems

    Features:
    - Query frequency tracking
    - Automatic top query identification
    - Startup and scheduled cache warming
    """

    def __init__(self, redis_host: str = "127.0.0.1", redis_port: int = 6379, redis_db: int = 2):
        try:
            self.redis = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=False,
                socket_timeout=5
            )
            self.redis.ping()
            logger.info(f"Cache warmer initialized: {redis_host}:{redis_port}")
        except Exception as e:
            logger.warning(f"Redis unavailable for cache warming: {e}")
            self.redis = None

    def track_query(self, query: str, technology_filter: Optional[str] = None):
        """Track query frequency for cache warming analysis"""
        if not self.redis:
            return

        try:
            timestamp = time.time()
            key = f"rag:query_freq"

            # Increment hit count
            self.redis.zincrby(key, 1, query)

            # Store metadata
            meta_key = f"rag:query_meta:{query}"
            self.redis.hset(meta_key, mapping={
                "last_accessed": timestamp,
                "technology_filter": technology_filter or "",
            })
            self.redis.expire(meta_key, 86400 * 30)  # 30 day TTL

        except Exception as e:
            logger.error(f"Failed to track query: {e}")

    def get_top_queries(self, n: int = 50) -> List[QueryStats]:
        """Get top N most frequent queries"""
        if not self.redis:
            return []

        try:
            key = "rag:query_freq"
            top_queries = self.redis.zrevrange(key, 0, n - 1, withscores=True)

            stats = []
            for query_bytes, score in top_queries:
                query = query_bytes.decode('utf-8')
                meta_key = f"rag:query_meta:{query}"
                meta = self.redis.hgetall(meta_key)

                if meta:
                    stats.append(QueryStats(
                        query=query,
                        hit_count=int(score),
                        last_accessed=float(meta.get(b'last_accessed', 0)),
                        technology_filter=meta.get(b'technology_filter', b'').decode('utf-8') or None
                    ))

            return stats

        except Exception as e:
            logger.error(f"Failed to get top queries: {e}")
            return []

    def get_stats(self) -> Dict:
        """Get cache warming statistics"""
        if not self.redis:
            return {"error": "Redis unavailable"}

        try:
            total_queries = self.redis.zcard("rag:query_freq")
            top_queries = self.get_top_queries(20)

            return {
                "total_unique_queries": total_queries,
                "top_20_queries": [
                    {"query": q.query[:50], "hits": q.hit_count}
                    for q in top_queries[:20]
                ],
                "cache_warming_enabled": True
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}


# Initialize global cache warmer
cache_warmer = CacheWarmer()

#!/usr/bin/env python3
"""
Error Recovery System for Production RAG
Circuit breakers and retry logic for ChromaDB/Redis failures
"""

import time
import logging
from typing import Optional, Callable
from functools import wraps

import pybreaker
import redis
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import chromadb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResilientRedisClient:
    """Redis client with circuit breaker and retry logic"""

    def __init__(self, host: str = "127.0.0.1", port: int = 6379, db: int = 2):
        self.host = host
        self.port = port
        self.db = db

        # Connection pool
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            socket_connect_timeout=2,
            socket_timeout=5,
            max_connections=50
        )

        self._client = None

        # Circuit breaker
        self.breaker = pybreaker.CircuitBreaker(
            fail_max=5,  # Open after 5 failures
            reset_timeout=60,  # Try recovery after 60s
            name='redis_client'
        )

    @property
    def client(self) -> redis.Redis:
        """Lazy-loaded Redis client"""
        if self._client is None:
            self._client = redis.Redis(connection_pool=self.pool, decode_responses=False)
        return self._client

    @retry(
        retry=retry_if_exception_type((redis.ConnectionError, redis.TimeoutError)),
        wait=wait_exponential(multiplier=2, min=1, max=30),
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _execute_with_retry(self, operation: Callable, *args, **kwargs):
        """Execute Redis operation with retry"""
        try:
            return self.breaker.call(operation, *args, **kwargs)
        except pybreaker.CircuitBreakerError:
            logger.error("Circuit breaker OPEN for Redis")
            raise

    def get(self, key: str) -> Optional[bytes]:
        """Get with error recovery"""
        try:
            return self._execute_with_retry(self.client.get, key)
        except Exception as e:
            logger.error(f"Redis GET failed: {e}")
            return None

    def set(self, key: str, value, ex: Optional[int] = None) -> bool:
        """Set with error recovery"""
        try:
            return self._execute_with_retry(self.client.set, key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis SET failed: {e}")
            return False

    def setex(self, key: str, time: int, value) -> bool:
        """Set with expiration and error recovery"""
        try:
            return self._execute_with_retry(self.client.setex, key, time, value)
        except Exception as e:
            logger.error(f"Redis SETEX failed: {e}")
            return False

    def ping(self) -> bool:
        """Health check"""
        try:
            return self._execute_with_retry(self.client.ping)
        except Exception:
            return False


class ResilientChromaClient:
    """ChromaDB client with circuit breaker and retry logic"""

    def __init__(self, host: str = "localhost", port: int = 8001):
        self.host = host
        self.port = port
        self._client = None

        # Circuit breaker
        self.breaker = pybreaker.CircuitBreaker(
            fail_max=5,
            reset_timeout=60,
            name='chromadb_client'
        )

    @property
    def client(self) -> chromadb.HttpClient:
        """Lazy-loaded ChromaDB client"""
        if self._client is None:
            self._client = chromadb.HttpClient(host=self.host, port=self.port)
        return self._client

    @retry(
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        wait=wait_exponential(multiplier=2, min=1, max=30),
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _execute_with_retry(self, operation: Callable, *args, **kwargs):
        """Execute ChromaDB operation with retry"""
        try:
            return self.breaker.call(operation, *args, **kwargs)
        except pybreaker.CircuitBreakerError:
            logger.error("Circuit breaker OPEN for ChromaDB")
            raise

    def get_collection(self, name: str):
        """Get collection with error recovery"""
        try:
            return self._execute_with_retry(self.client.get_collection, name)
        except Exception as e:
            logger.error(f"ChromaDB get_collection failed: {e}")
            raise

    def heartbeat(self) -> bool:
        """Health check"""
        try:
            return self._execute_with_retry(self.client.heartbeat) is not None
        except Exception:
            return False


# Global resilient clients
resilient_redis = ResilientRedisClient()
resilient_chroma = ResilientChromaClient()

#!/usr/bin/env python3
"""
Health Check System for MCP RAG Server
Provides liveness, readiness, and deep health checks
"""

import time
import asyncio
from typing import Dict, Any
from datetime import datetime
import logging

import chromadb
import redis
from sentence_transformers import SentenceTransformer
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthChecker:
    """Comprehensive health checking for RAG system"""

    def __init__(self):
        self.start_time = time.time()
        self.is_initialized = False

    async def check_chromadb(self, host: str = "localhost", port: int = 8001) -> Dict:
        """Check ChromaDB health"""
        try:
            client = chromadb.HttpClient(host=host, port=port)
            heartbeat = await asyncio.to_thread(client.heartbeat)
            collections = await asyncio.to_thread(client.list_collections)

            return {
                "status": "healthy",
                "heartbeat": heartbeat,
                "collections": len(collections),
                "connection": f"http://{host}:{port}"
            }
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def check_redis(self, host: str = "127.0.0.1", port: int = 6379, db: int = 2) -> Dict:
        """Check Redis health"""
        try:
            client = redis.Redis(
                host=host,
                port=port,
                db=db,
                socket_timeout=2,
                decode_responses=True
            )

            ping = await asyncio.to_thread(client.ping)
            info = await asyncio.to_thread(client.info, "server")

            return {
                "status": "healthy",
                "ping": ping,
                "version": info.get("redis_version", "unknown"),
                "connection": f"{host}:{port}"
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def check_embedding_model(self, model_name: str = "all-MiniLM-L6-v2") -> Dict:
        """Check embedding model health"""
        try:
            # Check if model can be loaded and encode
            test_text = "Health check test"
            model = SentenceTransformer(model_name)

            device = str(model.device)
            is_gpu = "cuda" in device.lower()

            start = time.time()
            embedding = await asyncio.to_thread(model.encode, [test_text])
            encoding_time = (time.time() - start) * 1000

            result = {
                "status": "healthy",
                "model_name": model_name,
                "device": device,
                "is_gpu": is_gpu,
                "encoding_time_ms": round(encoding_time, 2),
                "embedding_dim": len(embedding[0])
            }

            if is_gpu and torch.cuda.is_available():
                result["gpu_name"] = torch.cuda.get_device_name(0)
                result["gpu_memory_mb"] = round(torch.cuda.memory_allocated() / (1024**2), 2)

            return result

        except Exception as e:
            logger.error(f"Embedding model health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def liveness(self) -> Dict:
        """Simple liveness check - is the service running?"""
        return {
            "status": "healthy",
            "uptime_seconds": round(time.time() - self.start_time, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def readiness(self) -> Dict:
        """Readiness check - is the service ready to serve traffic?"""
        start = time.time()

        # Check all dependencies
        chroma = await self.check_chromadb()
        redis_check = await self.check_redis()
        model = await self.check_embedding_model()

        all_healthy = all(
            check.get("status") == "healthy"
            for check in [chroma, redis_check, model]
        )

        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": round(time.time() - self.start_time, 2),
            "check_duration_ms": round((time.time() - start) * 1000, 2),
            "dependencies": {
                "chromadb": chroma,
                "redis": redis_check,
                "embedding_model": model
            }
        }

    async def deep(self) -> Dict:
        """Deep diagnostic health check"""
        return await self.readiness()


# Global health checker
health_checker = HealthChecker()

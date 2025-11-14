#!/usr/bin/env python3
"""
GPU Acceleration Verification for AMD ROCm
Verifies GPU is being used for sentence-transformers embeddings
"""

import os
import sys
import time
import subprocess
from typing import Dict, List, Optional
import logging

import torch
from sentence_transformers import SentenceTransformer
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GPUVerifier:
    """Verify GPU acceleration for embedding models"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name

    def check_pytorch_gpu(self) -> Dict:
        """Verify PyTorch GPU support"""
        cuda_available = torch.cuda.is_available()
        device_count = torch.cuda.device_count() if cuda_available else 0

        result = {
            "cuda_available": cuda_available,
            "device_count": device_count,
            "pytorch_version": torch.__version__,
            "devices": []
        }

        if cuda_available:
            for i in range(device_count):
                result["devices"].append({
                    "id": i,
                    "name": torch.cuda.get_device_name(i),
                    "memory_gb": round(torch.cuda.get_device_properties(i).total_memory / (1024**3), 2)
                })

        return result

    def check_model_device(self, model: SentenceTransformer) -> Dict:
        """Check which device the model is using"""
        device = str(model.device)
        is_gpu = "cuda" in device.lower()

        result = {
            "model_device": device,
            "is_gpu": is_gpu,
            "device_type": "GPU (ROCm)" if is_gpu else "CPU"
        }

        if is_gpu:
            result["gpu_name"] = torch.cuda.get_device_name(0)

        return result

    def benchmark_cpu_vs_gpu(self, batch_sizes: List[int] = [1, 16, 64]) -> Dict:
        """Benchmark encoding performance"""
        logger.info("Running CPU vs GPU benchmark...")

        test_sentences = [
            f"This is test sentence number {i} for benchmarking."
            for i in range(max(batch_sizes))
        ]

        results = {"cpu": {}, "gpu": {}, "speedup": {}}

        # CPU benchmark
        logger.info("  Benchmarking CPU...")
        model_cpu = SentenceTransformer(self.model_name, device='cpu')

        for batch_size in batch_sizes:
            sentences = test_sentences[:batch_size]

            # Warmup
            _ = model_cpu.encode(sentences, show_progress_bar=False)

            # Benchmark
            start = time.time()
            _ = model_cpu.encode(sentences, show_progress_bar=False)
            cpu_time = time.time() - start

            results["cpu"][batch_size] = {
                "time_seconds": round(cpu_time, 3),
                "throughput": round(batch_size / cpu_time, 1)
            }

        # GPU benchmark
        if torch.cuda.is_available():
            logger.info("  Benchmarking GPU...")
            model_gpu = SentenceTransformer(self.model_name, device='cuda')

            for batch_size in batch_sizes:
                sentences = test_sentences[:batch_size]

                # Warmup
                _ = model_gpu.encode(sentences, convert_to_tensor=True, show_progress_bar=False)
                torch.cuda.synchronize()

                # Benchmark
                start = time.time()
                _ = model_gpu.encode(sentences, convert_to_tensor=True, show_progress_bar=False)
                torch.cuda.synchronize()
                gpu_time = time.time() - start

                results["gpu"][batch_size] = {
                    "time_seconds": round(gpu_time, 3),
                    "throughput": round(batch_size / gpu_time, 1)
                }

                speedup = cpu_time / gpu_time
                results["speedup"][batch_size] = round(speedup, 2)

                logger.info(f"    Batch {batch_size}: {speedup:.2f}x faster on GPU")

        return results

    def run_verification(self) -> Dict:
        """Run full GPU verification"""
        logger.info("="*60)
        logger.info("GPU ACCELERATION VERIFICATION")
        logger.info("="*60)

        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_name": self.model_name
        }

        # PyTorch GPU check
        report["pytorch_gpu"] = self.check_pytorch_gpu()

        if report["pytorch_gpu"]["cuda_available"]:
            # Model device check
            model_gpu = SentenceTransformer(self.model_name, device='cuda')
            report["model_device"] = self.check_model_device(model_gpu)

            # Benchmark
            report["benchmark"] = self.benchmark_cpu_vs_gpu()

            # Summary
            logger.info("\nVERIFICATION SUMMARY:")
            logger.info(f"✓ GPU: {report['pytorch_gpu']['devices'][0]['name']}")
            logger.info(f"✓ Device: {report['model_device']['device_type']}")

            if "speedup" in report["benchmark"]:
                avg_speedup = sum(report["benchmark"]["speedup"].values()) / len(report["benchmark"]["speedup"])
                logger.info(f"✓ Average Speedup: {avg_speedup:.2f}x")
        else:
            logger.warning("✗ GPU not available")
            report["model_device"] = {"device": "cpu", "is_gpu": False}

        return report


if __name__ == "__main__":
    verifier = GPUVerifier()
    report = verifier.run_verification()

    import json
    print("\n" + json.dumps(report, indent=2))

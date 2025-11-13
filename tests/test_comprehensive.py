#!/usr/bin/env python3
"""
Comprehensive test suite for RAG system
Tests: ChromaDB, MCP server, all technologies, GPU, error handling
"""

import pytest
import chromadb
from sentence_transformers import SentenceTransformer
import torch
import subprocess
import time
import json

class TestChromaDB:
    """Test ChromaDB connection and data integrity"""

    @pytest.fixture
    def client(self):
        return chromadb.HttpClient(host='localhost', port=8001)

    @pytest.fixture
    def collection(self, client):
        return client.get_collection('coding_knowledge')

    def test_chromadb_connection(self, client):
        """Test ChromaDB server is accessible"""
        assert client.heartbeat() > 0

    def test_collection_exists(self, collection):
        """Test coding_knowledge collection exists"""
        assert collection.name == 'coding_knowledge'

    def test_collection_has_documents(self, collection):
        """Test collection has expected document count"""
        count = collection.count()
        assert count > 70000, f"Expected >70000 docs, got {count}"
        assert count < 80000, f"Expected <80000 docs, got {count}"

    def test_metadata_structure(self, collection):
        """Test documents have correct metadata"""
        sample = collection.get(limit=10, include=['metadatas'])
        for meta in sample['metadatas']:
            assert 'source_file' in meta
            # Most should have technology
            if 'technology' in meta:
                assert isinstance(meta['technology'], str)
                assert len(meta['technology']) > 0


class TestEmbeddings:
    """Test embedding generation"""

    @pytest.fixture
    def model_cpu(self):
        return SentenceTransformer('all-MiniLM-L6-v2')

    @pytest.fixture
    def model_gpu(self):
        if torch.cuda.is_available():
            model = SentenceTransformer('all-MiniLM-L6-v2')
            return model.to('cuda')
        return None

    def test_embedding_shape(self, model_cpu):
        """Test embeddings have correct shape"""
        text = "Test sentence"
        embedding = model_cpu.encode([text])
        assert embedding.shape == (1, 384)

    def test_embedding_consistency(self, model_cpu):
        """Test same text produces same embedding"""
        text = "Test consistency"
        emb1 = model_cpu.encode([text])
        emb2 = model_cpu.encode([text])
        assert (emb1 == emb2).all()

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="GPU not available")
    def test_gpu_acceleration(self, model_gpu):
        """Test GPU acceleration is working"""
        assert model_gpu.device.type == 'cuda'
        text = "GPU test"
        embedding = model_gpu.encode([text])
        assert embedding.shape == (1, 384)


class TestSearchAccuracy:
    """Test search result accuracy"""

    @pytest.fixture
    def client(self):
        return chromadb.HttpClient(host='localhost', port=8001)

    @pytest.fixture
    def collection(self, client):
        return client.get_collection('coding_knowledge')

    @pytest.fixture
    def model(self):
        model = SentenceTransformer('all-MiniLM-L6-v2')
        if torch.cuda.is_available():
            model = model.to('cuda')
        return model

    def test_react_query(self, collection, model):
        """Test React-related query returns React docs"""
        query = "How do I use React hooks?"
        embedding = model.encode([query]).tolist()
        results = collection.query(query_embeddings=embedding, n_results=5)

        # Check we got results
        assert len(results['documents'][0]) == 5

        # Check top result is React-related
        top_meta = results['metadatas'][0][0]
        assert 'technology' in top_meta
        assert 'react' in top_meta['technology'].lower()

    def test_python_query(self, collection, model):
        """Test Python query returns Python docs"""
        query = "Python async await patterns"
        embedding = model.encode([query]).tolist()
        results = collection.query(query_embeddings=embedding, n_results=5)

        assert len(results['documents'][0]) == 5
        top_meta = results['metadatas'][0][0]
        assert 'technology' in top_meta
        assert 'python' in top_meta['technology'].lower()

    def test_docker_query(self, collection, model):
        """Test Docker query returns Docker docs"""
        query = "Docker networking and container communication"
        embedding = model.encode([query]).tolist()
        results = collection.query(query_embeddings=embedding, n_results=5)

        assert len(results['documents'][0]) == 5
        top_meta = results['metadatas'][0][0]
        assert 'technology' in top_meta
        assert 'docker' in top_meta['technology'].lower()


class TestTechnologyFilters:
    """Test all technology filters work correctly"""

    @pytest.fixture
    def client(self):
        return chromadb.HttpClient(host='localhost', port=8001)

    @pytest.fixture
    def collection(self, client):
        return client.get_collection('coding_knowledge')

    @pytest.fixture
    def model(self):
        model = SentenceTransformer('all-MiniLM-L6-v2')
        if torch.cuda.is_available():
            model = model.to('cuda')
        return model

    def test_get_all_technologies(self, collection):
        """Test we can enumerate all technologies"""
        all_metadata = collection.get(include=["metadatas"])
        technologies = set()
        for meta in all_metadata["metadatas"]:
            if 'technology' in meta:
                technologies.add(meta['technology'])

        assert len(technologies) >= 40, f"Expected >=40 technologies, got {len(technologies)}"
        return technologies

    def test_filter_by_technology(self, collection, model):
        """Test filtering by technology works"""
        query = "example code"
        embedding = model.encode([query]).tolist()

        # Get all technologies
        all_meta = collection.get(include=["metadatas"], limit=1000)
        technologies = set()
        for meta in all_meta["metadatas"]:
            if 'technology' in meta:
                technologies.add(meta['technology'])

        # Test filtering by first 5 technologies
        for tech in list(technologies)[:5]:
            results = collection.query(
                query_embeddings=embedding,
                n_results=3,
                where={"technology": tech}
            )

            # All results should be from that technology
            for meta in results['metadatas'][0]:
                assert meta.get('technology') == tech, f"Expected {tech}, got {meta.get('technology')}"


class TestPerformance:
    """Test performance meets requirements"""

    @pytest.fixture
    def client(self):
        return chromadb.HttpClient(host='localhost', port=8001)

    @pytest.fixture
    def collection(self, client):
        return client.get_collection('coding_knowledge')

    @pytest.fixture
    def model(self):
        model = SentenceTransformer('all-MiniLM-L6-v2')
        if torch.cuda.is_available():
            model = model.to('cuda')
        return model

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="GPU performance test")
    def test_gpu_query_speed(self, collection, model):
        """Test GPU queries are under 100ms"""
        query = "Test performance query"
        embedding = model.encode([query]).tolist()

        start = time.time()
        results = collection.query(query_embeddings=embedding, n_results=5)
        elapsed = time.time() - start

        assert elapsed < 0.1, f"Query took {elapsed*1000:.1f}ms (expected <100ms)"

    def test_batch_queries(self, collection, model):
        """Test batch query performance"""
        queries = [
            "React components",
            "Python functions",
            "Docker containers",
            "TypeScript types",
            "PostgreSQL queries"
        ]

        embeddings = model.encode(queries).tolist()

        start = time.time()
        for embedding in embeddings:
            _ = collection.query(query_embeddings=[embedding], n_results=5)
        elapsed = time.time() - start

        avg_time = elapsed / len(queries)
        assert avg_time < 0.5, f"Average query time: {avg_time*1000:.1f}ms (expected <500ms)"


class TestMCPServer:
    """Test MCP server functionality"""

    def test_mcp_server_starts(self):
        """Test MCP server can start"""
        proc = subprocess.Popen(
            ["./.venv/bin/python", "mcp_server/rag_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        time.sleep(2)
        assert proc.poll() is None, "MCP server failed to start"

        proc.terminate()
        proc.wait(timeout=5)


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.fixture
    def client(self):
        return chromadb.HttpClient(host='localhost', port=8001)

    @pytest.fixture
    def collection(self, client):
        return client.get_collection('coding_knowledge')

    @pytest.fixture
    def model(self):
        model = SentenceTransformer('all-MiniLM-L6-v2')
        if torch.cuda.is_available():
            model = model.to('cuda')
        return model

    def test_empty_query(self, collection, model):
        """Test handling of empty query"""
        # Empty query should still work (will just match randomly)
        embedding = model.encode([""]).tolist()
        results = collection.query(query_embeddings=embedding, n_results=5)
        assert len(results['documents'][0]) == 5

    def test_very_long_query(self, collection, model):
        """Test handling of very long query"""
        long_query = "test " * 500  # Very long query
        embedding = model.encode([long_query]).tolist()
        results = collection.query(query_embeddings=embedding, n_results=5)
        assert len(results['documents'][0]) == 5

    def test_invalid_technology_filter(self, collection, model):
        """Test filtering by non-existent technology"""
        query = "test query"
        embedding = model.encode([query]).tolist()
        results = collection.query(
            query_embeddings=embedding,
            n_results=5,
            where={"technology": "NonExistentTechnology123"}
        )
        # Should return 0 results
        assert len(results['documents'][0]) == 0


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

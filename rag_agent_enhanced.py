"""
Enhanced RAG Agent: Integration layer combining QueryRecognizer and ChromaDB
Demonstrates how to use rag_agent_optimizer with coding_knowledge_tool

This module shows the practical integration of intelligent routing with the existing
RAG knowledge base at localhost:8001
"""

from typing import Dict, List, Optional, Tuple
from rag_agent_optimizer import QueryRecognizer, RAGAgentPrompts, KnowledgeDomain, DOMAIN_REGISTRY
import chromadb

# ============================================================================
# ENHANCED RAG QUERY INTERFACE
# ============================================================================

class EnhancedRAGAgent:
    """
    Enhanced RAG agent with intelligent routing and domain-specific retrieval

    Combines:
    1. QueryRecognizer: Identifies knowledge domains
    2. ChromaDB client: Retrieves relevant chunks
    3. System prompts: Defines agent behavior
    """

    def __init__(self, chroma_host: str = "localhost", chroma_port: int = 8001):
        """Initialize agent with ChromaDB connection"""
        self.recognizer = QueryRecognizer()
        self.chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        self.collection = self.chroma_client.get_collection("coding_knowledge")

    def query_knowledge_base(
        self,
        query: str,
        n_results: int = 5,
        confidence_threshold: float = 0.2
    ) -> Dict:
        """
        Intelligent query with domain recognition and routing

        Args:
            query: User query string
            n_results: Number of results to retrieve
            confidence_threshold: Minimum confidence for domain routing

        Returns:
            Dict with:
                - domain: Identified knowledge domain
                - confidence: Domain confidence score
                - keywords: Matched keywords
                - results: Retrieved chunks with metadata
                - formatting_guide: Response formatting instructions
        """
        # Step 1: Recognize domain
        domain, confidence, keywords = self.recognizer.recognize(query)

        # Step 2: Determine if confidence is high enough
        if confidence < confidence_threshold:
            domain = KnowledgeDomain.GENERAL
            is_focused_domain = False
        else:
            is_focused_domain = True

        # Step 3: Get domain metadata
        metadata = self.recognizer.get_domain_context(domain)

        # Step 4: Build retrieval filters based on domain
        if is_focused_domain and domain != KnowledgeDomain.GENERAL:
            # Use domain-specific filters for targeted retrieval
            # Note: We filter by source names that appear in the technology field
            # This requires metadata to contain source names (e.g., "Figma", "React Docs")
            where_filters = {
                "technology": {"$in": metadata.sources[:10]}  # Top 10 source names
            }
        else:
            # Full database search for general queries
            where_filters = None

        # Step 5: Retrieve from ChromaDB with fallback mechanism
        try:
            if where_filters:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=where_filters,
                    include=["documents", "metadatas", "distances"]
                )

                # Fallback: If domain-specific filter returns 0 results,
                # retry without filters for broader coverage
                if not results["documents"] or not results["documents"][0]:
                    results = self.collection.query(
                        query_texts=[query],
                        n_results=n_results,
                        include=["documents", "metadatas", "distances"]
                    )
            else:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    include=["documents", "metadatas", "distances"]
                )
        except Exception as e:
            return {
                "error": f"Database query failed: {str(e)}",
                "domain": domain.value,
                "confidence": confidence,
                "results": None
            }

        # Step 6: Format response with routing metadata
        return {
            "domain": domain.value,
            "domain_enum": domain,
            "confidence": confidence,
            "confidence_pct": f"{confidence:.0%}",
            "is_focused_domain": is_focused_domain,
            "keywords": keywords,
            "sources": metadata.sources if is_focused_domain else ["Cross-Domain"],
            "topics": metadata.topics if is_focused_domain else [],
            "results": {
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else []
            },
            "formatting_guide": {
                "domain_identification": f"Query belongs to {domain.value} domain",
                "format": "DOMAIN > RETRIEVED > SYNTHESIS > RECOMMENDATIONS > CITATIONS",
                "citation_sources": [m.get("source_file") for m in (results["metadatas"][0] if results["metadatas"] else [])]
            }
        }

    def get_domain_for_query(self, query: str) -> Tuple[str, float, List[str]]:
        """
        Quick domain lookup without database retrieval

        Returns:
            (domain_name, confidence, keywords)
        """
        domain, confidence, keywords = self.recognizer.recognize(query)
        return domain.value, confidence, keywords

    def get_system_prompt(self) -> str:
        """Get the system definition prompt for agent initialization"""
        return RAGAgentPrompts.SYSTEM_PROMPT_DEFINITION()

    def get_routing_prompt(self) -> str:
        """Get the operational routing prompt for query handling"""
        return RAGAgentPrompts.OPERATION_PROMPT_ROUTING()

    def get_domain_context(self, domain_name: str) -> Optional[Dict]:
        """Get metadata for a specific domain"""
        try:
            domain = KnowledgeDomain[domain_name.upper()]
            metadata = self.recognizer.get_domain_context(domain)
            return {
                "domain": metadata.domain.value,
                "keywords": metadata.keywords,
                "sources": metadata.sources,
                "topics": metadata.topics,
                "description": metadata.description,
                "triggers": metadata.triggers
            }
        except (KeyError, AttributeError):
            return None


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_basic_usage():
    """Basic usage example"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Query with Domain Recognition")
    print("=" * 80)

    agent = EnhancedRAGAgent()

    query = "How do I design a responsive UI component?"
    result = agent.query_knowledge_base(query, n_results=3)

    print(f"\nQuery: {query}")
    print(f"Domain: {result['domain']} ({result['confidence_pct']} confidence)")
    print(f"Matched keywords: {', '.join(result['keywords'])}")
    print(f"Sources: {', '.join(result['sources'][:3])}")
    print(f"Retrieved {len(result['results']['documents'])} chunks")


def example_multi_domain_query():
    """Example with multi-domain query"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Multi-Domain Query")
    print("=" * 80)

    agent = EnhancedRAGAgent()

    query = "I need to automate my business process and set up accounting"
    result = agent.query_knowledge_base(query, n_results=5)

    print(f"\nQuery: {query}")
    print(f"Primary domain: {result['domain']} ({result['confidence_pct']} confidence)")
    print(f"Confidence threshold exceeded: {result['is_focused_domain']}")
    print(f"Retrieved sources: {', '.join(result['sources'][:3])}")
    print(f"Result count: {len(result['results']['documents'])}")


def example_domain_context():
    """Example of getting domain information"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Domain Context Information")
    print("=" * 80)

    agent = EnhancedRAGAgent()

    # Get context for ecommerce domain
    context = agent.get_domain_context("ecommerce")

    print(f"\nDomain: {context['domain']}")
    print(f"Description: {context['description']}")
    print(f"Topics: {', '.join(context['topics'][:4])}...")
    print(f"Sources: {', '.join(context['sources'][:3])}...")
    print(f"\nTrigger examples:")
    for i, trigger in enumerate(context['triggers'][:3], 1):
        print(f"  {i}. {trigger}")


def example_routing_decision():
    """Example of routing logic"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Query Routing Decision")
    print("=" * 80)

    agent = EnhancedRAGAgent()

    test_queries = [
        "How do I design a logo?",  # Should route to DESIGN
        "What's the DTF heat press temperature?",  # Should route to DTF
        "Tell me a joke",  # Should not route (low confidence)
    ]

    for query in test_queries:
        domain, confidence, keywords = agent.get_domain_for_query(query)
        should_route = confidence >= 0.2

        print(f"\nQuery: {query}")
        print(f"Domain: {domain}")
        print(f"Confidence: {confidence:.0%}")
        print(f"Route to RAG? {'✓ YES' if should_route else '✗ NO'}")


def example_prompts():
    """Display system prompts"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: System Prompts for Agent Initialization")
    print("=" * 80)

    agent = EnhancedRAGAgent()

    print("\n[SYSTEM PROMPT - Agent Definition]")
    print("-" * 80)
    system_prompt = agent.get_system_prompt()
    print(system_prompt[:500] + "...\n")

    print("[ROUTING PROMPT - Query Handling]")
    print("-" * 80)
    routing_prompt = agent.get_routing_prompt()
    print(routing_prompt[:500] + "...\n")

    print("(See rag_agent_optimizer.py for full prompts)")


# ============================================================================
# INTEGRATION WITH EXISTING CODING_KNOWLEDGE_TOOL
# ============================================================================

def integrate_with_existing_system():
    """
    Shows how to integrate with existing coding_knowledge_tool.py

    Existing call:
        query_knowledge_base(query="...", technology_filter="...", n_results=5)

    Enhanced call:
        enhanced_agent.query_knowledge_base(query="...")

    The enhanced version automatically:
    1. Identifies the domain
    2. Selects appropriate technology filters
    3. Routes to the right sources
    4. Formats the response with metadata
    """

    print("\n" + "=" * 80)
    print("EXAMPLE 6: Integration with coding_knowledge_tool.py")
    print("=" * 80)

    agent = EnhancedRAGAgent()

    # Example: Replace this old call...
    # result = query_knowledge_base(
    #     query="How do I use React hooks?",
    #     technology_filter="React Docs",
    #     n_results=5
    # )

    # ...with this enhanced call
    result = agent.query_knowledge_base(
        query="How do I use React hooks?",
        n_results=5
    )

    print(f"\nOld approach required manual technology_filter selection")
    print(f"New approach automatically identifies:")
    print(f"  - Domain: {result['domain']}")
    print(f"  - Confidence: {result['confidence_pct']}")
    print(f"  - Matched keywords: {', '.join(result['keywords'])}")
    print(f"  - Relevant sources: {', '.join(result['sources'][:2])}")


# ============================================================================
# CONFIGURATION FOR PRODUCTION DEPLOYMENT
# ============================================================================

PRODUCTION_CONFIG = {
    "chroma_host": "localhost",
    "chroma_port": 8001,
    "default_n_results": 5,
    "confidence_threshold": 0.2,
    "system_prompt": RAGAgentPrompts.SYSTEM_PROMPT_DEFINITION(),
    "routing_prompt": RAGAgentPrompts.OPERATION_PROMPT_ROUTING(),
    "domains": [d.value for d in KnowledgeDomain],
    "sources_count": sum(len(m.sources) for m in DOMAIN_REGISTRY.values()),
}


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ENHANCED RAG AGENT - EXAMPLES & INTEGRATION")
    print("=" * 80)

    # Run examples
    example_basic_usage()
    example_multi_domain_query()
    example_domain_context()
    example_routing_decision()
    example_prompts()
    integrate_with_existing_system()

    # Show production config
    print("\n" + "=" * 80)
    print("PRODUCTION CONFIGURATION")
    print("=" * 80)
    print(f"ChromaDB Host: {PRODUCTION_CONFIG['chroma_host']}")
    print(f"ChromaDB Port: {PRODUCTION_CONFIG['chroma_port']}")
    print(f"Default Results: {PRODUCTION_CONFIG['default_n_results']}")
    print(f"Confidence Threshold: {PRODUCTION_CONFIG['confidence_threshold']}")
    print(f"Knowledge Domains: {len(PRODUCTION_CONFIG['domains'])}")
    print(f"Total Sources: {PRODUCTION_CONFIG['sources_count']}")
    print(f"\nStatus: ✅ READY FOR DEPLOYMENT")

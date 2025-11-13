# Strategic Plan: Building a Specialized RAG System for Code Generation

This document outlines the strategy, architecture, and technologies required to build a comprehensive, private knowledge base that an AI agent (MCP) can query to write accurate, fact-based code.

## The Goal: An Agentic Code Generation System

The system will follow a Retrieval-Augmented Generation (RAG) pattern:

1.  **Task:** The user provides a high-level task to the primary agent (e.g., "Build a Python FastAPI endpoint that caches data in Redis").
2.  **Reasoning:** The agent determines it needs factual knowledge about FastAPI, Redis, and their interaction.
3.  **Retrieval:** The agent calls a dedicated tool, `get_coding_knowledge(query: str)`.
4.  **Augmentation:** This tool queries a specialized vector database for the most relevant, curated documents and code snippets.
5.  **Generation:** The tool returns this high-quality context to the agent, which then uses the factual, "augmented" information to generate accurate and reliable code.

---

## Phase 1: Data Acquisition & Curation (The Foundation)

The quality of the RAG system is entirely dependent on the quality of its data.

### Data Sources:

1.  **Official Documentation:** The highest-quality source. Clone documentation repositories for major technologies.
    *   **Languages:** Python, JavaScript/TypeScript, Go, Rust, Java, C#.
    *   **Frameworks:** React, Next.js, Vue, Angular, FastAPI, Django, Flask, Express.js, Spring Boot, .NET.
    *   **Tools:** Docker, Kubernetes, Terraform, Ansible, Git.
    *   **Databases:** PostgreSQL, MongoDB, Redis, SQLite.
    *   **Cloud SDKs:** Boto3 (AWS), Azure SDK for Python, Google Cloud Client Libraries.
    *   **User-specified additions:** Flutter, n8n, Stripe, Vercel (Next.js docs).

2.  **Code Repositories:** High-quality, idiomatic code examples.
    *   Identify and clone well-regarded open-source projects (e.g., from `awesome-*` lists on GitHub).

3.  **Books:** Powerful but requires care.
    *   **CRITICAL COPYRIGHT NOTICE:** You must have legal access to any books used. This means using books you have purchased or those with permissive open-source licenses. Do not scrape copyrighted material you do not own.
    *   **Formats:** Convert formats like EPUB or PDF into clean text (Markdown is ideal) using tools like `pandoc`.

### Data Processing:

*   **Extraction:** Pull clean text from files (`.md`, `.py`, `.ts`, `.txt`).
*   **Chunking:** Break down large documents into smaller, semantically meaningful chunks (e.g., a function with its docstring, a documentation paragraph). This is crucial for retrieval accuracy.

---

## Phase 2: The RAG Technology Stack

### Storage: The Vector Database

A **Vector Database** is required to store and retrieve information based on semantic meaning.

*   **Recommended Starter:** **ChromaDB**. It can run locally/embedded and is easy to set up. Your environment already shows a ChromaDB configuration file, making it a natural choice.
*   **Scalable Alternatives:** Pinecone, Weaviate, or Postgres with the `pgvector` extension.

### The Pipeline Components:

A framework like **LangChain** or **LlamaIndex** is needed to orchestrate the process.

A typical ingestion script will:
1.  **Load:** Point to the directory of curated data.
2.  **Chunk:** Use a text splitter to break documents into pieces.
3.  **Embed:** Use an embedding model (e.g., self-hosted `all-MiniLM-L6-v2` or API-based OpenAI models) to convert each chunk into a vector.
4.  **Store:** Feed the vectors and their corresponding text into the vector database (ChromaDB).

---

## Phase 3: Integration with Your Agentic Workflow (MCP)

A new tool will be created to expose the RAG database to the agent.

### Conceptual Tool Example:

```python
# In a new file, e.g., tools/knowledge_base.py

import chromadb
# from sentence_transformers import SentenceTransformer

class CodingKnowledgeTool:
    def __init__(self, mcp: "FastMCP"):
        """Initialize the Coding Knowledge Base tool."""
        # Initialize the ChromaDB client
        self.db_client = chromadb.PersistentClient(path="/path/to/your/db")
        self.collection = self.db_client.get_collection(name="coding_knowledge")
        
        # Initialize your embedding model
        # self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Register the tool with MCP
        mcp.tool(name='get_coding_knowledge')(self.query_knowledge_base)

    def query_knowledge_base(self, query: str, n_results: int = 5) -> str:
        """
        Queries the coding knowledge base for relevant documents and code snippets.
        """
        try:
            # 1. Embed the user's query
            query_embedding = self.embedding_model.encode(query).tolist()

            # 2. Query the vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

            # 3. Format and return the results
            context = "### Retrieved Knowledge ###\n\n"
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                source = metadata.get('source', 'Unknown')
                context += f"--- Document {i+1} from {source} ---\\n"
                context += doc + "\n\n"
            
            return context
        except Exception as e:
            return f"Error querying knowledge base: {e}"
```

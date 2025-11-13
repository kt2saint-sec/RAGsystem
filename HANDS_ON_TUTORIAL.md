# RAG Knowledge Base - Hands-On Tutorial

**Level**: Beginner to Advanced
**Duration**: 4-5 hours (includes exercises)
**Prerequisites**: ChromaDB running, MCP server configured
**System**: GPU-accelerated (AMD 7900 XTX)

---

## Table of Contents

**Part 1: Fundamentals** (30-45 min)
1. [Your First Query](#11-your-first-query)
2. [Understanding Technology Filters](#12-understanding-technology-filters)
3. [Adjusting Result Count](#13-adjusting-result-count)
4. [Reading Results Effectively](#14-reading-results-effectively)

**Part 2: Usage Methods** (45-60 min)
1. [Via Claude Code CLI](#21-via-claude-code-cli)
2. [Direct MCP Tool Invocation](#22-direct-mcp-tool-invocation)
3. [Python Scripts](#23-python-scripts-automation)

**Part 3: Practical Scenarios** (60-90 min)
1. [Web Development Workflow](#31-web-development-workflow)
2. [Learning New Technology](#32-learning-new-technology)
3. [Debugging & Troubleshooting](#33-debugging--troubleshooting)
4. [Code Review & Best Practices](#34-code-review--best-practices)
5. [Multi-Technology Integration](#35-multi-technology-integration)

**Part 4: Advanced Techniques** (45-60 min)
1. [Query Optimization](#41-query-optimization)
2. [Result Filtering & Post-Processing](#42-result-filtering--post-processing)
3. [Combining RAG with Other MCP Tools](#43-combining-rag-with-other-mcp-tools)
4. [Performance Monitoring](#44-performance-monitoring--benchmarking)

**Part 5: Troubleshooting & Tips** (20-30 min)
1. [Common Issues & Solutions](#51-common-issues--solutions)
2. [Pro Tips & Best Practices](#52-pro-tips--best-practices)

**Appendices**
- [Quick Reference Card](#appendix-a-quick-reference-card)
- [Technology Filter Cheat Sheet](#appendix-b-technology-filter-cheat-sheet)
- [Example Query Library](#appendix-c-example-query-library)

---

# PART 1: FUNDAMENTALS

## 1.1 Your First Query

### Learning Outcome
Understand basic query mechanics and result interpretation.

### Simple Query Example

```bash
# Start Claude Code (from any directory now!)
cd ~
claude
```

**Your first question**:
```
"Use the RAG knowledge base to search for how to create a React component"
```

**What happens behind the scenes**:
1. Claude recognizes "RAG knowledge base" trigger phrase
2. Calls `query_knowledge_base` MCP tool
3. MCP server generates embedding (GPU-accelerated, 2.5ms)
4. ChromaDB searches 70,652 documents (3.7ms)
5. Returns top 5 most relevant results
6. Claude formats response with code examples

### Understanding Results

**Example result structure**:
```json
{
  "rank": 1,
  "content": "Components are the building blocks of React applications. A component is a JavaScript function that returns JSX...",
  "technology": "React Docs",
  "source_url": "https://github.com/reactjs/react.dev",
  "source_file": "/home/rebelsts/RAG/data/repos/react_dev/src/content/learn/your-first-component.md",
  "similarity_score": 0.8532,
  "distance": 0.1468
}
```

**What each field means**:

| Field | Meaning | Example Value |
|-------|---------|---------------|
| `rank` | Relevance order (1 = best match) | 1 |
| `content` | Text chunk (max 1000 chars) | "Components are..." |
| `technology` | Source documentation | "React Docs" |
| `source_url` | GitHub/web URL | "https://github.com/..." |
| `source_file` | Local file path | ".../your-first-component.md" |
| `similarity_score` | Confidence (0-1 scale) | 0.8532 (85.32%) |
| `distance` | Inverse of similarity | 0.1468 |

**Interpreting Similarity Scores**:
- **0.85+**: Excellent match - highly relevant
- **0.70-0.85**: Good match - relevant
- **0.50-0.70**: Moderate - possibly useful
- **<0.50**: Weak match - consider rephrasing query

### Hands-On Exercise 1

**Task**: Query for Python async functions and identify the most relevant result.

```
"Query the RAG knowledge base for Python async await patterns"
```

**Questions to answer**:
1. What is the similarity score of the top result?
2. Which source file contains the best match?
3. Is the content from "Python Docs" or another technology?

**Expected similarity**: 0.75-0.90 (Python is well-documented in the knowledge base)

### Common Mistakes

❌ **Expecting exact keyword matching**:
```
Query: "async"
Problem: Too vague, semantic search needs context
```

✅ **Better query**:
```
Query: "Python async await error handling patterns"
Result: More specific, higher similarity scores
```

❌ **Ignoring low similarity scores**:
```
If all results are <0.6, rephrase your query
```

---

## 1.2 Understanding Technology Filters

### Learning Outcome
Use filters to narrow results to specific domains and technologies.

### Why Use Filters?

**Without filter** - broad search across all 36 technologies:
```
"dependency injection"
```

**Possible results**:
- Rank 1: FastAPI Docs (0.82)
- Rank 2: React Docs (0.75)
- Rank 3: Java SE Tutorials (0.71)
- Rank 4: TypeScript Docs (0.68)

**With filter** - targeted search:
```
"dependency injection" with technology_filter="FastAPI Docs"
```

**Results**:
- Rank 1: FastAPI DI patterns (0.88)
- Rank 2: FastAPI middleware injection (0.84)
- Rank 3: FastAPI database sessions (0.81)

**Benefits**:
✅ Higher similarity scores (more relevant)
✅ Faster queries (smaller search space)
✅ Domain-specific answers

### Available Technology Filters

**List all technologies**:
```
"Use list_technologies to show all available filters"
```

**Common filters** (36 total):

**Web Development**:
- `React Docs`
- `Next.js Docs (Vercel)`
- `Vue Docs`
- `Angular Docs`
- `TypeScript Docs`
- `MDN HTML Docs`
- `MDN Web Dev Guide`

**Backend/API**:
- `FastAPI Docs`
- `Python Docs`
- `Node.js Docs`
- `Express Docs`

**AI/ML**:
- `LangChain Docs`
- `Anthropic Docs`
- `OpenAI Docs`
- `Google Gemini Docs`
- `ComfyUI Repo`

**Full list in Appendix B**

### Filter Comparison Example

**Test**: Search "authentication" with and without filters

**Unfiltered**:
```
"Query the knowledge base for authentication patterns"
```

**Results mix**:
- JWT (FastAPI)
- OAuth (React)
- API keys (Various)
- Session tokens (Express)

**Filtered (FastAPI)**:
```
"Query the knowledge base for authentication patterns, filtered to FastAPI Docs"
```

**Results focus**:
- FastAPI JWT implementation
- OAuth2 with FastAPI
- Dependency injection for auth
- Middleware patterns

### Hands-On Exercise 2

**Task**: Compare results for "hooks" across React and Vue.

**Query 1** (React):
```
"Search RAG for hooks patterns, filter to React Docs, top 5 results"
```

**Query 2** (Vue):
```
"Search RAG for hooks patterns, filter to Vue Docs, top 5 results"
```

**Questions**:
1. How do similarity scores compare?
2. What are the conceptual differences?
3. Which framework has more hook-related documentation?

### Tips for Using Filters

✅ **Use `list_technologies()` when unsure**:
```
"List all technologies in the knowledge base"
```

✅ **Filter names are case-sensitive**:
- ❌ "react docs"
- ✅ "React Docs"

✅ **Check exact spelling**:
- ❌ "Nextjs Docs"
- ✅ "Next.js Docs (Vercel)"

✅ **Filters reduce search space**:
- Slightly faster queries
- More targeted results
- Higher similarity scores

---

## 1.3 Adjusting Result Count

### Learning Outcome
Control breadth vs depth of search results using `top_k` parameter.

### Default Behavior

**Without specifying `top_k`**:
```
"Query RAG for Docker multi-stage builds"
```

**Returns**: 5 results (default)

### When to Use Different Counts

**2-3 results** - Quick snippet needed:
```
"Search RAG for PostgreSQL connection string syntax, top 3"
```

**Use case**: You need a specific code example, don't want to read through many results.

**5 results** (default) - Balanced approach:
```
"Query RAG for React component lifecycle methods"
```

**Use case**: Most common queries, good balance of coverage and focus.

**10-15 results** - Comprehensive research:
```
"Search RAG for Rust ownership rules, top 15 results"
```

**Use case**: Learning a new topic, want to see multiple perspectives.

**20 results** (maximum) - Deep exploration:
```
"Query RAG for all available Docker networking patterns, top 20"
```

**Use case**: Comparing approaches, building a comprehensive guide.

### Result Quality by Rank

**Typical similarity score distribution**:

| Rank Range | Similarity Score | Quality |
|------------|------------------|---------|
| 1-3 | 0.75-0.90 | Highly relevant |
| 4-7 | 0.65-0.75 | Relevant |
| 8-12 | 0.55-0.65 | Moderately relevant |
| 13-20 | <0.55 | Diminishing returns |

### Hands-On Exercise 3

**Task**: Query "React hooks" with different `top_k` values and plot similarity scores.

**Query variations**:
```bash
# Create a simple test script
cat > ~/test_topk.py << 'EOF'
import chromadb
from sentence_transformers import SentenceTransformer
import torch

client = chromadb.HttpClient(host='localhost', port=8001)
collection = client.get_collection('coding_knowledge')

model = SentenceTransformer('all-MiniLM-L6-v2')
if torch.cuda.is_available():
    model = model.to('cuda')

query = "React hooks state management"
embedding = model.encode([query]).tolist()

for top_k in [3, 5, 10, 20]:
    results = collection.query(
        query_embeddings=embedding,
        n_results=top_k
    )

    print(f"\nTop {top_k} results:")
    for i, dist in enumerate(results['distances'][0]):
        similarity = 1 - dist
        print(f"  Rank {i+1}: {similarity:.4f}")
EOF

./.venv/bin/python ~/test_topk.py
```

**Expected output**:
```
Top 3 results:
  Rank 1: 0.8532
  Rank 2: 0.8201
  Rank 3: 0.7945

Top 5 results:
  Rank 1: 0.8532
  Rank 2: 0.8201
  Rank 3: 0.7945
  Rank 4: 0.7512
  Rank 5: 0.7289

Top 10 results:
  ...scores decline to 0.65-0.70...

Top 20 results:
  ...scores decline to 0.45-0.60...
```

**Observation**: Diminishing returns after rank 7-10 for most queries.

---

## 1.4 Reading Results Effectively

### Learning Outcome
Extract actionable information from RAG responses.

### Anatomy of a Result

**Full example breakdown**:
```json
{
  "rank": 1,
  "content": "Hooks are functions that let you \"hook into\" React state and lifecycle features from function components. React provides several built-in Hooks like useState and useEffect...",
  "technology": "React Docs",
  "source_url": "https://github.com/reactjs/react.dev",
  "source_file": "/home/rebelsts/RAG/data/repos/react_dev/src/content/reference/react/hooks.md",
  "similarity_score": 0.8532,
  "distance": 0.1468
}
```

### What Each Field Tells You

**1. `rank`**: Relevance ordering
- Use ranks 1-3 for code generation
- Review ranks 4-7 for additional context
- Scan ranks 8+ for alternative approaches

**2. `content`**: The actual text chunk
- **Max length**: 1000 characters
- **Chunking**: May be middle of document
- **Context**: Use `source_file` to read full document

**3. `technology`**: Source documentation
- Shows which official docs this came from
- Useful for multi-technology projects
- Cross-reference multiple sources

**4. `source_url`**: Original repository/website
- GitHub URL for code examples
- Official documentation site
- Use for latest updates

**5. `source_file`**: Exact file location
- Absolute path on your system
- Open in editor for full context
- See surrounding code/docs

**6. `similarity_score`**: Confidence metric
- **0.85+**: High confidence - use directly
- **0.70-0.85**: Good - review before using
- **0.50-0.70**: Medium - verify externally
- **<0.50**: Low - rephrase query

### Hands-On Exercise 4

**Task**: Query for TypeScript generics, then explore the full source file.

**Step 1: Query**:
```
"Query RAG for TypeScript generic type constraints, top 3"
```

**Step 2: Note the top result's source_file**:
```
Example: /home/rebelsts/RAG/data/repos/typescript_docs/handbook/generics.md
```

**Step 3: Read full file**:
```bash
# Use Read tool or cat
cat /home/rebelsts/RAG/data/repos/typescript_docs/handbook/generics.md
```

**Step 4: Compare**:
- What additional context did you find?
- Is the chunk representative of the full document?
- What information was in surrounding sections?

### Understanding Chunking

**Why chunks, not full documents?**
- Documents are too large for context windows
- Semantic search works better on focused content
- 1000 characters ≈ 250 words (manageable)

**Chunk overlap**: 150 characters
- Prevents information loss at boundaries
- Ensures concepts aren't split mid-sentence

**Example**:
```
Document: 5000 characters
Chunks created: 5-6 chunks
Overlap: 150 characters between each
Result: Multiple chunks from same file may appear in results
```

### Pro Tips for Reading Results

✅ **Multiple results from same file**:
```
If ranks 1, 3, and 5 are all from same source_file,
that document is very relevant to your query.
Read the full file for comprehensive understanding.
```

✅ **Cross-reference technologies**:
```
Query: "state management patterns"
Results from: React, Vue, Angular
Action: Compare patterns across frameworks
```

✅ **Use source_url for latest**:
```
RAG data snapshot: When ingestion was run
source_url: Live repository/docs
Action: Check URL for updates since ingestion
```

✅ **Low scores = rephrase**:
```
If all results <0.65:
1. Add more context to query
2. Use more specific technical terms
3. Try different phrasing
4. Check if topic is in knowledge base (list_technologies)
```

---

# PART 2: USAGE METHODS

## 2.1 Via Claude Code CLI

### Learning Outcome
Master conversational querying (primary method).

### Natural Language Patterns

**Direct command style**:
```
"Search the RAG for React hooks examples"
"Query the knowledge base for Docker networking patterns"
"Use the coding knowledge tool to find FastAPI authentication"
```

**Conversational style**:
```
"I'm building a React app. Can you query the knowledge base for component lifecycle methods?"
"I need help with Python async. Search the RAG for best practices."
```

**Follow-up queries**:
```
First: "Search RAG for React state management"
Then: "Now search for hooks alternatives to componentDidMount"
Then: "Compare those approaches and recommend one for my use case"
```

### Full Workflow Example

**Scenario**: Building a FastAPI application with PostgreSQL

**Step 1: Database connection**:
```
You: "Query the knowledge base for FastAPI database connections"

Claude: [Uses query_knowledge_base MCP tool]
        [Returns SQLAlchemy examples from FastAPI Docs]
```

**Step 2: Connection pooling**:
```
You: "Now search for PostgreSQL connection pooling best practices"

Claude: [Queries again]
        [Returns connection pool configuration from PostgreSQL Docs]
```

**Step 3: Code generation**:
```
You: "Based on those results, write a database.py module for my app"

Claude: [Uses RAG context]
        [Generates code with proper patterns from official docs]
```

**Result**: Production-ready code grounded in official documentation.

### Hands-On Exercise 5

**Task**: Complete a full workflow for Docker debugging.

**Scenario**: Docker container can't communicate with another container.

**Your queries**:
```
1. "Search RAG for Docker container networking"
2. "Query knowledge base for Docker bridge networks"
3. "Find Docker compose service discovery patterns"
4. "Based on these results, help me fix my docker-compose.yml"
```

**Expected flow**:
- Claude queries RAG 3 times
- Synthesizes networking concepts
- Generates working docker-compose.yml configuration

### Phrases Claude Recognizes

**Explicit RAG triggers**:
- "Search the RAG..."
- "Query the knowledge base..."
- "Use the coding knowledge tool..."
- "Check the RAG system..."
- "Look up in the knowledge base..."

**Implicit triggers** (Claude decides):
- "How do I use [technology]..."
- "What's the best practice for..."
- "Show me examples of..."
- "Explain [concept] in [framework]..."

### Performance Notes

**First query in session**:
- **Latency**: ~2 seconds
- **Reason**: GPU model loading (one-time)
- **Subsequent queries**: ~6ms

**Batch similar questions**:
```
Instead of:
"Search RAG for React hooks"
"Search RAG for React state"
"Search RAG for React effects"

Try:
"Search RAG for React hooks, state management, and effects - give me comprehensive examples"
```

---

## 2.2 Direct MCP Tool Invocation

### Learning Outcome
Use precise tool calls for specific needs.

### When to Use Direct Calls

**Exact control over parameters**:
```
"Use query_knowledge_base with:
  query='Python async patterns'
  technology_filter='Python Docs'
  top_k=10"
```

**Scripting/automation via Claude**:
```
"For each framework in [React, Vue, Angular],
query the knowledge base for routing patterns
and create a comparison table"
```

**Testing specific filters**:
```
"Use list_technologies, then query each technology
for authentication patterns"
```

### Available MCP Tools

**Tool 1: query_knowledge_base**
```
Parameters:
  - query (required): "Your search query"
  - collection_name (optional): "coding_knowledge" (default)
  - top_k (optional): 5 (default), max 20
  - technology_filter (optional): "React Docs", "Python Docs", etc.

Returns:
  - query: Echo of your query
  - results: Array of ranked results
  - total_found: Count of results
```

**Tool 2: list_technologies**
```
Parameters: None

Returns:
  - total_technologies: 36
  - total_documents: 70,652
  - technologies: Array of {name, document_count}
```

**Tool 3: get_collection_stats**
```
Parameters:
  - collection_name (optional): "coding_knowledge"

Returns:
  - collection_name: "coding_knowledge"
  - document_count: 70,652
  - metadata: Collection metadata
```

### Direct Tool Call Examples

**Example 1: Basic query**:
```
"Use query_knowledge_base to search for 'React hooks'"
```

**Example 2: Filtered with custom limit**:
```
"Use query_knowledge_base with:
  query='async patterns'
  technology_filter='Python Docs'
  top_k=10"
```

**Example 3: List technologies**:
```
"Use list_technologies to show all available filters"
```

**Example 4: Get stats**:
```
"Use get_collection_stats to show database information"
```

### Hands-On Exercise 6

**Task**: Use direct tool calls to create a technology comparison.

**Step 1: List technologies**:
```
"Use list_technologies"
```

**Step 2: Query each framework**:
```
"Use query_knowledge_base to search for 'component lifecycle'
in React Docs, then Vue Docs, then Angular Docs"
```

**Step 3: Create comparison**:
```
"Based on those three queries, create a comparison table of
lifecycle methods across frameworks"
```

### Comparison: Natural vs Direct

| Aspect | Natural Language | Direct Tool Call |
|--------|-----------------|------------------|
| **Ease of use** | Easier, conversational | Requires exact syntax |
| **Control** | Claude decides parameters | You specify all parameters |
| **Use case** | Exploratory queries | Automation, specific needs |
| **Example** | "Search RAG for hooks" | "query_knowledge_base('hooks', top_k=10)" |

---

## 2.3 Python Scripts (Automation)

### Learning Outcome
Build automated workflows with RAG queries.

### Full Working Example - Batch Query Script

**File**: `/home/rebelsts/RAG/my_batch_queries.py`

```python
#!/usr/bin/env python3
"""
Batch RAG queries - automate multiple searches
"""
import chromadb
from sentence_transformers import SentenceTransformer
import torch
import time

# Setup
client = chromadb.HttpClient(host='localhost', port=8001)
collection = client.get_collection('coding_knowledge')

# Load model with GPU
model = SentenceTransformer('all-MiniLM-L6-v2')
if torch.cuda.is_available():
    model = model.to('cuda')
    print(f"GPU: {torch.cuda.get_device_name(0)}")
else:
    print("Using CPU (slower)")

# Query function
def query_rag(query_text, tech_filter=None, top_k=5):
    """Query RAG knowledge base"""
    embedding = model.encode([query_text]).tolist()

    where = {"technology": tech_filter} if tech_filter else None

    start = time.time()
    results = collection.query(
        query_embeddings=embedding,
        n_results=top_k,
        where=where
    )
    elapsed = (time.time() - start) * 1000

    return results, elapsed

# Batch queries
queries = [
    ("React hooks patterns", "React Docs"),
    ("Python async/await best practices", "Python Docs"),
    ("Docker multi-stage builds", "Docker Docs"),
    ("TypeScript generic constraints", "TypeScript Docs"),
    ("FastAPI dependency injection", "FastAPI Docs"),
]

print("\n" + "="*80)
print("BATCH RAG QUERIES")
print("="*80)

total_time = 0

for i, (query, tech) in enumerate(queries, 1):
    print(f"\n[{i}/{len(queries)}] Query: \"{query}\"")
    print(f"    Filter: {tech}")

    results, elapsed = query_rag(query, tech, top_k=3)
    total_time += elapsed

    print(f"    Latency: {elapsed:.2f}ms")
    print(f"    Results:")

    for j, (doc, meta, dist) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        similarity = 1 - dist
        print(f"      {j}. Similarity: {similarity:.4f}")
        print(f"         {doc[:80]}...")

print("\n" + "="*80)
print(f"Total queries: {len(queries)}")
print(f"Total time: {total_time:.2f}ms")
print(f"Average: {total_time/len(queries):.2f}ms per query")
print("="*80 + "\n")
```

**Run it**:
```bash
cd /home/rebelsts/RAG
chmod +x my_batch_queries.py
./.venv/bin/python my_batch_queries.py
```

**Expected output**:
```
GPU: AMD Radeon RX 7900 XTX
================================================================================
BATCH RAG QUERIES
================================================================================

[1/5] Query: "React hooks patterns"
    Filter: React Docs
    Latency: 2456.23ms  # First query (model loading)
    Results:
      1. Similarity: 0.8532
         Hooks are functions that let you "hook into" React state and lifecycle...

[2/5] Query: "Python async/await best practices"
    Filter: Python Docs
    Latency: 6.12ms  # Subsequent queries fast!
    Results:
      1. Similarity: 0.8201
         Async functions are defined with the async def syntax...

... (continues) ...

================================================================================
Total queries: 5
Total time: 2522.47ms
Average: 504.49ms per query (includes first query model load)
================================================================================
```

### Real-World Use Cases

**Use Case 1: Pre-populate knowledge for code generation**:
```python
# Gather comprehensive context before generating code
topics = [
    "React component structure",
    "React state management",
    "React API integration",
    "React error handling"
]

context = {}
for topic in topics:
    results, _ = query_rag(topic, "React Docs", top_k=3)
    context[topic] = results

# Now generate code with full context
# ... code generation logic ...
```

**Use Case 2: Build custom documentation search tool**:
```python
def search_docs(user_query):
    """Interactive documentation search"""
    # Auto-detect technology from query
    # Query RAG
    # Display formatted results
    # Allow drilling down into source files
```

**Use Case 3: Automated code review context gathering**:
```python
def get_review_context(file_path, tech_stack):
    """Gather best practices for code review"""
    # Read file
    # Identify patterns (async, hooks, etc.)
    # Query RAG for each pattern
    # Return review checklist
```

### Hands-On Exercise 7

**Task**: Create a custom query script for your most common searches.

**Step 1: Identify your top 5 queries**:
```
Example for web dev:
1. React component patterns
2. FastAPI route handlers
3. PostgreSQL query optimization
4. Docker compose configuration
5. TypeScript type safety
```

**Step 2: Modify the batch script**:
```python
queries = [
    # Your custom queries here
    ("your query 1", "Technology Filter 1"),
    ("your query 2", "Technology Filter 2"),
    # ...
]
```

**Step 3: Run daily**:
```bash
# Add to cron for daily context refresh
crontab -e
# Add: 0 9 * * * /home/rebelsts/RAG/.venv/bin/python /home/rebelsts/RAG/my_daily_refresh.py
```

### Performance Notes

**First query**: ~2s (model loading)
**Subsequent queries**: ~6ms each
**Batch advantage**: Load model once, query many times

**Optimization tip**:
```python
# Batch encode for faster processing
queries_text = ["query 1", "query 2", "query 3"]
embeddings = model.encode(queries_text)  # Single GPU call

for i, embedding in enumerate(embeddings):
    results = collection.query(
        query_embeddings=[embedding.tolist()],
        n_results=5
    )
    # Process results...
```

---

# PART 3: PRACTICAL SCENARIOS

## 3.1 Web Development Workflow

### Scenario
Building a full-stack application: React frontend + FastAPI backend + PostgreSQL database

### Step-by-Step with Expected Results

**Query 1: React form validation**

```
You: "Search the RAG for React form validation patterns"
```

**Expected results**:
- Rank 1: useState + validation hooks (similarity: 0.82)
- Rank 2: Form libraries (React Hook Form) (similarity: 0.78)
- Rank 3: Input validation patterns (similarity: 0.75)

**Use case**: Implement signup form with client-side validation

**Query 2: FastAPI request validation**

```
You: "Query knowledge base for FastAPI request validation with Pydantic, filter to FastAPI Docs"
```

**Expected results**:
- Rank 1: BaseModel schemas (similarity: 0.88)
- Rank 2: Validation decorators (similarity: 0.84)
- Rank 3: Custom validators (similarity: 0.80)

**Use case**: Create API endpoint with validated request body

**Query 3: PostgreSQL foreign keys**

```
You: "Search RAG for PostgreSQL foreign key constraints and cascading deletes"
```

**Expected results**:
- Rank 1: Foreign key syntax (similarity: 0.85)
- Rank 2: CASCADE options (similarity: 0.82)
- Rank 3: Referential integrity (similarity: 0.79)

**Use case**: Design database schema with proper relationships

**Query 4: Integration - API calls from React**

```
You: "Query knowledge base for React API fetch patterns and error handling"
```

**Expected results**:
- Rank 1: Fetch API usage (similarity: 0.83)
- Rank 2: Async/await in components (similarity: 0.81)
- Rank 3: Error boundaries (similarity: 0.77)

**Use case**: Connect frontend to backend API

### Integration Workflow

**Ask Claude to synthesize**:
```
"Based on the four queries above:
1. Create a React signup form component
2. Create the FastAPI /signup endpoint
3. Create the PostgreSQL users table
4. Show how they connect together"
```

**Result**: Full-stack implementation grounded in official documentation from React Docs, FastAPI Docs, and PostgreSQL Docs.

### Hands-On Exercise 8

**Your turn**: Build a todo app using only RAG-retrieved knowledge.

**Queries needed**:
1. "React state management for todo list"
2. "FastAPI CRUD endpoints"
3. "PostgreSQL array columns for todo items"
4. "React form submission handling"

**Expected queries**: 10-15 total
**Average similarity**: 0.70-0.85 for focused queries
**Time**: 30-45 minutes

**Deliverable**: Working todo app with proper patterns from official docs.

---

## 3.2 Learning New Technology

### Scenario
You're new to Rust and need to understand ownership, a core concept.

### Progressive Query Strategy

**Stage 1: Broad Exploratory Query**

```
Query: "Rust ownership basics"
Filter: None (explore all Rust resources)
Top K: 10-15
```

**Purpose**: Survey the landscape, understand scope

**Expected results**:
- Multiple chunks from Rust Book
- Code examples
- Conceptual explanations

**Action**: Scan similarity scores to identify core concepts

**Stage 2: Focused Conceptual Query**

```
Query: "Rust borrow checker rules and lifetime annotations"
Filter: "Rust Book"
Top K: 5
```

**Purpose**: Deep dive into specific mechanism

**Expected results**:
- Higher similarity scores (0.85+)
- Detailed technical explanations
- Compiler error examples

**Action**: Read thoroughly, take notes

**Stage 3: Practical Examples**

```
Query: "Rust ownership code examples with common patterns"
Filter: "Rust Book"
Top K: 5
```

**Purpose**: See theory in practice

**Expected results**:
- Working code snippets
- Best practice patterns
- Anti-patterns to avoid

**Action**: Try code in your editor

**Stage 4: Pitfalls & Debugging**

```
Query: "common Rust ownership mistakes and how to fix them"
Filter: None
Top K: 10
```

**Purpose**: Learn from common errors

**Expected results**:
- Error messages and solutions
- Debugging strategies
- Real-world gotchas

**Action**: Build mental model of what to avoid

### Learning Path Visualization

```
Broad (10-15 results)
  ↓ Identify core concepts
Focused (5 results)
  ↓ Deep understanding
Examples (5 results)
  ↓ Practice
Pitfalls (10 results)
  ↓ Debugging skills
```

### Hands-On Exercise 9

**Task**: Learn a technology unfamiliar to you.

**Pick one**:
- Flutter (if you haven't done mobile dev)
- Go (if you're primarily Python/JS)
- Wireshark (if you haven't done network analysis)

**Follow the 4-stage query strategy**:
1. Broad exploratory (15 results)
2. Focused conceptual (5 results)
3. Practical examples (5 results)
4. Common mistakes (10 results)

**Track**:
- How similarity scores change across stages
- Which queries were most helpful
- How your understanding deepened

**Expected outcome**: Basic competency in new technology within 1-2 hours.

---

## 3.3 Debugging & Troubleshooting

### Scenario
Docker container can't connect to PostgreSQL database.

### Debugging Query Workflow

**Query 1: General issue space**

```
Query: "Docker networking containers can't communicate"
```

**Expected results**:
- Bridge network explanations
- Common connectivity issues
- Troubleshooting steps

**Action**: Understand the problem domain

**Query 2: Specific mechanism**

```
Query: "Docker compose service discovery and DNS resolution"
```

**Expected results**:
- Service name resolution
- Network configuration in docker-compose.yml
- DNS settings

**Action**: Identify likely cause

**Query 3: Technology-specific config**

```
Query: "PostgreSQL Docker connection refused errors"
```

**Expected results**:
- Bind address configuration
- Port mapping issues
- Authentication settings

**Action**: Apply specific fix

### Real Example Walkthrough

**Problem**: React app in Docker can't reach FastAPI backend

**Query 1**:
```
"Search RAG for Docker compose network configuration between services"
```

**Result**: Learn about custom networks and service discovery

**Action**: Create custom network in docker-compose.yml
```yaml
networks:
  app-network:
    driver: bridge
```

**Query 2**:
```
"Query knowledge base for environment variables in React for API endpoints"
```

**Result**: Learn about `.env` files and `REACT_APP_` prefix

**Action**: Set `REACT_APP_API_URL=http://backend:8000`

**Query 3**:
```
"Search RAG for CORS configuration in FastAPI"
```

**Result**: Learn about CORSMiddleware setup

**Action**: Add CORS middleware to FastAPI
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Outcome**: Problem solved using patterns from official docs.

### Hands-On Exercise 10

**Task**: Debug a simulated error using RAG.

**Scenario**: "TypeError: Cannot read property 'map' of undefined in React component"

**Your debugging queries**:
1. Query for React TypeError handling
2. Query for React state initialization
3. Query for React conditional rendering
4. Query for React error boundaries

**Expected**: Find multiple solutions, choose best one.

---

## 3.4 Code Review & Best Practices

### Scenario
Reviewing teammate's Python async code for best practices.

**Code to review**:
```python
async def fetch_users():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://api/users') as response:
            return await response.json()
```

### Review Query Workflow

**Query 1: Context manager best practices**

```
"Search RAG for Python async context managers best practices"
```

**Findings**:
✓ Proper session handling - code is correct
✓ Resource cleanup automatic - good

**Query 2: Error handling**

```
"Query knowledge base for aiohttp error handling patterns"
```

**Findings**:
❌ Missing try/except
❌ No timeout configured
❌ No status code checking

**Suggested improvements**:
```python
async def fetch_users():
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        try:
            async with session.get('http://api/users') as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Failed to fetch users: {e}")
            raise
```

**Query 3: Type annotations**

```
"Search RAG for Python async function typing and return types"
```

**Findings**:
❌ Missing return type hint
❌ No parameter types

**Suggested improvements**:
```python
from typing import List, Dict, Any

async def fetch_users() -> List[Dict[str, Any]]:
    ...
```

### Hands-On Exercise 11

**Task**: Review this React code using RAG.

```javascript
function UserList() {
  const [users, setUsers] = useState();

  useEffect(() => {
    fetch('/api/users')
      .then(res => res.json())
      .then(data => setUsers(data));
  }, []);

  return (
    <div>
      {users.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
    </div>
  );
}
```

**Your review queries**:
1. "React useState initialization best practices"
2. "React useEffect cleanup functions"
3. "React fetch error handling patterns"
4. "React conditional rendering"

**Expected findings**:
- Missing error handling
- No loading state
- useState should initialize to []
- Missing cleanup in useEffect

---

## 3.5 Multi-Technology Integration

### Scenario
Integrating Stripe payments into Next.js app with Supabase database.

**Tech stack**: Next.js + Stripe + Supabase

### Cross-Technology Query Pattern

**Query 1: Next.js API routes**

```
Query: "Next.js API routes server-side request handling"
Filter: "Next.js Docs (Vercel)"
```

**Goal**: Understand API route structure for webhook endpoint

**Query 2: Stripe webhook verification**

```
Query: "Stripe webhook signature verification security"
Filter: "Stripe Docs"
```

**Goal**: Implement secure webhook handling

**Query 3: Supabase transaction insertion**

```
Query: "Supabase insert with transaction handling"
Filter: "Supabase Docs"
```

**Goal**: Store payment records atomically

**Query 4: Error handling (cross-cutting)**

```
Query: "error handling async JavaScript API routes"
Filter: None (general pattern)
```

**Goal**: Robust error handling across entire stack

### Integration Architecture

**Ask Claude to synthesize**:
```
"Based on the 4 queries above, create a complete Stripe payment flow:
1. Next.js checkout page
2. API route to create payment intent
3. Webhook endpoint to handle payment success
4. Supabase database update on successful payment"
```

**Result**: End-to-end integration with patterns from 3 different official documentation sources.

### Hands-On Exercise 12

**Task**: Design a 3-technology integration of your choice.

**Example combinations**:
- React + Firebase + Figma API
- Flutter + Supabase + Stripe
- Next.js + PostgreSQL + SendGrid

**Process**:
1. Query each technology separately
2. Identify integration points
3. Query for cross-cutting concerns (auth, errors, etc.)
4. Synthesize into unified architecture

**Expected**: 8-12 queries, comprehensive integration design.

---

# PART 4: ADVANCED TECHNIQUES

## 4.1 Query Optimization

### Learning Outcome
Craft queries for maximum relevance and accuracy.

### Before/After Examples

**❌ Poor Query #1**: "react"
- **Problem**: Too vague, lacks context
- **Similarity scores**: 0.40-0.60 (low)
- **Results**: Mixed quality

**✅ Better Query**: "React custom hooks with TypeScript for state management"
- **Specificity**: Technology + feature + use case
- **Similarity scores**: 0.75-0.85 (high)
- **Results**: Targeted, relevant

---

**❌ Poor Query #2**: "error"
- **Problem**: Too generic
- **Results**: Errors from all technologies mixed

**✅ Better Query**: "FastAPI exception handling middleware patterns"
- **Specificity**: Framework + concept + implementation type
- **Results**: FastAPI-specific error handling

---

**❌ Poor Query #3**: "database"
- **Problem**: Ambiguous - which database? What aspect?

**✅ Better Query**: "PostgreSQL connection pooling with SQLAlchemy in production"
- **Specificity**: Database + feature + library + context
- **Results**: Production-ready patterns

### Query Crafting Patterns

**Pattern 1: Technology + Concept + Modifier**
```
"FastAPI dependency injection with database sessions"
"React hooks cleanup functions for subscriptions"
"Docker multi-stage builds for Python applications"
```

**Pattern 2: Problem-Oriented**
```
"How to prevent memory leaks in React useEffect"
"How to avoid N+1 queries in GraphQL resolvers"
"How to handle connection timeouts in aiohttp"
```

**Pattern 3: Code Structure**
```
"Python async function error handling patterns"
"TypeScript generic type constraints with extends"
"React component composition with children props"
```

**Pattern 4: Comparison Queries**
```
"React useState vs useReducer for complex state"
"Docker volumes vs bind mounts for persistence"
"PostgreSQL JSONB vs separate table for metadata"
```

### A/B Testing Queries

**Exercise**: Test these query pairs and compare results.

| Query A (Poor) | Query B (Better) | Expected Winner |
|----------------|------------------|-----------------|
| "docker" | "Docker multi-stage build optimization for Node.js" | B (specific) |
| "hooks" | "React hooks cleanup functions and dependency arrays" | B (detailed) |
| "auth" | "JWT authentication FastAPI middleware with refresh tokens" | B (comprehensive) |
| "typing" | "TypeScript utility types for React component props" | B (targeted) |

**Your task**: Run both queries, compare top 3 similarity scores.

```python
# Quick comparison script
queries_to_test = [
    ("docker", "Docker multi-stage build optimization for Node.js"),
    ("hooks", "React hooks cleanup functions and dependency arrays"),
    # ... add more
]

for poor, better in queries_to_test:
    print(f"\nTesting: '{poor}' vs '{better}'")

    results_poor = query_rag(poor, top_k=3)
    results_better = query_rag(better, top_k=3)

    avg_poor = sum(1 - d for d in results_poor[0]['distances'][0]) / 3
    avg_better = sum(1 - d for d in results_better[0]['distances'][0]) / 3

    print(f"Poor query avg similarity: {avg_poor:.4f}")
    print(f"Better query avg similarity: {avg_better:.4f}")
    print(f"Improvement: {((avg_better - avg_poor) / avg_poor * 100):.1f}%")
```

**Expected improvements**: 15-40% higher similarity scores with better queries.

### Similarity Score Interpretation Guide

**Actionable thresholds**:

**0.85+ (Excellent)**:
- Use directly in code generation
- High confidence in accuracy
- Official documentation match

**0.70-0.85 (Good)**:
- Review before implementing
- Generally accurate
- May need minor adjustments

**0.50-0.70 (Moderate)**:
- Use with caution
- Verify with external sources
- Good for ideation, not production

**<0.50 (Weak)**:
- Rephrase query
- Add more context
- Check if topic is in knowledge base

---

## 4.2 Result Filtering & Post-Processing

### Learning Outcome
Programmatically filter and rank results beyond basic queries.

### Custom Filtering Script

```python
#!/usr/bin/env python3
"""
Advanced result filtering and post-processing
"""
import chromadb
from sentence_transformers import SentenceTransformer
import torch
from collections import defaultdict

client = chromadb.HttpClient(host='localhost', port=8001)
collection = client.get_collection('coding_knowledge')

model = SentenceTransformer('all-MiniLM-L6-v2')
if torch.cuda.is_available():
    model = model.to('cuda')

def filter_by_similarity(results, threshold=0.7):
    """Only keep results above similarity threshold"""
    filtered = []

    for doc, meta, dist in zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ):
        similarity = 1 - dist
        if similarity >= threshold:
            filtered.append({
                'content': doc,
                'technology': meta.get('technology'),
                'source_file': meta.get('source_file'),
                'similarity': similarity
            })

    return filtered

def group_by_technology(results):
    """Group results by technology tag"""
    groups = defaultdict(list)

    for doc, meta, dist in zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ):
        tech = meta.get('technology', 'Unknown')
        groups[tech].append({
            'content': doc,
            'similarity': 1 - dist,
            'source_file': meta.get('source_file')
        })

    # Sort each group by similarity
    for tech in groups:
        groups[tech].sort(key=lambda x: x['similarity'], reverse=True)

    return dict(groups)

def deduplicate_by_source(results):
    """Remove duplicate chunks from same source file"""
    seen_files = set()
    deduplicated = []

    for doc, meta, dist in zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ):
        source_file = meta.get('source_file')

        # Keep first occurrence (highest ranked) from each file
        if source_file not in seen_files:
            seen_files.add(source_file)
            deduplicated.append({
                'content': doc,
                'technology': meta.get('technology'),
                'source_file': source_file,
                'similarity': 1 - dist
            })

    return deduplicated

# Example usage
query = "authentication patterns"
embedding = model.encode([query]).tolist()

results = collection.query(
    query_embeddings=embedding,
    n_results=20  # Get more for filtering
)

# Filter: Only high-quality results
high_quality = filter_by_similarity(results, threshold=0.65)
print(f"High quality results (>0.65): {len(high_quality)}")

# Group by technology
by_tech = group_by_technology(results)
print(f"\nResults by technology:")
for tech, items in by_tech.items():
    print(f"  {tech}: {len(items)} results")

# Deduplicate by source file
unique_sources = deduplicate_by_source(results)
print(f"\nUnique source files: {len(unique_sources)}")
```

### Use Cases for Advanced Filtering

**Use Case 1: Quality Control**
```python
# Only use results above confidence threshold for code generation
production_ready = filter_by_similarity(results, threshold=0.80)
```

**Use Case 2: Technology Comparison**
```python
# Compare which technology has best docs on a topic
query = "state management patterns"
results = collection.query(query_embeddings=embedding, n_results=30)
by_tech = group_by_technology(results)

# Which has most documentation?
for tech, items in sorted(by_tech.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"{tech}: {len(items)} relevant docs")
```

**Use Case 3: Aggregation**
```python
# Combine multiple chunks from same source file
def aggregate_by_source(results):
    """Combine chunks from same file for full context"""
    by_file = defaultdict(list)

    for doc, meta, dist in zip(...):
        source_file = meta.get('source_file')
        by_file[source_file].append({
            'content': doc,
            'similarity': 1 - dist
        })

    # For each file, concatenate chunks in order
    aggregated = []
    for file, chunks in by_file.items():
        combined_content = ' '.join(c['content'] for c in chunks)
        avg_similarity = sum(c['similarity'] for c in chunks) / len(chunks)

        aggregated.append({
            'source_file': file,
            'content': combined_content,
            'chunk_count': len(chunks),
            'avg_similarity': avg_similarity
        })

    return sorted(aggregated, key=lambda x: x['avg_similarity'], reverse=True)
```

### Hands-On Exercise 13

**Task**: Analyze authentication documentation across all technologies.

**Steps**:
```python
# 1. Query broadly
query = "authentication and authorization patterns"
results = collection.query(
    query_embeddings=embedding,
    n_results=50
)

# 2. Filter by quality
quality_results = filter_by_similarity(results, threshold=0.70)

# 3. Group by technology
by_tech = group_by_technology(results)

# 4. Analysis
print("Authentication coverage by technology:")
for tech, items in sorted(by_tech.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
    avg_sim = sum(i['similarity'] for i in items) / len(items)
    print(f"{tech:30} {len(items):3} docs (avg similarity: {avg_sim:.3f})")
```

**Expected insights**:
- Which technologies have best auth documentation?
- Which patterns appear across multiple frameworks?
- Which technologies need more auth examples in your knowledge base?

---

## 4.3 Combining RAG with Other MCP Tools

### Learning Outcome
Orchestrate RAG with GitHub, web search, and other MCPs for comprehensive workflows.

### Workflow Pattern 1: RAG + GitHub MCP

**Use case**: Review PR for React best practices using RAG context.

```
User: "Review GitHub PR #123 for React best practices"

Workflow:
1. GitHub MCP: Fetch PR files and diff
2. RAG: Query "React component best practices"
3. RAG: Query "React hooks rules and patterns"
4. RAG: Query "React performance optimization"
5. Synthesize: Compare PR code against RAG-retrieved best practices
6. GitHub MCP: Post review comments with RAG citations
```

**Example**:
```
Step 1 (GitHub): Get PR files
  - components/UserList.jsx (modified)
  - components/UserDetail.jsx (new)

Step 2 (RAG): Query best practices
  - "React component composition patterns"
  - Results: Official React Docs on component structure

Step 3 (Analysis): Compare PR against RAG results
  - PR uses class components (outdated)
  - RAG recommends function components with hooks (current)

Step 4 (GitHub): Post review
  - "Consider migrating to function components. According to React Docs (source: react.dev/learn/your-first-component), function components with hooks are the recommended approach since React 16.8."
```

### Workflow Pattern 2: RAG + Brave Search (Hybrid)

**Use case**: Get current best practices (RAG = stable patterns, Web = latest trends).

```
User: "What's the current best practice for Next.js authentication in 2025?"

Workflow:
1. Brave Search: "Next.js 15 authentication 2025 best practices"
   → Current trends, recent blog posts

2. RAG: Query "Next.js authentication patterns"
   → Stable patterns from official Next.js docs

3. Synthesize:
   - Web search: "Next.js 15 introduced server actions for auth"
   - RAG docs: "Official middleware-based auth patterns"
   - Combined: Latest features + stable foundation
```

**Why hybrid approach?**:
- RAG: Official documentation (trustworthy but may be older)
- Web Search: Latest updates and trends (current but varying quality)
- Together: Best of both worlds

### Workflow Pattern 3: RAG + Playwright (Test Generation)

**Use case**: Generate tests using RAG patterns and run with Playwright.

```
User: "Generate and run tests for this React component using testing best practices"

Workflow:
1. RAG: Query "React testing library best practices"
   → Testing patterns from official docs

2. RAG: Query "React component testing with Jest"
   → Test structure and assertions

3. Generate: Create test file based on RAG patterns
4. Playwright MCP: Run tests
5. If failures: Query RAG for debugging patterns
```

### Orchestration Principles

**Principle 1: RAG provides factual grounding**
```
RAG → Official documentation, stable patterns
Other MCPs → Real-time data, actions
```

**Principle 2: Sequential vs. Parallel**
```
Sequential: When results depend on each other
  GitHub get PR → RAG query based on files → GitHub post review

Parallel: When independent
  RAG query React patterns + RAG query Vue patterns → Compare
```

**Principle 3: Citation and Traceability**
```
Always cite RAG sources in outputs:
"According to FastAPI Docs (source: fastapi.tiangolo.com/tutorial/dependencies/),
dependency injection should..."
```

### Hands-On Exercise 14

**Task**: Build a multi-MCP workflow for a real scenario.

**Scenario**: "Research Docker security best practices, audit my docker-compose.yml, and create a security report."

**Your workflow design**:
```
1. RAG: Query "Docker security best practices"
2. RAG: Query "Docker secrets management"
3. RAG: Query "Docker network security"
4. (Read tool): Read local docker-compose.yml
5. Analysis: Compare file against RAG best practices
6. (Write tool): Generate security_audit_report.md
7. (Optional) GitHub MCP: Create PR with improvements
```

**Implementation**:
```
"Use the following workflow:
1. Query RAG for Docker security best practices (top 10 results)
2. Read my docker-compose.yml file
3. Compare the file against the best practices you found
4. Create a detailed security audit report
5. Suggest specific improvements with citations from RAG"
```

---

## 4.4 Performance Monitoring & Benchmarking

### Learning Outcome
Measure and optimize query performance.

### Running Built-in Benchmarks

```bash
cd /home/rebelsts/RAG
./.venv/bin/python benchmark_gpu.py
```

**Expected output**:
```
GPU-Accelerated RAG Benchmark
==============================

GPU: AMD Radeon RX 7900 XTX

Embedding Generation:
  CPU:     746.6ms
  GPU:       2.5ms
  Speedup: 301.38x faster

Full RAG Query (Embed + Search):
  CPU:     421.4ms
  GPU:       6.2ms
  Speedup: 67.91x faster

Throughput:
  Queries per second: 161.29
```

### Custom Benchmark Script

```python
#!/usr/bin/env python3
"""
Custom RAG performance benchmark
"""
import chromadb
from sentence_transformers import SentenceTransformer
import torch
import time
import statistics

client = chromadb.HttpClient(host='localhost', port=8001)
collection = client.get_collection('coding_knowledge')

model = SentenceTransformer('all-MiniLM-L6-v2')
if torch.cuda.is_available():
    model = model.to('cuda')

# Test queries (diverse)
queries = [
    "React hooks state management",
    "Python async await patterns",
    "Docker networking configuration",
    "TypeScript generic constraints",
    "FastAPI dependency injection",
    "PostgreSQL query optimization",
    "Next.js server components",
    "Vue composition API",
    "Rust ownership rules",
    "GraphQL resolver patterns",
]

print("RAG Performance Benchmark")
print("=" * 60)

# Warm-up query (model loading)
print("Warming up (loading model)...")
_ = model.encode(["warmup query"])
print("Model loaded.\n")

# Benchmark
latencies = []

for i, query in enumerate(queries, 1):
    start = time.time()

    embedding = model.encode([query])
    results = collection.query(
        query_embeddings=embedding.tolist(),
        n_results=5
    )

    elapsed = (time.time() - start) * 1000  # Convert to ms
    latencies.append(elapsed)

    print(f"Query {i:2d}: {elapsed:6.2f}ms - {query}")

print("\n" + "=" * 60)
print("Statistics:")
print(f"  Minimum:  {min(latencies):.2f}ms")
print(f"  Maximum:  {max(latencies):.2f}ms")
print(f"  Average:  {statistics.mean(latencies):.2f}ms")
print(f"  Median:   {statistics.median(latencies):.2f}ms")
print(f"  Std Dev:  {statistics.stdev(latencies):.2f}ms")
print(f"\nThroughput: {1000 / statistics.mean(latencies):.2f} queries/second")
print("=" * 60)
```

**Run it**:
```bash
./.venv/bin/python custom_benchmark.py
```

**Expected output**:
```
RAG Performance Benchmark
============================================================
Warming up (loading model)...
Model loaded.

Query  1:   6.23ms - React hooks state management
Query  2:   5.87ms - Python async await patterns
Query  3:   6.45ms - Docker networking configuration
Query  4:   5.92ms - TypeScript generic constraints
Query  5:   6.18ms - FastAPI dependency injection
Query  6:   6.32ms - PostgreSQL query optimization
Query  7:   6.01ms - Next.js server components
Query  8:   5.95ms - Vue composition API
Query  9:   6.28ms - Rust ownership rules
Query 10:   6.15ms - GraphQL resolver patterns

============================================================
Statistics:
  Minimum:  5.87ms
  Maximum:  6.45ms
  Average:  6.14ms
  Median:   6.17ms
  Std Dev:  0.19ms

Throughput: 162.87 queries/second
============================================================
```

### Performance Optimization Tips

**Tip 1: Batch encoding**
```python
# Slower (separate GPU calls)
for query in queries:
    embedding = model.encode([query])

# Faster (single GPU call)
embeddings = model.encode(queries)  # All at once
for embedding in embeddings:
    # Use pre-computed embedding
```

**Tip 2: Connection pooling (already done)**
```python
# Reuse client connection
client = chromadb.HttpClient(host='localhost', port=8001)

# Don't recreate client for each query
for query in queries:
    results = client.query(...)  # Same client
```

**Tip 3: Cache frequently used embeddings**
```python
# Simple in-memory cache
embedding_cache = {}

def get_cached_embedding(query_text):
    if query_text not in embedding_cache:
        embedding_cache[query_text] = model.encode([query_text])
    return embedding_cache[query_text]
```

### Hands-On Exercise 15

**Task**: Benchmark your most common queries and optimize.

**Step 1: Identify your top 10 queries** (from your usage)

**Step 2: Run baseline benchmark**
```python
# Use custom_benchmark.py with your queries
```

**Step 3: Implement optimizations**
- Batch encode if querying multiple at once
- Cache common query embeddings
- Use technology filters (reduces search space)

**Step 4: Re-benchmark and measure improvement**

**Expected gains**:
- Batch encoding: 10-20% faster for multiple queries
- Caching: 100% faster for repeated queries (near-instant)
- Technology filters: 5-15% faster per query

---

# PART 5: TROUBLESHOOTING & TIPS

## 5.1 Common Issues & Solutions

### Issue 1: No Results Found

**Symptom**:
```
Query: "React hooks with classes"
Result: "No relevant documents found" or empty results
```

**Diagnosis**:
```bash
# Check if technology filter is correct
claude
"Use list_technologies to show all filters"

# Verify exact name
# ❌ "react hooks" (wrong - lowercase)
# ✅ "React Docs" (correct - exact match)
```

**Solutions**:

**Solution 1: Fix filter spelling**
```
# Wrong
"Query RAG for hooks, filter to react docs"

# Correct
"Query RAG for hooks, filter to React Docs"
```

**Solution 2: Broaden query**
```
# Too specific (might return nothing)
"React 18.3 concurrent rendering with Suspense boundaries"

# Better (broader)
"React concurrent rendering and Suspense"
```

**Solution 3: Remove filter**
```
# If filtered query returns nothing, try without filter
"Query RAG for hooks"  # No filter, search all technologies
```

**Solution 4: Verify database**
```python
import chromadb

client = chromadb.HttpClient(host='localhost', port=8001)
collection = client.get_collection('coding_knowledge')

print(f"Documents in collection: {collection.count()}")
# Should be: 70,652

# Check if technology exists
sample = collection.get(limit=100, include=['metadatas'])
technologies = set(m.get('technology') for m in sample['metadatas'])
print(f"Sample technologies: {technologies}")
```

---

### Issue 2: Low Similarity Scores

**Symptom**:
```
Query: "coding"
Results: All similarities <0.50
```

**Root Causes**:
1. Query too generic
2. Terminology mismatch
3. Topic not in knowledge base

**Solutions**:

**Solution 1: Add specificity**
```
# Generic (low scores)
"coding" → Similarity: 0.42

# Specific (high scores)
"Python decorators for function caching" → Similarity: 0.82
```

**Solution 2: Use technical terms**
```
# Vague
"making things run at the same time"

# Technical
"Python asyncio concurrent task execution"
```

**Solution 3: Check available technologies**
```
"Use list_technologies"

# If your topic isn't listed, it's not in the knowledge base
# Example: If "Ruby Docs" isn't listed, Ruby queries will have low scores
```

---

### Issue 3: Slow Queries (>50ms)

**Symptom**:
```
Query latency: 100-500ms (should be ~6ms)
```

**Diagnosis**:

**Step 1: Check GPU**
```python
import torch

print(f"GPU available: {torch.cuda.is_available()}")
# Should be: True

if torch.cuda.is_available():
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
    # Should be: AMD Radeon RX 7900 XTX
```

**Step 2: Check temperature**
```bash
rocm-smi

# Temperature should be <80°C
# If >80°C, GPU may be thermal throttling
```

**Step 3: Check first query vs subsequent**
```python
import time

# First query (includes model loading)
start = time.time()
results1 = query_rag("test query 1")
first_query_time = (time.time() - start) * 1000

# Second query (model already loaded)
start = time.time()
results2 = query_rag("test query 2")
second_query_time = (time.time() - start) * 1000

print(f"First query:  {first_query_time:.2f}ms")  # ~2000ms
print(f"Second query: {second_query_time:.2f}ms")  # ~6ms
```

**Solutions**:

**If GPU not detected**:
```bash
# Reinstall PyTorch with ROCm support
cd /home/rebelsts/RAG
./.venv/bin/pip install torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/rocm6.2
```

**If thermal throttling**:
```bash
# Check GPU fans
rocm-smi --showfan

# Improve cooling or reduce GPU load
```

**If first query slow but subsequent fast**:
```
This is normal! Model loading takes ~2s
Subsequent queries are ~6ms
```

---

### Issue 4: Obsolete Config File Confusion

**Symptom**:
```
MCP server not showing in `claude mcp list` from certain directories
```

**Diagnosis**:
```bash
# Check if old config file exists
ls ~/.config/claude-code/mcp_servers.json

# Check correct location
cat ~/.claude.json | jq '.mcpServers'
```

**Solution**:
```bash
# Remove or rename obsolete file
mv ~/.config/claude-code/mcp_servers.json \
   ~/.config/claude-code/mcp_servers.json.obsolete

# Verify correct location has RAG server
cat ~/.claude.json | jq '.mcpServers."rag-knowledge-base"'
```

**Prevention**:
- Always use `~/.claude.json` for MCP servers
- Document obsolete files with README

---

## 5.2 Pro Tips & Best Practices

### Query Design Tips

✅ **DO**:
- Use specific technical terminology
  ```
  "FastAPI dependency injection with database session management"
  ```

- Include context (language, framework, use case)
  ```
  "React hooks for fetching data with TypeScript"
  ```

- Combine concepts for focused results
  ```
  "Docker multi-stage builds for optimizing Python Flask applications"
  ```

- Start broad, then narrow with filters
  ```
  Step 1: "state management patterns" (no filter, survey)
  Step 2: "state management" filter="React Docs" (focused)
  ```

❌ **DON'T**:
- Single-word queries
  ```
  "react" ← Too vague
  ```

- Assume exact keyword matching
  ```
  RAG uses semantic search, not grep
  Query for concepts, not exact strings
  ```

- Ignore similarity scores
  ```
  If all scores <0.65, rephrase your query
  ```

- Query for non-technical content
  ```
  RAG contains code/docs only
  No general knowledge, news, or opinions
  ```

### Workflow Best Practices

**1. Exploratory Phase**:
```
- No filters
- top_k=10-15
- Broad queries
- Scan for core concepts
```

**2. Focused Phase**:
```
- Use technology filters
- top_k=5
- Specific queries
- Deep dive into results
```

**3. Validation Phase**:
```
- Cross-reference multiple results
- Check similarity scores (>0.70)
- Read full source files when needed
```

**4. Synthesis Phase**:
```
- Combine RAG results with other sources
- Generate code based on patterns
- Cite sources in comments
```

### Result Interpretation

**High Confidence (>0.80)**:
```
✅ Use directly in code generation
✅ Trust for production implementations
✅ Official documentation match
```

**Medium Confidence (0.65-0.80)**:
```
⚠️ Review before implementing
⚠️ Generally accurate, may need adjustments
⚠️ Good foundation, verify edge cases
```

**Low Confidence (<0.65)**:
```
❌ Use as inspiration only
❌ Verify with external authoritative sources
❌ Consider rephrasing query
```

### Technology Filter Strategy

| Scenario | Filter Strategy |
|----------|-----------------|
| **Single-tech project** | Always filter (faster, focused) |
| **Multi-tech integration** | Query each tech separately, then combine |
| **Learning new topic** | Start unfiltered (survey), then filter (focus) |
| **Cross-cutting concern** | Unfiltered (errors, patterns apply to all) |
| **Best practice research** | Filter to specific framework first |
| **Comparison** | Query each tech with same query, compare |

### Hands-On Exercise 16

**Task**: Apply all best practices to a real query scenario.

**Scenario**: "You're implementing authentication for a new React + FastAPI app."

**Step 1: Exploratory (unfiltered, broad)**
```
"Query RAG for authentication and authorization patterns, top 15 results"
```

**Step 2: Focused (filtered, specific)**
```
"Query RAG for JWT authentication implementation, filter React Docs, top 5"
"Query RAG for FastAPI OAuth2 with JWT tokens, filter FastAPI Docs, top 5"
```

**Step 3: Validation (cross-reference)**
```
"Query RAG for authentication security best practices, no filter, top 10"
```

**Step 4: Synthesis**
```
"Based on the queries above, design a complete authentication flow:
1. React login form
2. FastAPI JWT endpoint
3. Token refresh mechanism
4. Protected routes
Include citations from RAG results"
```

**Expected outcome**:
- Comprehensive auth implementation
- Grounded in official React and FastAPI docs
- Security best practices applied
- All patterns cited with sources

---

# APPENDICES

## Appendix A: Quick Reference Card

### Common Commands

```bash
# List MCP servers
claude mcp list

# Start Claude Code (from any directory)
claude

# Test MCP server
cd /home/rebelsts/RAG
./.venv/bin/python test_mcp_server.py

# Run benchmarks
./.venv/bin/python benchmark_gpu.py
```

### Query Patterns

**Natural language**:
```
"Search the RAG for [topic]"
"Query the knowledge base for [topic]"
"Use the coding knowledge tool to find [topic]"
```

**Direct tool call**:
```
"Use query_knowledge_base with query='[topic]' and technology_filter='[Tech Docs]'"
"Use list_technologies"
"Use get_collection_stats"
```

### Typical Workflow

```
1. List technologies → Know available filters
2. Broad query (top_k=10) → Survey landscape
3. Filtered query (top_k=5) → Focus on specifics
4. Synthesize results → Generate code/solution
```

### Similarity Score Guide

```
0.85+        Excellent   → Use directly
0.70-0.85    Good        → Review first
0.50-0.70    Fair        → Use with caution
<0.50        Poor        → Rephrase query
```

### Performance Expectations

```
First query:      ~2000ms (model loading)
Subsequent:       ~6ms (GPU-accelerated)
Throughput:       160+ queries/second
Cache hit (future): <1ms
```

---

## Appendix B: Technology Filter Cheat Sheet

### Web Development (11)
```
React Docs
Next.js Docs (Vercel)
Vue Docs
Angular Docs
TypeScript Docs
MDN HTML Docs
MDN Web Dev Guide
Eloquent JavaScript Book
The Odin Project
```

### Backend/API (6)
```
FastAPI Docs
Python Docs
Node.js Docs
Express Docs
Rust Book
Java SE Tutorials
```

### AI/ML (8)
```
LangChain Docs
Anthropic Docs
OpenAI Docs
Google Gemini Docs
ComfyUI Repo
Stability AI Docs (SD/SDXL)
```

### Databases (4)
```
PostgreSQL Docs
MongoDB Docs
Redis Docs
Supabase Docs
Firebase Docs
```

### Mobile (2)
```
Flutter Docs
Flutter Samples
```

### Security (6)
```
Kali Linux Docs
Kali Linux Tools List
Wireshark User's Guide
Ghidra Book
Radare2 Book
Reverse Engineering for Beginners Book
```

### DevOps & Infrastructure (3)
```
Docker Docs
DigitalOcean Hosting Docs
```

### Business/Automation (3)
```
Stripe Docs
HubSpot API Docs
n8n Docs
```

### Design (5)
```
Figma API Docs
GIMP Docs
DTF Printing Guide
Wikipedia - Raster Graphics
Wikipedia - Halftone
```

### Other (3)
```
Refactoring Guru Design Patterns
cppreference.com C++
cppreference.com C
```

**Total**: 36 technologies

---

## Appendix C: Example Query Library

### Learning Queries

**Beginner level**:
```
"React component basics and JSX syntax"
"Python functions and parameters"
"Docker getting started tutorial"
```

**Intermediate level**:
```
"React custom hooks with dependency arrays"
"Python decorators and metaclasses"
"Docker networking and volume management"
```

**Advanced level**:
```
"React performance optimization with memoization"
"Python async context managers and generators"
"Docker security hardening and secrets management"
```

### Debugging Queries

```
"TypeScript type inference errors and solutions"
"PostgreSQL deadlock detection and prevention"
"React infinite render loop causes"
"FastAPI async database session management"
"Docker container networking troubleshooting"
```

### Integration Queries

```
"FastAPI CORS middleware configuration"
"Supabase realtime subscriptions with React"
"Next.js API routes with authentication"
"Stripe webhook signature verification"
"Docker compose multi-container orchestration"
```

### Best Practice Queries

```
"Python error handling with async functions"
"React hooks naming conventions and rules"
"Docker security best practices"
"FastAPI dependency injection patterns"
"PostgreSQL query optimization techniques"
```

### Comparison Queries

```
"React useState vs useReducer comparison"
"Docker volumes vs bind mounts"
"PostgreSQL JSONB vs separate tables"
"Python asyncio vs threading"
"Next.js SSR vs SSG vs ISR"
```

---

## Completion Certificate

🎉 **Congratulations!**

You've completed the RAG Knowledge Base Hands-On Tutorial.

**Skills Acquired**:
- ✅ Query construction and optimization
- ✅ Technology filter usage
- ✅ Result interpretation
- ✅ Multi-method access (CLI, direct, Python)
- ✅ Real-world workflow integration
- ✅ Advanced filtering and post-processing
- ✅ MCP tool orchestration
- ✅ Performance benchmarking
- ✅ Troubleshooting and optimization

**Next Steps**:
1. Practice with your real projects
2. Build custom automation scripts
3. Explore Week 1 enhancements (caching, batch queries)
4. Consider creating specialized agents for your common workflows

**Resources**:
- USER_GUIDE.md - Comprehensive reference
- PERFORMANCE_BENCHMARKS.md - Detailed performance data
- CLAUDE.md - System architecture
- GitHub: kt2saint-sec/RAGsystem

---

**Tutorial Version**: 1.0
**Last Updated**: 2025-01-13
**System**: GPU-Accelerated (AMD 7900 XTX)
**Total Learning Time**: 4-5 hours

**Happy querying! 🚀**

# Integration Instructions for MCP Agent

This guide explains how to integrate the `CodingKnowledgeTool` with your existing MCP (Model Context Protocol) agent framework.

## Core Concept

The `coding_knowledge_tool.py` script provides a class, `CodingKnowledgeTool`. This tool acts as a network client that connects to a central, standalone ChromaDB server.

This client-server architecture is essential for your use case. It allows multiple, independent processes (e.g., the Gemini CLI and the Claude Code CLI) to query the same database simultaneously without conflicting with each other. The server manages all requests, ensuring safe and concurrent access to the knowledge base.

When you initialize this tool with your agent's `mcp` instance, it automatically registers a new function that your agent can call: `query_knowledge_base`.

The agent's job is to use its reasoning capabilities to decide *when* to call this function to get factual information for a given task.

## Integration Steps

> **Prerequisite:** Before you can initialize this tool, the ChromaDB server must be running. See the `QUICKSTART.md` for instructions on how to start it.

### 1. Place the Tool

Ensure the `coding_knowledge_tool.py` file is in a location your main application can import from. For this project, you can import it directly from the `RAG/` directory.

### 2. Instantiate the Tool

In your main agent setup script (where you initialize your `FastMCP` object and your `Agent` classes), add the following lines:

```python
# In your main agent script (e.g., main.py or agent_loader.py)

# Assuming 'FastMCP' is your agent controller class
# from your_framework import FastMCP 
from RAG.coding_knowledge_tool import CodingKnowledgeTool

# 1. Initialize your agent controller
# mcp = FastMCP()

# 2. Instantiate the CodingKnowledgeTool with the mcp object
# This one line handles initialization and tool registration.
knowledge_tool = CodingKnowledgeTool(mcp)

print("✅ CodingKnowledgeTool has been initialized and is ready for the agent to use.")

# ... continue with the rest of your agent setup ...
```

That's it. The tool is now part of your agent's available functions.

## How the Agent Should Use the Tool

The power of this tool is unlocked by the agent's decision-making process. The agent needs to learn to query the knowledge base when it lacks confidence or requires specific, factual data.

### Example Agent Thought Process

**Scenario:** The agent receives the high-level task: `"Create a React component that fetches and displays a list of users from an API."`

**Agent's Internal Monologue (Conceptual):**

1.  "The user wants a React component."
2.  "This component needs to fetch data. This usually involves the `useEffect` and `useState` hooks."
3.  "I need to make an API call. What is the modern, standard way to do this? `fetch`? Or a library like `axios`?"
4.  "My internal knowledge might be slightly outdated. To ensure I provide the best, most current code, I should consult my knowledge base."
5.  **Decision:** "I will call the `query_knowledge_base` tool with a specific filter to get a reliable example."

### Agent's Action (Tool Call)

Based on its decision, the agent would execute the following tool call:

```python
query_knowledge_base(
    query="How to fetch data from an API in a React component using hooks",
    technology_filter="React Docs"
)
```

### Result

The `CodingKnowledgeTool` will search the vector database, specifically filtering for documents tagged as `"React Docs"`, and return the most relevant text chunks. This context, which comes directly from the official React documentation we downloaded, is then fed back to the agent.

Armed with this high-quality, factual context, the agent can now generate a correct, modern, and reliable React component that fulfills the user's request.

### Further Examples of Agent Logic

The same principle applies across all the domains we've added.

**Scenario 2: Security Tool Inquiry**
-   **User Task:** `"How do I use the 'nmap' tool on Kali Linux?"`
-   **Agent's Thought Process:** "The user is asking about a specific Kali Linux tool. I have a list of all Kali tools and their descriptions. I should query for 'nmap' to provide an accurate summary."
-   **Agent's Action (Tool Call):**
    ```python
    query_knowledge_base(
        query="nmap tool description and usage",
        technology_filter="Kali Linux Tools List"
    )
    ```

**Scenario 3: Network Analysis Task**
-   **User Task:** `"Show me how to inspect HTTP traffic on my network."`
-   **Agent's Thought Process:** "The user wants to inspect HTTP traffic. The best tool for this is Wireshark. I have the Wireshark User's Guide in my knowledge base. I will query it for instructions on filtering HTTP traffic."
-   **Agent's Action (Tool Call):**
    ```python
    query_knowledge_base(
        query="How to filter for and inspect HTTP traffic",
        technology_filter="Wireshark User's Guide"
    )
    ```

### Using the `technology_filter`

The `technology_filter` is a powerful feature that leverages the metadata we created during ingestion. Encourage your agent's prompting or logic to use this whenever the user's request implies a specific technology. This dramatically improves the relevance of the search results by narrowing the search space to only the most appropriate documents. The values for this filter correspond to the `"name"` field in the `targets.json` file.

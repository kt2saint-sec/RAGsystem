# Quickstart Guide

This guide provides the step-by-step commands to set up the environment, acquire all data sources, and build the RAG knowledge base.

Execute these commands from within the `/home/rebelsts/RAG/` directory.

### Prerequisites

Ensure you have `python3`, `pip`, and `venv` installed on your system.

### Step 1: Setup Virtual Environment and Install Dependencies

First, we create an isolated Python environment and install all the necessary libraries.

```bash
# Create the virtual environment
python3 -m venv .venv

# Activate the environment in your shell (optional, as commands below use the full path)
# source .venv/bin/activate

# Install all required packages
./.venv/bin/pip install langchain chromadb sentence-transformers pypdf beautifulsoup4 requests gitpython langchain-community langchain-text-splitters opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-http opentelemetry-exporter-console
```

### Step 2: Start the ChromaDB Server (Crucial for Multi-Agent Use)

To allow multiple clients (like the Gemini and Claude CLIs) to access the database simultaneously, we must run ChromaDB as a standalone server.

**In a new, dedicated terminal**, run the following command. This terminal must remain open in the background.

```bash
# Activate the environment in the new terminal
source /home/rebelsts/RAG/.venv/bin/activate

# Run the ChromaDB server, pointing to our existing database directory
chroma run --path /home/rebelsts/RAG/db --port 8001
```

### Step 3: Acquire the Data

This step runs the acquisition agent to download all Git repositories and scrape all websites defined in `targets.json`.

> **Note:** You can update `targets.json` with new sources at any time and re-run this script to download only the new content.

```bash
# Run the acquisition agent
./.venv/bin/python acquisition_agent.py
```

### Step 4: Ingest the Data into the Vector Database

This script connects to the ChromaDB server and ingests the downloaded files.

> **Note:** This script is incremental. After acquiring new data, you can safely re-run it. It will automatically detect and process only the new files that haven't been added to the database yet.

```bash
# Run the ingestion script
./.venv/bin/python ingest.py
```

### Step 5: Test the Knowledge Base

After ingestion is complete, you can run a quick test to ensure the knowledge base is working. This script will now connect to the server.

```bash
# Run the test script
./.venv/bin/python coding_knowledge_tool.py
```

You should see formatted output for a general Python query and a filtered React query, demonstrating that the tool can successfully connect to the database and retrieve information.

After completing these steps, your RAG knowledge base is fully built and ready for integration.

import chromadb
from sentence_transformers import SentenceTransformer
import logging
import time
from opentelemetry import trace, metrics

# Local import for telemetry setup
try:
    from telemetry_setup import initialize_telemetry
except ImportError:
    # Provide a dummy function if the setup file doesn't exist, so the tool can still run
    def initialize_telemetry(service_name=None):
        print("Warning: telemetry_setup.py not found. Telemetry will not be initialized.")
        pass

# --- Configuration ---
CHROMA_HOST = 'localhost'
CHROMA_PORT = '8001'
COLLECTION_NAME = 'coding_knowledge'
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CodingKnowledgeTool:
    """
    A tool that connects to a central RAG vector database server and provides
    a query interface for an MCP agent.
    """
    def __init__(self, mcp: "FastMCP"):
        """
        Initializes the tool, database connection, embedding model, and telemetry.

        Args:
            mcp: An instance of the main agent controller (FastMCP),
                 used to register the tool's functions.
        """
        # --- Telemetry Initialization ---
        initialize_telemetry(service_name="RAG.CodingKnowledgeTool")
        self.tracer = trace.get_tracer(__name__)
        self.meter = metrics.get_meter(__name__)

        # --- Metric Instruments ---
        self.query_counter = self.meter.create_counter(
            "rag.queries.total",
            description="Counts the total number of queries to the RAG system."
        )
        self.no_results_counter = self.meter.create_counter(
            "rag.queries.no_results",
            description="Counts the number of queries that returned no documents."
        )
        self.query_latency_histogram = self.meter.create_histogram(
            "rag.query.latency",
            unit="ms",
            description="Measures the duration of RAG queries."
        )

        logging.info("Initializing CodingKnowledgeTool to connect to ChromaDB server...")
        try:
            self.db_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            self.collection = self.db_client.get_collection(name=COLLECTION_NAME)
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            
            # Register the main query function as a tool for the agent
            mcp.tool(name='query_knowledge_base')(self.query)
            
            logging.info("CodingKnowledgeTool initialized and 'query_knowledge_base' tool registered.")
        except Exception as e:
            logging.error(f"Failed to initialize CodingKnowledgeTool or connect to ChromaDB server: {e}")
            logging.error(f"Please ensure the ChromaDB server is running and accessible at {CHROMA_HOST}:{CHROMA_PORT}.")
            raise

    def query(self, query: str, n_results: int = 5, technology_filter: str = None) -> str:
        """
        Queries the coding knowledge base for relevant documents and code snippets.

        Args:
            query (str): The question or topic to search for.
            n_results (int): The maximum number of results to return.
            technology_filter (str, optional): A specific technology to filter the search by 
                                               (e.g., "React Docs", "Python Docs"). Defaults to None.

        Returns:
            str: A formatted string containing the retrieved context and source metadata.
        """
        with self.tracer.start_as_current_span("rag.query") as span:
            start_time = time.time()
            
            # Add attributes to the span for observability
            span.set_attribute("rag.query.text", query)
            span.set_attribute("rag.query.n_results", n_results)
            if technology_filter:
                span.set_attribute("rag.filter.technology", technology_filter)

            # Increment the total query counter
            self.query_counter.add(1, {"filter.used": str(bool(technology_filter))})

            logging.info(f"Received query: '{query}' with filter: '{technology_filter}'")
            
            try:
                # 1. Create the query embedding
                query_embedding = self.embedding_model.encode(query).tolist()

                # 2. Construct the metadata filter if provided
                where_filter = {}
                if technology_filter:
                    where_filter = {"technology": technology_filter}
                    logging.info(f"Applying WHERE filter: {where_filter}")

                # 3. Query the vector database
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=where_filter if where_filter else None
                )

                # 4. Format and return the results
                context_str = """--- Retrieved Knowledge Base Context ---

"""
                if not results or not results.get('documents') or not results['documents'][0]:
                    span.set_attribute("rag.results.found", False)
                    self.no_results_counter.add(1)
                    return "No relevant documents found in the knowledge base."

                span.set_attribute("rag.results.found", True)
                span.set_attribute("rag.results.count", len(results['documents'][0]))

                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    source_file = metadata.get('source_file', 'Unknown')
                    tech = metadata.get('technology', 'General')
                    
                    context_str += f"--- Result {i+1} | Technology: {tech} | Source: {source_file} ---\n"
                    context_str += doc + "\n\n"
                
                context_str += "--- End of Retrieved Context ---"
                return context_str

            except Exception as e:
                logging.error(f"An error occurred during the query: {e}")
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, description=str(e)))
                return f"Error: Could not query the knowledge base. Details: {e}"
            
            finally:
                # Record the latency in milliseconds
                duration_ms = (time.time() - start_time) * 1000
                self.query_latency_histogram.record(duration_ms)


# --- Example Usage ---
if __name__ == '__main__':
    # This block demonstrates how to use the tool in a standalone fashion for testing.
    # In your actual application, you would just instantiate CodingKnowledgeTool(mcp).

    # Mock the FastMCP object for testing purposes
    class MockMCP:
        def tool(self, name):
            def decorator(func):
                logging.info(f"Mock-registering tool '{name}'")
                self.registered_tool = func
                return func
            return decorator

    logging.info("--- Running Standalone Test ---")
    mock_mcp = MockMCP()
    
    # Initialize the tool
    knowledge_tool = CodingKnowledgeTool(mock_mcp)
    
    # --- Test Case 1: General Query ---
    print("\n--- Test Case 1: General Python state management query ---")
    general_query = "How do I manage state in a Python application?"
    general_results = knowledge_tool.query(general_query)
    print(general_results)

    # --- Test Case 2: Filtered Query ---
    print("\n--- Test Case 2: Filtered query for React hooks ---")
    filtered_query = "How do I use the useState hook?"
    filtered_results = knowledge_tool.query(filtered_query, technology_filter="React Docs")
    print(filtered_results)

    # --- Test Case 3: No Results Expected ---
    print("\n--- Test Case 3: Query with no expected results ---")
    no_results_query = "asdfghjkl"
    no_results = knowledge_tool.query(no_results_query)
    print(no_results)

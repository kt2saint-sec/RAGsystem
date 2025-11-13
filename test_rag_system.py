import unittest
import sys
import os
import logging

# Add the RAG directory to the Python path to allow importing the tool
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from coding_knowledge_tool import CodingKnowledgeTool
except ImportError:
    print("Error: Could not import CodingKnowledgeTool. Make sure you are in the RAG directory.")
    sys.exit(1)

# --- Mock MCP Agent for Testing ---
class MockMCP:
    """A mock agent controller to allow tool initialization."""
    def tool(self, name):
        def decorator(func):
            logging.info(f"Mock-registering tool '{name}' for testing.")
            self.registered_tool = func
            return func
        return decorator

# --- Test Suite ---
class TestRAGSystem(unittest.TestCase):
    """
    Automated test suite for the RAG system's query functionality.
    """
    knowledge_tool = None

    @classmethod
    def setUpClass(cls):
        """
        Set up the test class once before any tests are run.
        This initializes the connection to the RAG system.
        """
        print("\n--- Setting up RAG System Test Suite ---")
        logging.disable(logging.CRITICAL) # Disable logging during tests for cleaner output

        try:
            mock_mcp = MockMCP()
            # This line will fail if the ChromaDB server is not running,
            # which is the desired behavior for a setup check.
            cls.knowledge_tool = CodingKnowledgeTool(mock_mcp)
            print("Successfully connected to the ChromaDB server.")
        except Exception as e:
            print("\nCRITICAL ERROR: Could not connect to the ChromaDB server.")
            print("Please ensure the server is running before executing tests.")
            print(f"Error details: {e}")
            # Exit the test suite if we can't connect to the DB
            sys.exit(1)

    @classmethod
    def tearDownClass(cls):
        """
        Clean up after all tests are run.
        """
        logging.disable(logging.NOTSET) # Re-enable logging
        print("\n--- RAG System Test Suite Finished ---")

    def test_01_general_query_returns_content(self):
        """
        Tests if a general query for a known topic returns a non-empty, valid response.
        """
        print("Running test_01_general_query_returns_content...")
        query = "What is a React hook?"
        response = self.knowledge_tool.query(query)
        
        self.assertIsInstance(response, str)
        self.assertNotIn("No relevant documents found", response)
        self.assertIn("React", response, "The response should contain the keyword 'React'")

    def test_02_filtered_query_returns_relevant_content(self):
        """
        Tests if a query with a technology_filter returns relevant, filtered results.
        """
        print("Running test_02_filtered_query_returns_relevant_content...")
        query = "How do I capture network packets?"
        response = self.knowledge_tool.query(query, technology_filter="Wireshark User's Guide")

        self.assertIsInstance(response, str)
        self.assertNotIn("No relevant documents found", response)
        self.assertIn("Wireshark", response, "The response should contain the keyword 'Wireshark'")
        self.assertIn("packet", response.lower(), "The response should contain the keyword 'packet'")

    def test_03_kali_tool_query(self):
        """
        Tests if a query for a specific Kali Linux tool returns the correct information.
        """
        print("Running test_03_kali_tool_query...")
        query = "What is nmap?"
        response = self.knowledge_tool.query(query, technology_filter="Kali Linux Tools List")

        self.assertIsInstance(response, str)
        self.assertNotIn("No relevant documents found", response)
        self.assertIn("nmap", response.lower(), "The response should contain 'nmap'")
        self.assertIn("tool", response.lower(), "The response should contain the keyword 'tool'") # More general assertion

    def test_04_nonsense_query_handles_no_results(self):
        """
        Tests if a nonsensical query returns the expected 'no results' message gracefully.
        """
        print("Running test_04_nonsense_query_handles_no_results...")
        query = "xyzzyplughqwertyuiop" # Even more random string
        response = self.knowledge_tool.query(query, n_results=1) # Limit results to 1 to be stricter

        self.assertIn("No relevant documents found", response)


if __name__ == '__main__':
    """

    Runner for the test suite.
    """
    print("=================================================")
    print("=         Automated RAG System Test             =")
    print("=================================================")
    print("This script will test the end-to-end query functionality of the RAG system.")
    print("NOTE: The ChromaDB server must be running for these tests to succeed.\n")
    
    unittest.main()

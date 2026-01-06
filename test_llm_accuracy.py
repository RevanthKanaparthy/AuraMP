import unittest
import json
import os
from unittest.mock import patch, Mock
from backend_complete import app, extractive_answer
from fastapi.testclient import TestClient

class TestLLMAccuracy(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_extractive_answer_with_context(self):
        context = "The quick brown fox jumps over the lazy dog. The dog is very lazy."
        query = "What is the dog?"
        answer = extractive_answer(context, query)
        self.assertIn("lazy", answer.lower())

    def test_extractive_answer_no_context(self):
        context = "The quick brown fox jumps over the lazy dog."
        query = "What about the cat?"
        answer = extractive_answer(context, query)
        self.assertIn("The quick brown fox jumps over the lazy dog.", answer)

    @unittest.skipIf(os.environ.get("SKIP_EMBEDDINGS") == "1", "Skipping LLM test to avoid network issues")
    @patch('backend_complete.generate_answer_with_llm')
    def test_query_rag_with_mock_llm(self, mock_generate_answer):
        # Mock the LLM to return a predictable response
        mock_generate_answer.return_value = "This is a test response from the mock LLM."

        # Make a request to the /api/query endpoint
        response = self.client.post("/api/query", json={"query": "test query"})

        # Assert that the response is what we expect
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['response'], "This is a test response from the mock LLM.")

    @unittest.skipIf(os.environ.get("SKIP_EMBEDDINGS") != "1", "Skipping no-LLM test")
    def test_query_rag_without_llm(self):
        # Make a request to the /api/query endpoint
        response = self.client.post("/api/query", json={"query": "test query"})

        # Assert that the response is what we expect
        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: The AI model could not be reached", response.json()['response'])
        
    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['backend'])
        self.assertIn(data['database'], [True, False])
        self.assertTrue(data['llm'])

if __name__ == '__main__':
    unittest.main()

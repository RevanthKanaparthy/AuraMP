#!/usr/bin/env python3
"""
Test script for the new chunking improvements and advanced retrieval features.
Tests semantic chunking, quality filtering, deduplication, and retrieval enhancements.
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chunking_utils import (
    create_semantic_chunks,
    deduplicate_chunks,
    prepare_chunks_for_embedding,
    AdvancedChunkingUtils
)
from advanced_retrieval import AdvancedRetriever, ContextOptimizer

def test_basic_chunking():
    """Test basic semantic chunking functionality."""
    print("🧪 Testing Basic Semantic Chunking...")

    # Sample text for testing
    test_text = """
    Machine Learning is a subset of artificial intelligence that focuses on algorithms
    and statistical models that computer systems use to perform specific tasks without
    explicit instructions. It relies on patterns and inference instead.

    Deep Learning is a subset of machine learning that uses neural networks with multiple
    layers to model complex patterns in data. These neural networks are inspired by the
    human brain's structure and function.

    Natural Language Processing (NLP) combines computational linguistics with statistical
    and machine learning models to give computers the ability to process and understand
    human language. This includes tasks like translation, sentiment analysis, and text generation.

    Computer Vision is a field of AI that trains computers to interpret and understand
    visual information from the world. It involves techniques like image recognition,
    object detection, and image segmentation.
    """

    try:
        # Test basic chunking
        chunks = create_semantic_chunks(test_text, document_id=1)
        print(f"✅ Created {len(chunks)} chunks")

        # Validate chunk structure
        required_fields = ['chunk_text', 'chunk_index', 'embedding_id', 'quality_score', 'keywords', 'metadata']
        for chunk in chunks:
            for field in required_fields:
                assert field in chunk, f"Missing field: {field}"

        print("✅ Chunk structure validation passed")

        # Test quality scores
        quality_scores = [chunk['quality_score'] for chunk in chunks]
        assert all(0 <= score <= 1 for score in quality_scores), "Quality scores out of range"
        print(f"✅ Quality scores valid: {quality_scores}")

        # Test keywords extraction
        for chunk in chunks[:2]:  # Test first 2 chunks
            keywords = chunk['keywords']
            assert isinstance(keywords, list), "Keywords should be a list"
            assert len(keywords) > 0, "Should have at least one keyword"
            print(f"✅ Keywords extracted: {keywords[:5]}...")  # Show first 5

        return True

    except Exception as e:
        print(f"❌ Basic chunking test failed: {e}")
        return False

def test_advanced_chunking():
    """Test advanced chunking features."""
    print("\n🧪 Testing Advanced Chunking Features...")

    chunker = AdvancedChunkingUtils(chunk_size=200, overlap=30)

    test_text = """
    Artificial Intelligence (AI) refers to the simulation of human intelligence in machines
    that are programmed to think like humans and mimic their actions. The term may also
    be applied to any machine that exhibits traits associated with a human mind such as
    learning and problem-solving.

    Machine Learning is a method of data analysis that automates analytical model building.
    It is a branch of artificial intelligence based on the idea that systems can learn from
    data, identify patterns and make decisions with minimal human intervention.

    Deep Learning is part of a broader family of machine learning methods based on artificial
    neural networks with representation learning. It can be supervised, semi-supervised or
    unsupervised. Deep learning architectures such as deep neural networks, deep belief
    networks, recurrent neural networks and convolutional neural networks have been applied
    to fields including computer vision, speech recognition, natural language processing,
    audio recognition, social network filtering, machine translation, bioinformatics, drug
    design, medical image analysis, material inspection and board game programs, where they
    have produced results comparable to and in some cases surpassing human expert performance.
    """

    try:
        # Test hierarchical chunking
        hierarchical_chunks = chunker.create_hierarchical_chunks(test_text, document_id=1)
        print(f"✅ Created hierarchical chunks: {list(hierarchical_chunks.keys())}")

        for level, chunks in hierarchical_chunks.items():
            print(f"  - {level}: {len(chunks)} chunks")
            assert len(chunks) > 0, f"No chunks created for {level}"

        # Test deduplication
        # Create some duplicate chunks for testing
        duplicate_chunks = chunks * 2  # Duplicate all chunks
        deduplicated = chunker.deduplicate_chunks(duplicate_chunks)
        print(f"✅ Deduplication: {len(duplicate_chunks)} → {len(deduplicated)} chunks")

        # Test quality filtering
        filtered_chunks = chunker.filter_low_quality_chunks(chunks, quality_threshold=0.3)
        print(f"✅ Quality filtering: {len(chunks)} → {len(filtered_chunks)} chunks")

        return True

    except Exception as e:
        print(f"❌ Advanced chunking test failed: {e}")
        return False

def test_retrieval_features():
    """Test advanced retrieval features."""
    print("\n🧪 Testing Advanced Retrieval Features...")

    try:
        retriever = AdvancedRetriever()
        optimizer = ContextOptimizer()

        # Create test chunks
        test_chunks = [
            {
                'chunk_text': 'Machine learning is a subset of AI that focuses on algorithms.',
                'chunk_index': 0,
                'quality_score': 0.8,
                'keywords': ['machine', 'learning', 'AI', 'algorithms'],
                'metadata': {'position': 0}
            },
            {
                'chunk_text': 'Deep learning uses neural networks with multiple layers.',
                'chunk_index': 1,
                'quality_score': 0.9,
                'keywords': ['deep', 'learning', 'neural', 'networks'],
                'metadata': {'position': 1}
            },
            {
                'chunk_text': 'Natural language processing handles human language understanding.',
                'chunk_index': 2,
                'quality_score': 0.7,
                'keywords': ['natural', 'language', 'processing', 'understanding'],
                'metadata': {'position': 2}
            }
        ]

        query = "What is deep learning?"

        # Test re-ranking
        reranked_chunks = retriever.rerank_chunks(query, test_chunks, top_k=2)
        print(f"✅ Re-ranking completed: {len(reranked_chunks)} chunks returned")

        # Test diverse retrieval
        diverse_chunks = retriever.diverse_retrieval(test_chunks, max_chunks=2)
        print(f"✅ Diverse retrieval completed: {len(diverse_chunks)} chunks returned")

        # Test dynamic context window
        context_window = retriever.dynamic_context_window(query)
        print(f"✅ Dynamic context window: {context_window} tokens for query")

        # Test context compression
        compressed_context = optimizer.compress_context(test_chunks[:2], max_tokens=100)
        print(f"✅ Context compression: {len(compressed_context)} characters")

        # Test source prioritization
        prioritized_chunks = optimizer.prioritize_sources(test_chunks)
        print(f"✅ Source prioritization completed: {len(prioritized_chunks)} chunks")

        return True

    except Exception as e:
        print(f"❌ Retrieval features test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n🧪 Testing Edge Cases...")

    try:
        # Test empty text
        empty_chunks = create_semantic_chunks("", document_id=1)
        assert len(empty_chunks) == 0, "Empty text should produce no chunks"
        print("✅ Empty text handling")

        # Test very short text
        short_chunks = create_semantic_chunks("Hello world.", document_id=1)
        assert len(short_chunks) > 0, "Short text should still produce chunks"
        print("✅ Short text handling")

        # Test text with special characters
        special_text = "Text with @#$%^&*() symbols and émojis 😀📚"
        special_chunks = create_semantic_chunks(special_text, document_id=1)
        assert len(special_chunks) > 0, "Special characters should be handled"
        print("✅ Special characters handling")

        # Test deduplication with identical chunks
        identical_chunks = [
            {'chunk_text': ' identical text ', 'chunk_index': 0, 'quality_score': 0.8, 'keywords': [], 'metadata': {}},
            {'chunk_text': ' identical text ', 'chunk_index': 1, 'quality_score': 0.8, 'keywords': [], 'metadata': {}}
        ]
        deduplicated = deduplicate_chunks(identical_chunks)
        assert len(deduplicated) == 1, "Identical chunks should be deduplicated"
        print("✅ Identical chunk deduplication")

        return True

    except Exception as e:
        print(f"❌ Edge cases test failed: {e}")
        return False

def test_performance():
    """Test performance of chunking operations."""
    print("\n🧪 Testing Performance...")

    import time

    # Create a larger test document
    large_text = """
    Introduction to Artificial Intelligence

    Artificial Intelligence (AI) is a branch of computer science that aims to create
    machines capable of intelligent behavior. AI research has been highly successful
    in developing effective techniques for solving a wide variety of problems, from
    game playing to medical diagnosis.

    Machine Learning Fundamentals

    Machine learning is a method of data analysis that automates analytical model building.
    It is based on the idea that systems can learn from data, identify patterns, and make
    decisions with minimal human intervention. Machine learning algorithms build a model
    based on training data in order to make predictions or decisions without being explicitly
    programmed to perform the task.

    Deep Learning Architectures

    Deep learning is a subset of machine learning that uses neural networks with multiple
    layers. These networks can learn complex patterns in data through a process called
    representation learning. Deep learning has achieved remarkable success in areas such
    as image recognition, speech recognition, and natural language processing.

    Applications of AI

    AI has numerous applications across various industries. In healthcare, AI assists in
    medical diagnosis and drug discovery. In finance, AI is used for fraud detection and
    algorithmic trading. In transportation, AI powers autonomous vehicles and traffic
    optimization systems. In entertainment, AI creates realistic graphics and personalized
    content recommendations.

    Future of Artificial Intelligence

    The future of AI holds great promise but also presents significant challenges. As AI
    systems become more sophisticated, questions about ethics, privacy, and job displacement
    become increasingly important. Research in AI safety and responsible AI development
    is crucial to ensure that AI benefits humanity as a whole.
    """ * 5  # Repeat to make it larger

    try:
        start_time = time.time()
        chunks = create_semantic_chunks(large_text, document_id=1)
        chunking_time = time.time() - start_time

        print(f"✅ Large document chunking: {len(chunks)} chunks in {chunking_time:.2f}s")
        print(f"  Average chunking speed: {len(large_text.split()) / chunking_time:.0f} words/second")

        # Test retrieval performance
        retriever = AdvancedRetriever()
        query = "applications of artificial intelligence"

        start_time = time.time()
        reranked = retriever.rerank_chunks(query, chunks[:10], top_k=5)  # Test with first 10 chunks
        retrieval_time = time.time() - start_time

        print(f"✅ Retrieval performance: {retrieval_time:.3f}s for re-ranking")

        return True

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Comprehensive Testing of Embedding Storage Improvements\n")

    tests = [
        ("Basic Chunking", test_basic_chunking),
        ("Advanced Chunking", test_advanced_chunking),
        ("Retrieval Features", test_retrieval_features),
        ("Edge Cases", test_edge_cases),
        ("Performance", test_performance)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)

        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            print(f"\n❌ FAILED: {test_name} - {e}")
            results.append((test_name, False))

    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The embedding storage improvements are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

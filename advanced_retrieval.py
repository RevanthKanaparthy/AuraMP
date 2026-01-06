"""
Advanced Retrieval and Context Optimization for RAG System
Implements re-ranking, diverse retrieval, and context optimization features.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
from typing import List, Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("Warning: sentence-transformers not available. Some features will be limited.")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

class AdvancedRetriever:
    """Advanced retrieval system with re-ranking and diverse retrieval."""

    def __init__(self):
        self.embedding_model = None
        self.cross_encoder = None
        self._load_models()

    def _load_models(self):
        """Load embedding and cross-encoder models."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Load sentence transformer for embeddings
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Warning: Could not load embedding model: {e}")
                self.embedding_model = None
        else:
            print("Sentence transformers not available, using fallback methods")
            self.embedding_model = None

        try:
            # Load cross-encoder for re-ranking
            self.cross_encoder = AutoModelForSequenceClassification.from_pretrained(
                'cross-encoder/ms-marco-MiniLM-L-6-v2'
            )
            self.cross_encoder_tokenizer = AutoTokenizer.from_pretrained(
                'cross-encoder/ms-marco-MiniLM-L-6-v2'
            )
        except Exception as e:
            print(f"Warning: Could not load cross-encoder: {e}")
            self.cross_encoder = None

    def rerank_chunks(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Re-rank chunks using cross-encoder for better relevance.

        Args:
            query: Search query
            chunks: List of chunk dictionaries
            top_k: Number of top chunks to return

        Returns:
            Re-ranked chunks
        """
        if not self.cross_encoder or not chunks:
            return chunks[:top_k]

        try:
            # Prepare input pairs for cross-encoder
            pairs = [[query, chunk['chunk_text']] for chunk in chunks]

            # Get cross-encoder scores
            inputs = self.cross_encoder_tokenizer(
                pairs, return_tensors='pt', padding=True, truncation=True, max_length=512
            )

            with torch.no_grad():
                scores = self.cross_encoder(**inputs).logits.squeeze()

            # Sort chunks by scores
            scored_chunks = list(zip(chunks, scores.tolist() if hasattr(scores, 'tolist') else scores))
            scored_chunks.sort(key=lambda x: x[1], reverse=True)

            return [chunk for chunk, score in scored_chunks[:top_k]]

        except Exception as e:
            print(f"Warning: Cross-encoder re-ranking failed: {e}")
            return chunks[:top_k]

    def diverse_retrieval(self, chunks: List[Dict[str, Any]], max_chunks: int = 10,
                          diversity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Select diverse chunks to avoid redundancy.

        Args:
            chunks: List of chunk dictionaries
            max_chunks: Maximum number of chunks to return
            diversity_threshold: Similarity threshold for diversity

        Returns:
            Diverse chunk selection
        """
        if not self.embedding_model or len(chunks) <= max_chunks:
            return chunks[:max_chunks]

        try:
            # Get embeddings for chunks
            texts = [chunk['chunk_text'] for chunk in chunks]
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)

            # Select diverse chunks using Maximal Marginal Relevance (MMR)
            selected_indices = []
            remaining_indices = list(range(len(chunks)))

            # Start with the highest quality chunk
            best_idx = max(remaining_indices, key=lambda i: chunks[i].get('quality_score', 0))
            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)

            while len(selected_indices) < max_chunks and remaining_indices:
                best_score = -1
                best_idx = None

                for idx in remaining_indices:
                    # Calculate relevance score (quality + recency bonus)
                    relevance = chunks[idx].get('quality_score', 0.5)

                    # Calculate diversity score (minimum similarity to selected chunks)
                    similarities = []
                    for selected_idx in selected_indices:
                        sim = cosine_similarity(
                            embeddings[idx].reshape(1, -1),
                            embeddings[selected_idx].reshape(1, -1)
                        )[0][0]
                        similarities.append(sim)

                    diversity = 1 - max(similarities) if similarities else 1.0

                    # MMR score
                    mmr_score = 0.5 * relevance + 0.5 * diversity

                    if mmr_score > best_score:
                        best_score = mmr_score
                        best_idx = idx

                if best_idx is not None:
                    selected_indices.append(best_idx)
                    remaining_indices.remove(best_idx)
                else:
                    break

            return [chunks[i] for i in selected_indices]

        except Exception as e:
            print(f"Warning: Diverse retrieval failed: {e}")
            return chunks[:max_chunks]

    def dynamic_context_window(self, query: str, base_window: int = 3000) -> int:
        """
        Determine optimal context window based on query complexity.

        Args:
            query: Search query
            base_window: Base context window size

        Returns:
            Optimal context window size
        """
        # Analyze query complexity
        words = query.split()
        complexity_factors = {
            'length': len(words),
            'question_words': len([w for w in words if w.lower() in
                                 ['what', 'how', 'why', 'when', 'where', 'who', 'which']]),
            'technical_terms': len([w for w in words if len(w) > 6 or '_' in w]),
        }

        complexity_score = (
            complexity_factors['length'] * 0.3 +
            complexity_factors['question_words'] * 0.4 +
            complexity_factors['technical_terms'] * 0.3
        )

        # Adjust window size based on complexity
        if complexity_score > 3:
            return int(base_window * 1.5)  # Complex queries need more context
        elif complexity_score > 1.5:
            return base_window  # Standard queries
        else:
            return int(base_window * 0.8)  # Simple queries need less context

class ContextOptimizer:
    """Context optimization with compression and prioritization."""

    def __init__(self):
        self.retriever = AdvancedRetriever()

    def compress_context(self, chunks: List[Dict[str, Any]], max_tokens: int = 2000) -> str:
        """
        Compress context by prioritizing important information.

        Args:
            chunks: List of chunk dictionaries
            max_tokens: Maximum tokens for compressed context

        Returns:
            Compressed context string
        """
        if not chunks:
            return ""

        # Sort chunks by quality and relevance
        sorted_chunks = sorted(
            chunks,
            key=lambda x: x.get('quality_score', 0.5) * x.get('relevance_score', 1.0),
            reverse=True
        )

        compressed_parts = []
        total_tokens = 0

        for chunk in sorted_chunks:
            text = chunk['chunk_text']
            # Estimate tokens (rough approximation)
            estimated_tokens = len(text.split()) * 1.3

            if total_tokens + estimated_tokens > max_tokens:
                # Truncate if needed
                remaining_tokens = max_tokens - total_tokens
                if remaining_tokens > 50:  # Only add if we have meaningful space
                    words = text.split()
                    truncated_words = words[:int(remaining_tokens / 1.3)]
                    compressed_parts.append(' '.join(truncated_words))
                break

            compressed_parts.append(text)
            total_tokens += estimated_tokens

        return '\n\n'.join(compressed_parts)

    def prioritize_sources(self, chunks: List[Dict[str, Any]],
                          recency_weight: float = 0.3,
                          authority_weight: float = 0.4,
                          quality_weight: float = 0.3) -> List[Dict[str, Any]]:
        """
        Prioritize chunks based on recency, authority, and quality.

        Args:
            chunks: List of chunk dictionaries
            recency_weight: Weight for recency scoring
            authority_weight: Weight for authority scoring
            quality_weight: Weight for quality scoring

        Returns:
            Prioritized chunks
        """
        current_time = datetime.now()

        for chunk in chunks:
            # Recency score (newer documents get higher scores)
            created_at = chunk.get('created_at')
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    created_at = current_time

            days_old = (current_time - created_at).days if created_at else 365
            recency_score = max(0, 1 - (days_old / 365))  # Score decays over a year

            # Authority score (based on document category and department)
            category = chunk.get('category', 'unknown')
            authority_scores = {
                'research': 0.9, 'patent': 0.8, 'publication': 0.8,
                'project': 0.7, 'proposal': 0.6, 'test': 0.5
            }
            authority_score = authority_scores.get(category, 0.5)

            # Quality score (from chunk metadata)
            quality_score = chunk.get('quality_score', 0.5)

            # Combined priority score
            priority_score = (
                recency_weight * recency_score +
                authority_weight * authority_score +
                quality_weight * quality_score
            )

            chunk['priority_score'] = priority_score

        # Sort by priority score
        return sorted(chunks, key=lambda x: x.get('priority_score', 0), reverse=True)

# Global instances
retriever = AdvancedRetriever()
context_optimizer = ContextOptimizer()

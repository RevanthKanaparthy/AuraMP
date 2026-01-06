import re
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class AdvancedChunkingUtils:
    """Advanced chunking utilities for RAG systems with semantic chunking, deduplication, and quality filtering."""

    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        """
        Initialize the chunking utilities.

        Args:
            chunk_size: Target chunk size in tokens (200-500 recommended)
            overlap: Token overlap between chunks (50 recommended)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text by normalizing whitespace and cleaning.

        Args:
            text: Raw text to preprocess

        Returns:
            Preprocessed text
        """
        if not text:
            return ""

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove excessive newlines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        return text

    def extract_text_structure(self, text: str) -> Dict[str, Any]:
        """
        Extract structural information from text (headers, sections, etc.).

        Args:
            text: Input text

        Returns:
            Dictionary with structural information
        """
        lines = text.split('\n')
        headers = []
        sections = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Detect headers (lines that are short, uppercase, or end with colons)
            if (len(line) < 100 and
                (line.isupper() or line.endswith(':') or
                 re.match(r'^[A-Z][^a-z]*$', line) or
                 len(line.split()) <= 6)):
                headers.append({
                    'text': line,
                    'line_number': i,
                    'level': self._estimate_header_level(line)
                })

        return {
            'headers': headers,
            'total_lines': len(lines),
            'estimated_sections': len([h for h in headers if h['level'] <= 2])
        }

    def _estimate_header_level(self, header_text: str) -> int:
        """Estimate header level based on text characteristics."""
        if header_text.isupper():
            return 1
        elif header_text.endswith(':'):
            return 2
        elif len(header_text.split()) <= 3:
            return 1
        else:
            return 2

    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract important keywords from text using TF-IDF like scoring.

        Args:
            text: Input text
            max_keywords: Maximum number of keywords to extract

        Returns:
            List of keywords
        """
        words = word_tokenize(text.lower())
        words = [w for w in words if w.isalnum() and w not in self.stop_words and len(w) > 2]

        # Simple frequency-based keyword extraction
        word_freq = defaultdict(int)
        for word in words:
            lemma = self.lemmatizer.lemmatize(word)
            word_freq[lemma] += 1

        # Sort by frequency and return top keywords
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:max_keywords]]

    def calculate_chunk_quality_score(self, chunk_text: str, position: int, total_chunks: int) -> float:
        """
        Calculate a quality score for a chunk based on various factors.

        Args:
            chunk_text: The chunk text
            position: Position of chunk in document (0-based)
            total_chunks: Total number of chunks

        Returns:
            Quality score between 0 and 1
        """
        if not chunk_text.strip():
            return 0.0

        score = 0.0

        # Length score (prefer chunks close to target size)
        word_count = len(chunk_text.split())
        length_score = 1.0 - abs(word_count - self.chunk_size) / self.chunk_size
        score += length_score * 0.3

        # Completeness score (prefer chunks that start/end with complete sentences)
        sentences = sent_tokenize(chunk_text)
        if sentences:
            first_complete = sentences[0].strip().endswith(('.', '!', '?'))
            last_complete = sentences[-1].strip().endswith(('.', '!', '?'))
            completeness = (first_complete + last_complete) / 2
            score += completeness * 0.3

        # Position score (slight preference for middle chunks)
        if total_chunks > 1:
            position_score = 1.0 - abs(2 * position / (total_chunks - 1) - 1) * 0.5
            score += position_score * 0.2

        # Information density (prefer chunks with more unique words)
        words = set(word_tokenize(chunk_text.lower()))
        unique_ratio = len(words) / max(1, word_count)
        score += min(unique_ratio, 1.0) * 0.2

        return min(score, 1.0)

    def create_semantic_chunks(self, text: str, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Create semantic chunks with overlapping windows and enhanced metadata.

        Args:
            text: Input text to chunk
            document_id: Optional document ID for metadata

        Returns:
            List of chunk dictionaries with metadata
        """
        # Preprocess text
        text = self.preprocess_text(text)
        if not text:
            return []

        # Extract structural information
        structure = self.extract_text_structure(text)

        # Tokenize into sentences for semantic chunking
        sentences = sent_tokenize(text)
        if not sentences:
            return []

        chunks = []
        current_chunk = []
        current_token_count = 0
        chunk_index = 0

        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            sentence_tokens = len(word_tokenize(sentence))

            # Check if adding this sentence would exceed chunk size
            if current_token_count + sentence_tokens > self.chunk_size and current_chunk:
                # Create chunk from current sentences
                chunk_text = ' '.join(current_chunk)
                chunk_metadata = self._create_chunk_metadata(
                    chunk_text, chunk_index, structure, len(sentences), document_id
                )
                chunks.append(chunk_metadata)

                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(current_chunk, self.overlap)
                current_chunk = overlap_sentences + [sentence]
                current_token_count = sum(len(word_tokenize(s)) for s in current_chunk)
                chunk_index += 1
            else:
                current_chunk.append(sentence)
                current_token_count += sentence_tokens

            i += 1

        # Add remaining sentences as final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk_metadata = self._create_chunk_metadata(
                chunk_text, chunk_index, structure, len(sentences), document_id
            )
            chunks.append(chunk_metadata)

        return chunks

    def _get_overlap_sentences(self, sentences: List[str], target_overlap_tokens: int) -> List[str]:
        """Get sentences for overlap that total approximately target_overlap_tokens."""
        overlap_sentences = []
        token_count = 0

        for sentence in reversed(sentences):
            sentence_tokens = len(word_tokenize(sentence))
            if token_count + sentence_tokens <= target_overlap_tokens:
                overlap_sentences.insert(0, sentence)
                token_count += sentence_tokens
            else:
                break

        return overlap_sentences

    def _create_chunk_metadata(self, chunk_text: str, chunk_index: int,
                              structure: Dict, total_sentences: int,
                              document_id: Optional[str] = None) -> Dict[str, Any]:
        """Create comprehensive metadata for a chunk."""
        # Calculate quality score
        quality_score = self.calculate_chunk_quality_score(chunk_text, chunk_index,
                                                         max(1, chunk_index + 1))

        # Extract keywords
        keywords = self.extract_keywords(chunk_text)

        # Find nearby headers
        nearby_headers = self._find_nearby_headers(chunk_text, structure)

        # Create unique embedding ID
        embedding_id = hashlib.md5(f"{document_id}_{chunk_index}_{chunk_text[:100]}".encode()).hexdigest()

        return {
            'chunk_text': chunk_text,
            'chunk_index': chunk_index,
            'embedding_id': embedding_id,
            'word_count': len(chunk_text.split()),
            'quality_score': quality_score,
            'keywords': keywords,
            'headers': nearby_headers,
            'metadata': {
                'position': chunk_index,
                'total_chunks': chunk_index + 1,  # Will be updated after all chunks created
                'document_structure': structure,
                'sentence_count': len(sent_tokenize(chunk_text)),
                'has_overlap': chunk_index > 0,
                'estimated_importance': quality_score
            }
        }

    def _find_nearby_headers(self, chunk_text: str, structure: Dict) -> List[Dict]:
        """Find headers that are contextually relevant to this chunk."""
        headers = structure.get('headers', [])
        chunk_lower = chunk_text.lower()

        relevant_headers = []
        for header in headers:
            header_lower = header['text'].lower()
            # Simple relevance check - header words appear in chunk
            header_words = set(word_tokenize(header_lower))
            chunk_words = set(word_tokenize(chunk_lower))

            if header_words.intersection(chunk_words):
                relevant_headers.append(header)

        return relevant_headers[:3]  # Limit to top 3 relevant headers

    def deduplicate_chunks(self, chunks: List[Dict[str, Any]],
                          similarity_threshold: float = 0.85) -> List[Dict[str, Any]]:
        """
        Remove duplicate or highly similar chunks.

        Args:
            chunks: List of chunk dictionaries
            similarity_threshold: Threshold for considering chunks duplicates (0-1)

        Returns:
            Deduplicated list of chunks
        """
        if len(chunks) <= 1:
            return chunks

        # Simple deduplication based on text similarity (can be enhanced with embeddings)
        unique_chunks = []
        seen_texts = set()

        for chunk in chunks:
            chunk_text = chunk['chunk_text'].strip().lower()
            # Create a simplified version for comparison
            simplified = re.sub(r'[^\w\s]', '', chunk_text)
            simplified = ' '.join(simplified.split()[:50])  # First 50 words

            is_duplicate = False
            for seen_text in seen_texts:
                # Simple Jaccard similarity
                set1 = set(simplified.split())
                set2 = set(seen_text.split())
                intersection = len(set1.intersection(set2))
                union = len(set1.union(set2))
                if union > 0 and intersection / union > similarity_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_chunks.append(chunk)
                seen_texts.add(simplified)

        return unique_chunks

    def filter_low_quality_chunks(self, chunks: List[Dict[str, Any]],
                                quality_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Filter out chunks below quality threshold.

        Args:
            chunks: List of chunk dictionaries
            quality_threshold: Minimum quality score (0-1)

        Returns:
            Filtered list of chunks
        """
        return [chunk for chunk in chunks if chunk.get('quality_score', 0) >= quality_threshold]

    def create_hierarchical_chunks(self, text: str, document_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Create hierarchical chunks for different query types.

        Args:
            text: Input text
            document_id: Optional document ID

        Returns:
            Dictionary with different levels of chunks
        """
        # Create different chunk sizes for different use cases
        chunk_configs = {
            'detailed': {'size': 200, 'overlap': 30},  # For detailed queries
            'standard': {'size': 300, 'overlap': 50},  # Standard RAG chunks
            'summary': {'size': 500, 'overlap': 80}    # For summary/overview queries
        }

        hierarchical_chunks = {}

        for level, config in chunk_configs.items():
            chunker = AdvancedChunkingUtils(config['size'], config['overlap'])
            chunks = chunker.create_semantic_chunks(text, document_id)
            chunks = chunker.deduplicate_chunks(chunks)
            chunks = chunker.filter_low_quality_chunks(chunks)
            hierarchical_chunks[level] = chunks

        return hierarchical_chunks

    def prepare_chunks_for_embedding(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare chunks for embedding storage with final metadata.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Prepared chunks ready for embedding
        """
        # Update total_chunks in metadata
        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            chunk['metadata']['total_chunks'] = total_chunks
            # Ensure embedding_id is present
            if 'embedding_id' not in chunk:
                chunk['embedding_id'] = hashlib.md5(
                    f"{chunk.get('document_id', 'unknown')}_{i}_{chunk['chunk_text'][:100]}".encode()
                ).hexdigest()

        return chunks


# Convenience functions for backward compatibility
def create_semantic_chunks(text: str, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Create semantic chunks with default settings."""
    chunker = AdvancedChunkingUtils()
    chunks = chunker.create_semantic_chunks(text, document_id)
    return chunker.prepare_chunks_for_embedding(chunks)

def deduplicate_chunks(chunks: List[Dict[str, Any]], threshold: float = 0.85) -> List[Dict[str, Any]]:
    """Deduplicate chunks with default settings."""
    chunker = AdvancedChunkingUtils()
    return chunker.deduplicate_chunks(chunks, threshold)

def prepare_chunks_for_embedding(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare chunks for embedding storage."""
    chunker = AdvancedChunkingUtils()
    return chunker.prepare_chunks_for_embedding(chunks)

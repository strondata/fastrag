"""Memory stream implementation for agents.

This module implements long-term memory with importance, recency,
and relevance scoring, inspired by "Generative Agents" research.
"""

import logging
import time
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from rag_chatbot.interfaces import IEmbeddingModel, IVectorStore, ILocalLLM, Documento

logger = logging.getLogger(__name__)


@dataclass
class Memory:
    """Represents a memory with content and metadata.
    
    Attributes:
        content: The memory content.
        importance: Importance score (1-10).
        timestamp: When the memory was created.
        metadata: Additional metadata.
    """
    content: str
    importance: float
    timestamp: float
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        """Generate ID after initialization."""
        if 'id' not in self.metadata:
            # Generate unique ID from content and timestamp
            unique_str = f"{self.content}_{self.timestamp}"
            self.metadata['id'] = hashlib.md5(unique_str.encode()).hexdigest()


class MemoryStream:
    """Long-term memory system with sophisticated retrieval.
    
    Combines three factors for memory retrieval:
    - Recency: How recently was the memory created?
    - Importance: How important is this memory?
    - Relevance: How relevant is this memory to the current query?
    
    References:
        - Generative Agents: "Memory stream with recency, importance, relevance"
        - Multi-factor retrieval: "Weighted combination improves memory selection"
        - Decay functions: "Exponential decay for recency modeling"
    """
    
    def __init__(
        self,
        embedder: IEmbeddingModel,
        vector_store: IVectorStore,
        llm: Optional[ILocalLLM] = None,
        recency_weight: float = 0.2,
        importance_weight: float = 0.3,
        relevance_weight: float = 0.5,
        recency_decay_rate: float = 0.995,
        **config
    ):
        """Initialize memory stream.
        
        Args:
            embedder: Embedding model for semantic search.
            vector_store: Storage for memory embeddings.
            llm: Optional LLM for importance evaluation.
            recency_weight: Weight for recency score (0-1).
            importance_weight: Weight for importance score (0-1).
            relevance_weight: Weight for relevance score (0-1).
            recency_decay_rate: Decay rate for recency (0-1, closer to 1 = slower decay).
            **config: Additional configuration.
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self.llm = llm
        
        # Normalize weights
        total_weight = recency_weight + importance_weight + relevance_weight
        self.recency_weight = recency_weight / total_weight
        self.importance_weight = importance_weight / total_weight
        self.relevance_weight = relevance_weight / total_weight
        
        self.recency_decay_rate = recency_decay_rate
        self.config = config
        
        logger.info(f"MemoryStream initialized (weights: R={self.recency_weight:.2f}, "
                   f"I={self.importance_weight:.2f}, V={self.relevance_weight:.2f})")
    
    def _evaluate_importance(self, memory_text: str) -> float:
        """Evaluate the importance of a memory using LLM.
        
        Args:
            memory_text: Memory content.
            
        Returns:
            Importance score (1-10).
        """
        if not self.llm:
            # Default importance if no LLM available
            return 5.0
        
        prompt = f"""On a scale of 1 to 10, rate the importance of the following memory 
for a conversational agent. Consider:
- Is this fundamental knowledge or a trivial detail?
- Will this be useful for future conversations?
- Does this represent a significant event or insight?

Memory: "{memory_text}"

Respond with only a number from 1 to 10.

Importance score:"""
        
        try:
            response = self.llm.generate(prompt).strip()
            # Extract first number from response
            import re
            match = re.search(r'\d+', response)
            if match:
                score = int(match.group())
                return max(1, min(10, score))  # Clamp to 1-10
            else:
                logger.warning(f"Could not parse importance score from: {response}")
                return 5.0
        except Exception as e:
            logger.error(f"Importance evaluation failed: {e}")
            return 5.0
    
    def add_memory(self, memory_text: str, importance: Optional[float] = None, metadata: Dict = None):
        """Add a memory to the stream.
        
        Args:
            memory_text: Content of the memory.
            importance: Optional pre-evaluated importance (1-10).
            metadata: Optional additional metadata.
        """
        logger.debug(f"Adding memory: {memory_text[:50]}...")
        
        # Evaluate importance if not provided
        if importance is None:
            importance = self._evaluate_importance(memory_text)
        
        # Create memory object
        memory_metadata = metadata or {}
        memory_metadata.update({
            'timestamp': time.time(),
            'importance': importance
        })
        
        memory = Memory(
            content=memory_text,
            importance=importance,
            timestamp=time.time(),
            metadata=memory_metadata
        )
        
        # Create document for vector store
        doc = Documento(content=memory_text, metadata=memory_metadata)
        
        # Generate embedding and store
        embedding = self.embedder.embed_query(memory_text)
        self.vector_store.add([doc], [embedding])
        
        logger.info(f"Memory added with importance {importance:.1f}")
    
    def _calculate_recency_score(self, timestamp: float) -> float:
        """Calculate recency score with exponential decay.
        
        Args:
            timestamp: When the memory was created.
            
        Returns:
            Recency score (0-1).
        """
        current_time = time.time()
        time_diff = current_time - timestamp
        
        # Time difference in hours
        hours_ago = time_diff / 3600.0
        
        # Exponential decay
        recency = self.recency_decay_rate ** hours_ago
        
        return max(0.0, min(1.0, recency))
    
    def retrieve_memories(self, query_text: str, top_k: int = 5) -> List[Documento]:
        """Retrieve most relevant memories using combined scoring.
        
        Args:
            query_text: Query to retrieve memories for.
            top_k: Number of memories to retrieve.
            
        Returns:
            List of most relevant memories.
        """
        logger.debug(f"Retrieving memories for: {query_text[:50]}...")
        
        # Get semantically relevant memories (cast wider net)
        query_embedding = self.embedder.embed_query(query_text)
        candidate_memories = self.vector_store.search(query_embedding, k=top_k * 5)
        
        if not candidate_memories:
            logger.warning("No memories found")
            return []
        
        # Calculate combined scores
        scored_memories = []
        
        for doc in candidate_memories:
            # Get stored metadata
            timestamp = doc.metadata.get('timestamp', time.time())
            importance = doc.metadata.get('importance', 5.0)
            
            # Assume semantic similarity from vector store (normalized 0-1)
            # In practice, the vector store should return similarity scores
            # For now, we'll use a placeholder
            relevance = 0.8  # Placeholder - actual implementation would use cosine similarity
            
            # Calculate recency score
            recency = self._calculate_recency_score(timestamp)
            
            # Normalize importance to 0-1
            normalized_importance = importance / 10.0
            
            # Combined score
            final_score = (
                self.recency_weight * recency +
                self.importance_weight * normalized_importance +
                self.relevance_weight * relevance
            )
            
            # Attach score to document
            doc.metadata['final_score'] = final_score
            doc.metadata['recency_score'] = recency
            doc.metadata['normalized_importance'] = normalized_importance
            doc.metadata['relevance_score'] = relevance
            
            scored_memories.append(doc)
        
        # Sort by final score
        scored_memories.sort(key=lambda m: m.metadata['final_score'], reverse=True)
        
        top_memories = scored_memories[:top_k]
        
        logger.info(f"Retrieved {len(top_memories)} memories (top score: {top_memories[0].metadata['final_score']:.3f})")
        
        return top_memories
    
    def clear_memories(self):
        """Clear all memories (for testing/reset)."""
        logger.warning("Clearing all memories")
        # Note: This requires the vector store to support clearing
        # Implementation depends on the specific vector store

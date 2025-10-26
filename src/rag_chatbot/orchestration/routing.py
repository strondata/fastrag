"""LLM routing for optimal model selection.

This module implements intelligent routing to select the best LLM
for a given task based on complexity, cost, and performance requirements.
"""

import logging
from typing import Dict, Optional
from enum import Enum
import numpy as np
from ..base import BaseComponent
from ..interfaces import ILocalLLM, IEmbeddingModel

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """LLM routing strategies."""
    SEMANTIC = "semantic"
    LLM_JUDGE = "llm_judge"
    RULE_BASED = "rule_based"


class Router(BaseComponent):
    """Routes prompts to the most appropriate LLM.
    
    Supports multiple routing strategies:
    - Semantic: Pre-computed task embeddings with similarity matching
    - LLM Judge: Uses a fast LLM to classify task complexity
    - Rule-based: Simple heuristics (query length, keywords)
    
    This optimizes for cost, latency, and quality by selecting
    the right model for each task.
    
    References:
        - LLM routing: "Match model capability to task complexity"
        - Cost optimization: "Use cheaper models for simple tasks"
        - Semantic routing: "Fast embedding-based classification"
    """
    
    def __init__(
        self,
        models: Dict[str, ILocalLLM],
        embedder: Optional[IEmbeddingModel] = None,
        default_strategy: RoutingStrategy = RoutingStrategy.RULE_BASED,
        **config
    ):
        """Initialize the router.
        
        Args:
            models: Dictionary mapping task types to LLM instances.
                   e.g., {"simple": llm1, "complex": llm2, "router": fast_llm}
            embedder: Optional embedding model for semantic routing.
            default_strategy: Default routing strategy.
            **config: Additional configuration.
        """
        super().__init__(
            models=models,
            embedder=embedder,
            default_strategy=default_strategy,
            **config
        )
        self.models = models
        self.embedder = embedder
        self.default_strategy = default_strategy
        
        # Pre-compute task embeddings for semantic routing
        self.task_embeddings = {}
        if embedder:
            self._precompute_task_embeddings()
        
        logger.info(f"Router initialized with {len(models)} models, "
                   f"strategy={default_strategy.value}")
    
    def _precompute_task_embeddings(self):
        """Pre-compute embeddings for task categories."""
        if not self.embedder:
            return
        
        # Define task categories with example queries
        task_categories = {
            "simple": [
                "What is X?",
                "Define Y",
                "List the features",
                "Simple factual question"
            ],
            "complex": [
                "Analyze the trade-offs between X and Y",
                "Explain the reasoning behind Z",
                "Compare and contrast A and B in detail",
                "Multi-step reasoning problem"
            ],
            "creative": [
                "Write a story about X",
                "Generate ideas for Y",
                "Create a plan for Z",
                "Brainstorm solutions"
            ]
        }
        
        logger.debug("Pre-computing task category embeddings...")
        
        for category, examples in task_categories.items():
            # Compute average embedding for this category
            embeddings = self.embedder.embed_documents(examples)
            avg_embedding = np.mean(embeddings, axis=0).tolist()
            self.task_embeddings[category] = avg_embedding
        
        logger.info(f"Pre-computed embeddings for {len(self.task_embeddings)} categories")
    
    def _route_semantic(self, query_text: str) -> ILocalLLM:
        """Route using semantic similarity to task categories.
        
        Args:
            query_text: The query to route.
            
        Returns:
            Selected LLM.
        """
        if not self.embedder or not self.task_embeddings:
            logger.warning("Semantic routing unavailable, falling back to rule-based")
            return self._route_rule_based(query_text)
        
        # Embed the query
        query_embedding = self.embedder.embed_query(query_text)
        
        # Find closest task category
        best_category = None
        best_similarity = -1
        
        for category, category_embedding in self.task_embeddings.items():
            # Calculate cosine similarity
            similarity = np.dot(query_embedding, category_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(category_embedding)
            )
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_category = category
        
        logger.debug(f"Semantic routing: '{best_category}' (similarity: {best_similarity:.3f})")
        
        # Map category to model
        if best_category in self.models:
            return self.models[best_category]
        elif "simple" in self.models:
            return self.models["simple"]
        else:
            # Return first available model
            return next(iter(self.models.values()))
    
    def _route_llm_judge(self, query_text: str) -> ILocalLLM:
        """Route using an LLM to judge task complexity.
        
        Args:
            query_text: The query to route.
            
        Returns:
            Selected LLM.
        """
        # Use a fast, cheap model as the router
        router_llm = self.models.get("router")
        
        if not router_llm:
            logger.warning("No router LLM configured, falling back to rule-based")
            return self._route_rule_based(query_text)
        
        judge_prompt = f"""Classify the following task as "simple" or "complex".

Simple tasks: factual questions, definitions, simple lookups
Complex tasks: multi-step reasoning, analysis, comparisons, creative tasks

Task: "{query_text}"

Classification (respond with only "simple" or "complex"):"""
        
        try:
            response = router_llm.generate(judge_prompt).strip().lower()
            
            if "simple" in response:
                classification = "simple"
            elif "complex" in response:
                classification = "complex"
            else:
                logger.warning(f"Unexpected classification: {response}")
                classification = "simple"
            
            logger.debug(f"LLM judge routing: '{classification}'")
            
            # Return appropriate model
            if classification in self.models:
                return self.models[classification]
            else:
                return self.models.get("simple", next(iter(self.models.values())))
                
        except Exception as e:
            logger.error(f"LLM judge routing failed: {e}")
            return self._route_rule_based(query_text)
    
    def _route_rule_based(self, query_text: str) -> ILocalLLM:
        """Route using simple heuristic rules.
        
        Args:
            query_text: The query to route.
            
        Returns:
            Selected LLM.
        """
        # Simple heuristics
        query_length = len(query_text.split())
        
        # Keywords indicating complexity
        complex_keywords = [
            "analyze", "compare", "contrast", "explain why", "reasoning",
            "trade-off", "multi-step", "detailed", "comprehensive"
        ]
        
        is_complex = (
            query_length > 20 or
            any(keyword in query_text.lower() for keyword in complex_keywords)
        )
        
        classification = "complex" if is_complex else "simple"
        logger.debug(f"Rule-based routing: '{classification}' (length={query_length})")
        
        # Return appropriate model
        if classification in self.models:
            return self.models[classification]
        else:
            # Return first available model
            return next(iter(self.models.values()))
    
    def route(self, query_text: str, strategy: Optional[RoutingStrategy] = None) -> ILocalLLM:
        """Route a query to the appropriate LLM.
        
        Args:
            query_text: The query to route.
            strategy: Optional override for routing strategy.
            
        Returns:
            Selected LLM for this query.
        """
        routing_strategy = strategy or self.default_strategy
        
        if routing_strategy == RoutingStrategy.SEMANTIC:
            return self._route_semantic(query_text)
        elif routing_strategy == RoutingStrategy.LLM_JUDGE:
            return self._route_llm_judge(query_text)
        elif routing_strategy == RoutingStrategy.RULE_BASED:
            return self._route_rule_based(query_text)
        else:
            raise ValueError(f"Unknown routing strategy: {routing_strategy}")
    
    def run(self, data, **kwargs):
        """Execute routing.
        
        Args:
            data: Query text to route.
            **kwargs: Additional parameters (strategy override).
            
        Returns:
            Selected LLM.
        """
        strategy = kwargs.get('strategy')
        if strategy and isinstance(strategy, str):
            strategy = RoutingStrategy(strategy)
        
        return self.route(data, strategy=strategy)

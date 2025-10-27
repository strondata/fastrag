"""Prompt compression techniques for reducing token usage.

This module implements methods to compress prompts before sending
to LLMs, reducing latency and API costs while preserving key information.
"""

import logging
import re
from typing import Optional
from ..base import BaseComponent
from ..interfaces import ILocalLLM

logger = logging.getLogger(__name__)


class PromptCompressor(BaseComponent):
    """Compress prompts to reduce token consumption.
    
    Implements multiple compression strategies:
    - Summarization using a fast LLM
    - Simple heuristics (removing redundancy, stopwords)
    - Length-based truncation
    
    References:
        - LLMLingua: "Prompt compression maintains quality with fewer tokens"
        - Selective context: "Not all context is equally important"
        - Cost optimization: "Shorter prompts = lower costs"
    """
    
    def __init__(
        self,
        summarization_llm: Optional[ILocalLLM] = None,
        compression_ratio: float = 0.5,
        **config
    ):
        """Initialize prompt compressor.
        
        Args:
            summarization_llm: Optional LLM for summarization-based compression.
            compression_ratio: Target compression ratio (0-1).
            **config: Additional configuration.
        """
        super().__init__(
            summarization_llm=summarization_llm,
            compression_ratio=compression_ratio,
            **config
        )
        self.summarization_llm = summarization_llm
        self.compression_ratio = compression_ratio
        logger.info(f"PromptCompressor initialized (ratio={compression_ratio})")
    
    def compress_by_summarization(self, prompt_text: str, ratio: float = None) -> str:
        """Compress prompt using LLM summarization.
        
        Args:
            prompt_text: Original prompt.
            ratio: Compression ratio override.
            
        Returns:
            Compressed prompt.
        """
        if not self.summarization_llm:
            logger.warning("No summarization LLM configured, using heuristic compression")
            return self.compress_heuristic(prompt_text, ratio)
        
        target_ratio = ratio if ratio is not None else self.compression_ratio
        target_length = int(len(prompt_text) * target_ratio)
        
        summarization_prompt = f"""Summarize the following text to approximately {target_length} characters.
Preserve the most important information.

Text:
{prompt_text}

Summary:"""
        
        try:
            compressed = self.summarization_llm.generate(summarization_prompt)
            logger.debug(f"Summarization: {len(prompt_text)} -> {len(compressed)} chars")
            return compressed.strip()
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return self.compress_heuristic(prompt_text, ratio)
    
    def compress_heuristic(self, prompt_text: str, ratio: float = None) -> str:
        """Compress prompt using simple heuristics.
        
        Removes redundancy, extra whitespace, and less important parts.
        
        Args:
            prompt_text: Original prompt.
            ratio: Compression ratio override.
            
        Returns:
            Compressed prompt.
        """
        target_ratio = ratio if ratio is not None else self.compression_ratio
        
        # Step 1: Remove extra whitespace
        compressed = re.sub(r'\s+', ' ', prompt_text)
        compressed = compressed.strip()
        
        # Step 2: Remove common filler phrases
        fillers = [
            r'as I mentioned before,?\s*',
            r'to be honest,?\s*',
            r'in my opinion,?\s*',
            r'I think that\s*',
            r'it seems like\s*',
        ]
        
        for filler in fillers:
            compressed = re.sub(filler, '', compressed, flags=re.IGNORECASE)
        
        # Step 3: If still too long, truncate while preserving question
        target_length = int(len(prompt_text) * target_ratio)
        
        if len(compressed) > target_length:
            # Try to keep the question at the end
            question_match = re.search(r'(QUESTION|PERGUNTA|Question|Pergunta):\s*(.+?)$', 
                                      compressed, re.IGNORECASE | re.DOTALL)
            
            if question_match:
                question_part = question_match.group(0)
                remaining_budget = target_length - len(question_part)
                
                if remaining_budget > 100:  # Keep some context
                    context_part = compressed[:remaining_budget]
                    compressed = context_part + "\n\n" + question_part
                else:
                    # Just keep the question if no room for context
                    compressed = question_part
            else:
                # No question found, simple truncation
                compressed = compressed[:target_length]
        
        logger.debug(f"Heuristic compression: {len(prompt_text)} -> {len(compressed)} chars")
        return compressed
    
    def compress(self, prompt_text: str, method: str = "heuristic", ratio: float = None) -> str:
        """Compress a prompt using specified method.
        
        Args:
            prompt_text: Original prompt.
            method: Compression method ('summarization' or 'heuristic').
            ratio: Compression ratio override.
            
        Returns:
            Compressed prompt.
        """
        if method == "summarization":
            return self.compress_by_summarization(prompt_text, ratio)
        elif method == "heuristic":
            return self.compress_heuristic(prompt_text, ratio)
        else:
            raise ValueError(f"Unknown compression method: {method}")
    
    def run(self, data, **kwargs):
        """Execute prompt compression.
        
        Args:
            data: Prompt text to compress.
            **kwargs: Compression parameters (method, ratio).
            
        Returns:
            Compressed prompt.
        """
        method = kwargs.get('method', 'heuristic')
        ratio = kwargs.get('ratio', None)
        return self.compress(data, method=method, ratio=ratio)

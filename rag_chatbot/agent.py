"""ReAct-style agent implementation.

This module implements an agent that uses Reasoning and Acting (ReAct)
to solve complex tasks by iteratively thinking and using tools.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from rag_chatbot.tools import BaseTool
from rag_chatbot.interfaces import ILocalLLM

logger = logging.getLogger(__name__)


class Agent:
    """ReAct-style reasoning agent.
    
    Implements the Reason + Act paradigm where the agent:
    1. Thinks about what to do (Thought)
    2. Decides on an action and tool to use (Action)
    3. Observes the result (Observation)
    4. Repeats until it has a final answer
    
    References:
        - ReAct: "Reasoning and Acting improves problem-solving"
        - Tool use: "LLMs can learn to use tools effectively"
        - Chain of thought: "Explicit reasoning improves accuracy"
    """
    
    REACT_PROMPT_TEMPLATE = """You are a helpful assistant that thinks step-by-step and uses tools to solve problems.

Available tools:
{tools_description}

Use the following format:

Thought: [Think about what to do next]
Action: [tool_name]
Action Input: [input for the tool]
Observation: [result from the tool - this will be filled in automatically]

Repeat Thought/Action/Observation as needed.

When you have the final answer, use:
Thought: I now have enough information to answer
Final Answer: [your answer here]

Question: {question}

Begin!
"""
    
    def __init__(
        self,
        llm: ILocalLLM,
        tools: List[BaseTool],
        memory: Optional[Any] = None,
        max_iterations: int = 5,
        **config
    ):
        """Initialize the agent.
        
        Args:
            llm: Language model for reasoning.
            tools: List of available tools.
            memory: Optional memory system.
            max_iterations: Maximum reasoning iterations.
            **config: Additional configuration.
        """
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.memory = memory
        self.max_iterations = max_iterations
        self.config = config
        
        logger.info(f"Agent initialized with {len(tools)} tools, max_iterations={max_iterations}")
    
    def _build_tools_description(self) -> str:
        """Build description of available tools.
        
        Returns:
            Formatted string describing all tools.
        """
        descriptions = []
        for name, tool in self.tools.items():
            descriptions.append(f"- {name}: {tool.description}")
        return "\n".join(descriptions)
    
    def _parse_thought(self, response: str) -> str:
        """Extract the thought from agent response.
        
        Args:
            response: LLM response.
            
        Returns:
            Extracted thought.
        """
        match = re.search(r'Thought:\s*(.+?)(?=\n|Action:|$)', response, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _parse_action(self, response: str) -> tuple:
        """Extract action and action input from response.
        
        Args:
            response: LLM response.
            
        Returns:
            Tuple of (action_name, action_input).
        """
        # Look for "Final Answer"
        final_match = re.search(r'Final Answer:\s*(.+)', response, re.DOTALL | re.IGNORECASE)
        if final_match:
            return ("Final Answer", final_match.group(1).strip())
        
        # Look for regular action
        action_match = re.search(r'Action:\s*(.+?)(?=\n|$)', response, re.IGNORECASE)
        input_match = re.search(r'Action Input:\s*(.+?)(?=\n|$)', response, re.DOTALL | re.IGNORECASE)
        
        action = action_match.group(1).strip() if action_match else None
        action_input = input_match.group(1).strip() if input_match else None
        
        return (action, action_input)
    
    def run(self, user_query: str, verbose: bool = False) -> str:
        """Execute the agent to answer a query.
        
        Args:
            user_query: User's question or task.
            verbose: Whether to log the reasoning process.
            
        Returns:
            Final answer.
        """
        logger.info(f"Agent processing query: {user_query[:50]}...")
        
        # Build initial prompt
        tools_desc = self._build_tools_description()
        prompt = self.REACT_PROMPT_TEMPLATE.format(
            tools_description=tools_desc,
            question=user_query
        )
        
        # ReAct loop: Thought -> Action -> Observation
        for iteration in range(self.max_iterations):
            logger.debug(f"Agent iteration {iteration + 1}/{self.max_iterations}")
            
            # Get LLM response
            try:
                response = self.llm.generate(prompt)
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                return f"I encountered an error while thinking: {str(e)}"
            
            if verbose:
                logger.info(f"\n--- Iteration {iteration + 1} ---\n{response}\n")
            
            # Parse thought and action
            thought = self._parse_thought(response)
            action, action_input = self._parse_action(response)
            
            # Check for final answer
            if action == "Final Answer":
                logger.info(f"Agent found final answer in {iteration + 1} iterations")
                return action_input
            
            # Execute action
            if action and action in self.tools:
                tool = self.tools[action]
                logger.debug(f"Executing tool: {action}")
                
                try:
                    observation = tool.use(action_input)
                except Exception as e:
                    observation = f"Error using tool: {str(e)}"
                    logger.error(f"Tool execution failed: {e}")
                
                # Add to prompt for next iteration
                prompt += f"\n\nThought: {thought}\nAction: {action}\nAction Input: {action_input}\nObservation: {observation}\n"
                
                if verbose:
                    logger.info(f"Observation: {observation}\n")
            else:
                # Tool not found or no action specified
                if action:
                    observation = f"Error: Tool '{action}' not found. Available tools: {list(self.tools.keys())}"
                else:
                    observation = "Error: No action specified. Please specify an action."
                
                prompt += f"\n\nObservation: {observation}\n"
        
        # Max iterations reached
        logger.warning(f"Agent reached max iterations ({self.max_iterations}) without final answer")
        return "I couldn't find a complete answer within the allowed thinking steps. Please try rephrasing your question or breaking it into smaller parts."
    
    def add_tool(self, tool: BaseTool):
        """Add a new tool to the agent.
        
        Args:
            tool: Tool to add.
        """
        self.tools[tool.name] = tool
        logger.info(f"Added tool: {tool.name}")
    
    def remove_tool(self, tool_name: str):
        """Remove a tool from the agent.
        
        Args:
            tool_name: Name of tool to remove.
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Removed tool: {tool_name}")

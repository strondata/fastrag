"""Multi-agent orchestration framework.

This module implements a crew-based multi-agent system inspired by crewAI,
allowing specialized agents to collaborate on complex tasks.
"""

import logging
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from .tools import BaseTool
from ..interfaces import ILocalLLM

logger = logging.getLogger(__name__)


class ProcessType(Enum):
    """Workflow process types."""
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"


@dataclass
class CrewAgent:
    """Specialized agent with a defined role and goal.
    
    Each CrewAgent has:
    - role: Their function in the team
    - goal: What they're trying to achieve
    - backstory: Context that shapes their behavior
    - tools: Capabilities they can use
    
    Attributes:
        role: Agent's role (e.g., "Researcher", "Writer").
        goal: Agent's objective.
        backstory: Agent's background and expertise.
        tools: List of tools available to the agent.
        llm: Language model for the agent.
    """
    role: str
    goal: str
    backstory: str
    tools: List[BaseTool]
    llm: Optional[ILocalLLM] = None
    
    def __post_init__(self):
        """Initialize agent after creation."""
        logger.info(f"CrewAgent created: {self.role}")
    
    def execute(self, task: 'Task', context: str = "") -> str:
        """Execute a task.
        
        Args:
            task: Task to execute.
            context: Context from previous tasks.
            
        Returns:
            Task result.
        """
        logger.info(f"Agent '{self.role}' executing task: {task.description[:50]}...")
        
        # Build prompt for the agent
        prompt = f"""You are a {self.role}.
Goal: {self.goal}
Background: {self.backstory}

{"Context from previous tasks: " + context if context else ""}

Task: {task.description}

Expected output: {task.expected_output}

Please complete this task:"""
        
        if self.llm:
            try:
                result = self.llm.generate(prompt)
                logger.debug(f"Agent '{self.role}' completed task")
                return result
            except Exception as e:
                logger.error(f"Agent '{self.role}' failed: {e}")
                return f"Error executing task: {str(e)}"
        else:
            # No LLM - return a placeholder
            return f"[{self.role}] Task completed: {task.description}"


@dataclass
class Task:
    """A unit of work to be completed by an agent.
    
    Attributes:
        description: What needs to be done.
        expected_output: What the output should look like.
        agent: Which agent should do this task.
        context: Optional list of tasks that provide context.
    """
    description: str
    expected_output: str
    agent: CrewAgent
    context: Optional[List['Task']] = None
    
    def __post_init__(self):
        """Initialize task after creation."""
        logger.debug(f"Task created for agent '{self.agent.role}'")


class Crew:
    """Orchestrates a team of agents to complete tasks.
    
    The Crew manages workflow, task assignment, and information
    flow between agents. Supports sequential and hierarchical processes.
    
    References:
        - crewAI: "Multi-agent collaboration framework"
        - Task delegation: "Specialized agents improve quality"
        - Workflow orchestration: "Sequential and hierarchical patterns"
    """
    
    def __init__(
        self,
        agents: List[CrewAgent],
        tasks: List[Task],
        process: ProcessType = ProcessType.SEQUENTIAL,
        verbose: bool = False,
        **config
    ):
        """Initialize the crew.
        
        Args:
            agents: List of agents in the crew.
            tasks: List of tasks to complete.
            process: Workflow process type.
            verbose: Whether to log detailed progress.
            **config: Additional configuration.
        """
        self.agents = agents
        self.tasks = tasks
        self.process = process
        self.verbose = verbose
        self.config = config
        
        logger.info(f"Crew initialized with {len(agents)} agents, "
                   f"{len(tasks)} tasks, process={process.value}")
    
    def kickoff(self) -> str:
        """Start the crew's work.
        
        Executes all tasks according to the defined process.
        
        Returns:
            Final output from the last task.
        """
        logger.info(f"Crew starting work ({self.process.value} process)")
        
        if self.process == ProcessType.SEQUENTIAL:
            return self._execute_sequential()
        elif self.process == ProcessType.HIERARCHICAL:
            return self._execute_hierarchical()
        else:
            raise ValueError(f"Unknown process type: {self.process}")
    
    def _execute_sequential(self) -> str:
        """Execute tasks sequentially.
        
        Each task's output becomes context for the next task.
        
        Returns:
            Output from the final task.
        """
        logger.debug("Executing sequential workflow")
        
        context = ""
        final_output = ""
        
        for i, task in enumerate(self.tasks):
            if self.verbose:
                logger.info(f"\n{'='*60}")
                logger.info(f"Task {i+1}/{len(self.tasks)}: {task.description[:50]}...")
                logger.info(f"Agent: {task.agent.role}")
                logger.info(f"{'='*60}\n")
            
            # Execute task with accumulated context
            result = task.agent.execute(task, context=context)
            
            if self.verbose:
                logger.info(f"Result: {result[:100]}...\n")
            
            # Add result to context for next task
            context += f"\n\n--- Task {i+1} Output ---\n{result}"
            final_output = result
        
        logger.info("Sequential workflow completed")
        return final_output
    
    def _execute_hierarchical(self) -> str:
        """Execute tasks in a hierarchical manner.
        
        Tasks can have dependencies and context from specific previous tasks.
        
        Returns:
            Combined output from all tasks.
        """
        logger.debug("Executing hierarchical workflow")
        
        task_outputs: Dict[int, str] = {}
        
        for i, task in enumerate(self.tasks):
            if self.verbose:
                logger.info(f"\nExecuting task {i+1}: {task.description[:50]}...")
            
            # Build context from dependent tasks
            context = ""
            if task.context:
                for ctx_task in task.context:
                    task_idx = self.tasks.index(ctx_task)
                    if task_idx in task_outputs:
                        context += f"\n\n--- Context from '{ctx_task.description[:30]}' ---\n"
                        context += task_outputs[task_idx]
            
            # Execute task
            result = task.agent.execute(task, context=context)
            task_outputs[i] = result
            
            if self.verbose:
                logger.info(f"Result: {result[:100]}...\n")
        
        # Combine all outputs
        final_output = "\n\n".join(
            f"=== Task {i+1}: {task.description[:40]} ===\n{output}"
            for i, (task, output) in enumerate(zip(self.tasks, task_outputs.values()))
        )
        
        logger.info("Hierarchical workflow completed")
        return final_output
    
    def add_agent(self, agent: CrewAgent):
        """Add an agent to the crew.
        
        Args:
            agent: Agent to add.
        """
        self.agents.append(agent)
        logger.info(f"Added agent: {agent.role}")
    
    def add_task(self, task: Task):
        """Add a task to the crew.
        
        Args:
            task: Task to add.
        """
        self.tasks.append(task)
        logger.debug(f"Added task for agent: {task.agent.role}")

"""Tests for Phase 4 components: crew orchestration and routing."""

import pytest
from unittest.mock import Mock, MagicMock
from rag_chatbot.crew import CrewAgent, Task, Crew, ProcessType
from rag_chatbot.routing import Router, RoutingStrategy
from rag_chatbot.tools import BaseTool


class TestCrewAgent:
    """Tests for CrewAgent."""
    
    def test_crew_agent_creation(self):
        """Test creating a crew agent."""
        tools = [Mock(spec=BaseTool)]
        
        agent = CrewAgent(
            role="Researcher",
            goal="Find accurate information",
            backstory="Expert researcher with 10 years experience",
            tools=tools
        )
        
        assert agent.role == "Researcher"
        assert agent.goal == "Find accurate information"
        assert len(agent.tools) == 1
    
    def test_crew_agent_execute_with_llm(self):
        """Test agent executing a task with LLM."""
        mock_llm = Mock()
        mock_llm.generate.return_value = "Research completed successfully"
        
        agent = CrewAgent(
            role="Researcher",
            goal="Research topics",
            backstory="Expert researcher",
            tools=[],
            llm=mock_llm
        )
        
        task = Task(
            description="Research Python programming",
            expected_output="Comprehensive research summary",
            agent=agent
        )
        
        result = agent.execute(task, context="")
        
        assert "Research completed" in result
        mock_llm.generate.assert_called_once()
    
    def test_crew_agent_execute_without_llm(self):
        """Test agent executing without LLM (placeholder mode)."""
        agent = CrewAgent(
            role="Writer",
            goal="Write content",
            backstory="Professional writer",
            tools=[]
        )
        
        task = Task(
            description="Write blog post",
            expected_output="Blog post content",
            agent=agent
        )
        
        result = agent.execute(task)
        
        assert "Writer" in result
        assert "Task completed" in result


class TestTask:
    """Tests for Task."""
    
    def test_task_creation(self):
        """Test creating a task."""
        agent = CrewAgent(
            role="Analyst",
            goal="Analyze data",
            backstory="Data analyst",
            tools=[]
        )
        
        task = Task(
            description="Analyze sales data",
            expected_output="Analysis report",
            agent=agent
        )
        
        assert task.description == "Analyze sales data"
        assert task.expected_output == "Analysis report"
        assert task.agent.role == "Analyst"


class TestCrew:
    """Tests for Crew orchestration."""
    
    @pytest.fixture
    def sample_crew(self):
        """Create a sample crew with agents and tasks."""
        # Create agents
        researcher = CrewAgent(
            role="Researcher",
            goal="Research information",
            backstory="Expert researcher",
            tools=[],
            llm=Mock()
        )
        
        writer = CrewAgent(
            role="Writer",
            goal="Write content",
            backstory="Professional writer",
            tools=[],
            llm=Mock()
        )
        
        # Configure mock LLMs
        researcher.llm.generate.return_value = "Research findings: Python is a programming language"
        writer.llm.generate.return_value = "Article: Python Programming Guide"
        
        # Create tasks
        research_task = Task(
            description="Research Python programming",
            expected_output="Research summary",
            agent=researcher
        )
        
        writing_task = Task(
            description="Write article based on research",
            expected_output="Complete article",
            agent=writer
        )
        
        # Create crew
        crew = Crew(
            agents=[researcher, writer],
            tasks=[research_task, writing_task],
            process=ProcessType.SEQUENTIAL
        )
        
        return crew
    
    def test_crew_initialization(self, sample_crew):
        """Test crew initialization."""
        assert len(sample_crew.agents) == 2
        assert len(sample_crew.tasks) == 2
        assert sample_crew.process == ProcessType.SEQUENTIAL
    
    def test_sequential_workflow(self, sample_crew):
        """Test sequential task execution."""
        result = sample_crew.kickoff()
        
        # Should execute both tasks
        assert sample_crew.tasks[0].agent.llm.generate.called
        assert sample_crew.tasks[1].agent.llm.generate.called
        
        # Result should be from last task
        assert "Article" in result or "Python Programming" in result
    
    def test_hierarchical_workflow(self):
        """Test hierarchical task execution with dependencies."""
        # Create agents
        agent1 = CrewAgent(
            role="Agent1",
            goal="Task 1",
            backstory="First agent",
            tools=[],
            llm=Mock()
        )
        
        agent2 = CrewAgent(
            role="Agent2",
            goal="Task 2",
            backstory="Second agent",
            tools=[],
            llm=Mock()
        )
        
        agent1.llm.generate.return_value = "Result 1"
        agent2.llm.generate.return_value = "Result 2"
        
        # Create tasks with dependencies
        task1 = Task(
            description="First task",
            expected_output="Output 1",
            agent=agent1
        )
        
        task2 = Task(
            description="Second task with context",
            expected_output="Output 2",
            agent=agent2,
            context=[task1]
        )
        
        crew = Crew(
            agents=[agent1, agent2],
            tasks=[task1, task2],
            process=ProcessType.HIERARCHICAL
        )
        
        result = crew.kickoff()
        
        # Both tasks should be executed
        assert agent1.llm.generate.called
        assert agent2.llm.generate.called
        # Result should contain both outputs
        assert "Result 1" in result or "Result 2" in result
    
    def test_add_agent_and_task(self):
        """Test adding agents and tasks to crew."""
        crew = Crew(agents=[], tasks=[], process=ProcessType.SEQUENTIAL)
        
        agent = CrewAgent(
            role="NewAgent",
            goal="New goal",
            backstory="New backstory",
            tools=[]
        )
        
        task = Task(
            description="New task",
            expected_output="New output",
            agent=agent
        )
        
        crew.add_agent(agent)
        crew.add_task(task)
        
        assert len(crew.agents) == 1
        assert len(crew.tasks) == 1


class TestRouter:
    """Tests for LLM Router."""
    
    @pytest.fixture
    def mock_llms(self):
        """Create mock LLMs for routing."""
        simple_llm = Mock()
        simple_llm.generate.return_value = "Simple answer"
        
        complex_llm = Mock()
        complex_llm.generate.return_value = "Complex answer"
        
        router_llm = Mock()
        router_llm.generate.return_value = "simple"
        
        return {
            "simple": simple_llm,
            "complex": complex_llm,
            "router": router_llm
        }
    
    def test_router_initialization(self, mock_llms):
        """Test router initialization."""
        router = Router(
            models=mock_llms,
            default_strategy=RoutingStrategy.RULE_BASED
        )
        
        assert len(router.models) == 3
        assert router.default_strategy == RoutingStrategy.RULE_BASED
    
    def test_rule_based_routing_simple(self, mock_llms):
        """Test rule-based routing for simple query."""
        router = Router(models=mock_llms)
        
        simple_query = "What is Python?"
        selected_llm = router.route(simple_query, strategy=RoutingStrategy.RULE_BASED)
        
        # Should select simple model
        assert selected_llm == mock_llms["simple"]
    
    def test_rule_based_routing_complex(self, mock_llms):
        """Test rule-based routing for complex query."""
        router = Router(models=mock_llms)
        
        complex_query = "Analyze and compare the trade-offs between functional and object-oriented programming paradigms"
        selected_llm = router.route(complex_query, strategy=RoutingStrategy.RULE_BASED)
        
        # Should select complex model
        assert selected_llm == mock_llms["complex"]
    
    def test_llm_judge_routing(self, mock_llms):
        """Test LLM-based routing."""
        # Mock router LLM to classify as simple
        mock_llms["router"].generate.return_value = "simple"
        
        router = Router(models=mock_llms)
        
        query = "What is the capital of France?"
        selected_llm = router.route(query, strategy=RoutingStrategy.LLM_JUDGE)
        
        # Should call router LLM
        mock_llms["router"].generate.assert_called_once()
        # Should select simple model based on classification
        assert selected_llm == mock_llms["simple"]
    
    def test_semantic_routing_with_embedder(self, mock_llms):
        """Test semantic routing with embeddings."""
        mock_embedder = Mock()
        # Return different embeddings for categories
        mock_embedder.embed_documents.return_value = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ]
        mock_embedder.embed_query.return_value = [0.9, 0.1, 0.0]
        
        router = Router(
            models=mock_llms,
            embedder=mock_embedder
        )
        
        query = "Simple question"
        selected_llm = router.route(query, strategy=RoutingStrategy.SEMANTIC)
        
        # Should call embedder
        mock_embedder.embed_query.assert_called_once()
    
    def test_semantic_routing_fallback(self, mock_llms):
        """Test semantic routing falls back when no embedder."""
        router = Router(models=mock_llms, embedder=None)
        
        query = "Test query"
        selected_llm = router.route(query, strategy=RoutingStrategy.SEMANTIC)
        
        # Should fall back to rule-based
        assert selected_llm in mock_llms.values()
    
    def test_run_method(self, mock_llms):
        """Test run() method."""
        router = Router(models=mock_llms)
        
        result = router.run("What is AI?", strategy="rule_based")
        
        assert result in mock_llms.values()

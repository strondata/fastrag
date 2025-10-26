"""Comprehensive unit tests for LLMs."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.rag_chatbot.components.llms import OllamaLLM, MockLLM


class TestOllamaLLM:
    """Test suite for OllamaLLM."""
    
    @pytest.fixture
    def mock_ollama_client(self):
        """Mock ollama client."""
        with patch('rag_chatbot.components.llms.ollama.Client') as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            yield mock_instance
    
    def test_init_default_model(self, mock_ollama_client):
        """Test initialization with default model."""
        llm = OllamaLLM()
        assert llm.model_name is not None
        assert llm.client is not None
    
    def test_init_custom_model(self, mock_ollama_client):
        """Test initialization with custom model name."""
        llm = OllamaLLM(model_name="mistral")
        assert llm.model_name == "mistral"
    
    def test_generate_success(self, mock_ollama_client):
        """Test successful text generation."""
        # Setup mock response - generate returns dict with 'response' key
        mock_response = {'response': 'Generated response'}
        mock_ollama_client.generate.return_value = mock_response
        
        llm = OllamaLLM()
        result = llm.generate("Test prompt")
        
        assert result == 'Generated response'
        mock_ollama_client.generate.assert_called_once()
    
    def test_generate_with_images(self, mock_ollama_client):
        """Test generation with images (multimodal)."""
        mock_response = {'response': 'Response with image analysis'}
        mock_ollama_client.generate.return_value = mock_response
        
        llm = OllamaLLM()
        result = llm.generate("Describe this image", images_base64=["base64_image_data"])
        
        assert result == 'Response with image analysis'
    
    def test_generate_empty_prompt(self, mock_ollama_client):
        """Test generation with empty prompt."""
        mock_response = {'response': ''}
        mock_ollama_client.generate.return_value = mock_response
        
        llm = OllamaLLM()
        result = llm.generate("")
        
        assert result == ''
    
    def test_generate_error_handling(self, mock_ollama_client):
        """Test error handling in generate."""
        mock_ollama_client.generate.side_effect = Exception("Connection error")
        
        llm = OllamaLLM()
        
        # OllamaLLM catches exceptions and returns error message
        result = llm.generate("Test prompt")
        assert "Erro ao contatar o LLM" in result
    
    def test_generate_with_multiline_prompt(self, mock_ollama_client):
        """Test generation with multiline prompt."""
        mock_response = {'response': 'Multiline response'}
        mock_ollama_client.generate.return_value = mock_response
        
        llm = OllamaLLM()
        prompt = """Line 1
        Line 2
        Line 3"""
        
        result = llm.generate(prompt)
        assert result == 'Multiline response'


class TestMockLLM:
    """Test suite for MockLLM."""
    
    def test_generate_default_response(self):
        """Test default mock response."""
        llm = MockLLM()
        result = llm.generate("Any prompt")
        
        assert result == "Esta é uma resposta mock do LLM."
    
    def test_generate_custom_response(self):
        """Test custom mock response."""
        custom_response = "Custom test response"
        llm = MockLLM(default_response=custom_response)
        
        result = llm.generate("Any prompt")
        assert result == custom_response
    
    def test_generate_with_different_prompts(self):
        """Test that MockLLM returns same response for different prompts."""
        llm = MockLLM(default_response="Consistent response")
        
        result1 = llm.generate("Prompt 1")
        result2 = llm.generate("Prompt 2")
        
        assert result1 == result2 == "Consistent response"
    
    def test_generate_with_empty_prompt(self):
        """Test MockLLM with empty prompt."""
        llm = MockLLM()
        result = llm.generate("")
        
        assert result == "Esta é uma resposta mock do LLM."
    
    def test_generate_with_images(self):
        """Test MockLLM with images (should be ignored)."""
        llm = MockLLM()
        result = llm.generate("Describe image", images_base64=["base64_data"])
        
        # MockLLM should ignore images and return default
        assert result == "Esta é uma resposta mock do LLM."
    
    def test_mock_llm_for_testing_purposes(self):
        """Test that MockLLM is suitable for testing."""
        # This is useful for testing RAG pipeline without actual LLM
        llm = MockLLM(default_response="Test answer")
        
        # Simulate RAG usage
        context = "Some context"
        question = "Some question"
        prompt = f"Context: {context}\nQuestion: {question}"
        
        result = llm.generate(prompt)
        assert result == "Test answer"

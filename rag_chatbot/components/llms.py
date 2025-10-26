"""Implementações de Local LLMs."""

import logging
from typing import Optional

try:
    import ollama
except ImportError:
    ollama = None

from rag_chatbot.interfaces import ILocalLLM
from rag_chatbot.config import DEFAULT_LLM_MODEL, OLLAMA_HOST

logger = logging.getLogger(__name__)


class OllamaLLM(ILocalLLM):
    """LLM local usando Ollama.
    
    Conecta-se ao Ollama para geração de texto usando modelos locais.
    """
    
    def __init__(self, model_name: str = DEFAULT_LLM_MODEL):
        """Inicializa a conexão com Ollama.
        
        Args:
            model_name: Nome do modelo Ollama a usar (ex: 'llama3', 'mistral').
        """
        if ollama is None:
            logger.error("Pacote 'ollama' não está instalado. Execute: pip install ollama")
            raise ImportError("Pacote 'ollama' não encontrado")
        
        self.model_name = model_name
        
        # Configurar cliente Ollama com host customizado se especificado
        if OLLAMA_HOST:
            self.client = ollama.Client(host=OLLAMA_HOST)
            logger.info(f"LLM Local ({model_name}) configurado com host: {OLLAMA_HOST}")
        else:
            self.client = ollama.Client()
            logger.info(f"LLM Local ({model_name}) configurado com host padrão.")
        
        # Verificar se o modelo está disponível (opcional)
        try:
            # Tentar listar modelos para verificar conexão
            models = self.client.list()
            logger.debug(f"Ollama conectado. Modelos disponíveis verificados.")
        except Exception as e:
            logger.warning(f"Não foi possível verificar conexão com Ollama: {e}")
            logger.warning("Certifique-se de que o Ollama está rodando.")
    
    def generate(self, prompt: str) -> str:
        """Gera texto a partir de um prompt.
        
        Args:
            prompt: O prompt para geração.
            
        Returns:
            Texto gerado pelo modelo.
        """
        logger.debug(f"Gerando resposta com modelo {self.model_name}")
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                stream=False
            )
            
            generated_text = response['response']
            logger.debug(f"Resposta gerada com sucesso ({len(generated_text)} caracteres).")
            return generated_text
            
        except Exception as e:
            logger.error(f"Erro na geração do LLM: {e}")
            return f"Erro ao contatar o LLM: {str(e)}"


class MockLLM(ILocalLLM):
    """Mock LLM para testes sem necessidade de Ollama.
    
    Retorna respostas fixas ou baseadas em regras simples.
    """
    
    def __init__(self, default_response: str = "Esta é uma resposta mock do LLM."):
        """Inicializa o Mock LLM.
        
        Args:
            default_response: Resposta padrão a retornar.
        """
        self.default_response = default_response
        logger.info("Mock LLM inicializado (para testes).")
    
    def generate(self, prompt: str) -> str:
        """Retorna uma resposta mock.
        
        Args:
            prompt: O prompt (ignorado no mock).
            
        Returns:
            Resposta mock.
        """
        logger.debug("Mock LLM gerando resposta.")
        return self.default_response

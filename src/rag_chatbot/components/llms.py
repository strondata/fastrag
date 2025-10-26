"""Implementações de Local LLMs."""

import logging
from typing import Optional, List

try:
    import ollama
except ImportError:
    ollama = None

from rag_chatbot.interfaces import ILocalLLM
from rag_chatbot.config import DEFAULT_LLM_MODEL, DEFAULT_MULTIMODAL_LLM_MODEL, OLLAMA_HOST

logger = logging.getLogger(__name__)


class OllamaLLM(ILocalLLM):
    """LLM local usando Ollama.
    
    Conecta-se ao Ollama para geração de texto usando modelos locais.
    Suporta modelos multimodais quando imagens são fornecidas.
    """
    
    def __init__(
        self, 
        model_name: str = DEFAULT_LLM_MODEL,
        multimodal_model_name: str = DEFAULT_MULTIMODAL_LLM_MODEL
    ):
        """Inicializa a conexão com Ollama.
        
        Args:
            model_name: Nome do modelo Ollama a usar (ex: 'llama3', 'mistral').
            multimodal_model_name: Nome do modelo multimodal (ex: 'llava').
        """
        if ollama is None:
            logger.error("Pacote 'ollama' não está instalado. Execute: pip install ollama")
            raise ImportError("Pacote 'ollama' não encontrado")
        
        self.model_name = model_name
        self.multimodal_model_name = multimodal_model_name
        
        # Configurar cliente Ollama com host customizado se especificado
        if OLLAMA_HOST:
            self.client = ollama.Client(host=OLLAMA_HOST)
            logger.info(f"LLM Local ({model_name}) configurado com host: {OLLAMA_HOST}")
        else:
            self.client = ollama.Client()
            logger.info(f"LLM Local ({model_name}) configurado com host padrão.")
        
        logger.info(f"Modelo multimodal configurado: {multimodal_model_name}")
        
        # Verificar se o modelo está disponível (opcional)
        try:
            # Tentar listar modelos para verificar conexão
            models = self.client.list()
            logger.debug(f"Ollama conectado. Modelos disponíveis verificados.")
        except Exception as e:
            logger.warning(f"Não foi possível verificar conexão com Ollama: {e}")
            logger.warning("Certifique-se de que o Ollama está rodando.")
    
    def generate(self, prompt: str, images_base64: List[str] = None) -> str:
        """Gera texto a partir de um prompt.
        
        Args:
            prompt: O prompt para geração.
            images_base64: Lista de imagens em base64 (opcional, para modelos multimodais).
            
        Returns:
            Texto gerado pelo modelo.
        """
        # Escolher modelo baseado na presença de imagens
        if images_base64:
            model_to_use = self.multimodal_model_name
            logger.debug(f"Gerando resposta com modelo multimodal {model_to_use}")
        else:
            model_to_use = self.model_name
            logger.debug(f"Gerando resposta com modelo {model_to_use}")
        
        try:
            # Preparar parâmetros para a chamada
            params = {
                "model": model_to_use,
                "prompt": prompt,
                "stream": False
            }
            
            # Adicionar imagens se fornecidas
            if images_base64:
                params["images"] = images_base64
            
            response = self.client.generate(**params)
            
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
    
    def generate(self, prompt: str, images_base64: List[str] = None) -> str:
        """Retorna uma resposta mock.
        
        Args:
            prompt: O prompt (ignorado no mock).
            images_base64: Imagens (ignoradas no mock).
            
        Returns:
            Resposta mock.
        """
        logger.debug("Mock LLM gerando resposta.")
        if images_base64:
            logger.debug(f"Mock LLM recebeu {len(images_base64)} imagem(s).")
        return self.default_response

"""Configurações do RAG Chatbot."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Diretórios
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
LOGS_DIR = Path(os.getenv("LOGS_DIR", BASE_DIR / "logs"))
CHROMA_PERSIST_DIRECTORY = Path(os.getenv("CHROMA_PERSIST_DIRECTORY", BASE_DIR / "chroma_data"))

# Criar diretórios se não existirem
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
CHROMA_PERSIST_DIRECTORY.mkdir(exist_ok=True)

# Modelos
DEFAULT_EMBEDDING_MODEL = os.getenv("DEFAULT_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "llama3")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", None)

# Vector Store
DEFAULT_COLLECTION_NAME = os.getenv("DEFAULT_COLLECTION_NAME", "rag_store")

# RAG Settings
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "3"))

# Logging
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO")
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR.upper(), logging.INFO)
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "rag_chatbot.log"

# Configurar logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

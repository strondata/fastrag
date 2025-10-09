"""
Basic example of using FastRAG.
"""

from fastrag import RAGSystem


def main():
    # Initialize the RAG system
    rag = RAGSystem()
    
    # Add some documents
    documents = [
        "Python is a high-level programming language.",
        "FastRAG is a library for building RAG systems.",
        "Retrieval-Augmented Generation combines retrieval and generation.",
    ]
    
    for doc in documents:
        rag.add_document(doc)
    
    # Query the system
    query = "What is FastRAG?"
    response = rag.query(query)
    
    print(f"Query: {query}")
    print(f"Response: {response}")


if __name__ == "__main__":
    main()

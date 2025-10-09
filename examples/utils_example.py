"""
Example using utility functions.
"""

from fastrag.utils import chunk_text, preprocess_text


def main():
    # Example text
    text = """
    This is a longer text that we want to process.
    It contains multiple sentences and paragraphs.
    We can use the utility functions to preprocess and chunk it.
    """
    
    # Preprocess the text
    processed = preprocess_text(text)
    print("Preprocessed text:")
    print(processed)
    print()
    
    # Chunk the text
    chunks = chunk_text(processed, chunk_size=50, overlap=10)
    print(f"Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1}: {chunk}")


if __name__ == "__main__":
    main()

# Sample Data Files for FastRAG v3.0

This directory contains sample files demonstrating the multi-format support in FastRAG v3.0.

## Files Included

### 1. v3_features.md (Markdown)
Overview of FastRAG v3.0 features including:
- Smart document chunking
- Multi-format support
- Multimodal analysis
- Conversational memory

### 2. rag_concepts.md (Markdown)
Comprehensive guide to RAG (Retrieval-Augmented Generation):
- Core components
- Workflow and pipeline
- Best practices
- Evaluation metrics

### 3. faq.txt (Text)
Frequently Asked Questions about FastRAG covering:
- Installation and setup
- Feature usage
- Configuration
- Troubleshooting

### 4. quickstart.pdf (PDF)
Quick start guide in PDF format demonstrating PDF processing capability.

### 5. architecture.docx (Word Document)
System architecture overview in DOCX format demonstrating Word document processing.

## Usage

To use these sample files:

1. Copy this directory to your FastRAG data folder:
   ```bash
   cp -r sample_data/* data/
   ```

2. Start the FastRAG application:
   ```bash
   streamlit run app.py
   ```

3. Go to the "Manage RAG" tab and click "Feed RAG"

4. Start asking questions in the "Chat" tab, such as:
   - "What are the new features in v3.0?"
   - "How does RAG work?"
   - "How do I install FastRAG?"
   - "What is the system architecture?"

## Format Coverage

These files demonstrate all supported formats:
- ✅ `.txt` - Plain text (faq.txt)
- ✅ `.md` - Markdown (v3_features.md, rag_concepts.md)
- ✅ `.pdf` - PDF documents (quickstart.pdf)
- ✅ `.docx` - Word documents (architecture.docx)

## Testing Features

Use these files to test:

### 1. Smart Chunking
The larger files (rag_concepts.md, architecture.docx) will be split into multiple chunks. Check the source metadata to see chunk indices.

### 2. Multi-Format Loading
Upload all files at once - the UniversalLoader will automatically detect and process each format.

### 3. Cross-Document Queries
Ask questions that span multiple documents:
- "Compare the quick start steps with the installation instructions in the FAQ"
- "What does the architecture document say about the components mentioned in the features overview?"

### 4. Conversational Memory
Have multi-turn conversations:
- "What are the main RAG components?"
- "Tell me more about the second one"
- "How does it compare to the first one you mentioned?"

### 5. Source Verification
Click "View sources used" to see:
- Which file the information came from
- Which chunk within that file
- The exact text that was retrieved

## Notes

- These files contain comprehensive information about FastRAG and RAG systems
- They are designed to work well together for cross-referencing
- Total size is moderate (~60KB) for quick processing
- Content is in Portuguese to match the application's default language

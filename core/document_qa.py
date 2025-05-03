"""
Document Q&A Module for PDF Research Paper Q&A
Handles document processing and question answering.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

from pdf_research_qa.core.ollama_client import OllamaClient
from pdf_research_qa.core.pdf_processor import PDFProcessor, extract_title, extract_authors

class DocumentQA:
    def __init__(self, ollama_client: OllamaClient):
        """Initialize with an OllamaClient."""
        self.ollama = ollama_client
        self.chunks = []
        self.embeddings = []
        self.document_text = ""
        self.title = ""
        self.authors = ""
        
    def load_document(self, text: str, chunk_size: int = 1000, overlap: int = 200):
        """Load and process a document for Q&A."""
        self.document_text = text
        self.title = extract_title(text)
        self.authors = extract_authors(text)
        
        processor = PDFProcessor("")  # Empty path as we already have the text
        self.chunks = processor.split_text(text, chunk_size, overlap)
        
        self.embeddings = []
        for chunk in self.chunks:
            embedding = self.ollama.get_embedding(chunk)
            if embedding:
                self.embeddings.append(embedding)
        
    def answer_question(self, question: str, n_chunks: int = 3) -> str:
        """Answer a question based on the document."""
        # Get embedding for the question
        question_embedding = self.ollama.get_embedding(question)
        if not question_embedding:
            return "Failed to generate embedding for the question"
        
        # Calculate similarities
        similarities = []
        for emb in self.embeddings:
            similarity = cosine_similarity([question_embedding], [emb])[0][0]
            similarities.append(similarity)
        
        # Get indices of top N similar chunks
        if not similarities:
            return "No document chunks available for answering"
            
        top_indices = np.argsort(similarities)[-n_chunks:][::-1]
        
        # Build context from top chunks
        context = "\n\n".join([self.chunks[i] for i in top_indices])
        
        # Generate system prompt
        system_prompt = """You are a research assistant helping to answer questions based on the provided research paper.
Use ONLY the information from the provided context to answer the question.
If the answer cannot be determined from the context, say so clearly. 
Do not make up information or rely on prior knowledge."""
        
        # Build prompt
        prompt = f"""Context from research paper:
{context}

Question: {question}

Answer:"""
        
        # Generate answer
        return self.ollama.generate(prompt, system_prompt)
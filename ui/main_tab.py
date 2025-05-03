"""
Main tab for PDF Q&A functionality.
"""

import os
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

from ..core.ollama_client import OllamaClient
from ..core.document_qa import DocumentQA
from ..core.resource_monitor import ResourceMonitor
from .components import ResourceDisplayPanel, InfoDisplay


class MainTab(ttk.Frame):
    """Main tab for PDF Q&A functionality."""
    
    def __init__(self, parent, status_bar):
        """Initialize the main tab.
        
        Args:
            parent: Parent widget
            status_bar: Status bar for showing messages
        """
        super().__init__(parent, padding=10)
        self.status_bar = status_bar
        self.logger = None
        
        # Initialize Ollama client
        self.ollama_client = OllamaClient(model="gemma3:4b-it-q8_0")
        self.document_qa = None
        self.pdf_path = ""
        
        # Initialize resource monitor
        self.resource_monitor = ResourceMonitor()
        
        # Timing variables
        self.pdf_start_time = 0
        self.pdf_end_time = 0
        self.query_start_time = 0
        self.query_end_time = 0
        
        # Create the UI
        self.create_ui()
        
        # Populate models dropdown
        self.update_model_list()
        
        # Start periodic resource updates
        self.update_resource_info()
    
    def set_logger(self, logger):
        """Set the logger for this tab."""
        self.logger = logger
    
    def create_ui(self):
        """Create the user interface for the main tab."""
        # Configure the grid
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Left panel - PDF selection and model settings
        self.create_left_panel()
        
        # Right panel - Q&A interaction
        self.create_right_panel()
    
    def create_left_panel(self):
        """Create the left panel with settings and document info."""
        left_frame = ttk.LabelFrame(self, text="Settings", padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # PDF selection
        ttk.Label(left_frame, text="PDF File:").grid(row=0, column=0, sticky="w", pady=5)
        self.pdf_path_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.pdf_path_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(left_frame, text="Browse", command=self.browse_pdf).grid(row=0, column=2, padx=5, pady=5)
        
        # Model selection
        ttk.Label(left_frame, text="LLM Model:").grid(row=1, column=0, sticky="w", pady=5)
        self.model_var = tk.StringVar(value="")
        self.model_dropdown = ttk.Combobox(left_frame, textvariable=self.model_var, width=28)
        self.model_dropdown.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(left_frame, text="Refresh", command=self.update_model_list).grid(row=1, column=2, padx=5, pady=5)
        
        # Embedding model selection
        ttk.Label(left_frame, text="Embedding Model:").grid(row=2, column=0, sticky="w", pady=5)
        self.embedding_model_var = tk.StringVar(value="nomic-embed-text:latest")
        ttk.Entry(left_frame, textvariable=self.embedding_model_var, width=30).grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Load PDF button
        ttk.Button(left_frame, text="Load PDF", command=self.load_pdf).grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")
        
        # Document info frame
        self.doc_info = InfoDisplay(left_frame)
        self.doc_info.grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)
        
        # Resource usage frame
        self.resource_display = ResourceDisplayPanel(left_frame)
        self.resource_display.grid(row=5, column=0, columnspan=3, sticky="ew", pady=10)
    
    def create_right_panel(self):
        """Create the right panel with Q&A functionality."""
        right_frame = ttk.LabelFrame(self, text="Research Paper Q&A", padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_frame.columnconfigure(1, weight=1)
        right_frame.rowconfigure(1, weight=1)
        right_frame.rowconfigure(2, weight=1)
        
        # Question input
        ttk.Label(right_frame, text="Question:").grid(row=0, column=0, sticky="w", pady=5)
        self.question_var = tk.StringVar()
        question_entry = ttk.Entry(right_frame, textvariable=self.question_var, width=50)
        question_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        question_entry.bind("<Return>", lambda e: self.ask_question())
        ttk.Button(right_frame, text="Ask", command=self.ask_question).grid(row=0, column=2, padx=5, pady=5)
        
        # Answer display
        ttk.Label(right_frame, text="Answer:").grid(row=1, column=0, sticky="nw", pady=5)
        self.answer_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, width=50, height=20)
        self.answer_text.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # Chat history
        history_frame = ttk.LabelFrame(right_frame, text="Q&A History", padding=10)
        history_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=10)
        
        self.history_text = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, width=50, height=10)
        self.history_text.pack(fill=tk.BOTH, expand=True)
        self.history_text.config(state=tk.DISABLED)
    
    def browse_pdf(self):
        """Open file dialog to select a PDF file."""
        pdf_file = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if pdf_file:
            self.pdf_path_var.set(pdf_file)
            self.status_bar.set_status(f"Selected: {os.path.basename(pdf_file)}")
    
    def update_model_list(self):
        """Update the model dropdown with available models from Ollama."""
        self.status_bar.set_status("Fetching available models from Ollama...")
        try:
            models = self.ollama_client.list_models()
            if models:
                self.model_dropdown['values'] = models
                # Set default model if available
                for model in models:
                    if 'gemma' in model.lower():
                        self.model_var.set(model)
                        break
                    elif 'llama' in model.lower():
                        self.model_var.set(model)
                        break
                
                # If no default set yet, use the first model
                if not self.model_var.get() and models:
                    self.model_var.set(models[0])
                    
                self.status_bar.set_status(f"Found {len(models)} models")
            else:
                self.status_bar.set_status("No models found. Is Ollama running?")
        except Exception as e:
            self.status_bar.set_status(f"Error fetching models: {str(e)}")
            if self.logger:
                self.logger.log_error("fetch_models", str(e))
    
    def load_pdf(self):
        """Load and process the selected PDF file."""
        pdf_path = self.pdf_path_var.get()
        if not pdf_path:
            messagebox.showwarning("Warning", "Please select a PDF file first.")
            return
            
        model = self.model_var.get()
        if not model:
            messagebox.showwarning("Warning", "Please select an LLM model.")
            return
            
        embedding_model = self.embedding_model_var.get()
        if not embedding_model:
            messagebox.showwarning("Warning", "Please specify an embedding model.")
            return
        
        # Update client with selected models
        self.ollama_client.model = model
        self.ollama_client.embedding_model = embedding_model
        
        # Start resource monitoring
        self.resource_monitor.start()
        
        # Begin processing
        self.status_bar.set_status(f"Loading PDF: {os.path.basename(pdf_path)}")
        self.pdf_start_time = time.time()
        
        try:
            # Process in a separate thread to avoid freezing UI
            threading.Thread(target=self._process_pdf, args=(pdf_path,), daemon=True).start()
        except Exception as e:
            self.status_bar.set_status(f"Error loading PDF: {str(e)}")
            if self.logger:
                self.logger.log_error("load_pdf", str(e))
            self.resource_monitor.stop()
    
    def _process_pdf(self, pdf_path):
        """Process the PDF in a background thread."""
        try:
            from ..core.pdf_processor import PDFProcessor
            
            # Extract text from PDF
            processor = PDFProcessor(pdf_path)
            text = processor.extract_text()
            
            # Create new DocumentQA instance
            self.document_qa = DocumentQA(self.ollama_client)
            self.document_qa.load_document(text)
            
            # Update UI with document info
            self.after(0, self._update_document_info)
            
            # Calculate processing time
            self.pdf_end_time = time.time()
            processing_time = self.pdf_end_time - self.pdf_start_time
            
            # Log the PDF load
            if self.logger:
                self.logger.log_pdf_load(
                    pdf_path=pdf_path,
                    model=self.ollama_client.model,
                    embedding_model=self.ollama_client.embedding_model,
                    processing_time=processing_time,
                    title=self.document_qa.title,
                    authors=self.document_qa.authors
                )
            
            # Update status
            self.after(0, lambda: self.status_bar.set_status(
                f"PDF loaded in {processing_time:.2f} seconds. Ready for questions!"
            ))
            
            # Stop resource monitoring
            self.resource_monitor.stop()
            
        except Exception as e:
            self.after(0, lambda: self.status_bar.set_status(f"Error processing PDF: {str(e)}"))
            if self.logger:
                self.logger.log_error("process_pdf", str(e))
            self.resource_monitor.stop()
    
    def _update_document_info(self):
        """Update the UI with document information."""
        if self.document_qa:
            self.doc_info.update(
                title=self.document_qa.title,
                authors=self.document_qa.authors,
                chunks=len(self.document_qa.chunks)
            )
    
    def ask_question(self):
        """Process a question about the document."""
        question = self.question_var.get().strip()
        if not question:
            messagebox.showwarning("Warning", "Please enter a question.")
            return
            
        if not self.document_qa:
            messagebox.showwarning("Warning", "Please load a PDF document first.")
            return
        
        # Clear answer box and prepare for new answer
        self.answer_text.delete(1.0, tk.END)
        self.answer_text.insert(tk.END, "Thinking...")
        self.answer_text.update()
        
        # Start resource monitoring
        self.resource_monitor.start()
        
        # Begin processing
        self.status_bar.set_status("Processing question...")
        self.query_start_time = time.time()
        
        try:
            # Process in a separate thread to avoid freezing UI
            threading.Thread(target=self._process_question, args=(question,), daemon=True).start()
        except Exception as e:
            self.status_bar.set_status(f"Error processing question: {str(e)}")
            if self.logger:
                self.logger.log_error("process_question", str(e))
            self.resource_monitor.stop()
    
    def _process_question(self, question):
        """Process the question in a background thread."""
        try:
            # Get answer from document
            answer = self.document_qa.answer_question(question)
            
            # Calculate processing time
            self.query_end_time = time.time()
            query_time = self.query_end_time - self.query_start_time
            
            # Log the query
            if self.logger:
                self.logger.log_query(
                    question=question,
                    answer=answer,
                    model=self.ollama_client.model,
                    query_time=query_time
                )
            
            # Update UI with answer
            self.after(0, lambda: self._update_answer(question, answer))
            
            # Update status
            self.after(0, lambda: self.status_bar.set_status(
                f"Question answered in {query_time:.2f} seconds."
            ))
            
            # Stop resource monitoring
            self.resource_monitor.stop()
            
        except Exception as e:
            self.after(0, lambda: self.status_bar.set_status(f"Error processing question: {str(e)}"))
            if self.logger:
                self.logger.log_error("process_question", str(e))
            self.resource_monitor.stop()
    
    def _update_answer(self, question, answer):
        """Update the UI with the answer and add to history."""
        # Update answer box
        self.answer_text.delete(1.0, tk.END)
        self.answer_text.insert(tk.END, answer)
        
        # Add to history
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, f"\nQ: {question}\n")
        self.history_text.insert(tk.END, f"A: {answer}\n")
        self.history_text.insert(tk.END, "-" * 50 + "\n")
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)
        
        # Clear question entry
        self.question_var.set("")
    
    def update_resource_info(self):
        """Update the resource usage info in the UI."""
        try:
            usage = self.resource_monitor.get_current_usage()
            self.resource_display.update(usage)
        except Exception as e:
            print(f"Error updating resource info: {e}")
            
        # Schedule next update
        self.after(1000, self.update_resource_info)
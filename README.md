# PDF Research Paper Q&A System with Ollama

A sophisticated question-answering system designed specifically for research papers using Ollama for document analysis and RAG (Retrieval-Augmented Generation) techniques.

## 🚀 Features

- **Intelligent Document Analysis**: Process and analyze PDF research papers with advanced text extraction
- **RAG Implementation**: Uses Retrieval-Augmented Generation with cosine similarity for accurate information retrieval
- **User-Friendly GUI**: Clean Tkinter interface for easy interaction and document management
- **Advanced Embeddings**: Integrates nomic-embed-text model for high-quality text embeddings
- **Custom API Integration**: Built with custom OllamaClient for seamless API communication

## 🛠️ Technology Stack

- **Python**: Core programming language
- **Ollama**: Document analysis and language model integration
- **Tkinter**: GUI framework for user interface
- **RAG (Retrieval-Augmented Generation)**: For intelligent information retrieval
- **Cosine Similarity**: For finding relevant document sections
- **nomic-embed-text**: Advanced embedding model for text processing

## 📋 Prerequisites

- Python 3.8+
- Ollama installed and running
- Required Python packages (see requirements.txt)

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/Harsh-Negi/pdf_research_qa.git
cd pdf_research_qa
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure Ollama is installed and running on your system

## 🎯 Usage

1. Run the application:
```bash
python main.py
```

2. Upload your PDF research paper using the GUI
3. Ask questions about the document content
4. Get intelligent, context-aware responses based on the paper's content

## 🏗️ Architecture

The system implements a sophisticated RAG pipeline:

1. **PDF Processing**: Extracts and preprocesses text from research papers
2. **Embedding Generation**: Creates vector representations using nomic-embed-text
3. **Similarity Search**: Uses cosine similarity to find relevant document sections
4. **Response Generation**: Leverages Ollama for generating contextual answers

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Harsh Wardhan Singh Negi**
- Email: negirishu30@email.com
- GitHub: [@Harsh-Negi](https://github.com/Harsh-Negi)

## 🙏 Acknowledgments

- Ollama team for the excellent language model framework
- Contributors to the nomic-embed-text model
- Open source community for various Python libraries used

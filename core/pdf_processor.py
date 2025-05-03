"""
PDF Processor for Research Paper Q&A
Handles PDF text extraction and chunking for question answering.
"""

import re
from typing import List, Dict, Any
from PyPDF2 import PdfReader

class PDFProcessor:
    def __init__(self, pdf_path: str):
        """Initialize with the path to a PDF file."""
        self.pdf_path = pdf_path
        
    def extract_text(self) -> str:
        """Extract all text from the PDF."""
        reader = PdfReader(self.pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
        
    def split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split the text into overlapping chunks."""
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            if len(chunk) >= 100:  # Only include chunks with sufficient content
                chunks.append(chunk)
        return chunks

    def extract_metadata(self) -> Dict[str, Any]:
        """Extract metadata from the PDF."""
        reader = PdfReader(self.pdf_path)
        metadata = reader.metadata
        
        result = {}
        if metadata:
            for key in metadata:
                if metadata[key]:
                    clean_key = key
                    if key.startswith('/'):
                        clean_key = key[1:]
                    result[clean_key] = metadata[key]
        
        return result

def extract_authors(text):
    """Extract author names from the PDF text using improved pattern recognition."""
    # Focus on the first few pages where author information typically appears
    first_pages_text = text[:5000]  # Increased from 3000 to capture more content
    lines = first_pages_text.split('\n')
    
    # Multiple approaches to find author information
    potential_author_lines = []
    
    # APPROACH 1: Look for explicit author sections
    author_section_started = False
    author_section_ended = False
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Check for explicit author section markers
        if not author_section_started and re.search(r'\b(authors?:|authors?)[^a-z]', line.lower()):
            author_section_started = True
            potential_author_lines.append(line)
            continue
            
        # Check for end of author section
        if author_section_started and not author_section_ended:
            if re.search(r'\b(abstract|introduction|keywords)[:.]?\s*$', line.lower()) or line == '':
                author_section_ended = True
                continue
            
            # Add lines within the author section
            potential_author_lines.append(line)
    
    # APPROACH 2: Look for affiliation patterns if approach 1 didn't find much
    if len(potential_author_lines) <= 1:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        affiliation_markers = ['university', 'institute', 'department', 'laboratory', 'school of', 'college']
        
        for i, line in enumerate(lines[:30]):  # Focus on the top part of the document
            line = line.strip()
            
            # Skip very short lines or obvious non-author lines
            if len(line) < 3 or re.search(r'\b(abstract|keywords|copyright|proceedings)\b', line.lower()):
                continue
                
            # Email is a strong indicator
            if re.search(email_pattern, line):
                # Get this line and surrounding lines
                start_idx = max(0, i-1)
                end_idx = min(len(lines), i+2)
                for j in range(start_idx, end_idx):
                    if lines[j].strip() and lines[j].strip() not in potential_author_lines:
                        potential_author_lines.append(lines[j].strip())
                        
            # Affiliation indicators
            elif any(marker in line.lower() for marker in affiliation_markers):
                # Look for author line above the affiliation
                if i > 0 and lines[i-1].strip() and lines[i-1].strip() not in potential_author_lines:
                    potential_author_lines.append(lines[i-1].strip())
                potential_author_lines.append(line)
    
    # APPROACH 3: Look for typical author formatting patterns
    if len(potential_author_lines) <= 1:
        for i, line in enumerate(lines[:20]):  # Focus on the beginning
            line = line.strip()
            
            # Skip obvious non-author lines
            if len(line) < 3 or re.search(r'\b(abstract|keywords|copyright|proceedings)\b', line.lower()):
                continue
                
            # Common author separator patterns
            if (',' in line and (' and ' in line.lower() or ' & ' in line)) or \
               (line.count(',') >= 1 and len(line.split(',')) <= 5):  # Reasonable number of commas for author lists
                potential_author_lines.append(line)
                
            # Superscript number patterns common in author lists (e.g., "Author Name¹")
            if re.search(r'[A-Za-z]\s*[¹²³⁴⁵⁶⁷⁸⁹]\s*[,]?', line) or re.search(r'[A-Za-z]\s*\^\s*[1-9]', line):
                potential_author_lines.append(line)
    
    # APPROACH 4: Position-based heuristic (after title, before abstract)
    if len(potential_author_lines) <= 1:
        title_index = -1
        abstract_index = -1
        
        # Find title (usually within first few lines)
        for i, line in enumerate(lines[:10]):
            if len(line) > 20 and not re.search(r'\b(abstract|keywords|copyright|proceedings)\b', line.lower()):
                title_index = i
                break
        
        # Find abstract
        for i, line in enumerate(lines[:50]):  # Look within first 50 lines
            if re.search(r'\b(abstract)[:.]?\s*$', line.lower()):
                abstract_index = i
                break
        
        # If we found title and abstract, look at the lines between them
        if title_index >= 0 and abstract_index > title_index:
            candidate_lines = []
            for i in range(title_index + 1, abstract_index):
                line = lines[i].strip()
                # Skip empty lines and very long lines (likely not author names)
                if line and len(line) < 100:
                    candidate_lines.append(line)
            
            # Take up to 3 lines after the title that look like author info
            for line in candidate_lines[:3]:
                if line not in potential_author_lines:
                    potential_author_lines.append(line)
    
    # Post-processing to clean up and format the author information
    if potential_author_lines:
        # Remove duplicates while preserving order
        unique_lines = []
        for line in potential_author_lines:
            if line not in unique_lines:
                unique_lines.append(line)
        
        # Combine the lines
        result = "\n".join(unique_lines)
        
        # Clean up any markers like "Authors:" at the beginning
        result = re.sub(r'^authors?:?\s*', '', result, flags=re.IGNORECASE)
        
        return result
    
    return "Unable to extract author information"

def extract_title(text):
    """Attempt to extract the title from the PDF text."""
    # Look at the first page
    first_page_text = text[:1500]
    lines = first_page_text.split('\n')
    
    # The title is typically one of the first few non-empty lines
    # and is often longer than author names or other header info
    for i, line in enumerate(lines[:10]):
        line = line.strip()
        
        # Skip empty lines, very short lines, or lines with specific patterns
        if not line or len(line) < 10:
            continue
            
        # Skip lines containing common metadata patterns
        if any(marker in line.lower() for marker in ['doi:', 'issn:', 'volume', 'issue', 'http']):
            continue
            
        # Skip lines with journal names or copyright info
        if any(marker in line.lower() for marker in ['journal of', 'copyright', 'proceedings']):
            continue
            
        # Skip lines that look like dates
        if re.match(r'^[a-zA-Z]+ \d{1,2}(st|nd|rd|th)?, \d{4}$', line):
            continue
            
        # This is likely the title
        return line
    
    return "Unable to extract title"
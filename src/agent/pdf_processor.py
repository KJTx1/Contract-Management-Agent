"""PDF processing and text extraction."""

import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import PyPDF2

from .config import Config
from .oci_storage import OCIStorage


class PDFProcessor:
    """Handles PDF text extraction and chunking."""
    
    def __init__(self):
        self.config = Config
        self.oci_storage = OCIStorage()
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Tuple[str, int]:
        """Extract text from PDF file.
        
        Returns:
            Tuple of (text_content, page_count)
        """
        try:
            with open(pdf_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                page_count = len(pdf_reader.pages)
                
                text_parts = []
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        # Add page marker for reference
                        text_parts.append(f"[Page {page_num}]\n{page_text}")
                
                full_text = "\n\n".join(text_parts)
                return full_text, page_count
                
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from PDF: {e}")
    
    def extract_text_from_memory(self, pdf_bytes: bytes, filename: str = "unknown.pdf") -> Tuple[str, int]:
        """Extract text from PDF bytes (streaming processing).
        
        Args:
            pdf_bytes: PDF content as bytes
            filename: Original filename for error messages
            
        Returns:
            Tuple of (text_content, page_count)
        """
        try:
            from io import BytesIO
            pdf_stream = BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            page_count = len(pdf_reader.pages)
            
            text_parts = []
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    # Add page marker for reference
                    text_parts.append(f"[Page {page_num}]\n{page_text}")
            
            full_text = "\n\n".join(text_parts)
            return full_text, page_count
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from PDF bytes ({filename}): {e}")
    
    def chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks.
        
        Uses character-based chunking with word boundaries.
        """
        # Clean up text
        text = self._clean_text(text)
        
        # Approximate tokens by characters (rough: 1 token ~= 4 chars)
        char_chunk_size = chunk_size * 4
        char_overlap = overlap * 4
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + char_chunk_size
            
            # Find the last sentence/period before the end
            if end < len(text):
                # Try to break at sentence boundary
                period_pos = text.rfind('. ', start, end)
                if period_pos > start + char_chunk_size // 2:  # Only if reasonable
                    end = period_pos + 1
                else:
                    # Otherwise break at word boundary
                    space_pos = text.rfind(' ', start, end)
                    if space_pos > start:
                        end = space_pos
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start with overlap
            start = end - char_overlap if end < len(text) else end
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page markers for cleaner chunks (we keep them in original)
        text = re.sub(r'\[Page \d+\]\s*', '', text)
        
        # Remove common PDF artifacts
        text = text.replace('\x00', '')
        
        return text.strip()
    
    def extract_metadata_with_llm(self, text: str, filename: str) -> Dict[str, Any]:
        """Extract metadata from document using LLM."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=Config.OPENAI_API_KEY)
            
            # Create prompt for metadata extraction
            prompt = self._create_metadata_prompt(text, filename)
            
            response = client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a logistics document analysis assistant. Extract structured metadata from documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            metadata = json.loads(content)
            
            return metadata
            
        except Exception as e:
            print(f"Warning: LLM metadata extraction failed: {e}")
            return self._extract_basic_metadata(text, filename)
    
    def _create_metadata_prompt(self, text: str, filename: str) -> str:
        """Create prompt for LLM metadata extraction."""
        # Limit text to first 2000 characters for prompt
        text_sample = text[:2000]
        
        return f"""
Extract structured metadata from this logistics document. Return ONLY a valid JSON object.

Document filename: {filename}

Document content (first 2000 characters):
{text_sample}

Extract and return JSON with these fields (use null if not found):
{{
    "customer_name": "Company or customer name",
    "doc_type": "invoice|bill_of_lading|customs|packing_list|other",
    "doc_date": "YYYY-MM-DD format if found",
    "shipment_id": "Shipment or tracking ID",
    "container_id": "Container ID if mentioned",
    "port_of_origin": "Origin port",
    "port_of_destination": "Destination port",
    "invoice_number": "Invoice number",
    "invoice_amount": 12345.67
}}

Return only the JSON object, no other text.
"""
    
    def _extract_basic_metadata(self, text: str, filename: str) -> Dict[str, Any]:
        """Fallback basic metadata extraction using regex."""
        metadata = {
            "customer_name": None,
            "doc_type": "other",
            "doc_date": None,
            "shipment_id": None,
            "container_id": None,
            "port_of_origin": None,
            "port_of_destination": None,
            "invoice_number": None,
            "invoice_amount": None
        }
        
        text_lower = text.lower()
        
        # Detect document type
        if "invoice" in text_lower or "invoice" in filename.lower():
            metadata["doc_type"] = "invoice"
        elif "bill of lading" in text_lower or "b/l" in text_lower:
            metadata["doc_type"] = "bill_of_lading"
        elif "customs" in text_lower:
            metadata["doc_type"] = "customs"
        elif "packing list" in text_lower:
            metadata["doc_type"] = "packing_list"
        
        # Extract dates (simple pattern)
        date_pattern = r'\b(\d{4}[-/]\d{2}[-/]\d{2})\b'
        date_match = re.search(date_pattern, text)
        if date_match:
            metadata["doc_date"] = date_match.group(1).replace('/', '-')
        
        # Extract invoice number
        invoice_pattern = r'invoice\s*#?\s*:?\s*([A-Z0-9-]+)'
        invoice_match = re.search(invoice_pattern, text, re.IGNORECASE)
        if invoice_match:
            metadata["invoice_number"] = invoice_match.group(1)
        
        # Extract container ID
        container_pattern = r'\b([A-Z]{4}\d{7})\b'
        container_match = re.search(container_pattern, text)
        if container_match:
            metadata["container_id"] = container_match.group(1)
        
        return metadata
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def calculate_bytes_hash(self, pdf_bytes: bytes) -> str:
        """Calculate SHA256 hash of PDF bytes."""
        return hashlib.sha256(pdf_bytes).hexdigest()
    
    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes."""
        return file_path.stat().st_size
    
    def get_bytes_size(self, pdf_bytes: bytes) -> int:
        """Get size of PDF bytes."""
        return len(pdf_bytes)
    
    async def process_pdf_from_memory(self, pdf_bytes: bytes, filename: str, oci_url: str) -> Dict[str, Any]:
        """Process PDF bytes directly from OCI (streaming processing).
        
        Args:
            pdf_bytes: PDF content as bytes
            filename: Original filename
            oci_url: OCI Object Storage URL
            
        Returns:
            Dict containing processing results
        """
        try:
            # Extract text and metadata from bytes
            text_content, page_count = self.extract_text_from_memory(pdf_bytes, filename)
            
            # Generate metadata
            metadata = self._extract_basic_metadata(text_content, filename)
            
            # Calculate file properties from bytes
            file_hash = self.calculate_bytes_hash(pdf_bytes)
            file_size = self.get_bytes_size(pdf_bytes)
            
            # Create chunks
            chunks = self.chunk_text(text_content)
            
            return {
                "text_content": text_content,
                "page_count": page_count,
                "chunks": chunks,
                "metadata": metadata,
                "file_hash": file_hash,
                "file_size": file_size,
                "oci_url": oci_url,
                "filename": filename
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to process PDF bytes ({filename}): {e}")
    
    async def process_pdf_with_oci(self, pdf_path: Path) -> Dict[str, Any]:
        """Process PDF with OCI storage integration.
        
        Returns:
            Dict containing processing results and OCI object URL
        """
        try:
            # Extract text and metadata
            text_content, page_count = self.extract_text_from_pdf(pdf_path)
            
            # Generate metadata
            metadata = self.extract_metadata(text_content)
            
            # Calculate file properties
            file_hash = self.calculate_file_hash(pdf_path)
            file_size = self.get_file_size(pdf_path)
            
            # Upload to OCI Object Storage
            oci_url = None
            if self.oci_storage.is_available():
                oci_url = await self.oci_storage.upload_document(str(pdf_path))
                if oci_url:
                    print(f"PDF uploaded to OCI: {oci_url}")
                else:
                    print("Warning: Failed to upload to OCI, using local path")
            else:
                print("OCI storage not available, using local path")
            
            # Create chunks
            chunks = self.create_chunks(text_content)
            
            return {
                "text_content": text_content,
                "page_count": page_count,
                "metadata": metadata,
                "file_hash": file_hash,
                "file_size": file_size,
                "chunks": chunks,
                "oci_url": oci_url,
                "local_path": str(pdf_path)
            }
            
        except Exception as e:
            print(f"Error processing PDF with OCI: {e}")
            return {
                "text_content": "",
                "page_count": 0,
                "metadata": {},
                "file_hash": "",
                "file_size": 0,
                "chunks": [],
                "oci_url": None,
                "local_path": str(pdf_path),
                "error": str(e)
            }


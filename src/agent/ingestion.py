"""Document ingestion pipeline."""

import shutil
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .config import Config
from .database import Database
from .pdf_processor import PDFProcessor
from .vector_operations import VectorStore, EmbeddingGenerator


class DocumentIngestionPipeline:
    """Complete pipeline for ingesting PDF documents."""
    
    def __init__(self):
        self.db = Database()
        self.pdf_processor = PDFProcessor()
        self.vector_store = VectorStore()
        self.embedding_gen = EmbeddingGenerator()
    
    async def ingest_document(self, pdf_path: Path, use_llm_metadata: bool = True) -> str:
        """Ingest a single PDF document.
        
        Args:
            pdf_path: Path to PDF file
            use_llm_metadata: Whether to use LLM for metadata extraction
        
        Returns:
            Document ID
        """
        print(f"\n📄 Ingesting: {pdf_path.name}")
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        try:
            # 1. Extract text from PDF
            print("  └─ Extracting text...")
            text_content, page_count = self.pdf_processor.extract_text_from_pdf(pdf_path)
            
            if not text_content.strip():
                raise ValueError("No text content extracted from PDF")
            
            # 2. Extract metadata
            print("  └─ Extracting metadata...")
            if use_llm_metadata and Config.OPENAI_API_KEY:
                metadata = self.pdf_processor.extract_metadata_with_llm(text_content, pdf_path.name)
            else:
                metadata = self.pdf_processor._extract_basic_metadata(text_content, pdf_path.name)
            
            # 3. Store PDF (local only)
            print("  └─ Storing PDF...")
            stored_pdf_path, oci_url = await self._store_pdf(pdf_path, doc_id)
            pdf_url = f"file://{stored_pdf_path.absolute()}"
            
            # 4. Insert document record
            file_size = self.pdf_processor.get_file_size(pdf_path)
            
            doc_data = {
                "doc_id": doc_id,
                "filename": pdf_path.name,
                "pdf_path": str(stored_pdf_path),
                "pdf_url": pdf_url,
                "file_size": file_size,
                "page_count": page_count,
                "processing_status": "processing",
                **metadata
            }
            
            self.db.insert_document(doc_data)
            
            # 5. Chunk text
            print("  └─ Chunking text...")
            chunks = self.pdf_processor.chunk_text(
                text_content,
                chunk_size=Config.CHUNK_SIZE,
                overlap=Config.CHUNK_OVERLAP
            )
            
            print(f"  └─ Created {len(chunks)} chunks")
            
            # 6. Generate embeddings and store
            print("  └─ Generating embeddings...")
            embeddings = self.embedding_gen.generate_embeddings(chunks)
            
            # Add to FAISS
            embedding_ids = self.vector_store.add_vectors(embeddings)
            
            # 7. Store chunks in database
            print("  └─ Storing chunks...")
            for chunk_idx, (chunk_text, embedding_id) in enumerate(zip(chunks, embedding_ids)):
                chunk_data = {
                    "doc_id": doc_id,
                    "chunk_index": chunk_idx,
                    "chunk_text": chunk_text,
                    "chunk_embedding_id": embedding_id,
                    "customer_name": metadata.get("customer_name"),
                    "doc_type": metadata.get("doc_type"),
                    "doc_date": metadata.get("doc_date"),
                    "shipment_id": metadata.get("shipment_id"),
                    "pdf_url": pdf_url
                }
                self.db.insert_chunk(chunk_data)
            
            # 8. Update document status
            self.db.update_document_status(doc_id, "completed")
            
            print(f"  ✅ Successfully ingested document: {doc_id}")
            print(f"     Customer: {metadata.get('customer_name', 'N/A')}")
            print(f"     Type: {metadata.get('doc_type', 'N/A')}")
            print(f"     Date: {metadata.get('doc_date', 'N/A')}")
            
            return doc_id
            
        except Exception as e:
            error_msg = f"Ingestion failed: {str(e)}"
            print(f"  ❌ {error_msg}")
            
            # Update status as failed
            try:
                self.db.update_document_status(doc_id, "failed", error_msg)
            except:
                pass
            
            raise RuntimeError(error_msg)
    
    async def _store_pdf(self, pdf_path: Path, doc_id: str) -> tuple[Path, Optional[str]]:
        """Store PDF locally (OCI upload disabled for now).
        
        Returns:
            Tuple of (local_path, None)
        """
        # Store locally only
        local_storage_path = Config.PDF_STORAGE_DIR / f"{doc_id}_{pdf_path.name}"
        shutil.copy2(pdf_path, local_storage_path)
        
        print("  └─ Stored locally (OCI upload disabled)")
        
        return local_storage_path, None
    
    async def ingest_from_oci(self, use_llm_metadata: bool = True) -> Dict[str, Any]:
        """Ingest all PDFs from OCI Object Storage using streaming processing (no local storage).
        
        Returns:
            Dict with ingestion results
        """
        print("🔄 Starting OCI Object Storage streaming ingestion...")
        
        if not hasattr(self.pdf_processor, 'oci_storage') or not self.pdf_processor.oci_storage.is_available():
            raise RuntimeError("OCI Object Storage not available")
        
        # List documents in OCI (check root and common prefixes)
        documents = []
        
        # Try root first
        root_docs = await self.pdf_processor.oci_storage.list_documents(prefix="")
        documents.extend(root_docs)
        
        # Try common prefixes
        for prefix in ["documents/", "pdfs/", "files/", "data/"]:
            try:
                prefix_docs = await self.pdf_processor.oci_storage.list_documents(prefix=prefix)
                documents.extend(prefix_docs)
            except:
                pass  # Ignore errors for prefixes that don't exist
        
        pdf_documents = [doc for doc in documents if doc['name'].lower().endswith('.pdf')]
        
        if not pdf_documents:
            print("❌ No PDF documents found in OCI Object Storage")
            return {"success": False, "message": "No PDF documents found"}
        
        print(f"📄 Found {len(pdf_documents)} PDF documents in OCI")
        
        results = {
            "success": True,
            "total_documents": len(pdf_documents),
            "processed": 0,
            "errors": 0,
            "documents": []
        }
        
        for doc in pdf_documents:
            try:
                print(f"\n📄 Processing: {doc['name']}")
                
                # Stream PDF bytes from OCI to memory (no local storage)
                pdf_bytes = await self.pdf_processor.oci_storage.get_document_bytes(doc['url'])
                if not pdf_bytes:
                    print(f"❌ Failed to stream {doc['name']} from OCI")
                    results["errors"] += 1
                    continue
                
                # Process PDF bytes directly from memory (no temp files)
                print("  └─ Processing PDF from memory...")
                processing_result = await self.pdf_processor.process_pdf_from_memory(
                    pdf_bytes, doc['name'], doc['url']
                )
                
                # Generate document ID
                doc_id = str(uuid.uuid4())
                
                # Extract metadata
                print("  └─ Extracting metadata...")
                if use_llm_metadata and Config.OPENAI_API_KEY:
                    metadata = self.pdf_processor.extract_metadata_with_llm(
                        processing_result["text_content"], doc['name']
                    )
                else:
                    metadata = processing_result["metadata"]
                
                # Store document record (with OCI URL, no local path)
                doc_data = {
                    "doc_id": doc_id,
                    "filename": doc['name'],
                    "pdf_path": f"oci://{doc['url']}",  # OCI URL stored as path reference
                    "pdf_url": doc['url'],  # OCI URL
                    "file_size": processing_result["file_size"],
                    "page_count": processing_result["page_count"],
                    "processing_status": "processing",
                    **metadata
                }
                
                self.db.insert_document(doc_data)
                
                # Process chunks
                print("  └─ Chunking text...")
                chunks = processing_result["chunks"]
                print(f"  └─ Created {len(chunks)} chunks")
                
                # Generate embeddings and store
                print("  └─ Generating embeddings...")
                embeddings = self.embedding_gen.generate_embeddings(chunks)
                
                # Add to FAISS
                embedding_ids = self.vector_store.add_vectors(embeddings)
                
                # Store chunks in database
                print("  └─ Storing chunks...")
                for chunk_idx, (chunk_text, embedding_id) in enumerate(zip(chunks, embedding_ids)):
                    chunk_data = {
                        "doc_id": doc_id,
                        "chunk_index": chunk_idx,
                        "chunk_text": chunk_text,
                        "chunk_embedding_id": embedding_id,
                        "customer_name": metadata.get("customer_name"),
                        "doc_type": metadata.get("doc_type"),
                        "doc_date": metadata.get("doc_date"),
                        "shipment_id": metadata.get("shipment_id"),
                        "pdf_url": doc['url']
                    }
                    self.db.insert_chunk(chunk_data)
                
                # Update document status
                self.db.update_document_status(doc_id, "completed")
                
                results["documents"].append({
                    "doc_id": doc_id,
                    "name": doc['name'],
                    "size": doc['size'],
                    "oci_url": doc['url'],
                    "chunks": len(chunks)
                })
                results["processed"] += 1
                
                print(f"✅ Successfully ingested: {doc['name']}")
                print(f"   Customer: {metadata.get('customer_name', 'Unknown')}")
                print(f"   Type: {metadata.get('doc_type', 'other')}")
                print(f"   Date: {metadata.get('doc_date', 'Unknown')}")
                
            except Exception as e:
                print(f"❌ Error processing {doc['name']}: {e}")
                results["errors"] += 1
        
        print(f"\n🎉 OCI streaming ingestion complete!")
        print(f"   📄 Processed: {results['processed']}")
        print(f"   ❌ Errors: {results['errors']}")
        
        return results

    async def ingest_directory(self, directory_path: Path, use_llm_metadata: bool = True) -> Dict[str, Any]:
        """Ingest all PDFs from a directory.
        
        Returns:
            Summary of ingestion results
        """
        pdf_files = list(directory_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {directory_path}")
            return {"total": 0, "successful": 0, "failed": 0}
        
        print(f"\n📁 Found {len(pdf_files)} PDF files to ingest")
        
        successful = []
        failed = []
        
        for pdf_path in pdf_files:
            try:
                doc_id = await self.ingest_document(pdf_path, use_llm_metadata)
                successful.append((pdf_path.name, doc_id))
            except Exception as e:
                failed.append((pdf_path.name, str(e)))
        
        # Print summary
        print(f"\n📊 Ingestion Summary:")
        print(f"  Total: {len(pdf_files)}")
        print(f"  Successful: {len(successful)}")
        print(f"  Failed: {len(failed)}")
        
        if failed:
            print("\n  Failed files:")
            for filename, error in failed:
                print(f"    - {filename}: {error}")
        
        return {
            "total": len(pdf_files),
            "successful": len(successful),
            "failed": len(failed),
            "successful_docs": successful,
            "failed_docs": failed
        }


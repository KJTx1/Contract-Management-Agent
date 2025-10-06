"""SQLite database operations for metadata and chunks."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

from .config import Config


class Database:
    """Handles all SQLite database operations."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Config.DB_PATH
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            # Documents table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    pdf_path TEXT NOT NULL,
                    pdf_url TEXT,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_size INTEGER,
                    page_count INTEGER,
                    
                    -- Extracted metadata
                    customer_name TEXT,
                    doc_type TEXT,
                    doc_date TEXT,
                    shipment_id TEXT,
                    container_id TEXT,
                    port_of_origin TEXT,
                    port_of_destination TEXT,
                    invoice_number TEXT,
                    invoice_amount REAL,
                    
                    -- Status
                    processing_status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    
                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Chunks table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    chunk_embedding_id INTEGER,
                    
                    -- Inherited metadata for quick filtering
                    customer_name TEXT,
                    doc_type TEXT,
                    doc_date TEXT,
                    shipment_id TEXT,
                    pdf_url TEXT,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for faster queries
            cur.execute("CREATE INDEX IF NOT EXISTS idx_doc_type ON documents(doc_type)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_customer ON documents(customer_name)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_doc_date ON documents(doc_date)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_shipment ON documents(shipment_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_id)")
            
            conn.commit()
    
    def insert_document(self, doc_data: Dict[str, Any]) -> str:
        """Insert a new document."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            columns = ", ".join(doc_data.keys())
            placeholders = ", ".join(["?" for _ in doc_data])
            
            cur.execute(f"""
                INSERT INTO documents ({columns})
                VALUES ({placeholders})
            """, list(doc_data.values()))
            
            return doc_data["doc_id"]
    
    def insert_chunk(self, chunk_data: Dict[str, Any]) -> int:
        """Insert a document chunk."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO chunks (
                    doc_id, chunk_index, chunk_text, chunk_embedding_id,
                    customer_name, doc_type, doc_date, shipment_id, pdf_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chunk_data["doc_id"],
                chunk_data["chunk_index"],
                chunk_data["chunk_text"],
                chunk_data.get("chunk_embedding_id"),
                chunk_data.get("customer_name"),
                chunk_data.get("doc_type"),
                chunk_data.get("doc_date"),
                chunk_data.get("shipment_id"),
                chunk_data.get("pdf_url")
            ))
            
            return cur.lastrowid
    
    def insert_chunks_batch(self, chunks_data: List[Dict[str, Any]]) -> List[int]:
        """Insert multiple chunks in a single transaction for better performance."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            # Prepare data for batch insert
            batch_data = []
            for chunk_data in chunks_data:
                batch_data.append((
                    chunk_data["doc_id"],
                    chunk_data["chunk_index"],
                    chunk_data["chunk_text"],
                    chunk_data.get("chunk_embedding_id"),
                    chunk_data.get("customer_name"),
                    chunk_data.get("doc_type"),
                    chunk_data.get("doc_date"),
                    chunk_data.get("shipment_id"),
                    chunk_data.get("pdf_url")
                ))
            
            # Execute batch insert
            cur.executemany("""
                INSERT INTO chunks (
                    doc_id, chunk_index, chunk_text, chunk_embedding_id,
                    customer_name, doc_type, doc_date, shipment_id, pdf_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_data)
            
            # Return the IDs of inserted chunks
            if cur.lastrowid is not None:
                first_id = cur.lastrowid - len(batch_data) + 1
                return list(range(first_id, cur.lastrowid + 1))
            else:
                # Fallback: return sequential IDs starting from 1
                return list(range(1, len(batch_data) + 1))
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get a document by ID."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,))
            row = cur.fetchone()
            return dict(row) if row else None
    
    def get_chunks_by_ids(self, chunk_ids: List[int]) -> List[Dict]:
        """Get multiple chunks by their IDs."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            placeholders = ", ".join(["?" for _ in chunk_ids])
            cur.execute(f"""
                SELECT * FROM chunks
                WHERE chunk_id IN ({placeholders})
            """, chunk_ids)
            
            return [dict(row) for row in cur.fetchall()]
    
    def search_chunks(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict]:
        """Search chunks with metadata filters."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            query = "SELECT * FROM chunks WHERE 1=1"
            params = []
            
            if filters:
                for key, value in filters.items():
                    query += f" AND {key} = ?"
                    params.append(value)
            
            query += f" LIMIT {limit}"
            
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]
    
    def update_document_status(self, doc_id: str, status: str, error_message: Optional[str] = None):
        """Update document processing status."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE documents
                SET processing_status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
                WHERE doc_id = ?
            """, (status, error_message, doc_id))
    
    def get_documents_by_filters(self, filters: Dict[str, Any], limit: int = 100) -> List[Dict]:
        """Get documents matching metadata filters."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            query = "SELECT * FROM documents WHERE 1=1"
            params = []
            
            for key, value in filters.items():
                query += f" AND {key} = ?"
                params.append(value)
            
            query += f" LIMIT {limit}"
            
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]
    
    def get_all_documents(self, limit: int = 100) -> List[Dict]:
        """Get all documents."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM documents ORDER BY created_at DESC LIMIT {limit}")
            return [dict(row) for row in cur.fetchall()]
    
    def delete_document(self, doc_id: str):
        """Delete a document and its chunks."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) as count FROM documents")
            doc_count = cur.fetchone()["count"]
            
            cur.execute("SELECT COUNT(*) as count FROM chunks")
            chunk_count = cur.fetchone()["count"]
            
            cur.execute("SELECT COUNT(DISTINCT customer_name) as count FROM documents WHERE customer_name IS NOT NULL")
            customer_count = cur.fetchone()["count"]
            
            return {
                "total_documents": doc_count,
                "total_chunks": chunk_count,
                "unique_customers": customer_count
            }


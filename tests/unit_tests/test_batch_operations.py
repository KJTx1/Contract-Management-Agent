"""Unit tests for batch database operations."""

import pytest
from unittest.mock import Mock, patch
from typing import List, Dict, Any

from agent.database import Database


class TestBatchOperations:
    """Test batch database operations."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database for testing."""
        db = Database()
        
        # Mock the connection context manager
        mock_conn = Mock()
        mock_cur = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        
        with patch.object(db, 'get_connection') as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_conn
            mock_get_conn.return_value.__exit__.return_value = None
            yield db
    
    def test_insert_chunks_batch_success(self, mock_db):
        """Test successful batch insertion of chunks."""
        # Prepare test data
        chunks_data = [
            {
                "doc_id": "doc1",
                "chunk_index": 0,
                "chunk_text": "chunk 1",
                "chunk_embedding_id": 1,
                "customer_name": "Test Corp",
                "doc_type": "invoice",
                "doc_date": "2024-01-01",
                "shipment_id": "SHIP001",
                "pdf_url": "oci://test.pdf"
            },
            {
                "doc_id": "doc1",
                "chunk_index": 1,
                "chunk_text": "chunk 2",
                "chunk_embedding_id": 2,
                "customer_name": "Test Corp",
                "doc_type": "invoice",
                "doc_date": "2024-01-01",
                "shipment_id": "SHIP001",
                "pdf_url": "oci://test.pdf"
            }
        ]
        
        # Mock the cursor to return a lastrowid
        mock_cur = Mock()
        mock_cur.lastrowid = 100
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cur
        
        with patch.object(mock_db, 'get_connection') as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_conn
            mock_get_conn.return_value.__exit__.return_value = None
            
            # Execute batch insert
            result = mock_db.insert_chunks_batch(chunks_data)
            
            # Verify results
            assert result == [99, 100]  # lastrowid - len + 1 to lastrowid
            mock_cur.executemany.assert_called_once()
            
            # Verify the SQL query
            call_args = mock_cur.executemany.call_args
            sql_query = call_args[0][0]
            assert "INSERT INTO chunks" in sql_query
            assert "doc_id, chunk_index, chunk_text" in sql_query
    
    def test_insert_chunks_batch_with_none_values(self, mock_db):
        """Test batch insertion with None values."""
        chunks_data = [
            {
                "doc_id": "doc1",
                "chunk_index": 0,
                "chunk_text": "chunk 1",
                "chunk_embedding_id": None,  # None value
                "customer_name": None,  # None value
                "doc_type": "invoice",
                "doc_date": None,  # None value
                "shipment_id": None,  # None value
                "pdf_url": "oci://test.pdf"
            }
        ]
        
        mock_cur = Mock()
        mock_cur.lastrowid = 50
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cur
        
        with patch.object(mock_db, 'get_connection') as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_conn
            mock_get_conn.return_value.__exit__.return_value = None
            
            # Execute batch insert
            result = mock_db.insert_chunks_batch(chunks_data)
            
            # Verify results
            assert result == [50]
            mock_cur.executemany.assert_called_once()
            
            # Verify the data was properly prepared
            call_args = mock_cur.executemany.call_args
            batch_data = call_args[0][1]
            assert len(batch_data) == 1
            assert batch_data[0] == (
                "doc1", 0, "chunk 1", None, None, "invoice", None, None, "oci://test.pdf"
            )
    
    def test_insert_chunks_batch_empty_list(self, mock_db):
        """Test batch insertion with empty list."""
        mock_cur = Mock()
        mock_cur.lastrowid = 0
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cur
        
        with patch.object(mock_db, 'get_connection') as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_conn
            mock_get_conn.return_value.__exit__.return_value = None
            
            # Execute batch insert with empty list
            result = mock_db.insert_chunks_batch([])
            
            # Verify results
            assert result == []
            mock_cur.executemany.assert_called_once()
    
    def test_insert_chunks_batch_large_dataset(self, mock_db):
        """Test batch insertion with large dataset."""
        # Create a large dataset
        chunks_data = []
        for i in range(100):
            chunks_data.append({
                "doc_id": f"doc{i}",
                "chunk_index": i,
                "chunk_text": f"chunk {i}",
                "chunk_embedding_id": i,
                "customer_name": f"Customer {i}",
                "doc_type": "invoice",
                "doc_date": "2024-01-01",
                "shipment_id": f"SHIP{i:03d}",
                "pdf_url": f"oci://test{i}.pdf"
            })
        
        mock_cur = Mock()
        mock_cur.lastrowid = 1000
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cur
        
        with patch.object(mock_db, 'get_connection') as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_conn
            mock_get_conn.return_value.__exit__.return_value = None
            
            # Execute batch insert
            result = mock_db.insert_chunks_batch(chunks_data)
            
            # Verify results
            assert len(result) == 100
            assert result == list(range(900, 1000))  # lastrowid - len + 1 to lastrowid
            mock_cur.executemany.assert_called_once()
            
            # Verify all data was processed
            call_args = mock_cur.executemany.call_args
            batch_data = call_args[0][1]
            assert len(batch_data) == 100
    
    def test_insert_chunks_batch_transaction_rollback(self, mock_db):
        """Test that batch operations are properly transactional."""
        chunks_data = [
            {
                "doc_id": "doc1",
                "chunk_index": 0,
                "chunk_text": "chunk 1",
                "chunk_embedding_id": 1,
                "customer_name": "Test Corp",
                "doc_type": "invoice",
                "doc_date": "2024-01-01",
                "shipment_id": "SHIP001",
                "pdf_url": "oci://test.pdf"
            }
        ]
        
        mock_cur = Mock()
        mock_cur.executemany.side_effect = Exception("Database error")
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cur
        
        with patch.object(mock_db, 'get_connection') as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_conn
            mock_get_conn.return_value.__exit__.return_value = None
            
            # Execute batch insert that should fail
            with pytest.raises(Exception, match="Database error"):
                mock_db.insert_chunks_batch(chunks_data)
            
            # Verify rollback was called
            mock_conn.rollback.assert_called_once()
            mock_conn.commit.assert_not_called()
    
    def test_batch_vs_individual_performance(self, mock_db):
        """Test that batch operations are more efficient than individual inserts."""
        chunks_data = [
            {
                "doc_id": f"doc{i}",
                "chunk_index": i,
                "chunk_text": f"chunk {i}",
                "chunk_embedding_id": i,
                "customer_name": "Test Corp",
                "doc_type": "invoice",
                "doc_date": "2024-01-01",
                "shipment_id": f"SHIP{i:03d}",
                "pdf_url": f"oci://test{i}.pdf"
            }
            for i in range(10)
        ]
        
        mock_cur = Mock()
        mock_cur.lastrowid = 100
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cur
        
        with patch.object(mock_db, 'get_connection') as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_conn
            mock_get_conn.return_value.__exit__.return_value = None
            
            # Execute batch insert
            mock_db.insert_chunks_batch(chunks_data)
            
            # Verify that executemany was called once (not 10 times)
            mock_cur.executemany.assert_called_once()
            mock_cur.execute.assert_not_called()  # Should not use individual inserts


class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    def test_database_schema_compatibility(self):
        """Test that batch operations are compatible with database schema."""
        # This test verifies that the batch insert SQL is compatible
        # with the expected database schema
        
        db = Database()
        
        # Mock the connection
        mock_cur = Mock()
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cur
        
        with patch.object(db, 'get_connection') as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_conn
            mock_get_conn.return_value.__exit__.return_value = None
            
            # Test data that matches the schema
            chunks_data = [
                {
                    "doc_id": "test_doc",
                    "chunk_index": 0,
                    "chunk_text": "test content",
                    "chunk_embedding_id": 1,
                    "customer_name": "Test Customer",
                    "doc_type": "invoice",
                    "doc_date": "2024-01-01",
                    "shipment_id": "SHIP001",
                    "pdf_url": "oci://test.pdf"
                }
            ]
            
            # Execute batch insert
            db.insert_chunks_batch(chunks_data)
            
            # Verify the SQL query structure
            call_args = mock_cur.executemany.call_args
            sql_query = call_args[0][0]
            
            # Verify all expected columns are present
            expected_columns = [
                "doc_id", "chunk_index", "chunk_text", "chunk_embedding_id",
                "customer_name", "doc_type", "doc_date", "shipment_id", "pdf_url"
            ]
            
            for column in expected_columns:
                assert column in sql_query
            
            # Verify the VALUES clause structure
            assert "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)" in sql_query
    
    def test_data_type_handling(self, mock_db):
        """Test that different data types are handled correctly."""
        chunks_data = [
            {
                "doc_id": "doc1",
                "chunk_index": 0,
                "chunk_text": "chunk with special chars: éñ中文",
                "chunk_embedding_id": 12345,
                "customer_name": "Customer with spaces",
                "doc_type": "bill_of_lading",
                "doc_date": "2024-12-31",
                "shipment_id": "SHIP-001-ABC",
                "pdf_url": "oci://namespace/bucket/document.pdf"
            }
        ]
        
        mock_cur = Mock()
        mock_cur.lastrowid = 100
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cur
        
        with patch.object(mock_db, 'get_connection') as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_conn
            mock_get_conn.return_value.__exit__.return_value = None
            
            # Execute batch insert
            result = mock_db.insert_chunks_batch(chunks_data)
            
            # Verify results
            assert result == [100]
            
            # Verify the data was properly prepared
            call_args = mock_cur.executemany.call_args
            batch_data = call_args[0][1]
            assert len(batch_data) == 1
            
            # Verify all data types are preserved
            row_data = batch_data[0]
            assert row_data[0] == "doc1"  # doc_id
            assert row_data[1] == 0  # chunk_index
            assert row_data[2] == "chunk with special chars: éñ中文"  # chunk_text
            assert row_data[3] == 12345  # chunk_embedding_id
            assert row_data[4] == "Customer with spaces"  # customer_name
            assert row_data[5] == "bill_of_lading"  # doc_type
            assert row_data[6] == "2024-12-31"  # doc_date
            assert row_data[7] == "SHIP-001-ABC"  # shipment_id
            assert row_data[8] == "oci://namespace/bucket/document.pdf"  # pdf_url

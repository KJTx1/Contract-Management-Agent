"""Unit tests for concurrent processing functionality."""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
from typing import Dict, Any, List

from agent.ingestion import DocumentIngestionPipeline
from agent.pdf_processor import PDFProcessor, RateLimitedOpenAIClient
from agent.database import Database
from agent.vector_operations import VectorStore, EmbeddingGenerator


class TestRateLimitedOpenAIClient:
    """Test the rate-limited OpenAI client."""
    
    def test_initialization(self):
        """Test client initialization."""
        client = RateLimitedOpenAIClient(requests_per_minute=60)
        assert client.requests_per_minute == 60
        assert client.min_interval == 1.0  # 60 seconds / 60 requests
        assert isinstance(client.semaphore, asyncio.Semaphore)
        assert client.semaphore._value == 60
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test that rate limiting works correctly."""
        client = RateLimitedOpenAIClient(requests_per_minute=2)  # Very low rate for testing
        
        # Mock the OpenAI client
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"test": "data"}'
        
        with patch('agent.pdf_processor.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            # Test that requests are properly rate limited
            start_time = asyncio.get_event_loop().time()
            
            # Make two requests quickly
            tasks = [
                client.create_completion(model="test", messages=[]),
                client.create_completion(model="test", messages=[])
            ]
            
            await asyncio.gather(*tasks)
            
            end_time = asyncio.get_event_loop().time()
            # Should take at least 1 second due to rate limiting
            assert end_time - start_time >= 0.5  # Allow some tolerance


class TestConcurrentIngestion:
    """Test concurrent document ingestion."""
    
    @pytest.fixture
    def mock_documents(self):
        """Mock documents for testing."""
        return [
            {
                "name": "test1.pdf",
                "url": "oci://namespace/bucket/test1.pdf",
                "size": 1024
            },
            {
                "name": "test2.pdf", 
                "url": "oci://namespace/bucket/test2.pdf",
                "size": 2048
            }
        ]
    
    @pytest.fixture
    def mock_pipeline(self):
        """Create a mock pipeline with mocked dependencies."""
        pipeline = DocumentIngestionPipeline(max_concurrent=2)
        
        # Mock database
        pipeline.db = Mock(spec=Database)
        pipeline.db.insert_document = Mock()
        pipeline.db.insert_chunks_batch = Mock()
        pipeline.db.update_document_status = Mock()
        
        # Mock vector store
        pipeline.vector_store = Mock(spec=VectorStore)
        pipeline.vector_store.add_vectors = Mock(return_value=[1, 2, 3])
        
        # Mock embedding generator
        pipeline.embedding_gen = Mock(spec=EmbeddingGenerator)
        pipeline.embedding_gen.generate_embeddings = Mock(return_value=[[0.1, 0.2], [0.3, 0.4]])
        
        # Mock PDF processor
        pipeline.pdf_processor = Mock(spec=PDFProcessor)
        pipeline.pdf_processor.oci_storage = Mock()
        pipeline.pdf_processor.oci_storage.get_document_bytes = AsyncMock()
        pipeline.pdf_processor.process_pdf_from_memory = AsyncMock()
        pipeline.pdf_processor.extract_metadata_with_llm = AsyncMock()
        
        return pipeline
    
    @pytest.mark.asyncio
    async def test_concurrent_processing_success(self, mock_pipeline, mock_documents):
        """Test successful concurrent processing."""
        # Setup mocks
        mock_pipeline.pdf_processor.oci_storage.get_document_bytes.return_value = b"fake pdf content"
        mock_pipeline.pdf_processor.process_pdf_from_memory.return_value = {
            "text_content": "test content",
            "page_count": 1,
            "chunks": ["chunk1", "chunk2"],
            "metadata": {"customer_name": "Test Corp"},
            "file_size": 1024,
            "file_hash": "hash123"
        }
        mock_pipeline.pdf_processor.extract_metadata_with_llm.return_value = {
            "customer_name": "Test Corp",
            "doc_type": "invoice"
        }
        
        # Test concurrent processing
        result = await mock_pipeline.ingest_documents_concurrent(mock_documents)
        
        # Verify results
        assert result["success"] is True
        assert result["total_documents"] == 2
        assert result["processed"] == 2
        assert result["errors"] == 0
        assert len(result["successful_docs"]) == 2
        
        # Verify database calls
        assert mock_pipeline.db.insert_document.call_count == 2
        assert mock_pipeline.db.insert_chunks_batch.call_count == 2
        assert mock_pipeline.db.update_document_status.call_count == 2
    
    @pytest.mark.asyncio
    async def test_concurrent_processing_with_errors(self, mock_pipeline, mock_documents):
        """Test concurrent processing with some failures."""
        # Setup mocks - first document fails, second succeeds
        def mock_get_bytes(url):
            if "test1.pdf" in url:
                return None  # Simulate failure
            return b"fake pdf content"
        
        mock_pipeline.pdf_processor.oci_storage.get_document_bytes.side_effect = mock_get_bytes
        mock_pipeline.pdf_processor.process_pdf_from_memory.return_value = {
            "text_content": "test content",
            "page_count": 1,
            "chunks": ["chunk1"],
            "metadata": {"customer_name": "Test Corp"},
            "file_size": 1024,
            "file_hash": "hash123"
        }
        mock_pipeline.pdf_processor.extract_metadata_with_llm.return_value = {
            "customer_name": "Test Corp",
            "doc_type": "invoice"
        }
        
        # Test concurrent processing
        result = await mock_pipeline.ingest_documents_concurrent(mock_documents)
        
        # Verify results
        assert result["success"] is True
        assert result["total_documents"] == 2
        assert result["processed"] == 1
        assert result["errors"] == 1
        assert len(result["successful_docs"]) == 1
        assert len(result["failed_docs"]) == 1
    
    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(self, mock_pipeline, mock_documents):
        """Test that semaphore properly limits concurrency."""
        # Create a pipeline with max_concurrent=1
        pipeline = DocumentIngestionPipeline(max_concurrent=1)
        
        # Mock all dependencies
        pipeline.db = Mock(spec=Database)
        pipeline.vector_store = Mock(spec=VectorStore)
        pipeline.embedding_gen = Mock(spec=EmbeddingGenerator)
        pipeline.pdf_processor = Mock(spec=PDFProcessor)
        
        # Track concurrent executions
        concurrent_count = 0
        max_concurrent = 0
        
        async def mock_process_doc(doc):
            nonlocal concurrent_count, max_concurrent
            concurrent_count += 1
            max_concurrent = max(max_concurrent, concurrent_count)
            
            # Simulate processing time
            await asyncio.sleep(0.1)
            
            concurrent_count -= 1
            return {"success": True, "doc_id": "test"}
        
        # Replace the actual processing method
        pipeline._process_single_document = mock_process_doc
        
        # Process multiple documents
        await pipeline.ingest_documents_concurrent(mock_documents)
        
        # Verify that concurrency was limited
        assert max_concurrent <= 1  # Should never exceed semaphore limit
    
    @pytest.mark.asyncio
    async def test_batch_database_operations(self, mock_pipeline):
        """Test that batch database operations are used."""
        # Create a single document for testing
        doc = {
            "name": "test.pdf",
            "url": "oci://namespace/bucket/test.pdf",
            "size": 1024
        }
        
        # Setup mocks
        mock_pipeline.pdf_processor.oci_storage.get_document_bytes.return_value = b"fake pdf content"
        mock_pipeline.pdf_processor.process_pdf_from_memory.return_value = {
            "text_content": "test content",
            "page_count": 1,
            "chunks": ["chunk1", "chunk2", "chunk3"],
            "metadata": {"customer_name": "Test Corp"},
            "file_size": 1024,
            "file_hash": "hash123"
        }
        mock_pipeline.pdf_processor.extract_metadata_with_llm.return_value = {
            "customer_name": "Test Corp",
            "doc_type": "invoice"
        }
        
        # Process document
        result = await mock_pipeline._process_single_document(doc)
        
        # Verify batch operation was used
        assert result["success"] is True
        mock_pipeline.db.insert_chunks_batch.assert_called_once()
        
        # Verify the batch data structure
        call_args = mock_pipeline.db.insert_chunks_batch.call_args[0][0]
        assert len(call_args) == 3  # 3 chunks
        assert all("doc_id" in chunk for chunk in call_args)
        assert all("chunk_text" in chunk for chunk in call_args)


class TestConcurrentIntegration:
    """Integration tests for concurrent processing."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_concurrent_processing(self):
        """Test end-to-end concurrent processing with real components."""
        # This test would require actual OCI setup, so we'll mock it
        pipeline = DocumentIngestionPipeline(max_concurrent=2)
        
        # Mock OCI storage
        pipeline.pdf_processor.oci_storage = Mock()
        pipeline.pdf_processor.oci_storage.get_document_bytes = AsyncMock(return_value=b"fake pdf")
        
        # Mock PDF processing
        pipeline.pdf_processor.process_pdf_from_memory = AsyncMock(return_value={
            "text_content": "test content",
            "page_count": 1,
            "chunks": ["chunk1"],
            "metadata": {"customer_name": "Test Corp"},
            "file_size": 1024,
            "file_hash": "hash123"
        })
        
        # Mock metadata extraction
        pipeline.pdf_processor.extract_metadata_with_llm = AsyncMock(return_value={
            "customer_name": "Test Corp",
            "doc_type": "invoice"
        })
        
        # Mock database operations
        pipeline.db = Mock(spec=Database)
        pipeline.db.insert_document = Mock()
        pipeline.db.insert_chunks_batch = Mock()
        pipeline.db.update_document_status = Mock()
        
        # Mock vector operations
        pipeline.vector_store = Mock(spec=VectorStore)
        pipeline.vector_store.add_vectors = Mock(return_value=[1])
        
        pipeline.embedding_gen = Mock(spec=EmbeddingGenerator)
        pipeline.embedding_gen.generate_embeddings = Mock(return_value=[[0.1, 0.2]])
        
        # Test documents
        documents = [
            {"name": "test1.pdf", "url": "oci://test1.pdf", "size": 1024},
            {"name": "test2.pdf", "url": "oci://test2.pdf", "size": 2048}
        ]
        
        # Run concurrent processing
        result = await pipeline.ingest_documents_concurrent(documents)
        
        # Verify results
        assert result["success"] is True
        assert result["total_documents"] == 2
        assert result["processed"] == 2
        assert result["errors"] == 0
        
        # Verify all components were called
        assert pipeline.pdf_processor.oci_storage.get_document_bytes.call_count == 2
        assert pipeline.pdf_processor.process_pdf_from_memory.call_count == 2
        assert pipeline.db.insert_document.call_count == 2
        assert pipeline.db.insert_chunks_batch.call_count == 2


class TestErrorHandling:
    """Test error handling in concurrent processing."""
    
    @pytest.mark.asyncio
    async def test_exception_handling_in_concurrent_processing(self):
        """Test that exceptions are properly handled in concurrent processing."""
        pipeline = DocumentIngestionPipeline(max_concurrent=2)
        
        # Mock dependencies to raise exceptions
        pipeline.db = Mock(spec=Database)
        pipeline.vector_store = Mock(spec=VectorStore)
        pipeline.embedding_gen = Mock(spec=EmbeddingGenerator)
        pipeline.pdf_processor = Mock(spec=PDFProcessor)
        
        # Make OCI storage raise an exception
        pipeline.pdf_processor.oci_storage = Mock()
        pipeline.pdf_processor.oci_storage.get_document_bytes = AsyncMock(
            side_effect=Exception("OCI connection failed")
        )
        
        documents = [
            {"name": "test1.pdf", "url": "oci://test1.pdf", "size": 1024},
            {"name": "test2.pdf", "url": "oci://test2.pdf", "size": 2048}
        ]
        
        # Run concurrent processing
        result = await pipeline.ingest_documents_concurrent(documents)
        
        # Verify that errors are captured
        assert result["success"] is True  # Overall operation succeeded
        assert result["total_documents"] == 2
        assert result["processed"] == 0
        assert result["errors"] == 2
        assert len(result["failed_docs"]) == 2
        
        # Verify error details
        for failure in result["failed_docs"]:
            assert "error" in failure
            assert "OCI connection failed" in failure["error"]
    
    @pytest.mark.asyncio
    async def test_partial_failure_handling(self):
        """Test handling of partial failures in concurrent processing."""
        pipeline = DocumentIngestionPipeline(max_concurrent=2)
        
        # Mock dependencies
        pipeline.db = Mock(spec=Database)
        pipeline.vector_store = Mock(spec=VectorStore)
        pipeline.embedding_gen = Mock(spec=EmbeddingGenerator)
        pipeline.pdf_processor = Mock(spec=PDFProcessor)
        
        # Setup mixed success/failure scenario
        def mock_get_bytes(url):
            if "test1.pdf" in url:
                return b"fake pdf content"
            else:
                raise Exception("Network error")
        
        pipeline.pdf_processor.oci_storage = Mock()
        pipeline.pdf_processor.oci_storage.get_document_bytes = AsyncMock(side_effect=mock_get_bytes)
        
        pipeline.pdf_processor.process_pdf_from_memory = AsyncMock(return_value={
            "text_content": "test content",
            "page_count": 1,
            "chunks": ["chunk1"],
            "metadata": {"customer_name": "Test Corp"},
            "file_size": 1024,
            "file_hash": "hash123"
        })
        
        pipeline.pdf_processor.extract_metadata_with_llm = AsyncMock(return_value={
            "customer_name": "Test Corp",
            "doc_type": "invoice"
        })
        
        pipeline.vector_store.add_vectors = Mock(return_value=[1])
        pipeline.embedding_gen.generate_embeddings = Mock(return_value=[[0.1, 0.2]])
        
        documents = [
            {"name": "test1.pdf", "url": "oci://test1.pdf", "size": 1024},
            {"name": "test2.pdf", "url": "oci://test2.pdf", "size": 2048}
        ]
        
        # Run concurrent processing
        result = await pipeline.ingest_documents_concurrent(documents)
        
        # Verify mixed results
        assert result["success"] is True
        assert result["total_documents"] == 2
        assert result["processed"] == 1
        assert result["errors"] == 1
        assert len(result["successful_docs"]) == 1
        assert len(result["failed_docs"]) == 1


class TestPerformance:
    """Test performance characteristics of concurrent processing."""
    
    @pytest.mark.asyncio
    async def test_concurrent_vs_sequential_performance(self):
        """Test that concurrent processing is faster than sequential."""
        # This is a performance test that verifies the concurrent approach
        # is actually faster than sequential processing
        
        pipeline = DocumentIngestionPipeline(max_concurrent=3)
        
        # Mock all dependencies
        pipeline.db = Mock(spec=Database)
        pipeline.vector_store = Mock(spec=VectorStore)
        pipeline.embedding_gen = Mock(spec=EmbeddingGenerator)
        pipeline.pdf_processor = Mock(spec=PDFProcessor)
        
        # Mock processing time
        async def mock_process_doc(doc):
            await asyncio.sleep(0.1)  # Simulate processing time
            return {"success": True, "doc_id": "test"}
        
        pipeline._process_single_document = mock_process_doc
        
        # Test with multiple documents
        documents = [
            {"name": f"test{i}.pdf", "url": f"oci://test{i}.pdf", "size": 1024}
            for i in range(6)
        ]
        
        # Measure concurrent processing time
        start_time = asyncio.get_event_loop().time()
        await pipeline.ingest_documents_concurrent(documents)
        concurrent_time = asyncio.get_event_loop().time() - start_time
        
        # Concurrent processing should be faster than sequential
        # With 6 documents and max_concurrent=3, should take ~0.2 seconds
        # Sequential would take ~0.6 seconds
        assert concurrent_time < 0.5  # Should be much faster than sequential

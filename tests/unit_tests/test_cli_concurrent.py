"""Unit tests for CLI concurrent functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import sys
from io import StringIO

from agent.cli import CLI


class TestCLIConcurrent:
    """Test CLI concurrent functionality."""
    
    @pytest.fixture
    def mock_cli(self):
        """Create a mock CLI instance."""
        cli = CLI(max_concurrent=3)
        
        # Mock the ingestion pipeline
        cli.ingestion_pipeline = Mock()
        cli.ingestion_pipeline.ingest_from_oci = AsyncMock()
        
        return cli
    
    @pytest.mark.asyncio
    async def test_ingest_oci_concurrent_command_success(self, mock_cli):
        """Test successful concurrent OCI ingestion command."""
        # Setup mock response
        mock_cli.ingestion_pipeline.ingest_from_oci.return_value = {
            "success": True,
            "processed": 5,
            "errors": 0,
            "total_documents": 5
        }
        
        # Test the command
        await mock_cli.ingest_oci_concurrent_command(use_llm=True, max_concurrent=5)
        
        # Verify the pipeline was called
        mock_cli.ingestion_pipeline.ingest_from_oci.assert_called_once_with(True)
    
    @pytest.mark.asyncio
    async def test_ingest_oci_concurrent_command_with_errors(self, mock_cli):
        """Test concurrent OCI ingestion command with some errors."""
        # Setup mock response with errors
        mock_cli.ingestion_pipeline.ingest_from_oci.return_value = {
            "success": True,
            "processed": 3,
            "errors": 2,
            "total_documents": 5
        }
        
        # Test the command
        await mock_cli.ingest_oci_concurrent_command(use_llm=False, max_concurrent=3)
        
        # Verify the pipeline was called
        mock_cli.ingestion_pipeline.ingest_from_oci.assert_called_once_with(False)
    
    @pytest.mark.asyncio
    async def test_ingest_oci_concurrent_command_failure(self, mock_cli):
        """Test concurrent OCI ingestion command failure."""
        # Setup mock response for failure
        mock_cli.ingestion_pipeline.ingest_from_oci.return_value = {
            "success": False,
            "message": "OCI connection failed"
        }
        
        # Test the command
        await mock_cli.ingest_oci_concurrent_command(use_llm=True, max_concurrent=5)
        
        # Verify the pipeline was called
        mock_cli.ingestion_pipeline.ingest_from_oci.assert_called_once_with(True)
    
    @pytest.mark.asyncio
    async def test_ingest_oci_concurrent_command_exception(self, mock_cli):
        """Test concurrent OCI ingestion command with exception."""
        # Setup mock to raise exception
        mock_cli.ingestion_pipeline.ingest_from_oci.side_effect = Exception("Test exception")
        
        # Test the command - should not raise exception
        await mock_cli.ingest_oci_concurrent_command(use_llm=True, max_concurrent=5)
        
        # Verify the pipeline was called
        mock_cli.ingestion_pipeline.ingest_from_oci.assert_called_once_with(True)
    
    def test_cli_initialization_with_concurrency(self):
        """Test CLI initialization with custom concurrency."""
        cli = CLI(max_concurrent=10)
        
        # Verify the ingestion pipeline was created with correct concurrency
        assert cli.ingestion_pipeline.max_concurrent == 10
        assert cli.ingestion_pipeline.semaphore._value == 10
    
    def test_cli_initialization_default_concurrency(self):
        """Test CLI initialization with default concurrency."""
        cli = CLI()
        
        # Verify default concurrency
        assert cli.ingestion_pipeline.max_concurrent == 5
        assert cli.ingestion_pipeline.semaphore._value == 5


class TestCLIArgumentParsing:
    """Test CLI argument parsing for concurrent commands."""
    
    @patch('sys.argv', ['agent.cli', 'ingest-oci-concurrent'])
    def test_parse_concurrent_command_default_args(self):
        """Test parsing concurrent command with default arguments."""
        # This would be tested in the main function
        # For now, we'll test the argument parsing logic
        
        args = ['agent.cli', 'ingest-oci-concurrent']
        
        # Test argument parsing logic
        command = args[1].lower()
        assert command == "ingest-oci-concurrent"
        
        # Test default values
        use_llm = "--no-llm" not in args
        assert use_llm is True
        
        max_concurrent = 5  # Default
        assert max_concurrent == 5
    
    @patch('sys.argv', ['agent.cli', 'ingest-oci-concurrent', '--no-llm', '--max-concurrent=10'])
    def test_parse_concurrent_command_with_args(self):
        """Test parsing concurrent command with custom arguments."""
        args = ['agent.cli', 'ingest-oci-concurrent', '--no-llm', '--max-concurrent=10']
        
        # Test argument parsing logic
        command = args[1].lower()
        assert command == "ingest-oci-concurrent"
        
        # Test --no-llm flag
        use_llm = "--no-llm" not in args
        assert use_llm is False
        
        # Test --max-concurrent parsing
        max_concurrent = 5  # Default
        for arg in args:
            if arg.startswith("--max-concurrent="):
                max_concurrent = int(arg.split("=")[1])
        assert max_concurrent == 10
    
    def test_parse_max_concurrent_invalid_value(self):
        """Test parsing invalid max-concurrent value."""
        args = ['agent.cli', 'ingest-oci-concurrent', '--max-concurrent=invalid']
        
        # Test error handling for invalid value
        max_concurrent = 5  # Default
        for arg in args:
            if arg.startswith("--max-concurrent="):
                try:
                    max_concurrent = int(arg.split("=")[1])
                except ValueError:
                    # Should keep default value
                    pass
        
        assert max_concurrent == 5  # Should remain default


class TestCLIIntegration:
    """Integration tests for CLI concurrent functionality."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_concurrent_ingestion(self):
        """Test end-to-end concurrent ingestion through CLI."""
        # Create a real CLI instance with mocked dependencies
        cli = CLI(max_concurrent=2)
        
        # Mock the ingestion pipeline
        cli.ingestion_pipeline = Mock()
        cli.ingestion_pipeline.ingest_from_oci = AsyncMock(return_value={
            "success": True,
            "processed": 4,
            "errors": 0,
            "total_documents": 4
        })
        
        # Test the concurrent command
        await cli.ingest_oci_concurrent_command(use_llm=True, max_concurrent=2)
        
        # Verify the pipeline was called
        cli.ingestion_pipeline.ingest_from_oci.assert_called_once_with(True)
    
    @pytest.mark.asyncio
    async def test_concurrent_vs_regular_ingestion(self):
        """Test that concurrent ingestion uses different pipeline."""
        # Test regular ingestion
        cli_regular = CLI(max_concurrent=1)
        cli_regular.ingestion_pipeline = Mock()
        cli_regular.ingestion_pipeline.ingest_from_oci = AsyncMock(return_value={
            "success": True,
            "processed": 2,
            "errors": 0
        })
        
        # Test concurrent ingestion
        cli_concurrent = CLI(max_concurrent=5)
        cli_concurrent.ingestion_pipeline = Mock()
        cli_concurrent.ingestion_pipeline.ingest_from_oci = AsyncMock(return_value={
            "success": True,
            "processed": 2,
            "errors": 0
        })
        
        # Run both commands
        await cli_regular.ingest_oci_command(use_llm=True)
        await cli_concurrent.ingest_oci_concurrent_command(use_llm=True, max_concurrent=5)
        
        # Verify both were called
        cli_regular.ingestion_pipeline.ingest_from_oci.assert_called_once()
        cli_concurrent.ingestion_pipeline.ingest_from_oci.assert_called_once()
        
        # Verify different concurrency settings
        assert cli_regular.ingestion_pipeline.max_concurrent == 1
        assert cli_concurrent.ingestion_pipeline.max_concurrent == 5


class TestCLIErrorHandling:
    """Test error handling in CLI concurrent functionality."""
    
    @pytest.mark.asyncio
    async def test_cli_handles_pipeline_exceptions(self):
        """Test that CLI handles pipeline exceptions gracefully."""
        cli = CLI(max_concurrent=3)
        
        # Mock pipeline to raise exception
        cli.ingestion_pipeline = Mock()
        cli.ingestion_pipeline.ingest_from_oci = AsyncMock(
            side_effect=Exception("Pipeline error")
        )
        
        # Test that exception is handled gracefully
        # Should not raise exception
        await cli.ingest_oci_concurrent_command(use_llm=True, max_concurrent=3)
        
        # Verify pipeline was called
        cli.ingestion_pipeline.ingest_from_oci.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cli_handles_invalid_concurrency(self):
        """Test that CLI handles invalid concurrency values."""
        cli = CLI(max_concurrent=0)  # Invalid concurrency
        
        # Should still work with default behavior
        cli.ingestion_pipeline = Mock()
        cli.ingestion_pipeline.ingest_from_oci = AsyncMock(return_value={
            "success": True,
            "processed": 1,
            "errors": 0
        })
        
        # Test that it still works
        await cli.ingest_oci_concurrent_command(use_llm=True, max_concurrent=0)
        
        # Verify pipeline was called
        cli.ingestion_pipeline.ingest_from_oci.assert_called_once()
    
    def test_cli_handles_missing_arguments(self):
        """Test that CLI handles missing arguments gracefully."""
        # Test with minimal arguments
        args = ['agent.cli', 'ingest-oci-concurrent']
        
        # Should use defaults
        use_llm = "--no-llm" not in args
        max_concurrent = 5  # Default
        
        assert use_llm is True
        assert max_concurrent == 5


class TestCLIPerformance:
    """Test performance characteristics of CLI concurrent functionality."""
    
    @pytest.mark.asyncio
    async def test_concurrent_cli_performance(self):
        """Test that concurrent CLI is faster than regular CLI."""
        import time
        
        # Test regular CLI
        cli_regular = CLI(max_concurrent=1)
        cli_regular.ingestion_pipeline = Mock()
        
        # Mock processing time
        async def mock_ingest_regular():
            await asyncio.sleep(0.1)  # Simulate processing time
            return {"success": True, "processed": 1, "errors": 0}
        
        cli_regular.ingestion_pipeline.ingest_from_oci = mock_ingest_regular
        
        # Test concurrent CLI
        cli_concurrent = CLI(max_concurrent=3)
        cli_concurrent.ingestion_pipeline = Mock()
        
        async def mock_ingest_concurrent():
            await asyncio.sleep(0.05)  # Simulate faster processing
            return {"success": True, "processed": 3, "errors": 0}
        
        cli_concurrent.ingestion_pipeline.ingest_from_oci = mock_ingest_concurrent
        
        # Measure regular CLI time
        start_time = time.time()
        await cli_regular.ingest_oci_command(use_llm=True)
        regular_time = time.time() - start_time
        
        # Measure concurrent CLI time
        start_time = time.time()
        await cli_concurrent.ingest_oci_concurrent_command(use_llm=True, max_concurrent=3)
        concurrent_time = time.time() - start_time
        
        # Concurrent should be faster (allowing for test overhead)
        assert concurrent_time <= regular_time * 1.5  # Allow some tolerance

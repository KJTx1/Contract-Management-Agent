"""Test script for the Logistics RAG MVP."""

import asyncio
import os
import sys
from pathlib import Path

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Only set test key if no real key is present
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "test-key"

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.config import Config
from agent.database import Database
from agent.pdf_processor import PDFProcessor
from agent.vector_operations import VectorStore, EmbeddingGenerator


async def test_database():
    """Test database operations."""
    print("🧪 Testing Database...")
    try:
        db = Database()
        stats = db.get_stats()
        print(f"  ✅ Database initialized")
        print(f"     Documents: {stats['total_documents']}")
        print(f"     Chunks: {stats['total_chunks']}")
        return True
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False


async def test_pdf_processor():
    """Test PDF processing."""
    print("\n🧪 Testing PDF Processor...")
    try:
        processor = PDFProcessor()
        
        # Find a test PDF
        test_pdf = Path("docs/logistics-services-contract-mockup-full.pdf")
        if not test_pdf.exists():
            print(f"  ⚠️  No test PDF found at {test_pdf}")
            return True  # Skip test
        
        print(f"  └─ Processing {test_pdf.name}...")
        
        # Test text extraction
        text, pages = processor.extract_text_from_pdf(test_pdf)
        print(f"  └─ Extracted {len(text)} characters from {pages} pages")
        
        # Test chunking
        chunks = processor.chunk_text(text, chunk_size=500, overlap=50)
        print(f"  ✅ Created {len(chunks)} chunks")
        
        return True
    except Exception as e:
        print(f"  ❌ PDF processor test failed: {e}")
        return False


async def test_vector_store():
    """Test vector store."""
    print("\n🧪 Testing Vector Store...")
    try:
        import numpy as np
        
        vector_store = VectorStore()
        print(f"  ✅ Vector store initialized")
        print(f"     Vectors in index: {vector_store.get_vector_count()}")
        
        # Test adding vectors (mock embeddings)
        if vector_store.get_vector_count() == 0:
            test_vectors = np.random.rand(3, Config.EMBEDDING_DIMENSION).astype(np.float32)
            ids = vector_store.add_vectors(test_vectors)
            print(f"  └─ Added {len(ids)} test vectors")
        
        # Test search
        query_vector = np.random.rand(Config.EMBEDDING_DIMENSION).astype(np.float32)
        distances, indices = vector_store.search(query_vector, k=min(3, vector_store.get_vector_count()))
        print(f"  ✅ Search returned {len(indices)} results")
        
        return True
    except Exception as e:
        print(f"  ❌ Vector store test failed: {e}")
        return False


async def test_config():
    """Test configuration."""
    print("\n🧪 Testing Configuration...")
    try:
        Config.setup_directories()
        print(f"  ✅ Data directory: {Config.DATA_DIR}")
        print(f"  ✅ PDF storage: {Config.PDF_STORAGE_DIR}")
        print(f"  ✅ Database: {Config.DB_PATH}")
        print(f"  ✅ FAISS index: {Config.FAISS_INDEX_PATH}")
        
        # Check if API key is set
        if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "test-key":
            print(f"  ✅ OpenAI API key configured")
        else:
            print(f"  ⚠️  OpenAI API key not configured (set OPENAI_API_KEY environment variable)")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Logistics RAG MVP - System Test\n")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_config),
        ("Database", test_database),
        ("PDF Processor", test_pdf_processor),
        ("Vector Store", test_vector_store),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All systems operational! Ready to ingest documents.")
        print("\nNext steps:")
        print("  1. Set OPENAI_API_KEY environment variable")
        print("  2. python -m agent.cli ingest ./docs")
        print("  3. python -m agent.cli query 'your question'")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())


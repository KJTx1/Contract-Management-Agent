"""Command-line interface for the Logistics RAG Assistant."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from .config import Config
from .ingestion import DocumentIngestionPipeline
from .rag_pipeline import graph
from .database import Database


class CLI:
    """Command-line interface for document ingestion and querying."""
    
    def __init__(self):
        self.ingestion_pipeline = DocumentIngestionPipeline()
        self.db = Database()
    
    async def ingest_command(self, path: str, use_llm: bool = True):
        """Ingest PDF(s) from a file or directory."""
        path_obj = Path(path)
        
        if not path_obj.exists():
            print(f"❌ Path does not exist: {path}")
            return
        
        if path_obj.is_file() and path_obj.suffix.lower() == '.pdf':
            # Ingest single file
            try:
                await self.ingestion_pipeline.ingest_document(path_obj, use_llm)
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif path_obj.is_dir():
            # Ingest directory
            try:
                await self.ingestion_pipeline.ingest_directory(path_obj, use_llm)
            except Exception as e:
                print(f"❌ Error: {e}")
        
        else:
            print(f"❌ Invalid path: must be a PDF file or directory")
    
    async def ingest_oci_command(self, use_llm: bool = True):
        """Ingest PDFs from OCI Object Storage using streaming processing (no local storage)."""
        try:
            result = await self.ingestion_pipeline.ingest_from_oci(use_llm)
            if result["success"]:
                print(f"✅ Successfully processed {result['processed']} documents")
                if result["errors"] > 0:
                    print(f"⚠️  {result['errors']} documents had errors")
            else:
                print(f"❌ Ingestion failed: {result.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def query_command(self, query: str, filters: Optional[dict] = None, top_k: int = 5):
        """Query the document database."""
        try:
            # Run RAG pipeline
            result = await graph.ainvoke(
                {"user_query": query},
                config={"configurable": {"top_k": top_k, "filters": filters or {}}}
            )
            
            print("\n" + result["response"])
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def stats_command(self):
        """Show database statistics."""
        stats = self.db.get_stats()
        
        print("\n📊 Database Statistics")
        print("=" * 50)
        print(f"Total Documents:    {stats['total_documents']}")
        print(f"Total Chunks:       {stats['total_chunks']}")
        print(f"Unique Customers:   {stats['unique_customers']}")
        print()
    
    def list_command(self, limit: int = 20):
        """List recent documents."""
        docs = self.db.get_all_documents(limit=limit)
        
        print(f"\n📄 Recent Documents (showing {len(docs)})")
        print("=" * 100)
        
        for doc in docs:
            status_icon = "✅" if doc['processing_status'] == 'completed' else "⏳"
            print(f"\n{status_icon} {doc['filename']}")
            print(f"   ID: {doc['doc_id']}")
            if doc.get('customer_name'):
                print(f"   Customer: {doc['customer_name']}")
            if doc.get('doc_type'):
                print(f"   Type: {doc['doc_type']}")
            if doc.get('doc_date'):
                print(f"   Date: {doc['doc_date']}")
        
        print()
    
    def interactive_mode(self):
        """Start interactive query mode."""
        print("\n🤖 Logistics RAG Assistant - Interactive Mode")
        print("=" * 50)
        print("Type your questions or 'quit' to exit")
        print("=" * 50 + "\n")
        
        while True:
            try:
                query = input("\n❓ Your question: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! 👋")
                    break
                
                # Run query
                asyncio.run(self.query_command(query))
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


async def main():
    """Main CLI entry point."""
    cli = CLI()
    
    if len(sys.argv) < 2:
        print("\n🚀 Logistics Document RAG Assistant")
        print("=" * 50)
        print("\nUsage:")
        print("  python -m agent.cli ingest <path>     Ingest PDF(s)")
        print("  python -m agent.cli ingest-oci         Ingest from OCI Object Storage (streaming)")
        print("  python -m agent.cli query <question>  Query documents")
        print("  python -m agent.cli interactive        Interactive mode")
        print("  python -m agent.cli stats              Show statistics")
        print("  python -m agent.cli list               List documents")
        print("\nExamples:")
        print("  python -m agent.cli ingest ./docs")
        print("  python -m agent.cli query 'UrbanWear invoices March 2024'")
        print("  python -m agent.cli interactive")
        print()
        return
    
    command = sys.argv[1].lower()
    
    if command == "ingest":
        if len(sys.argv) < 3:
            print("❌ Usage: python -m agent.cli ingest <path>")
            return
        
        path = sys.argv[2]
        use_llm = "--no-llm" not in sys.argv
        await cli.ingest_command(path, use_llm)
    
    elif command == "query":
        if len(sys.argv) < 3:
            print("❌ Usage: python -m agent.cli query <question>")
            return
        
        query = " ".join(sys.argv[2:])
        await cli.query_command(query)
    
    elif command == "interactive":
        cli.interactive_mode()
    
    elif command == "stats":
        cli.stats_command()
    
    elif command == "list":
        cli.list_command()
    
    elif command == "ingest-oci":
        use_llm = "--no-llm" not in sys.argv
        await cli.ingest_oci_command(use_llm)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run without arguments to see usage")


if __name__ == "__main__":
    asyncio.run(main())


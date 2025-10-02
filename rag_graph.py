# rag_graph.py

import faiss
import sqlite3
import openai
from langgraph.graph import Graph

# ---- CONFIG ----
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
DB_PATH = "logistics.db"
FAISS_INDEX_PATH = "faiss_index.index"

# ---- DB Setup ----
def connect_db():
    return sqlite3.connect(DB_PATH)

# ---- LangGraph Nodes ----

# 1. Embedding Node
def embed_query(query: str):
    """Generate embedding for user query."""
    response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=query
    )
    return response["data"][0]["embedding"]

# 2. Retriever Node (FAISS + SQLite)
def retrieve(query_embedding, filters=None, k=5):
    """
    Search FAISS for semantic similarity and apply metadata filters from SQLite.
    Filters: dict with keys like { 'customer_name': 'UrbanWear', 'doc_type': 'invoice' }
    """
    # Load FAISS index
    index = faiss.read_index(FAISS_INDEX_PATH)

    # Search
    D, I = index.search([query_embedding], k)
    
    conn = connect_db()
    cur = conn.cursor()

    results = []
    for idx in I[0]:
        cur.execute("SELECT doc_id, chunk_text, customer_name, doc_type, doc_date, pdf_url FROM logistics_chunks WHERE rowid=?", (idx+1,))
        row = cur.fetchone()
        if not row:
            continue

        # Apply metadata filters
        if filters:
            match = True
            for key, val in filters.items():
                col_idx = {"doc_id":0,"chunk_text":1,"customer_name":2,"doc_type":3,"doc_date":4,"pdf_url":5}[key]
                if str(row[col_idx]) != str(val):
                    match = False
                    break
            if not match:
                continue
        
        results.append({
            "doc_id": row[0],
            "chunk_text": row[1],
            "customer_name": row[2],
            "doc_type": row[3],
            "doc_date": row[4],
            "pdf_url": row[5]
        })

    conn.close()
    return results

# 3. Combiner Node
def combine_context(query, retrieved_chunks):
    """Build prompt with query + context for LLM."""
    context = "\n\n".join([f"[{r['doc_id']}] {r['chunk_text']} (Source: {r['pdf_url']})"
                           for r in retrieved_chunks])
    return f"Question: {query}\n\nRelevant Docs:\n{context}\n\nAnswer clearly and cite sources."

# 4. LLM Node
def generate_answer(prompt):
    """Call LLM with context-enhanced prompt."""
    response = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[{"role": "system", "content": "You are a logistics assistant."},
                  {"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# 5. Output Node
def output_response(answer):
    print("\n=== ANSWER ===\n")
    print(answer)
    print("\n==============\n")


# ---- Graph Assembly ----
def build_graph():
    g = Graph()

    g.add_node("embed_query", embed_query)
    g.add_node("retrieve", retrieve)
    g.add_node("combine", combine_context)
    g.add_node("generate", generate_answer)
    g.add_node("output", output_response)

    g.add_edge("embed_query", "retrieve")
    g.add_edge("retrieve", "combine")
    g.add_edge("combine", "generate")
    g.add_edge("generate", "output")

    g.set_entry_point("embed_query")

    return g

# ---- Runner ----
if __name__ == "__main__":
    user_query = input("Enter your query: ")

    # Example metadata filter (optional)
    filters = {
        "customer_name": "UrbanWear",
        "doc_type": "invoice"
    }

    g = build_graph()
    g.run(user_query, filters=filters)

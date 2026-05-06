"""Simple test to check if services load correctly."""
print("[TEST] Starting simple test...")

print("[TEST] Loading vector store...")
from app.services.vector_store import vector_store
print(f"✓ Vector store loaded. Current docs: {vector_store.count_documents()}")

print("[TEST] Loading RAG service...")
from app.services.rag_service import rag_service
print("✓ RAG service loaded")

print("[TEST] Testing search...")
results = vector_store.search("harga PJUTS", n_results=3)
print(f"✓ Search returned {len(results)} results")

for i, doc in enumerate(results, 1):
    print(f"  {i}. Type: {doc.get('metadata', {}).get('type')}, Distance: {doc.get('distance', 999):.3f}")

print("\n[TEST] All basic tests passed!")

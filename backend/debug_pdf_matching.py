"""Debug script untuk test PDF matching dan response generation."""
import asyncio
from app.services.vector_store import vector_store
from app.services.rag_service import rag_service, IntentDetector
from app.services.response_builder import RuleBasedResponseBuilder

print("="*80)
print("DEBUG: PDF MATCHING & RESPONSE GENERATION")
print("="*80)

# Initialize RAG service (load PDFs)
print("\n[STEP 1] Initializing knowledge base...")
rag_service.initialize_default_knowledge()
print(f"Total documents in vector store: {vector_store.count_documents()}")

# Test queries
test_queries = [
    "Apa itu produk yang ada di PDF?",
    "Berapa harga produk?",
    "Informasi tentang garansi?",
    "Produk apa yang cocok untuk area besar?",
    "Bagaimana cara maintenance?"
]

print("\n[STEP 2] Testing queries...\n")

for message in test_queries:
    print(f"\n{'='*80}")
    print(f"Query: \"{message}\"")
    print(f"{'='*80}")
    
    # Detect intent
    intent = IntentDetector.detect(message)
    print(f"✓ Detected Intent: {intent}")
    
    # Search documents
    context_docs = vector_store.search(message, n_results=10)
    print(f"✓ Found {len(context_docs)} documents from search")
    
    # Rank documents
    context_docs = rag_service._rank_documents_by_intent(context_docs, intent)
    print(f"✓ Ranked to {len(context_docs)} relevant documents")
    
    # Show top 3 docs
    if context_docs:
        print(f"\nTop documents:")
        for i, doc in enumerate(context_docs[:3], 1):
            doc_type = doc.get("metadata", {}).get("type", "unknown")
            doc_source = doc.get("metadata", {}).get("source", "unknown")
            distance = doc.get("distance", 999)
            content_preview = doc.get("content", "")[:100]
            print(f"  {i}. Type: {doc_type}, Source: {doc_source}, Distance: {distance:.3f}")
            print(f"     Content: {content_preview}...")
    
    # Generate response
    response = RuleBasedResponseBuilder.build_response(intent, context_docs, message)
    print(f"\n✓ Generated Response:")
    print(f"  {response[:300]}...")
    
    # Check if uploaded knowledge is used
    uploaded_in_top3 = sum(1 for d in context_docs[:3] if d.get('metadata', {}).get('source') == 'uploaded_knowledge')
    print(f"\n✓ Uploaded knowledge in top 3: {uploaded_in_top3}/3")

print("\n" + "="*80)
print("DEBUG COMPLETE")
print("="*80)

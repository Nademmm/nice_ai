"""Test script untuk product recommendation dari PDF."""
import asyncio
from app.services.vector_store import vector_store
from app.services.rag_service import rag_service, IntentDetector
from app.services.response_builder import RuleBasedResponseBuilder

print("="*80)
print("TEST: PRODUCT RECOMMENDATION FROM PDF")
print("="*80)

# Initialize knowledge base
print("\n[INIT] Initializing knowledge base from PDF...")
rag_service.initialize_default_knowledge()
total_docs = vector_store.count_documents()
print(f"✓ Total documents loaded: {total_docs}")

# Count by type
all_docs = vector_store.get_all_documents()
doc_types = {}
for doc in all_docs:
    doc_type = doc.get('metadata', {}).get('type', 'unknown')
    doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

print(f"✓ Documents by type: {doc_types}")

# Test queries untuk product recommendation
test_queries = [
    "Saya butuh lampu untuk taman rumah saya",
    "Rekomendasi lampu untuk area besar",
    "Lampu apa yang cocok untuk perumahan?",
    "Produk PJUTS apa saja yang tersedia?",
    "Saya ingin penerangan untuk area komersial yang luas",
]

print("\n" + "="*80)
print("TEST QUERIES")
print("="*80)

for i, message in enumerate(test_queries, 1):
    print(f"\n{'─'*80}")
    print(f"Test #{i}: \"{message}\"")
    print(f"{'─'*80}")
    
    # Detect intent
    intent = IntentDetector.detect(message)
    print(f"✓ Intent: {intent}")
    
    # Search documents
    search_results = vector_store.search(message, n_results=15)
    print(f"✓ Search found: {len(search_results)} documents")
    
    # Show top 3 by type
    product_count = sum(1 for d in search_results if d.get('metadata', {}).get('type') in ['product', 'uploaded_knowledge'])
    print(f"✓ Product/uploaded docs in results: {product_count}")
    
    # Rank documents
    ranked_docs = rag_service._rank_documents_by_intent(search_results, intent)
    print(f"✓ After ranking: {len(ranked_docs)} documents")
    
    # Intelligently classify uploaded knowledge as product if relevant
    for doc in ranked_docs:
        if doc.get('metadata', {}).get('source') == 'uploaded_knowledge':
            content = doc.get('content', '').lower()
            product_keywords = ['pjuts', 'watt', 'baterai', 'battery', 'panel surya', 'spesifikasi', 
                               'solar', 'lampu', 'tinggi tiang', 'ah', 'cocok untuk', 'kapasitas']
            if any(keyword in content for keyword in product_keywords):
                doc['metadata']['type'] = 'product'
    
    # Show top docs
    print(f"\n  Top 3 documents:")
    for idx, doc in enumerate(ranked_docs[:3], 1):
        doc_type = doc.get('metadata', {}).get('type', 'unknown')
        doc_source = doc.get('metadata', {}).get('source', 'unknown')
        distance = doc.get('distance', 999)
        print(f"    {idx}. Type: {doc_type}, Source: {doc_source}, Distance: {distance:.3f}")
    
    # Generate response
    response = RuleBasedResponseBuilder.build_response(intent, ranked_docs, message)
    print(f"\n✓ Generated Response:")
    print(f"{response}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)

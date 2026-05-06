"""Test script untuk memastikan product recommendation tidak error."""
import sys
import traceback
from app.services.vector_store import vector_store
from app.services.rag_service import rag_service, IntentDetector
from app.services.response_builder import RuleBasedResponseBuilder

print("="*80)
print("TEST: PRODUCT RECOMMENDATION ERROR FIX")
print("="*80)

try:
    # Initialize knowledge base
    print("\n[INIT] Initializing knowledge base...")
    rag_service.initialize_default_knowledge()
    total_docs = vector_store.count_documents()
    print(f"✓ Total documents loaded: {total_docs}")

    # Test queries
    test_queries = [
        "Saya butuh lampu untuk taman rumah saya",
        "Rekomendasi lampu untuk area besar",
        "Lampu apa yang cocok untuk perumahan?",
    ]

    print("\n" + "="*80)
    print("TESTING QUERIES (Error Check)")
    print("="*80)

    for i, message in enumerate(test_queries, 1):
        print(f"\n{'─'*80}")
        print(f"Test #{i}: \"{message}\"")
        print(f"{'─'*80}")

        try:
            # Detect intent
            intent = IntentDetector.detect(message)
            print(f"✓ Intent: {intent}")

            # Search documents
            search_results = vector_store.search(message, n_results=15)
            print(f"✓ Search found: {len(search_results)} documents")

            # Rank documents
            ranked_docs = rag_service._rank_documents_by_intent(search_results, intent)
            print(f"✓ After ranking: {len(ranked_docs)} documents")

            # Generate response - THIS IS WHERE THE ERROR OCCURRED
            print("✓ Generating response...")
            response = RuleBasedResponseBuilder.build_response(intent, ranked_docs, message)
            print(f"✓ Response generated successfully!")
            print(f"Response preview: {response[:100]}...")

        except Exception as e:
            print(f"❌ ERROR in test #{i}: {e}")
            print(f"Error type: {type(e).__name__}")
            traceback.print_exc()
            continue

    print("\n" + "="*80)
    print("TEST COMPLETE - NO ERRORS!")
    print("="*80)

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

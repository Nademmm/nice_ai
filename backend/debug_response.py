from app.services.vector_store import vector_store
from app.services.rag_service import rag_service, IntentDetector
from app.services.response_builder import RuleBasedResponseBuilder
import asyncio

# Test multiple queries
test_queries = ['lampu', 'harga', 'produk PJUTS', 'garansi', 'berapa watt']

for message in test_queries:
    intent = IntentDetector.detect(message)
    print(f'\n{"="*60}')
    print(f'Query: "{message}"')
    print(f'Intent: {intent}')
    
    context_docs = vector_store.search(message, n_results=10)
    context_docs = rag_service._rank_documents_by_intent(context_docs, intent)
    
    print(f'Docs: {len(context_docs)}')
    if context_docs:
        print(f'Top doc type: {context_docs[0].get("metadata", {}).get("type")}')
        print(f'Top doc distance: {context_docs[0].get("distance", 999):.3f}')
    
    response = RuleBasedResponseBuilder.build_response(intent, context_docs, message)
    print(f'Response preview: {response[:200]}...')
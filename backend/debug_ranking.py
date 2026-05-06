from app.services.rag_service import rag_service, IntentDetector

message = 'harga'
intent = IntentDetector.detect(message)
print(f'Detected intent: {intent}')

context_docs = rag_service.vector_store.search(message, n_results=10)
print(f'Initial docs: {len(context_docs)}')

context_docs = rag_service._rank_documents_by_intent(context_docs, intent)
print(f'Ranked docs: {len(context_docs)}')

faq_count = sum(1 for d in context_docs if d.get('metadata', {}).get('type') == 'faq')
print(f'FAQ docs in ranked: {faq_count}')

for doc in context_docs[:5]:
    print(f'Type: {doc.get("metadata", {}).get("type")}, Distance: {doc.get("distance", 999):.3f}')
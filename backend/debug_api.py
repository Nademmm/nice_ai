from app.services.vector_store import vector_store
from app.services.rag_service import rag_service, IntentDetector
import asyncio

message = 'harga'
intent = IntentDetector.detect(message)
print(f'Intent: {intent}')

# Simulate process_message steps
context_docs = vector_store.search(message, n_results=10)
print(f'Initial docs: {len(context_docs)}')

context_docs = rag_service._rank_documents_by_intent(context_docs, intent)
print(f'Ranked docs: {len(context_docs)}')

uploaded_docs = [d for d in context_docs if d.get('metadata', {}).get('source') == 'uploaded_knowledge']
default_docs = [d for d in context_docs if d.get('metadata', {}).get('source') != 'uploaded_knowledge']
context_docs = uploaded_docs + default_docs
print(f'After priority: uploaded {len(uploaded_docs)}, default {len(default_docs)}')

faq_in_final = sum(1 for d in context_docs if d.get('metadata', {}).get('type') == 'faq')
print(f'FAQ in final docs: {faq_in_final}')

print('\nTesting rag_service.process_message:')
result = asyncio.run(rag_service.process_message(message, 'test'))
print(f'Intent: {result["intent"]}')
print(f'Answer: {result["answer"][:300]}...')
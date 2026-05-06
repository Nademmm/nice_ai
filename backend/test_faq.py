from app.services.response_builder import RuleBasedResponseBuilder
from app.services.vector_store import vector_store

docs = vector_store.search('harga', n_results=10)
print(f'Found {len(docs)} docs')
faq_docs = RuleBasedResponseBuilder.filter_docs_by_type(docs, 'faq')
print(f'FAQ docs: {len(faq_docs)}')
for doc in faq_docs[:2]:
    print(f'Distance: {doc.get("distance", 999):.3f}')
    print(f'Content: {doc["content"][:100]}...')

response = RuleBasedResponseBuilder.build_faq_answer(docs, 'harga')
print('Response:', response[:200])
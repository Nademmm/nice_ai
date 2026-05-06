from app.services.response_builder import RuleBasedResponseBuilder
from app.services.vector_store import vector_store

# Test short query with no relevant docs
docs = vector_store.search('xyz', n_results=10)
print(f'Retrieved {len(docs)} docs for "xyz"')
for doc in docs[:3]:
    print(f'Distance: {doc.get("distance", 999):.3f}')

intent = 'general'
user_input = 'xyz'  # Short query, no relevant docs
response = RuleBasedResponseBuilder.build_response(intent, docs, user_input)
print('Response for short query "xyz":')
print(response)